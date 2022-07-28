################################################################################
#
# Straw Prep (Paper Pull) GUI
#
# First step in straw processing in which straw ids/barcodes are assigned to
# straws, they enter the database for the first time, and they are assigned to
# a cutting pallet (which also enters the database for the first time).
#
# After getting entered into the database, their paper is removed, quality
# graded, and data saved.
#
# Next step: resistance test
#
################################################################################
from guis.common.panguilogger import SetupPANGUILogger

logger = SetupPANGUILogger("root", "StrawPrep")

import pyautogui
import time
import os
import csv
import sys
from datetime import datetime
from PyQt5.QtCore import QRect, Qt, QTimer, QMetaObject, QCoreApplication, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QBrush
from PyQt5.QtWidgets import (
    QInputDialog,
    QLabel,
    QFrame,
    QStackedWidget,
    QWidget,
    QPushButton,
    QSizePolicy,
    QCheckBox,
    QVBoxLayout,
    QLayout,
    QSpinBox,
    QLineEdit,
    QMainWindow,
    QApplication,
    QComboBox,
    QMessageBox,
)
from pynput.keyboard import Key, Controller
from pathlib import Path
from guis.straw.prep.design import Ui_MainWindow  ## edit via Qt Designer
from data.workers.credentials.credentials import Credentials
from guis.straw.prep.straw_label_script import print_barcodes
from guis.common.db_classes.straw import Straw
from guis.common.db_classes.straw_location import StrawPosition, CuttingPallet
from guis.common.getresources import GetProjectPaths
from guis.common.save_straw_workers import saveWorkers

# import guis.common.dataProcessor as DP
from guis.common.dataProcessor import SQLDataProcessor as DP
from guis.common.gui_utils import generateBox, except_hook
from guis.common.timer import QLCDTimer

pyautogui.FAILSAFE = True  # Move mouse to top left corner to abort script

# to change hitting enter to hitting tab
keyboard = Controller()


class Prep(QMainWindow):

    LockGUI = pyqtSignal(bool)
    timer_signal = pyqtSignal()

    def __init__(self, paths, webapp=None, parent=None):
        super(Prep, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.stationID = "prep"
        self.workerDirectory = paths["prepworkers"]
        self.palletDirectory = paths["pallets"]
        self.prepDirectory = paths["prepdata"]
        self.boardPath = paths["board"]
        self.ui.PortalButtons.buttonClicked.connect(self.Change_worker_ID)
        self.ui.tab_widget.setCurrentIndex(0)
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

        self.ui.start.clicked.connect(self.beginProcess)
        self.ui.finishPull.clicked.connect(self.checkPPGData)
        self.ui.finish.clicked.connect(self.saveData)
        self.ui.reset.clicked.connect(self.resetGUI)
        self.LockGUI.connect(self.lockGUI)

        # Q Objects to enter data
        self.input_palletID = self.ui.input_palletID
        self.input_palletNumber = self.ui.input_palletNumber
        self.input_batchBarcode = self.ui.input_list_strawBatch
        self.input_strawID = self.ui.input_list_strawID
        self.input_paperPullGrade = self.ui.input_list_paperPullGrade

        # Connect Tab
        for i in range(24):
            self.input_batchBarcode[i].returnPressed.connect(self.bbScan)
            self.input_strawID[i].returnPressed.connect(self.tab)
            self.input_paperPullGrade[i].returnPressed.connect(self.ppgScan)

        self.input_palletID.returnPressed.connect(self.tab)
        self.input_palletNumber.returnPressed.connect(self.tab)

        # Data to be saved
        self.palletID = ""
        self.palletNumber = ""
        self.batchBarcodes = [
            "" for i in range(24)
        ]  # Use if straws are from different batches
        self.pos1StrawID = ""  # Use if all straws are sequential
        self.strawIDs = ["" for i in range(24)]
        self.paperPullGrades = ["" for i in range(24)]

        self.strawCount = None  # will be either 23 or 24, initialy unobtained
        self.sameBatch = None  # will be boolean

        self.dataValidity = {
            "Pallet ID": False,
            "Pallet Number": False,
            "Batch Barcode": [False for i in range(24)],
            "Straw ID": [False for i in range(24)],
            "PPG": [False for i in range(24)],
        }
        self.data = None  # Data processor wants an object like this

        # Worker Info
        self.sessionWorkers = []
        self.credentialChecker = Credentials(self.stationID)

        self.ui.sec_disp.setNumDigits(2)
        self.ui.sec_disp.setSegmentStyle(2)
        self.ui.min_disp.setNumDigits(2)
        self.ui.min_disp.setSegmentStyle(2)
        self.ui.hour_disp.setNumDigits(2)
        self.ui.hour_disp.setSegmentStyle(2)
        self.justLogOut = ""
        saveWorkers(self.workerDirectory, self.Current_workers, self.justLogOut)

        # Progression Information
        self.PalletInfoCollected = False
        self.dataSaved = False

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
        self.pro = 2
        self.pro_index = self.pro - 1
        self.DP = DP(
            gui=self,
            stage="straws",
        )

        # Start it off with the prep tab frozen
        self.LockGUI.emit(False)

    ############################################################################
    # Process steps, top-level functions
    # 1. start button: collect pallet metainfo and enable ppg fields
    # 2. finish paper pull button: checkPPGData
    # 3. finish button: saveData
    ############################################################################
    # 1. Start button: get prelim data, then enable ppg fields
    def beginProcess(self):
        # collect panel prelim/metadata
        if not self.PalletInfoCollected:
            self.getUncollectedPalletInfo()

        # enable ppg data collection
        # (if pallet info collection failed, will need to press start again)
        if not self.PalletInfoCollected:
            return

        self.enablePPGDataCollection()
        self.timing = True
        self.startTimer()

        # Make sure old cpal ID is empty
        old_cpals = CuttingPallet._queryPalletsByID(int(self.getPalletID()[-2:])).all()
        logger.debug(f"clearing straws from old cpals\n{old_cpals}")
        for cpal in old_cpals:
            filled_positions = cpal.getFilledPositions()
            if len(filled_positions):
                logger.debug(
                    f"Clearing {len(filled_positions)} straws from this CPALID."
                )
                cpal.removeAllStraws()
                if cpal.isEmpty():
                    logger.debug(
                        f"CPALID is cleared of old straw and ready to be filled with new ones."
                    )

        # initialize procedure and commit it to the DB
        self.DP.saveStart()

        logger.info(f"This procedure's pallet is {self.getPalletID()}, {self.getPalletNumber()}")

    # disable prelim fields, enable ppg fields
    def enablePPGDataCollection(self):
        self.ui.input_palletID.setDisabled(True)
        self.ui.input_palletNumber.setDisabled(True)

        for i in range((24 - self.strawCount), 24):
            self.ui.input_list_strawBatch[i].setEnabled(False)
            self.ui.input_list_strawID[i].setEnabled(False)
            self.ui.input_list_paperPullGrade[i].setEnabled(True)

        self.ui.start.setDisabled(True)
        self.ui.finishPull.setEnabled(True)

        # Set focus to first Paper Pull Input
        self.input_paperPullGrade[24 - self.strawCount].setFocus()

    # walk user through pallet prelim/metadata collection
    def getUncollectedPalletInfo(self):
        QMessageBox.question(
            self, "Pallet cleaned?", "Clean the pallet with alcohol.", QMessageBox.Ok
        )

        reply = QMessageBox.question(
            self,
            "Print Barcodes",
            "Do you need to print barcodes?",
            QMessageBox.Yes,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            QMessageBox.question(
                self,
                "Prepare for barcodes",
                "Barcodes are about to print--hit ok then do not touch the mouse until finished printing!",
                QMessageBox.Ok,
            )

            print_barcodes()

            QMessageBox.question(
                self, "Barcodes", "Barcodes are printing...", QMessageBox.Ok
            )

        QMessageBox.question(
            self,
            "Attach barcodes",
            "Attach sheet of four pallet barcodes to pallet\nand tape row of 24 straw barcodes to pallet",
            QMessageBox.Ok,
        )

        # Pallet ID
        c = 0  # Loop counter
        while not self.verifyPalletID() and c <= 3:

            # If invalid entry was put in manually, make lineEdit red
            if self.input_palletID.text() != "":
                self.updateLineEdit(self.input_palletID, False)

            new_id = self.askForInfo("Pallet ID")

            if new_id == "":
                return

            valid = self.verifyPalletID(new_id)
            self.updateLineEdit(self.input_palletID, valid, new_id)
            if valid:
                self.palletID = new_id
                self.dataValidity["Pallet ID"] = valid
            c += 1

        if c > 3:
            return

        if self.verifyPalletID():
            self.updateLineEdit(
                self.input_palletID, self.verifyPalletID(), self.palletID
            )

        # Pallet Number
        c = 0  # Loop counter
        while c < 3:

            # get number
            input_number = None
            # on first loop, get number from manual input field
            if c == 0 and self.input_palletNumber.text() != "":
                input_number = self.input_palletNumber.text()
            # otherwise, prompt user
            else:
                input_number = self.askForInfo("Pallet Number")
                if not input_number:
                    return

            # check number
            valid = self.verifyPalletNumber(input_number)
            # update the display field
            self.updateLineEdit(self.input_palletNumber, valid, input_number)
            if valid:
                self.palletNumber = input_number
                self.dataValidity["Pallet Number"] = valid
                break

            c += 1

        if c > 3:
            return

        # Get straw count
        c = 0  # loop counter
        while self.strawCount == None and c <= 1:
            self.getStrawCount()
            c += 1

        # If user doesn't cooperate (and give a straw count), stop running the function
        if self.strawCount == None:
            return

        # Get top Straw ID, then apply to all (sequentially)
        c = 0  # Loop counter
        while not self.verifyStrawID() and c <= 3:
            new_id = self.askForInfo("Straw ID")
            bottom_id = self.askForInfo("Bottom Straw ID")

            if int(bottom_id[2:]) - int(new_id[2:]) != self.strawCount - 1:
                QMessageBox.question(
                    self,
                    "Error! Barcodes Sheets Swapped",
                    "First and last barcodes scanned don't make sense! Check the barcode placement order and retry. Exiting now.",
                    QMessageBox.Ok,
                )
                sys.exit()

            if new_id == "":
                return

            valid = self.verifyStrawID(new_id)
            if valid:
                # If valid, apply to all
                self.pos1StrawID = new_id
                self.assignStrawIDs()
                for i in range(24):
                    lineEdit = self.input_strawID[i]
                    string = self.strawIDs[
                        i
                    ]  # Skips index 0 (top straw) if self.strawCount == 23
                    self.updateLineEdit(lineEdit, valid, string)  # Display
                    if (
                        i == 0 and self.strawCount == 23
                    ):  # Preserve 'disabled' look on top row
                        lineEdit.setStyleSheet("")

                # Save Validity
                self.dataValidity["Straw ID"] = [valid for i in range(24)]
            else:
                # DisStill display bad id in top input
                self.updateLineEdit(self.input_strawID[0], valid, new_id)
            c += 1

        if c > 3:
            return

        # Batch Barcodes

        all_bbs_recorded = True
        for boolean in self.dataValidity["Batch Barcode"]:
            if not boolean:
                all_bbs_recorded = False

        if not all_bbs_recorded:
            message = "Are all the straws from the same batch?"
            buttonReply = QMessageBox.question(
                self, "Straw Batch", message, QMessageBox.Yes | QMessageBox.No
            )
            if buttonReply == QMessageBox.Yes:
                self.sameBatch = True
            elif buttonReply == QMessageBox.No:
                self.sameBatch = False
            else:
                return  # This indicates user pressed (x), in which case, stop looping

        if self.sameBatch:
            for i in range(0, 24):
                if i == 0 and self.strawCount == 23:
                    break
                lineEdit = self.input_batchBarcode[i]
                lineEdit.setDisabled(True)
                lineEdit.setStyleSheet("")
                lineEdit.setText("")

            # Straws are sequential, get top barcode then apply to all (sequentially)
            c = 0  # Loop counter
            new_bb = str()
            while not self.verifyBatchBarcode(new_bb) and c <= 3:
                new_bb = self.askForInfo("Batch Barcode")

                if new_bb == "":
                    return

                valid = self.verifyBatchBarcode(new_bb)
                if valid:
                    # If valid, apply to all
                    self.batchBarcodes = [new_bb for i in range(24)]

                    # Display
                    for i in range(24):
                        lineEdit = self.input_batchBarcode[i]
                        if i == 0 and self.strawCount == 23:
                            pass  # Don't change
                        else:
                            self.updateLineEdit(lineEdit, valid, new_bb)  # Display
                    # Save Validity
                    self.dataValidity["Batch Barcode"] = [valid for i in range(24)]

                    # If not valid, loop and ask for barcode again
                    c += 1

                if c > 3:
                    return

        if (
            not self.sameBatch
        ):  # if NOT self.sameBatch, obtain and display each individually
            i = 24 - self.strawCount
            loop = 0
            while i < 24 and loop <= 3:

                # Check if lineEdit doesn't already contain a valid barcode
                valid = self.verifyBatchBarcode(self.input_batchBarcode[i].text())

                if not valid:
                    new_bb = self.askForInfo("Batch Barcode", i).upper()
                    # If user enters nothing (pressed X), stop looping.
                    if new_bb == "":
                        break

                    # Display new entry
                    valid = self.verifyBatchBarcode(new_bb)
                    lineEdit = self.input_batchBarcode[i]
                    self.updateLineEdit(lineEdit, valid, new_bb)
                    lineEdit.setEnabled(True)  # Keep edittable incase mistake is made

                    if valid:
                        # If valid, save data
                        self.batchBarcodes[i] = new_bb
                        self.dataValidity["Batch Barcode"][i] = valid

                if valid:
                    # If valid, move onto next straw
                    i += 1
                    loop = 0
                else:
                    # Otherwise, stay on current straw
                    loop += 1

            if c > 3:
                return

            if self.strawCount == 23:
                self.input_batchBarcode[0].setText(self.input_batchBarcode[1].text())

        self.PalletInfoCollected = self.verifyPalletInfo()

    def assignStrawIDs(self):
        # takes the numbers from the first straw's ID and assigns IDs to the remaining straws

        # Don't run function if self.pos1strawid isn't verified
        if not self.verifyStrawID():
            return

        # Note: function assumes the straws are sequential
        initial = self.pos1StrawID
        st = initial[0:2]
        new = initial[2:7]
        char_find = None
        for i in range(5):  # splits the leading zeros from the numbers that matter
            if new[i] != "0":
                char_find = i
                break
        st = st + new[0:char_find]
        first = new[char_find:]
        first = int(first)

        for i in range(24):  # makes the inital box values
            self.strawIDs[i] = st + str(first + i)

        s = self.strawIDs
        for ite in range(len(s)):  # makes sure the number has a length of 5
            if len(s[ite]) > 7:
                p1 = s[ite][0:2]
                p2 = s[ite][3:8]
                s[ite] = p1 + p2

    def getStrawCount(self):
        box = QMessageBox()
        box.setIcon(QMessageBox.Question)
        box.setWindowTitle("How many straws?")
        box.setText("How many straws are on the pallet?")
        box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        button23 = box.button(QMessageBox.Yes)
        button23.setText("23")
        button24 = box.button(QMessageBox.No)
        button24.setText("24")
        box.exec_()

        if box.clickedButton() == button23:
            self.strawCount = 23
        elif box.clickedButton() == button24:
            self.strawCount = 24
        else:
            self.strawCount = None

        if self.strawCount == 23:
            # When only testing 23 straws, disable the top row of lineEdits
            inputs = [
                self.input_strawID,
                self.input_batchBarcode,
                self.input_paperPullGrade,
            ]
            for i in inputs:
                lineEdit = i[0]  # Get first lineEdit in list
                # Disable it
                lineEdit.setDisabled(True)
            self.input_paperPullGrade[0].setText("NO STRAW")
            self.input_batchBarcode[0].setText("NO STRAW")
            self.dataValidity["Batch Barcode"][0] = True

    # 2. finish paper pull button, validate ppg data
    def checkPPGData(self):
        # Makes sure all ppg inputs are good, then stops timing
        # all_pass = True

        for i in range(self.strawCount):
            if not (
                self.dataValidity["PPG"][23 - i]
            ):  # First, check that data hasn't already been verified
                # "Scan in" all unrecorded ppg entries
                self.input_paperPullGrade[23 - i].setFocus()
                self.ppgScan()

        all_pass = True

        # Evaluate all relevant ppg pass/fail's
        for i in range((24 - self.strawCount), 24):
            boolean = self.dataValidity["PPG"][i]
            if not boolean:
                all_pass = False

        # Once all ppg's have been verified...
        if all_pass:
            # Record all in self.paperPullGrades
            self.paperPullGrades = ["" for ppg in range(24)]
            for i in range(24):
                self.paperPullGrades[i] = self.input_paperPullGrade[i].text().upper()

            # Stop timing
            self.timing = False
            self.stopTimer()
            self.DP.saveFinish()

            # (Dis/En)able "Finish" Buttons
            self.ui.finishPull.setEnabled(False)
            self.ui.finish.setEnabled(True)

    # 3. finish button, save
    def saveData(self):
        logger.info("Saving data...")
        self.saveDataToText()
        self.saveDataToDB()

        self.dataSaved = True

        logger.info("dataSaved: " + str(self.dataSaved))

        self.ui.finish.setEnabled(False)

        QMessageBox.about(self, "Save", "Data saved successfully!!")

        self.resetGUI()

    def saveDataToText(self):
        workers_str = ", ".join(
            self.sessionWorkers
        ).upper()  # Converts self.sessionWorkers to a string csv-style: "wk-worker01, wk-worker02, etc..."
        self.saveStrawDataToText(workers_str)
        self.savePalletDataToText(workers_str)

    def saveStrawDataToText(self, workers_str):
        file_name = self.stationID + "_" + self.palletNumber + ".csv"
        data_file = self.prepDirectory / file_name
        with open(data_file, "w+") as file:
            file.write("Station: " + self.stationID)
            header = "Timestamp, Pallet ID, Pallet Number, Paper pull time (H:M:S), workers ***NEWLINE***: Comments (optional)***\n"
            file.write(header)
            file.write(datetime.now().strftime("%Y-%m-%d_%H:%M") + ",")
            file.write(self.palletID + ",")
            file.write(self.palletNumber + ",")
            file.write(
                str(self.ui.hour_disp.intValue())
                + ":"
                + str(self.ui.min_disp.intValue())
                + ":"
                + str(self.ui.sec_disp.intValue())
                + ","
            )

            # If top straw doesn't exist yet, don't save underscores in top straw data fields
            if self.strawCount == 23:
                self.strawIDs[0] = "_______"  # _ x7 (st#####)
                self.batchBarcodes[0] = "_________"  # _ x7 (MMDDYY.B#)
                self.paperPullGrades[0] = "____"  # _ x4 (PP._)

            # Record Workers
            file.write(workers_str)
            file.write("\n")
            # Comments
            if self.ui.commentBox.document().toPlainText() != "":
                file.write(self.ui.commentBox.document().toPlainText())
            file.write("\n\n")

            # Straw-Specific Data
            fieldnames = ["straw", "batch", "paperPullGrade"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            writer.writeheader()
            for i in range(24):
                straw_data = {
                    "straw": self.strawIDs[i],
                    "batch": self.batchBarcodes[i],
                    "paperPullGrade": self.paperPullGrades[i],
                }
                writer.writerow(straw_data)

            # Done creating data file

    def savePalletDataToText(self, workers_str):
        pfile = self.palletDirectory / self.palletID / str(self.palletNumber + ".csv")
        with open(pfile, "w+") as file:
            header = "Time Stamp, Task, 24 Straw Names/Statuses, Workers"
            header += ", ***" + str(self.strawCount) + " straws initially on pallet***"
            header += f" {self.palletID}"
            header += "\n"
            file.write(header)

            # Record Session Data
            file.write(datetime.now().strftime("%Y-%m-%d_%H:%M") + ",")
            file.write(self.stationID + ",")

            # Record each straw and whether it passes/fails
            for i in range(24):
                straw = self.strawIDs[i]

                # If top straw doesn't exist, record save _'s for straw ID and pass_fail
                if i == 0 and self.strawCount == 23:
                    straw = "_______"  # _ x7
                    pass_fail = "_"

                # In all other cases, save the straw ID, and evaluate pass_fail
                else:
                    ppg = self.paperPullGrades[i]

                    if ppg == "PP.A" or ppg == "PP.B":
                        pass_fail = "P"
                    else:
                        pass_fail = "F"

                file.write(straw + "," + pass_fail + ",")

            file.write(workers_str)

    # Add entries to the straw, straw_present and measurement_prep tables
    def saveDataToDB(self):
        # our procedure (created and) knows our CPAL. In creating the CPAL
        # straw location, we made 24 "straw positions" (in the
        # straw_position" table), aka slots where straws can go.
        cpal = self.DP.procedure.getStrawLocation()
        logger.debug(cpal)
        
        for position in range(24):
            if self.strawIDs[position] != '_______':
                logger.debug(f"{position}")
                straw_id = int(self.strawIDs[position][2:])
                batch = self.batchBarcodes[position]
                batch = "".join(filter(str.isalnum, batch))  # for the db, drop the period
                ppg = self.paperPullGrades[position][-1]

                logger.debug(straw_id)
                logger.debug(batch)
                logger.debug(ppg)

                # new entry in straw table
                straw = Straw.Straw(id=straw_id, batch=batch)

                logger.debug(straw)

                # new entry in straw_present table.
                cpal.addStraw(straw, position)

                # new entry in measurement_prep table
                self.DP.procedure.StrawPrepMeasurement(
                    procedure=self.DP.procedure,
                    straw_id=straw_id,
                    paper_pull_grade=ppg,
                    evaluation=None,
                ).commit()

    ############################################################################
    # Worker login and gui lock
    ############################################################################
    def Change_worker_ID(self, btn):
        label = btn.text()
        portalNum = 0
        if label == "Log In":
            portalNum = int(btn.objectName().strip("portal")) - 1
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
            portalNum = int(btn.objectName().strip("portal")) - 1
            worker = self.Current_workers[portalNum].text()
            self.justLogOut = worker
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
            self.ui.tab_widget.setTabText(1, "Straw Prep")
            self.ui.tab_widget.setTabEnabled(1, True)
        else:
            self.ui.tab_widget.setCurrentIndex(0)
            self.ui.tab_widget.setTabText(1, "Straw Prep *Locked*")
            self.ui.tab_widget.setTabEnabled(1, False)

    ############################################################################
    # Verification functions
    ############################################################################
    def verifyPalletInfo(self):
        # This function is predominately to check if new data has been entered.
        # Pallet ID
        if (
            self.palletID != self.input_palletID.text()
            or not self.dataValidity["Pallet ID"]
        ):  # If new data has been entered, or pallet ID was never verified:
            new_id = self.input_palletID.text()
            valid = self.verifyPalletID(new_id)
            if valid:
                self.palletID = new_id  # Record it
            else:
                self.palletID = ""  # Set to null string
            self.updateLineEdit(
                self.input_palletID, valid
            )  # And update the lineEdit background
            self.dataValidity["Pallet ID"] = valid

        # Pallet Number
        if (
            self.palletNumber != self.input_palletNumber.text()
            or not self.dataValidity["Pallet Number"]
        ):  # If new data has been entered, or pallet Number was never verified:
            new_num = self.input_palletNumber.text()
            valid = self.verifyPalletNumber(new_num)
            if valid:
                self.palletNumber = new_num  # Record it
            else:
                self.palletNumber = ""  # Set to null string
            self.updateLineEdit(
                self.input_palletNumber, valid
            )  # And update the lineEdit background
            self.dataValidity["Pallet Number"] = valid

        # Batch Barcodes
        for i in range((24 - self.strawCount), 24):
            batch = self.input_batchBarcode[i].text()
            if (batch != self.batchBarcodes[i]) or not (
                self.dataValidity["Batch Barcode"][i]
            ):
                valid = self.verifyBatchBarcode(batch)
                if valid:
                    self.batchBarcodes[i] = batch  # Record if valid

                self.dataValidity["Batch Barcode"][i] = valid
                self.updateLineEdit(
                    self.input_batchBarcode[i], valid
                )  # update linEdit background

        # Straw IDs
        for i in range((24 - self.strawCount), 24):
            current_id = self.input_strawID[i].text()
            if (current_id != self.strawIDs[i]) or not self.dataValidity["Straw ID"][i]:
                valid = self.verifyStrawID(current_id)
                if valid:
                    self.strawIDs[i] = batch  # Record if valid

                self.dataValidity["Straw ID"][i] = valid
                self.updateLineEdit(
                    self.input_batchBarcode, valid
                )  # update linEdit background

        # Summarize Booleans
        all_pass = True
        if not self.dataValidity["Pallet ID"] or not self.dataValidity["Pallet Number"]:
            all_pass = False
        for boolean in self.dataValidity["Batch Barcode"]:
            if not boolean:
                all_pass = False
        for boolean in self.dataValidity["Straw ID"]:
            if not boolean:
                all_pass = False

        return all_pass

    def verifyPalletID(self, potential_id=None):

        # If no specific string is given to check as an ID, finds the most
        # relevant string to use, and saves it.
        if not potential_id:
            if self.palletID != self.input_palletID.text().upper():
                self.palletID = self.input_palletID.text().upper()
            potential_id = self.palletID

        potential_id = potential_id.strip().upper()

        verify = True
        if len(potential_id) != 8:
            verify = False

        # Starts correctly
        elif not potential_id.startswith("CPALID"):
            verify = False

        # Check this to prevent error checking next...
        elif not potential_id[6:].isnumeric():
            verify = False

        elif not int(potential_id[6:]) > 0 or not int(potential_id[6:]) < 25:
            verify = False

        return verify

    # if given number is good set self.palletNumber
    # if no number is given try using the value in the display field
    def verifyPalletNumber(self, potential_num):
        if not potential_num:
            potential_num = self.input_palletNumber.text().upper()

        potential_num = potential_num.strip().upper()

        if len(potential_num) != 8:
            return False
        if not potential_num.startswith("CPAL"):
            return False
        if not potential_num[4:].isnumeric():
            return False

        for id in range(1, 24):
            file = potential_num + ".csv"
            path = self.palletDirectory / str("CPALID" + str(id).zfill(2)) / file
            if os.path.exists(path):
                logger.info(f"{potential_num} has been prepped.")
                QMessageBox.question(
                    self,
                    "Duplicate CPAL Number",
                    "This pallet has been prepped!",
                    QMessageBox.Ok,
                )
                return False

        # verified -- set self.palletNumber
        self.palletNumber = potential_num
        return True

    def verifyBatchBarcode(self, potential_batchID):
        potential_batchID = potential_batchID.strip().upper()
        verify = True
        if len(potential_batchID) != 9:
            verify = False

        # Starts correctly
        elif not potential_batchID[:6].isnumeric():
            verify = False

        elif not potential_batchID[8].isnumeric():
            verify = False

        elif not potential_batchID[6:8].upper() == ".B":
            verify = False

        return verify

    def verifyStrawID(self, potential_ID=None):
        if potential_ID == None:
            potential_ID = self.pos1StrawID

        potential_ID = potential_ID.strip().upper()

        verify = True
        if len(potential_ID) != 7:
            verify = False

        elif not potential_ID.startswith("ST"):
            verify = False

        elif not potential_ID[2:].isnumeric():
            verify = False

        return verify

    def verifyPaperPullGrade(self, potential_ppg):
        potential_ppg = (
            potential_ppg.strip().upper()
        )  # Always evaluate the uppercase version of the given string with no spaces

        valid = True

        if potential_ppg == "DNE":
            valid = True

        elif len(potential_ppg) != 4:
            valid = False

        elif not potential_ppg.startswith("PP."):
            valid = False

        elif not potential_ppg[3] in ["A", "B", "C", "D"]:
            valid = False

        return valid

    def bbScan(self):
        # Get current lineEdit
        lineEdit = self.focusWidget()

        if not lineEdit in self.input_batchBarcode:  # Make sure this is a ppg lineEdit
            return

        potential_bb = lineEdit.text().upper()
        valid = self.verifyBatchBarcode(potential_bb)
        self.updateLineEdit(lineEdit, valid, potential_bb)

        # If entry is invalid, set scanner to that input
        if not valid:
            lineEdit.setFocus()
            lineEdit.selectAll()

        # If entry IS valid, move onto next entry
        if valid:
            index = self.input_batchBarcode.index(lineEdit)
            self.batchBarcodes[index] = potential_bb
            self.dataValidity["Batch Barcode"] = valid

    def ppgScan(self):
        # Get current lineEdit
        lineEdit = self.focusWidget()

        if (
            not lineEdit in self.input_paperPullGrade
        ):  # Make sure this is a ppg lineEdit
            return

        # Get PPG and evaluate
        potential_ppg = self.getPreparedPPG(
            lineEdit
        )  # Get lineEdit text, convert to CAPS and no spaces, puls change letters to corresponding ppg code
        valid = self.verifyPaperPullGrade(potential_ppg)

        # Update Display
        self.updateLineEdit(lineEdit, valid, potential_ppg)

        # If entry is invalid, set focus to that input
        if not valid:
            lineEdit.setFocus()
            lineEdit.selectAll()

        # After all evaluations, save entry and validity
        index = self.input_paperPullGrade.index(lineEdit)
        self.paperPullGrades[index] = potential_ppg
        self.dataValidity["PPG"][index] = valid

    def getPreparedPPG(self, lineEdit):
        # Gets the text from a given lineEdit and converts it into an evalutable PPG

        if not lineEdit in self.input_paperPullGrade:
            return ""

        # Put string in all caps, and remove spaces
        string = lineEdit.text().strip().upper()

        # For ease of use if barcode scanner isn't working, simply typing a, b, c, or d, can be converted to a ppg code:
        letterToPPGCode = {
            "A": "PP.A",
            "B": "PP.B",
            "C": "PP.C",
            "D": "PP.D",
            "X": "DNE",
        }
        # Convert entered letter to correspondig PPG Code ( letter --> PP.[letter] )
        if string in letterToPPGCode.keys():
            string = letterToPPGCode[string]

        # Double check C or D entries
        if string in ["PP.C", "PP.D"]:

            # Get additional lineEdit information
            index = self.input_paperPullGrade.index(lineEdit)
            straw_ID = self.strawIDs[index]

            # Send the user a message double-checking that their input was correct
            message = "Was " + straw_ID + " actually a " + string[-1] + " grade?"
            buttonReply = QMessageBox.question(
                self, "Verify Input", message, QMessageBox.Yes | QMessageBox.No
            )

            if buttonReply == QMessageBox.No:
                string = ""

        return string

    ############################################################################
    # Utility
    ############################################################################

    def updateLineEdit(
        self,
        lineEdit,
        boolean=None,
        string=None,
    ):
        # Displays text and changes background of given Q LineEdit
        styleSheets = {
            True: "background-color:rgb(0, 255, 51)",
            False: "background-color:rgb(255, 0, 0)",
        }

        if boolean != None:
            lineEdit.setStyleSheet(styleSheets[boolean])
            lineEdit.setDisabled(
                boolean
            )  # If valid data is given, disable lineEdit (and visa versa)

        if string != None:
            lineEdit.setText(string)
        # If no string argument is given, don't touch text

    def resetGUI(self):
        # Pallet ID
        self.input_palletID.setText("")
        self.input_palletID.setPlaceholderText("CPALID##")
        self.input_palletID.setStyleSheet("")
        self.input_palletID.setEnabled(True)

        # Pallet Number
        self.input_palletNumber.setText("")
        self.input_palletNumber.setPlaceholderText("CPAL####")
        self.input_palletNumber.setStyleSheet("")
        self.input_palletNumber.setEnabled(True)

        # BatchBarcodes
        for lineEdit in self.input_batchBarcode:
            lineEdit.setText("")
            lineEdit.setPlaceholderText("MMDDYY.B#")
            lineEdit.setStyleSheet("")
            lineEdit.setEnabled(False)

        # Straw IDs
        for lineEdit in self.input_strawID:
            lineEdit.setText("")
            lineEdit.setPlaceholderText("ST#####")
            lineEdit.setStyleSheet("")
            lineEdit.setEnabled(False)

        # PPGs
        for lineEdit in self.input_paperPullGrade:
            lineEdit.setText("")
            lineEdit.setPlaceholderText("PP._")
            lineEdit.setStyleSheet("")
            lineEdit.setEnabled(False)

        # Buttons
        self.ui.finish.setEnabled(False)
        self.ui.finishPull.setEnabled(False)
        self.ui.start.setEnabled(True)

        # Time Display
        self.resetTimer()

        # Comments
        self.ui.commentBox.clear()

        # Actual data to be saved
        self.palletID = ""
        self.palletNumber = ""
        self.batchBarcodes = [
            "" for i in range(24)
        ]  # Use if straws are from different batches
        self.pos1StrawID = ""  # Use if all straws are sequential
        self.strawIDs = ["" for i in range(24)]
        self.paperPullGrades = ["" for i in range(24)]

        self.strawCount = None  # will be either 23 or 24, initialy unobtained
        self.sameBatch = None  # will be boolean

        self.dataValidity = {
            "Pallet ID": False,
            "Pallet Number": False,
            "Batch Barcode": [False for i in range(24)],
            "Straw ID": [False for i in range(24)],
            "PPG": [False for i in range(24)],
        }

        self.ui.sec_disp.setNumDigits(2)
        self.ui.sec_disp.setSegmentStyle(2)
        self.ui.min_disp.setNumDigits(2)
        self.ui.min_disp.setSegmentStyle(2)
        self.ui.hour_disp.setNumDigits(2)
        self.ui.hour_disp.setSegmentStyle(2)

        self.PalletInfoCollected = False

        # Timing info
        self.timing = False

        # If data has been saved: also log out
        if self.dataSaved:
            self.dataSaved = False
            for i in range(len(self.Current_workers)):
                if self.Current_workers[i].text() != "":
                    self.Change_worker_ID(self.portals[i])
            self.sessionWorkers = []
            self.justLogOut = ""
            saveWorkers(self.workerDirectory, self.Current_workers, self.justLogOut)

    def closeEvent(self, event):
        event.accept()
        self.DP.handleClose()
        self.close()
        sys.exit()

    def askForInfo(self, identifier, iterator=None):
        # Asks user to scan given barcode. Returns user input.
        if iterator != None:
            message = {
                "Batch Barcode": "position "
                + str(int(iterator))
                + " batch barcode (MMDDYY.B#)",
                "Straw ID": "position " + str(int(iterator)) + " straw ID (st#####)",
            }

        else:
            message = {
                "Pallet ID": "pallet ID (CPALID##)",
                "Pallet Number": "pallet number (CPAL####)",
                "Batch Barcode": "batch barcode (MMDDYY.B#)",
                "Straw ID": "top straw ID (st#####)",
                "Bottom Straw ID": "bottom straw ID (st#####)",
            }

        if identifier not in message.keys():
            return

        string, ok = QInputDialog.getText(
            self, identifier, "Please scan " + message[identifier]
        )
        string = string.upper()

        return string

    def tab(self):
        keyboard.press(Key.tab)

    def getPalletID(self):
        return self.palletID

    def getPalletNumber(self):
        return self.palletNumber

    ############################################################################
    # Deprecated
    ############################################################################

    def updateBoard(self):
        status = []
        try:
            with open(self.boardPath + "Progression Status.csv") as readfile:
                data = csv.reader(readfile)
                for row in data:
                    for pallet in row:
                        status.append(pallet)
            status[int(self.palletID[6:]) - 1] == 11
            with open(self.boardPath + "Progression Status.csv", "w") as writefile:
                i = 0
                for pallet in status:
                    writefile.write(pallet)
                    if i != 23:
                        writefile.write(",")
                    i = i + 1
        except IOError:
            logger.error(
                "Could not update board due to board file being accessed concurrently"
            )


def run():
    sys.excepthook = except_hook  # crash, don't hang when an exception is raised
    app = QApplication(sys.argv)
    paths = GetProjectPaths()
    ctr = Prep(paths)
    ctr.show()
    app.exec_()


if __name__ == "__main__":
    run()
