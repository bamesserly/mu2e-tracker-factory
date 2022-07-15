################################################################################
#
# Attach CO2 endpieces
#
# Only record the epoxy batches, the process duration, and the CPAL.
#
# Don't save straw-by-straw info for this process.
#
# Next step: leak test
#
################################################################################
from guis.common.panguilogger import SetupPANGUILogger

logger = SetupPANGUILogger("root", "CO2")

from tests.do_a_mergedown import run as do_a_mergedown

do_a_mergedown()

from datetime import datetime
import csv
import os
import pyautogui
import sys
from PyQt5.QtCore import QRect, Qt, QTimer, QMetaObject, QCoreApplication, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QBrush
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFrame,
    QInputDialog,
    QLabel,
    QLayout,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from pynput.keyboard import Key, Controller
from pathlib import Path

from data.workers.credentials.credentials import Credentials
from guis.common.dataProcessor import SQLDataProcessor as DP
from guis.common.db_classes.straw_location import CuttingPallet
from guis.common.getresources import GetProjectPaths
from guis.common.gui_utils import except_hook, generateBox
from guis.common.save_straw_workers import saveWorkers
from guis.common.timer import QLCDTimer
from guis.straw.checkstraw import Check, StrawFailedError
from guis.straw.co2.co2 import Ui_MainWindow  ## edit via Qt Designer
from guis.straw.removestraw import removeStraw

pyautogui.FAILSAFE = True  # Move mouse to top left corner to abort script

# to change hitting enter to hitting tab
keyboard = Controller()

kRESET_EXIT_CODE = 12


class CO2EndpieceGUI(QMainWindow):
    LockGUI = pyqtSignal(bool)
    timer_signal = pyqtSignal()

    def __init__(self, paths, webapp=None, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.workerDirectory = paths["co2workers"]
        self.palletDirectory = paths["pallets"]
        self.epoxyDirectory = paths["co2epoxy"]
        self.boardPath = paths["board"]
        self.ui.PortalButtons.buttonClicked.connect(self.Change_worker_ID)
        self.stationID = "C-O2"
        self.credentialChecker = Credentials(self.stationID)
        self.Current_workers = [
            self.ui.Current_worker1,
            self.ui.Current_worker2,
            self.ui.Current_worker3,
            self.ui.Current_worker4,
        ]
        self.portals = [
            self.ui.portal1,
            self.ui.portal2,
            self.ui.portal3,
            self.ui.portal4,
        ]
        self.ui.start.clicked.connect(self.start)
        self.ui.finishInsertion.clicked.connect(self.finish_insertion)
        self.ui.finish.clicked.connect(self.finish)
        self.ui.viewButton.clicked.connect(self.editPallet)

        self.LockGUI.connect(self.lockGUI)

        self.ui.palletNumInput.returnPressed.connect(self.preverify)
        self.ui.epoxyBatchInput.returnPressed.connect(self.preverify)
        self.ui.DP190BatchInput.returnPressed.connect(self.preverify)

        self.setTabOrder(self.ui.palletNumInput, self.ui.epoxyBatchInput)
        self.setTabOrder(self.ui.epoxyBatchInput, self.ui.DP190BatchInput)
        self.setTabOrder(self.ui.DP190BatchInput, self.ui.start)

        self.palletID = ""
        self.palletNum = ""
        self.epoxyBatch = ""
        self.DP190Batch = ""
        self.straws = []
        self.sessionWorkers = []

        self.startTime = 0

        self.ui.sec_disp.setNumDigits(2)
        self.ui.sec_disp.setSegmentStyle(2)
        self.ui.min_disp.setNumDigits(2)
        self.ui.min_disp.setSegmentStyle(2)
        self.ui.hour_disp.setNumDigits(2)
        self.ui.hour_disp.setSegmentStyle(2)
        self.justLogOut = ""
        saveWorkers(self.workerDirectory, self.Current_workers, self.justLogOut)

        # Timing info
        self.timer = QLCDTimer(
            self.ui.hour_disp,
            self.ui.min_disp,
            self.ui.sec_disp,
            lambda: self.timer_signal.emit(),
            max_time=28800,
        )  # 0 - Main Timer: Turns red after 8 hours
        self.timer_signal.connect(self.timer.display)

        self.startTimer = lambda: self.timer.start()
        self.stopTimer = lambda: self.timer.stop()
        self.resetTimer = lambda: self.timer.reset()
        self.mainTimer = self.timer  # data processor wants it
        self.running = lambda: self.timer.isRunning()

        self.timing = False

        # Data Processor
        # Record station and session, not yet procedure or straw location
        # Those are recorded during saveStart
        self.pro = 4
        self.pro_index = self.pro - 1

        # Creating this DP object starts a session (makes a DB entry)
        # and makes a None procedure.
        self.DP = DP(
            gui=self,
            stage="straws",
        )

        # Start it off with the prep tab frozen
        self.LockGUI.emit(False)

    ############################################################################
    # Worker login and gui lock
    ############################################################################
    def Change_worker_ID(self, btn):
        label = btn.text()
        portalNum = self.portals.index(btn)
        if label == "Log In":
            Current_worker, ok = QInputDialog.getText(
                self, "Worker Log In", "Scan your worker ID:"
            )
            Current_worker = Current_worker.upper().strip()
            if not ok:
                return
            if not self.DP.validateWorkerID(Current_worker):
                generateBox("critical", "Login Error", "Invalid worker ID.")
            elif self.DP.workerLoggedIn(Current_worker):
                generateBox(
                    "critical",
                    "Login Error",
                    "This worker ID is already logged in.",
                )
            else:
                # Record login with data processor
                logger.info(f"{Current_worker} logged in")
                self.DP.saveLogin(Current_worker)
                self.sessionWorkers.append(Current_worker)
                self.Current_workers[portalNum].setText(Current_worker)
                logger.info("Welcome " + self.Current_workers[portalNum].text() + " :)")
                btn.setText("Log Out")
                self.ui.tab_widget.setCurrentIndex(1)

        elif label == "Log Out":
            worker = self.Current_workers[portalNum].text()
            self.justLogOut = self.Current_workers[portalNum].text()
            self.sessionWorkers.remove(worker)
            self.DP.saveLogout(worker)
            logger.info("Goodbye " + worker + " :(")
            self.Current_workers[portalNum].setText("")
            btn.setText("Log In")

        # Recheck credentials
        self.LockGUI.emit(self.DP.checkCredentials())

        saveWorkers(self.workerDirectory, self.Current_workers, self.justLogOut)
        self.justLogOut = ""

    def lockGUI(self, credentials):
        if credentials:
            self.ui.tab_widget.setTabText(1, "CO2 Endpiece")
            self.ui.tab_widget.setTabEnabled(1, True)
        else:
            self.ui.tab_widget.setCurrentIndex(0)
            self.ui.tab_widget.setTabText(1, "CO2 Endpiece *Locked*")
            self.ui.tab_widget.setTabEnabled(1, False)

    ############################################################################
    # Start Button
    # Verify inputs (cpal, epoxy batch, dp190 batch), save them in the DB
    # Start the timer
    ############################################################################
    def start(self):
        valid = [bool() for i in range(4)]

        # Get inputs
        self.palletNum = self.ui.palletNumInput.text().strip().upper()
        self.epoxyBatch = self.ui.epoxyBatchInput.text().strip().upper()
        self.DP190Batch = self.ui.DP190BatchInput.text().strip().upper()

        # Verify inputs (and color the UI fields accordingly)
        # Also: set the pallet number and ID, for use in creating the DP's
        # procedure.
        valid[1] = self.verifyPalletNumber(self.palletNum)
        valid[2] = self.verifyEpoxyBatch(self.epoxyBatch)
        valid[3] = self.verifyDP190Batch(self.DP190Batch)
        valid[0] = self.find_cpal_file(self.palletNum)

        self.update_colors(valid)

        if not all(valid):
            return

        # Verify pallet file has record of prep and ohms being completed
        pallet_checker = Check()
        try:
            pallet_checker.check(self.palletNum, ["prep", "ohms"])
        except StrawFailedError as error:
            QMessageBox.critical(
                self,
                "Testing Error",
                "Unable to test this pallet:\n" + error.message,
            )
            self.editPallet()
            return

        # Record procedure in the DB
        procedure_is_recorded = self.record_procedure()
        if not procedure_is_recorded:
            return

        # save epoxies in the DB
        self.DP.procedure.setEpoxyBatch(self.epoxyBatch[-9:].replace(".", ""))
        self.DP.procedure.setDP190(self.DP190Batch[-3:])

        # disable entry fields, enable finish button
        self.update_ui_for_running()

        self.timing = True
        self.startTimer()

    # initialize procedure and commit it to the DB
    def record_procedure(self):
        try:
            print(self.getPalletID(), self.getPalletNumber())
            self.DP.saveStart()

        # "Can't create pallet".
        #
        # This pallet isn't in DB, so we try to create it, BUT the palletID
        # we're using (which we got from the txt files) is already filled with
        # (another pallet's) straws.
        #
        # Most likely way we got here? User mis-typed the CPAL.
        except AssertionError:
            logger.debug(
                f"Can't create pallet error. {self.getPalletID()}-{self.getPalletNumber()}."
            )
            reply = QMessageBox.question(
                self,
                f"{self.getPalletNumber()} Not Found in DB",
                (
                    "Check that pallet number was entered correctly."
                    "\n\nPress Cancel to start over."
                    "\n\nOr press OK to proceed with this pallet, but please notify Ben."
                ),
                QMessageBox.Ok,
                QMessageBox.Cancel,
            )
            if reply == QMessageBox.Ok:
                logger.debug(
                    f"Clearing old straws from {self.getPalletID()}. Creating new straw location {self.getPalletNumber()} at {self.getPalletID()}."
                )
                CuttingPallet.remove_straws_from_pallet_by_id(
                    int(self.getPalletID()[-2:])
                )
                self.DP.saveStart()
            else:
                logger.debug(f"Aborting pallet creation.")
                self.resetGUI()
                return False

        # Procedure already exists!
        if not self.DP.procedure.isNew():
            logger.debug(
                f"CO2 endpieces already installed for this pallet {self.getPalletNumber()}."
            )
            reply = QMessageBox.question(
                self,
                "Endpieces Already Installed",
                (
                    f"According to the DB, endpieces have already been installed for {self.getPalletNumber()}. "
                    "Do want to proceed?"
                ),
                QMessageBox.Yes,
                QMessageBox.No,
            )
            if reply == QMessageBox.No:
                self.resetGUI()
                return False

        # can't get isNew() to work
        # if self.DP.procedure.getStrawLocation().isNew():
        #    logger.warning("New pallet entered into the DB! It won't have any straws associated with it!")

        return True

    # Enable and disable various buttons and fields while the timer is running
    def update_ui_for_running(self):
        self.ui.palletNumInput.setDisabled(True)
        self.ui.epoxyBatchInput.setDisabled(True)
        self.ui.DP190BatchInput.setDisabled(True)
        self.ui.start.setDisabled(True)
        self.ui.viewButton.setEnabled(True)
        self.ui.finishInsertion.setEnabled(True)
        self.ui.finish.setDisabled(True)

    ############################################################################
    # Finish insertion button
    # Stop timer, enable finish button
    ############################################################################
    def finish_insertion(self):
        self.timing = False
        self.stopTimer()
        self.ui.finishInsertion.setDisabled(True)
        self.ui.finish.setEnabled(True)

    ############################################################################
    # Edit pallet button
    ############################################################################
    def editPallet(self):
        rem = removeStraw(self.sessionWorkers)
        rem.palletDirectory = self.palletDirectory
        CPAL, lastTask, straws, passfail, CPALID = rem.getPallet(self.palletNum)
        rem.displayPallet(CPAL, lastTask, straws, passfail)
        rem.exec_()

    ############################################################################
    # Finish button
    # Mark procedure as finished in DB, save data to spreadsheet, save duration
    # to db, reset gui
    ############################################################################
    def finish(self):
        self.DP.saveFinish()
        self.saveData()
        self.resetGUI()

    ############################################################################
    # Save data (called by finish)
    ############################################################################
    def saveData(self):
        self.savePalletDataToText()
        self.saveProcessDataToText()
        process_duration = (
            self.ui.hour_disp.intValue() * 3600
            + self.ui.min_disp.intValue() * 60
            + self.ui.sec_disp.intValue()
        )
        self.DP.procedure.setEpoxyTime(process_duration)

    def savePalletDataToText(self):
        pfile = self.palletDirectory / self.palletID / str(self.palletNum + ".csv")

        # get straws
        with open(pfile, "r") as palletFile:
            dummy = csv.reader(palletFile)
            pallet = []
            for line in dummy:
                pallet.append(line)
            for row in range(len(pallet)):
                if row == len(pallet) - 1:
                    for entry in range(len(pallet[row])):
                        if entry > 1 and entry < 50:
                            if entry % 2 == 0:
                                self.straws.append(pallet[row][entry])

        with open(pfile, "r+") as palletWrite:
            text = (
                palletWrite.readlines()
            )  # read whole file so next write will be at end of file
            if (
                text[-1][-1] != "\n"
            ):  # if last character of last line is not newline, add it
                palletWrite.write("\n")
            palletWrite.write(datetime.now().strftime("%Y-%m-%d_%H:%M") + ",")
            palletWrite.write(self.stationID + ",")
            for straw in self.straws:
                palletWrite.write(straw)
                palletWrite.write(",")
                if straw != "":
                    palletWrite.write("P")
                palletWrite.write(",")
            i = 0
            for worker in self.sessionWorkers:
                palletWrite.write(worker.lower())
                if i != len(self.sessionWorkers) - 1:
                    palletWrite.write(",")
                i = i + 1

    def saveProcessDataToText(self):
        efile = self.epoxyDirectory / str(self.palletNum + ".csv")
        with open(efile, "w+") as ef:
            header = "Timestamp, Pallet ID, Epoxy Batch #, DP190 Batch #, CO2 endpiece insertion time (H:M:S), workers ***NEWLINE: Comments (optional)***\n"
            ef.write(header)
            ef.write(datetime.now().strftime("%Y-%m-%d_%H:%M") + ",")
            ef.write(
                self.palletID + "," + self.epoxyBatch + "," + self.DP190Batch + ","
            )
            ef.write(
                str(self.ui.hour_disp.intValue())
                + ":"
                + str(self.ui.min_disp.intValue())
                + ":"
                + str(self.ui.sec_disp.intValue())
                + ","
            )
            i = 0
            for worker in self.sessionWorkers:
                ef.write(worker)
                if i != len(self.sessionWorkers) - 1:
                    ef.write(",")
                i = i + 1
            if self.ui.commentBox.document().toPlainText() != "":
                ef.write("\n" + self.ui.commentBox.document().toPlainText())

        QMessageBox.about(self, "Save", "Data saved successfully!")

    ############################################################################
    # Reset gui (called by finish)
    # Sorry, the easiest way I can find to properly reset the DP is to
    # completely reboot the gui
    ############################################################################
    def resetGUI(self):
        if self.DP:
            self.DP.handleClose()
        QCoreApplication.exit(kRESET_EXIT_CODE)

    ############################################################################
    # Verification functions
    ############################################################################
    def verifyPalletNumber(self, pallet_num):
        # Verifies that the given pallet id is of a valid format
        verify = True

        # check that last 4 characters of ID are integers
        if len(pallet_num) == 8:
            verify = pallet_num[
                4:7
            ].isnumeric()  # makes sure last four digits are numbers
        else:
            verify = False  # fails if palled_num

        if not pallet_num.upper().startswith("CPAL"):
            verify = False

        return verify

    def verifyEpoxyBatch(self, eb):
        eb = eb.strip().upper()

        if len(eb) != 13:
            return False
        if not eb.startswith("CO2."):
            return False
        if eb[4:9].isnumeric():
            # Month
            if not int(eb[4:6]) in range(13):
                return False
            # Day
            if not int(eb[6:8]) in range(1, 32):
                return False
            # Year
            if not int(eb[8:10]) in range(
                17, (datetime.now().year - 2000) + 1
            ):  # Max: current year
                return False
        if not eb[10] == ".":
            return False
        if not eb[11:13].isnumeric():
            return False

        return True

    def verifyDP190Batch(self, string):
        string = string.upper().strip()

        if len(string) == 9:
            return string.startswith("DP190.") and string[6:9].isnumeric()
        else:
            return False

    ############################################################################
    # Misc
    ############################################################################
    def find_cpal_file(self, pallet):
        for palletid in os.listdir(self.palletDirectory):
            for pallet in os.listdir(self.palletDirectory / palletid):
                if self.palletNum + ".csv" == pallet:
                    self.palletID = palletid
                    return True
        QMessageBox.critical(
            self,
            "Pallet File Error",
            f"Unable to find CPAL File for {self.palletNum}",
        )
        return False

    # Color the input fields whether they're valid (green) or not (red)
    def update_colors(self, valid):
        if valid[0] and valid[1]:
            self.ui.palletNumInput.setStyleSheet("")
            self.ui.palletNumInput.setText(self.palletNum)
            self.ui.viewButton.setEnabled(True)
        else:
            self.ui.palletNumInput.setStyleSheet("background-color:rgb(255, 0, 0)")

        if valid[2]:
            self.ui.epoxyBatchInput.setStyleSheet("")
            self.ui.epoxyBatchInput.setText(self.epoxyBatch)
        else:
            self.ui.epoxyBatchInput.setStyleSheet("background-color:rgb(255, 0, 0)")

        if valid[3]:
            self.ui.DP190BatchInput.setStyleSheet("")
            self.ui.DP190BatchInput.setText(self.DP190Batch)
        else:
            self.ui.DP190BatchInput.setStyleSheet("background-color:rgb(255, 0, 0)")

    def preverify(self):
        lineEdit = self.focusWidget()

        string = lineEdit.text().strip().upper()

        verify = {
            self.ui.palletNumInput: self.verifyPalletNumber(string),
            self.ui.epoxyBatchInput: self.verifyEpoxyBatch(string),
            self.ui.DP190BatchInput: self.verifyDP190Batch(string),
        }

        if verify[lineEdit]:
            lineEdit.setText(string)
            lineEdit.setStyleSheet("")
            self.tab()

            if lineEdit == self.ui.palletNumInput:
                self.palletNum = string
                self.ui.viewButton.setEnabled(True)

        else:
            lineEdit.setFocus()
            lineEdit.selectAll()
            lineEdit.setStyleSheet("background-color:rgb(255, 0, 0)")

    def tab(self):
        keyboard.press(Key.tab)

    def closeEvent(self, event):
        event.accept()
        if self.DP:
            self.DP.handleClose()
        QCoreApplication.exit(0)

    def getPalletID(self):
        return self.palletID

    def getPalletNumber(self):
        return self.palletNum


def run():
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    paths = GetProjectPaths()
    ctr = CO2EndpieceGUI(paths)
    ctr.show()
    exit_code = app.exec_()


if __name__ == "__main__":
    run()
