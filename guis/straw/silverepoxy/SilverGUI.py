################################################################################
#
# Silver Epoxy Application GUI
#
# After laser cutting, we attach endpieces with silver epoxy.
#
# Just record CPAL number, epoxy batch, and timer
#
# Next step: Load onto LPALs
#
################################################################################
from guis.common.panguilogger import SetupPANGUILogger

logger = SetupPANGUILogger("root", "Silver")

import pyautogui
import time
import os
import csv
import sys
import threading
from datetime import datetime
from pathlib import Path
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal

# from PyQt5.QtCore import QRect, Qt, QTimer, QMetaObject, QCoreApplication
from PyQt5.QtGui import QFont, QPalette, QColor, QBrush
from PyQt5.QtWidgets import (
    QLabel,
    QFrame,
    QStackedWidget,
    QWidget,
    QPushButton,
    QSizePolicy,
    QCheckBox,
    QInputDialog,
    QVBoxLayout,
    QLayout,
    QSpinBox,
    QLineEdit,
    QMainWindow,
    QApplication,
    QComboBox,
    QMessageBox,
)
from data.workers.credentials.credentials import Credentials
from guis.common.db_classes.straw import Straw
from guis.common.db_classes.straw_location import StrawPosition, CuttingPallet
from guis.common.getresources import GetProjectPaths
from guis.common.save_straw_workers import saveWorkers
from guis.straw.checkstraw import *
from guis.straw.remove import Ui_Dialogw
from guis.straw.removestraw import removeStraw
from guis.straw.silverepoxy.silver import Ui_MainWindow  ## edit via Qt Designer

# import guis.common.dataProcessor as DP
from guis.common.dataProcessor import SQLDataProcessor as DP
from guis.common.gui_utils import generateBox, except_hook
from guis.common.timer import QLCDTimer

pyautogui.FAILSAFE = True  # Move mouse to top left corner to abort script


class Silver(QMainWindow):

    LockGUI = pyqtSignal(bool)
    timer_signal = pyqtSignal()

    def __init__(self, paths, webapp=None, parent=None):
        super(Silver, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.stationID = "silv"
        self.palletDirectory = paths["pallets"]
        self.workerDirectory = paths["silverworkers"]
        self.silverDirectory = paths["silverdata"]
        self.boardPath = paths["board"]
        self.ui.PortalButtons.buttonClicked.connect(self.Change_worker_ID)
        # self.ui.tab_widget.setCurrentIndex(0)
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

        self.ui.start.clicked.connect(self.collectInitialData)
        self.ui.finishInsertion.clicked.connect(self.timeUp)
        self.ui.finish.clicked.connect(self.saveData)
        self.ui.viewButton.clicked.connect(self.editPallet)

        self.ui.epoxyBatchInput.setText("N/A")

        # Data to be saved
        self.palletID = ""
        self.palletNum = ""
        self.epoxyBatch = ""
        self.sessionWorkers = []
        self.straws = []
        self.temp = True
        self.dataSaved = False

        self.LockGUI.connect(self.lockGUI)
        self.credentialChecker = Credentials(self.stationID)
        self.justLogOut = ""
        saveWorkers(self.workerDirectory, self.Current_workers, self.justLogOut)

        # Timing info
        self.ui.sec_disp.setNumDigits(2)
        self.ui.sec_disp.setSegmentStyle(2)
        self.ui.min_disp.setNumDigits(2)
        self.ui.min_disp.setSegmentStyle(2)
        self.ui.hour_disp.setNumDigits(2)
        self.ui.hour_disp.setSegmentStyle(2)

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
        self.pro = 9
        self.pro_index = self.pro - 1
        self.DP = DP(
            gui=self,
            stage="straws",
        )

        # Start it off with the prep tab frozen
        self.LockGUI.emit(False)

    def getPalletID(self):
        return self.palletID

    def getPalletNumber(self):
        return self.palletNum

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
                # self.ui.tab_widget.setCurrentIndex(1)

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
            self.ui.tabWidget.setTabText(1, "Silver Epoxy")
            self.ui.tabWidget.setTabEnabled(1, True)
        else:
            self.ui.tabWidget.setTabText(1, "Silver Epoxy *Locked*")
            self.ui.tabWidget.setTabEnabled(1, False)

    def updateBoard(self):
        status = []
        try:
            with open(self.boardPath + "Progression Status.csv") as readfile:
                data = csv.reader(readfile)
                for row in data:
                    for pallet in row:
                        status.append(pallet)
            status[int(self.palletID[6:]) - 1] == 100
            with open(self.boardPath + "Progression Status.csv", "w") as writefile:
                i = 0
                for pallet in status:
                    writefile.write(pallet)
                    if i != 23:
                        writefile.write(",")
                    i = i + 1
        except IOError:
            print(
                "Could not update board due to board file being accessed concurrently"
            )

    # Start Button
    def collectInitialData(self):
        self.palletNum = self.ui.palletNumInput.text()
        self.epoxyBatch = self.ui.epoxyBatchInput.text()

        valid = [True, True, True]

        # cpal entry has valid format
        if not self.verifyPalletNumber():
            valid[1] = False
            if self.palletNum == "":
                self.ui.palletNumInput.setStyleSheet(
                    "background-color:rgb(149, 186, 255)"
                )
            else:
                self.ui.palletNumInput.setStyleSheet("background-color:rgb(255, 0, 0)")

        # look for cpal file and associated cpalID
        for palletid in os.listdir(self.palletDirectory):
            for pallet in os.listdir(self.palletDirectory / palletid):
                if self.palletNum + ".csv" == pallet:
                    self.palletID = palletid
                    valid[0] = True

        """
        # epoxy batch has valid format
        if not self.verifyEpoxyBatch():
            valid[2] = False
            if self.epoxyBatch == "":
                self.ui.epoxyBatchInput.setStyleSheet(
                    "background-color:rgb(149, 186, 255)"
                )
            else:
                self.ui.epoxyBatchInput.setStyleSheet("background-color:rgb(255, 0, 0)")
        """

        if valid[1]:
            self.ui.palletNumInput.setStyleSheet("")
        if valid[2]:
            self.ui.epoxyBatchInput.setStyleSheet("")

        # Check in the CPAL file that the pre-requisite steps have been
        # completed.
        #
        # This can fail if (case A) pallet file doesn't have all the requisite
        # pre-steps OR if (case B) we can't find a CPAL file (e.g. due to no
        # mergedown, or no consolidate step)
        #
        # Either way, ask user to resolve CPAL file issue and exit
        previousSteps = ["leng", "lasr"]
        check = Check()
        passed = False
        try:
            check.check(self.palletNum, previousSteps)
            passed = True
        except StrawFailedError as error:
            pfiles = check.findPalletFiles(self.palletNum)
            # case A: can't find CPAL file
            if not pfiles:
                logger.error("CPAL file not found.")
                QMessageBox.critical(
                    self,
                    "CPAL File Not Found",
                    "Consolidate process either did not run, or, more likely, "
                    "you need to mergedown on the computer that performed the "
                    "consolidation and then mergedown on this computer. "
                    "Please find or make this file and try again.",
                )
            # case B: CPAL file missing steps or some failed straws on pallet.
            # TODO give user option to edit CPAL file.
            else:
                logger.error(
                    f"{self.palletNum} found in the following cpal files: {pfiles}"
                )
                logger.error(f"{error}")
                logger.error(
                    "None of these files had passing straws for the previous "
                    "straw processing steps."
                )
                QMessageBox.critical(
                    self,
                    "Failed Straws Error",
                    "One or more of these straws has failed a prior straw "
                    "processing step.\nThat, or, something else is wrong with "
                    "the CPAL file. Please resolve this problem in the CPAL "
                    "file and try again.",
                )

                """
                # none of this stuff is currently working
                reply = QMessageBox.critical(
                    self,
                    "Modify CPAL?",
                    "Do you want to view the CPAL file and have the option to "
                    "remove failed straws?",
                    QMessageBox.Yes,
                    QMessageBox.No,
                )

                if reply == QMessageBox.Yes:
                    self.editPallet()
                self.resetGUI()
                """

            sys.exit()

        # Lock starting buttons and fields, unlock finishing buttons and fields
        # Initialize procedure and commit it to the DB
        if all(valid) and passed:
            self.ui.palletNumInput.setDisabled(True)
            self.ui.epoxyBatchInput.setDisabled(True)
            self.ui.start.setDisabled(True)
            self.ui.viewButton.setEnabled(True)
            self.ui.finishInsertion.setEnabled(True)

            # Catch when trying to create this cpal in the DB (consolidate
            # should do this but it doesn't currently) AND failing because
            # this cpal ID still has straws on it (according to the DB).
            try:
                self.DP.saveStart()
            except AssertionError:
                logger.info(
                    "Adding this CPAL to the DB. Clearing the old straws from this CPALID."
                )
                old_cpals = CuttingPallet._queryPalletsByID(
                    int(self.getPalletID()[-2:])
                ).all()
                for cpal in [i for i in old_cpals if not i.isEmpty()]:
                    logger.info(f"Clearing straws from CPAL{cpal.number}.")
                    if len(cpal.getFilledPositions()):
                        cpal.removeAllStraws()
                    assert cpal.isEmpty()
                self.DP.saveStart()

            self.start_timer()

    # set self.palletNum
    def verifyPalletNumber(self, pallet_number=None):
        if not pallet_number:
            pallet_number = self.ui.palletNumInput.text().upper()

        pallet_number = pallet_number.strip().upper()

        if len(pallet_number) != 8:
            return False
        if not pallet_number.startswith("CPAL"):
            return False
        if not pallet_number[4:].isnumeric():
            return False

        """
        for id in range(1, 24):
            file = pallet_number + ".csv"
            path = self.palletDirectory / str("CPALID" + str(id).zfill(2)) / file
            if os.path.exists(path):
                logger.info(f"{pallet_number} has been prepped.")
                QMessageBox.question(
                    self,
                    "Duplicate CPAL Number",
                    "This pallet has been prepped!",
                    QMessageBox.Ok,
                )
                return False
        """

        # verified -- set self.palletNumber
        self.palletNumber = pallet_number
        return True

    # set self.epoxyBatch
    # SE.010122000
    def verifyEpoxyBatch(self, epoxy_batch=None):
        if (
            not len(self.epoxyBatch) == 12
            or not self.epoxyBatch.startswith("SE.")
            or not int(self.epoxyBatch[3:5]) in range(1, 13)
            or not int(self.epoxyBatch[5:7]) in range(1, 32)
            or not int(self.epoxyBatch[7:9])
            in range(17, (datetime.now().year - 2000) + 1)
            or not self.epoxyBatch[-2:].isnumeric()
        ):
            return False
        else:
            return True

    # start timer
    def start_timer(self):
        self.timing = True
        self.startTimer()
        self.temp = False
        # begin = time.time()
        # while self.temp:
        #    running = time.time() - begin
        #    self.ui.hour_disp.display(int(running / 3600))
        #    self.ui.min_disp.display(int(running / 60) % 60)
        #    self.ui.sec_disp.display(int(running) % 60)
        #    app.processEvents()
        #    time.sleep(0.1)
        # self.temp = True
        # self.ui.finishInsertion.setDisabled(True)
        # self.ui.finish.setEnabled(True)

    # stop timer
    def timeUp(self):
        self.timing = False
        self.stopTimer()
        self.DP.saveFinish()
        self.temp = True
        self.ui.finishInsertion.setDisabled(True)
        self.ui.finish.setEnabled(True)

    def saveData(self):
        # save to DB
        # self.DP.procedure.setEpoxyBatch(self.epoxyBatch)
        self.DP.procedure.setEpoxyTime(self.timer.getElapsedTime().total_seconds())

        # update pallet file
        pfile = self.palletDirectory / self.palletID / str(self.palletNum + ".csv")
        if pfile.is_file():
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

            with open(pfile, "a") as palletWrite:
                palletWrite.write(datetime.now().strftime("%Y-%m-%d_%H:%M") + ",silv,")
                for straw in self.straws:
                    palletWrite.write(straw)

                    if straw != "_______":
                        palletWrite.write(",P,")
                    else:
                        palletWrite.write(",_,")

                palletWrite.write(",".join(self.sessionWorkers))

        # save to epoxy file
        sfile = self.silverDirectory / str(self.palletNum + ".csv")
        with open(sfile, "w+") as file:
            header = "Timestamp, Pallet ID, Epoxy Batch #, Endpiece Insertion time (H:M:S), Workers, Comments (optional)\n"
            file.write(header)
            file.write(datetime.now().strftime("%Y-%m-%d_%H:%M") + ",")
            file.write(self.palletID + "," + self.epoxyBatch + ",")
            file.write(
                str(self.ui.hour_disp.intValue())
                + ":"
                + str(self.ui.min_disp.intValue())
                + ":"
                + str(self.ui.sec_disp.intValue())
                + ","
            )
            i = 0
            for worker in self.sessionWorkers:
                file.write(worker)
                if i != len(self.sessionWorkers) - 1:
                    file.write(",")
                i = i + 1
            if self.ui.commentBox.document().toPlainText() != "":
                file.write(self.ui.commentBox.document().toPlainText())

        reply = QMessageBox.question(
            self,
            "Failed Straws",
            "Were all the insertions successful?",
            QMessageBox.Yes,
            QMessageBox.No,
        )

        if reply != QMessageBox.Yes:
            QMessageBox.question(
                self,
                "Pallet cleaned?",
                "Please remove the failed straws.\n The edit pallet menu will pop up next.",
                QMessageBox.Ok,
            )
            self.editPallet()

        # closing
        reply = QMessageBox.critical(self, "All Done", "Goodbye")
        sys.exit(0)

    def getStraws(self):
        pfile = self.palletDirectory / self.palletID / str(self.palletNum + ".csv")
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

    def resetGUI(self):
        self.palletID = ""
        self.palletNum = ""
        self.epoxyBatch = ""
        self.straws = []
        self.temp = True
        # self.sessionWorkers = []
        self.ui.palletNumInput.setEnabled(True)
        self.ui.epoxyBatchInput.setEnabled(True)
        self.ui.palletNumInput.setText("")
        self.ui.epoxyBatchInput.setText("")
        self.ui.commentBox.document().setPlainText("")
        self.ui.start.setEnabled(True)
        self.ui.hour_disp.display(0)
        self.ui.min_disp.display(0)
        self.ui.sec_disp.display(0)
        self.ui.viewButton.setDisabled(True)
        self.ui.finishInsertion.setDisabled(True)
        self.ui.finish.setDisabled(True)

    def logOut(self):
        for i in range(len(self.Current_workers)):
            if self.Current_workers[i].text() != "":
                self.Change_worker_ID(self.portals[i])

    def editPallet(self):
        rem = removeStraw(self.sessionWorkers)
        rem.palletDirectory = self.palletDirectory
        CPAL, lastTask, straws, passfail = rem.getPallet(self.palletNum)
        rem.displayPallet(CPAL, lastTask, straws, passfail)
        rem.exec_()

    def closeEvent(self, event):
        event.accept()
        sys.exit(0)


def run():
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    paths = GetProjectPaths()
    ctr = Silver(paths)
    ctr.show()
    app.exec_()


if __name__ == "__main__":
    run()
