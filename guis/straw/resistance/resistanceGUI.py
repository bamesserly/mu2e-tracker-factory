################################################################################
#
# Straw Resistance Test GUI
#
# Read resistance data for a full panel of straws all at once from an Arduino
# Uno and PCB. Save all the data at the very end.
#
# Next step:
#
################################################################################

from guis.common.panguilogger import SetupPANGUILogger

logger = SetupPANGUILogger("root", "StrawResistance")

import sys
from pathlib import Path
import os
import csv
from datetime import datetime
import time
from PyQt5.QtCore import QRect, Qt, QTimer, QMetaObject, QCoreApplication, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QBrush, QPixmap
from PyQt5.QtWidgets import (
    QInputDialog,
    QDialog,
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
    QLCDNumber,
)
from guis.straw.resistance.design import Ui_MainWindow

from guis.straw.resistance.resistanceMeter import Resistance
from guis.straw.resistance.measureByHand import MeasureByHandPopup
from guis.straw.removestraw import removeStraw
from data.workers.credentials.credentials import Credentials
from guis.common.getresources import GetProjectPaths
from guis.common.save_straw_workers import saveWorkers
from guis.common.dataProcessor import SQLDataProcessor as DP
from guis.common.gui_utils import generateBox

from random import uniform
from enum import Enum, auto
from guis.common.timer import QLCDTimer


class ResistanceMeasurementConfig(Enum):
    II = 0  # inner-inner
    IO = auto()  # inner-outer
    OI = auto()  # outer-inner
    OO = auto()  # outer-outer


class StrawResistanceGUI(QDialog):
    LockGUI = pyqtSignal(bool)
    timer_signal = pyqtSignal()

    def __init__(self, paths, app):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()
        self.app = app

        self.meas_input = (
            self.ui.meas_input_list
        )  # QLineEdit objects that display measurements
        self.led = (
            self.ui.meas_led_list
        )  # QLabel objects whose color indicates status of corresponding measurement
        self.box = (
            self.ui.boxlist
        )  # QGroupBox objects holding info for each position of resistance measurement device
        self.straw_ID_labels = (
            self.ui.strawID_label_list
        )  # QLabel objects labeling each box with unique straw ID

        # Directories
        self.workerDirectory = paths["resistanceworkers"]
        self.palletDirectory = paths["pallets"]

        # Connect buttons to respective functions
        self.ui.collect_button.clicked.connect(self.collectData)
        self.ui.byHand_button.clicked.connect(self.measureByHand)
        self.ui.reset_button.clicked.connect(self.resetGUI)
        self.ui.save_button.clicked.connect(self.finish)
        self.ui.editPallet_button.clicked.connect(self.editPallet)
        self.LockGUI.connect(self.lockGUI)

        # Measurement and Bool Lists
        # Prefills lists to record 4 measurements for 24 straws
        self.measurements = [[None for i in range(4)] for pos in range(24)]
        self.old_measurements = [[None for i in range(4)] for pos in range(24)]
        self.bools = [[None for i in range(4)] for pos in range(24)]
        self.old_bools = [[None for i in range(4)] for pos in range(24)]

        self.meas_type_labels = {
            0: "inside-inside",
            1: "inside-outside",
            2: "outside-inside",
            3: "outside-outside",
        }

        self.meas_type_labels_apprev = {0: "ii", 1: "io", 2: "oi", 3: "oo"}

        self.meas_type_eval = {  # Evaluates each type of measurement
            0: lambda meas: (40.0 <= meas <= 300.0),  # i-i
            1: lambda meas: (meas >= 1000.0),  # i-o
            2: lambda meas: (meas >= 1000.0),  # o-i
            3: lambda meas: (40.0 <= meas <= 250.0),  # o-o
        }
        # to determine if a given measurement passes or fails:
        #   pass_fail = self.meas_type_eval[meas_type](meas)

        self.failed_measurements = []  # used in self.measureByHand()

        # Measurement classes
        self.removeStraw = removeStraw([])
        self.resistanceMeter = Resistance()  # resistance class
        self.byHandPopup = None  # Gets created later if necessary

        # Pallet Info
        self.stationID = "ohms"
        self.palletNumber = None
        self.strawExists = [False for i in range(24)]
        self.pallet_lastTask = ""
        self.straw1ID = None
        self.strawIDs = [None for i in range(24)]  # list of straw IDs filled with
        self.palletInfoVerified = False
        self.calledInitializePallet = False
        self.palletID = None

        # Worker Info
        self.credentialChecker = Credentials(self.stationID)
        self.Current_workers = [
            self.ui.Current_worker1,
            self.ui.Current_worker2,
            self.ui.Current_worker3,
            self.ui.Current_worker4,
        ]
        self.sessionWorkers = []

        # Worker Portal
        self.portals = [
            self.ui.portal1,
            self.ui.portal2,
            self.ui.portal3,
            self.ui.portal4,
        ]
        self.ui.portalButtons.buttonClicked.connect(self.Change_worker_ID)

        # Saving Data
        self.dataRecorded = False
        self.clean_data = [[None for i in range(4)] for pos in range(24)]
        self.saveFile = ""

        self.db_entries = []

        # Measurement Status
        self.collectData_counter = 0
        self.collectData_limit = 500
        self.measureByHand_counter = 0

        # Configure Buttons using Measurement Status
        self.enableButtons()

        # LogOut
        self.justLogOut = ""
        saveWorkers(self.workerDirectory, self.Current_workers, self.justLogOut)

        # timing
        self.timer = QLCDTimer(
            QLCDNumber(),  # no timer display for this ui TODO
            QLCDNumber(),  # no timer display for this ui TODO
            QLCDNumber(),  # no timer display for this ui TODO
            lambda: self.timer_signal.emit(),
            max_time=28800,
        )  # 0 - Main Timer: Turns red after 8 hours
        self.timer_signal.connect(self.timer.display)

        self.startTimer = lambda: self.timer.start()
        self.stopTimer = lambda: self.timer.stop()
        self.resetTimer = lambda: self.timer.reset()
        self.mainTimer = self.timer  # data processor wants it
        self.running = lambda: self.timer.isRunning()

        # Data Processor
        self.pro = 3
        self.pro_index = self.pro - 1
        self.DP = DP(gui=self, stage="straws",)

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
                    "critical", "Login Error", "This worker ID is already logged in.",
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
            self.ui.tab_widget.setTabText(1, "Resistance")
            self.ui.tab_widget.setTabEnabled(1, True)
        else:
            self.resetGUI()
            self.ui.tab_widget.setCurrentIndex(0)
            self.ui.tab_widget.setTabText(1, "Resistance *Locked*")
            self.ui.tab_widget.setTabEnabled(1, False)

    #############################################################################
    # Pallet Info -- set, get, validate
    #############################################################################
    def setPalletNumber(self):
        pallet, ok = QInputDialog().getText(
            self, "Pallet Number", "Please scan the Pallet Number", text="CPAL####"
        )

        pallet = pallet.strip().upper()  # remove spaces and put in CAPS

        if ok:
            if self.verifyPalletNumber(pallet):
                self.palletNumber = pallet
            else:
                self.setPalletNumber()

    def verifyPalletNumber(self, pallet_num):
        # Verifies that the given pallet number is of a valid format
        verify = True

        # check that last 4 characters of ID are integers
        if len(pallet_num) == 8:
            verify = pallet_num[
                4:7
            ].isnumeric()  # makes sure last four digits are numbers
        else:
            verify = False

        if not pallet_num.upper().startswith("CPAL"):
            verify = False

        return verify

    def getPalletID(self):
        return self.palletID

    def getPalletNumber(self):
        return self.palletNumber

    # Get straw list and other info from pallet txt file
    def initializePallet(self):
        if not self.palletNumber:
            self.setPalletNumber()

        if self.palletNumber:
            # Display Pallet Info Window
            #   - Hint that user remove all failed straws
            #   - Calls interpretEditPallet() to
            #     obtain most recent pallet info
            # self.editPallet()
            rem = removeStraw(self.sessionWorkers)
            rem.palletDirectory = self.palletDirectory
            rem.sessionWorkers = self.sessionWorkers
            CPAL, lastTask, straws, passfail, self.palletID = rem.getPallet(
                self.palletNumber
            )
            self.interpretEditPallet(CPAL, lastTask, straws, passfail)

        self.calledInitializePallet = True

    # Remove straws from the pallet -- using the removeStraw gui.
    def editPallet(self):
        rem = removeStraw(self.sessionWorkers)
        rem.palletDirectory = self.palletDirectory
        rem.sessionWorkers = self.sessionWorkers
        CPAL, lastTask, straws, passfail, self.palletID = rem.getPallet(
            self.palletNumber
        )
        rem.displayPallet(CPAL, lastTask, straws, passfail)
        rem.exec_()

        CPAL, lastTask, straws, passfail, self.palletID = rem.getPallet(
            self.palletNumber
        )  # Run again incase changes were made (straws removed, moved, etc...)
        # After executing
        self.interpretEditPallet(CPAL, lastTask, straws, passfail)

    # Set the straw list, verify previous step was prep
    def interpretEditPallet(self, CPAL, lastTask, straws, passfail):
        self.palletInfoVerified = (
            True  # Initially assume True, can only be switched to False
        )

        if lastTask != "prep":
            self.palletInfoVerified = False
            self.setStatus(self.palletInfoVerified)
            # Error Message
            QMessageBox.about(
                self,
                "Remove Straws",
                "Please verify that this pallet has been prepped/ hasn't already been resistance tested",
            )
            return

        # Check for failed straws
        remove_straws = []
        for i in range(24):
            if passfail[i] == "Fail":
                remove_straws.append(straws[i])

        self.setStatus((len(remove_straws) == 0))

        # No failed straws are present
        if len(remove_straws) == 0:
            self.checkForMovedStraws(
                straws
            )  # Checks if any straws have been moved. If so, transfers data

            # Assign strawIDs
            self.strawIDs = [None for i in range(24)]  # defaults to None
            for i in range(24):
                if straws[i] != "Empty":
                    self.strawIDs[i] = straws[i]  # If slot isn't empty, save strawID
            self.updatePositionDisplay()

        # If failed straws are present, instruct user to remove them and run
        # editPallet() (which will call this function again)
        else:
            self.palletInfoVerified = False

            instructions = "The following straws failed Straw Prep and need to be removed before testing resistance:"
            for strawID in remove_straws:
                instructions += "\n" + strawID
            logger.debug(instructions)
            buttonreply = QMessageBox.question(
                self,
                "Remove Straws",
                instructions,
                QMessageBox.Ok | QMessageBox.Cancel,
                QMessageBox.Cancel,
            )

            if buttonreply != QMessageBox.Cancel:
                self.editPallet()

        logger.debug(f"interpretEditPallet self.strawIDs {self.strawIDs}")

    def checkForMovedStraws(self, newStrawIDs):
        # straws_moved = False
        if self.strawIDs == ["" for i in range(24)]:
            return

        for i1 in range(24):
            if self.strawIDs[i1] or newStrawIDs[i1] not in self.strawIDs:
                continue

            i2 = self.strawIDs.index(newStrawIDs[i1])

            # Swap ids, measurements, and bools
            self.strawIDs[i1], self.strawIDs[i2] = (
                self.strawIDs[i2],
                self.strawIDs[i1],
            )

            for j in range(4):
                self.measurements[i1][j], self.measurements[i2][j] = (
                    self.measurements[i2][j],
                    self.measurements[i1][j],
                )
                self.bools[i1][j], self.bools[i2][j] = (
                    self.bools[i2][j],
                    self.bools[i1][j],
                )

                # Update both positions' displays
                self.meas_input[i1][j].setText(
                    self.resMeasString(self.measurements[i1][j])
                )
                self.meas_input[i2][j].setText(
                    self.resMeasString(self.measurements[i2][j])
                )
                self.LEDchange(self.bools[i1][j], self.led[i1][j])
                self.LEDchange(self.bools[i2][j], self.led[i2][j])

    #############################################################################
    # Control flow: collect data, measure by hand, finish, measure by hand
    #
    # TODO Currently, the collectData function is way overloaded -- it's tied
    # to the collect data button and it IS the process's flow control -- first
    # collecting pallet metainfo, then triggering the arduino, then managing
    # the data
    #############################################################################
    # start here -- make sure pallet info collected, then run the automatic
    # resistance measurement arduino
    def collectData(self):
        self.setStatus("processing")
        time.sleep(0.01)

        if not self.palletInfoVerified:
            self.initializePallet()

        if not (
            self.palletInfoVerified
            or self.collectData_counter >= self.collectData_limit
        ):
            return

        self.startTimer()
        self.DP.saveStart()  # initialize procedure and commit it to the DB
        self.procedure = self.DP.procedure  # Resistance(StrawProcedure) object

        try:
            self.measurements = self.resistanceMeter.rMain()
        except FileNotFoundError as e:
            logger.error("File not found", e)
            self.displayError(True)
            return
        except:
            logger.error("Arduino Error")
            self.displayError(True)
            return

        # useful for debug
        # self.measurements = [[uniform(200, 249) for i in range(4)] for pos in range(24)]
        # self.measurements = [[205.0, 1000.0, 200.0, 206.0] for pos in range(24)]

        self.consolidateOldAndNewMeasurements()

        self.updatePassFailStatus()

        self.displayData()

        # save new data to old data
        for pos in range(24):
            for i in range(4):
                # Get old values
                old_meas = self.measurements[pos][i]
                old_bool = self.bools[pos][i]
                # Save to lists
                self.old_measurements[pos][i] = old_meas
                self.old_bools[pos][i] = old_bool

        self.displayError(False)
        self.dataRecorded = True
        self.collectData_counter += 1
        self.enableButtons()

    # If measurements failed, ask whether to re-measure by hand, otherwise,
    # just save.
    def finish(self):
        self.updatePassFailStatus()  # UPDATE self.bools
        self.setFailedMeasurements()  # RESET AND FILL self.failed_measurements
        logger.debug(
            f"top of finish: measure by hand counter {self.measureByHand_counter}"
        )
        logger.debug(
            f"top of finish: len(failed measurements) {len(self.failed_measurements)}"
        )
        if len(self.failed_measurements) != 0:
            message = "There are some failed measurements. Would you like to try measuring by hand?"
            buttonReply = QMessageBox.question(
                self, "Measure By-Hand", message, QMessageBox.Yes | QMessageBox.No
            )
            if buttonReply == QMessageBox.Yes:
                self.measureByHand()
                return

        warning = "Are you sure you want to Save?"
        buttonReply = QMessageBox.question(
            self, "Save?", warning, QMessageBox.Yes | QMessageBox.No
        )

        if buttonReply == QMessageBox.No:
            return

        self.stopTimer()
        self.DP.saveFinish()
        self.saveData()
        # self.resetGUI()

        """#Ask to reset
        reset_text = "Would you like to resistance test another pallet?"
        buttonReply = QMessageBox.question(self, 'Test another pallet?', reset_text, QMessageBox.Yes | QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            self.resetGUI() #reset; user can start another pallet
        """

    # In addition to having its own button, also called from the finish
    # function, which is tied to the save data button, which only gets pressed
    # after collecting the data with the resistance meter.
    def measureByHand(self):
        self.updatePassFailStatus()
        self.setFailedMeasurements()

        # no failed measurements, we're done here
        if len(self.failed_measurements) == 0:
            message = "Data looks good. No by-hand measurements required!"
            QMessageBox.about(self, "Measure By-Hand", message)
            return

        # ask user to turn on multimeter
        instructions = "Turn on the Multimeter. This program will crash if you do not."
        buttonReply = QMessageBox.question(
            self, "Measure By-Hand", instructions, QMessageBox.Ok | QMessageBox.Cancel,
        )
        if buttonReply != QMessageBox.Ok:
            return

        # Initialize by-hand measurer, connect to multimeter
        if self.byHandPopup == None:
            self.byHandPopup = MeasureByHandPopup()  # Create Popup Window
        while not self.byHandPopup.multiMeter:
            self.byHandPopup.getMultiMeter()  # Tries to connect to multimeter
            if not self.byHandPopup.multiMeter:
                message = (
                    "There was an error connecting to the multimeter. "
                    "Make sure it is turned on and plugged into the computer, then try again."
                )
                QMessageBox.about(self, "Connection Error", message)
                logger.error("hit the not thing")

        logger.debug(f"measureByHand: failed measurements {self.failed_measurements}")

        # loop through failed measurements to redo them by hand
        for el in self.failed_measurements:
            # Record measured by hand
            self.measureByHand_counter += 1
            # Get Specific Measurement Information
            pos = el[0]
            if not bool(self.strawIDs[pos]):
                continue
            strawID = self.strawIDs[pos]
            meas_type = el[1]
            meas_type_label = self.meas_type_labels[meas_type]
            eval_expression = self.meas_type_eval[meas_type]
            # Prepare labels in popup display
            self.byHandPopup.setLabels(pos, strawID, meas_type_label)

            # Get Data
            meas, pass_fail = self.byHandPopup.byHand_main(eval_expression)

            # Save new data -- also set self.bools
            self.measurements[pos][meas_type] = meas  # save meas
            self.bools[pos][meas_type] = pass_fail  # save bool

            # Display new measurement
            if (
                meas != 0.0
            ):  # meas == 0.0 if no text if entered (user presses x in corner)
                if meas >= 1000.0:
                    self.meas_input[pos][meas_type].setText("Inf")
                else:
                    self.meas_input[pos][meas_type].setText(str(meas))
                # Change LED
                self.LEDchange(pass_fail, self.led[pos][meas_type])
                # If collectData() is run again later, combineData() needs most recent measurements
                self.old_measurements[pos][meas_type] = meas
                self.old_bools[pos][meas_type] = pass_fail

                if not any(
                    None in x
                    for x in [i for i, j in zip(self.bools, self.strawIDs) if j]
                ):
                    self.dataRecorded = True
                    self.enableButtons()
            else:
                self.measureByHand_counter -= (
                    1  # if broken early, counter doesn't increase
                )
                break  # user pressed x in corner, stop running measureByHand()

    def consolidateOldAndNewMeasurements(self):
        for pos in range(24):
            for i in range(4):
                new_measurement = self.measurements[pos][i]
                old_measurement = self.old_measurements[pos][i]
                if old_measurement != None:  # Prevents errors during first collection
                    # Save smallest measurement
                    keep_meas = min(old_measurement, new_measurement)
                    self.measurements[pos][i] = keep_meas

    # Update self.bools (the measurements' pass-fail status) from the
    # measurements themselves using the dict self.meas_type_eval
    def updatePassFailStatus(self):
        for pos in range(0, 24):
            for i in range(4):
                meas = self.measurements[pos][i]
                self.bools[pos][i] = self.meas_type_eval[i](meas)

    # Set the data member self.failed_measurements from self.bools.
    # It's a list of lists [ [position, int(ResistanceMeasurementConfig)], ...]
    def setFailedMeasurements(self):
        self.failed_measurements = list()
        for pos in range(24):
            for i in range(4):
                if not self.bools[pos][i] and self.strawIDs[pos]:
                    self.failed_measurements.append([pos, i])

    def showByHandMeasurementInstructions(self, pos, measurement_type):
        left_instructions = {0: "inside", 1: "inside", 2: "outside", 3: "outside"}
        right_instructions = {0: "inside", 1: "outside", 2: "inside", 3: "outside"}

        strawID = self.strawIDs[pos]

        # Instructions
        instructions = "Measure straw at position " + str(pos) + " (" + strawID + ").\n"
        instructions += (
            "Person on left measure "
            + left_instructions[measurement_type]
            + " the straw.\n"
        )
        instructions += (
            "Person on right measure "
            + right_instructions[measurement_type]
            + " the straw.\n"
        )

        QMessageBox.about(self, "Measure by Hand", instructions)

    #############################################################################
    # Save
    #############################################################################
    def saveData(self):
        logger.info("Saving Data!")
        self.configureSaveData()
        self.saveDataToText()
        self.saveDataToDB()
        QMessageBox.about(self, "Save", "Data saved successfully!")

    def saveDataToText(self):
        self.saveResistanceDataToText()
        self.savePalletDataToText()

    def saveDataToDB(self):
        # TODO perform checks on the validity/completeness of entries
        [entry.commit() for entry in self.db_entries]

    # save the csv file of straw-by-straw measurements
    def saveResistanceDataToText(self):
        self.prepareSaveFile()
        file_name = self.makeResistanceDataFileName()
        logger.debug(f"Saving resistance data to {file_name}")
        saveF = open(file_name, "a+")
        saveF.write(self.saveFile)
        saveF.close()

    # save in the pallet file whether each straw passed or failed resistance
    # measurements
    def savePalletDataToText(self):
        for palletid in os.listdir(self.palletDirectory):
            for pallet in os.listdir(self.palletDirectory / palletid):
                if self.palletNumber + ".csv" == pallet:
                    pfile = self.palletDirectory / palletid / pallet
                    logger.debug(f"Saving pallet info to {pfile}")
                    with open(pfile, "a") as file:
                        # Record Session Data
                        file.write(
                            "\n" + datetime.now().strftime("%Y-%m-%d_%H:%M") + ","
                        )  # Date
                        file.write(self.stationID + ",")  # Test ID

                        # Record each straw and whether it passes/fails
                        for i in range(24):
                            straw = self.strawIDs[i]
                            pass_fail = ""

                            # If straw doesn't exist
                            if straw == None:
                                straw = "_______"  # _ x7
                                pass_fail = "_"

                            # If straw exists, summarize all four booleans (1 fail --> straw fails)
                            else:
                                boolean = True
                                for j in range(4):
                                    if self.bools[i][j] == False:
                                        boolean = False

                                if boolean:
                                    pass_fail = "P"
                                else:
                                    pass_fail = "F"

                            file.write(straw + "," + pass_fail + ",")

                        i = 0
                        for worker in self.sessionWorkers:
                            file.write(worker)
                            if i != len(self.sessionWorkers) - 1:
                                file.write(",")
                            i += 1

    # clean data -- assemble self.db_entries and self.clean_data from raw
    # self.measurements array. Don't make db entries where there no straws.
    def configureSaveData(self):
        logger.debug("Cleaning data...")
        assert self.strawIDs is not None, logger.error(
            "configureSaveData: self.strawIDs is None!"
        )
        # straw loop
        for pos in range(24):
            db_entry = None
            if self.strawIDs[pos]:
                straw_id = int(self.strawIDs[pos][2:])
                db_entry = self.procedure.StrawResistanceMeasurement(
                    procedure=self.procedure, straw=straw_id
                )
            else:
                logger.debug(f"No straw in position {pos}.")

            for config in ResistanceMeasurementConfig:
                i = config.value  # for backwards compatibility
                resistance = self.measurements[pos][i]
                resistance = resistance if resistance <= 1000 else float("inf")

                pass_fail = "pass" if self.bools[pos][i] else "fail"

                if self.strawIDs[pos] and db_entry:
                    db_entry.setMeasurement(resistance, config.name.lower())

                # TODO stop using self.clean_data multi-dim array for anything
                self.clean_data[pos][i] = (
                    resistance,
                    pass_fail,
                )

            if self.strawIDs[pos] and db_entry:
                self.db_entries.append(db_entry)

    # assemble csv file of straw-by-straw resistance measurements
    def prepareSaveFile(self):
        heading = "Straw Number, Timestamp, Worker ID, Pallet ID, Resistance(Ohms), Temp(C), Humidity(%), Measurement Type, Pass/Fail \n"
        # temperature, humidity = self.getTempHumid()
        temperature, humidity = 70.1, 40

        worker_with_creds = ""
        for worker in self.sessionWorkers:
            if self.credentialChecker.checkCredentials(worker):
                worker_with_creds = worker.lower()
                break

        # Start compiling data into self.saveFile:
        self.saveFile += heading
        for pos in range(24):
            strawID = self.strawIDs[pos]

            for i in range(4):
                if strawID:
                    measurement_type = self.meas_type_labels_apprev[i]
                    measurement = self.clean_data[pos][i][0]
                    pass_fail = self.clean_data[pos][i][1]
                    self.saveFile += strawID.lower() + ","
                    self.saveFile += datetime.now().strftime("%Y-%m-%d_%H%M%S_") + ","
                    self.saveFile += worker_with_creds + ","
                    self.saveFile += self.palletNumber.lower() + ","
                    self.saveFile += "%9.5f" % measurement + ","
                    self.saveFile += str(temperature) + ","
                    self.saveFile += str(humidity) + ","
                    self.saveFile += measurement_type + ","
                    self.saveFile += pass_fail

                else:
                    # Save blanks for all cells
                    self.saveFile += "_______,__________________,"  # strawID, timestamp
                    for i in range(len(worker_with_creds)):
                        self.saveFile += "_"  # workerID
                    self.saveFile += (
                        ",________,___,____,__,__,____"  # CPAL --> pass/fail
                    )

                self.saveFile += "\n"

    # get straw-by-straw resistance measurement csv file fullpath
    def makeResistanceDataFileName(self):
        day = datetime.now().strftime("%Y-%m-%d_%H%M%S_")
        # Get lowest straw id
        i = 0
        while self.strawIDs[i] == None:
            i += 1
        j = 23
        while self.strawIDs[j] == None:
            j -= 1
        first_strawID = self.strawIDs[i]
        last_strawID = self.strawIDs[j]
        data_dir = GetProjectPaths()["strawresistance"]
        return data_dir / f"Straw_Resistance{day}_{first_strawID}-{last_strawID}.csv"

    #############################################################################
    # GUI Display/Control
    #############################################################################
    def enableButtons(self):
        # enable/disable buttons depending on state in data collection process
        self.ui.save_button.setEnabled(bool(self.dataRecorded))
        self.ui.collect_button.setEnabled(
            self.collectData_counter < self.collectData_limit
        )
        self.ui.collect_button.setAutoDefault(
            self.collectData_counter < self.collectData_limit
        )
        self.ui.editPallet_button.setEnabled(bool(self.palletNumber))

    def updatePositionDisplay(self):
        # Uses most recent self.strawIDs list to (dis/en)able position boxes and label with straw ID.
        for i in range(24):
            # If there is a straw in the given position:
            if self.strawIDs[i]:
                self.straw_ID_labels[i].setText(
                    self.strawIDs[i]
                )  # Given position box the appropriate straw label
            else:
                self.straw_ID_labels[i].setText("NO STRAW")  # no label
                for lineEdit in self.meas_input[i]:
                    lineEdit.setText("")
                    lineEdit.setPlaceholderText("")
                    lineEdit.setReadOnly(True)
                for led in self.led[i]:
                    self.LEDchange(None, led)
            self.box[i].setEnabled(
                bool(self.strawIDs[i])
            )  # (En/Dis)able all elements in box if straw does(n't) exist

    def displayData(self):
        for pos in range(24):
            if self.strawIDs[pos]:  #!= None
                for i in range(4):
                    self.LEDchange(self.bools[pos][i], self.led[pos][i])
                    the_measurement = self.measurements[pos][i]
                    self.meas_input[pos][i].setText(self.resMeasString(the_measurement))

    def resMeasString(self, meas):
        if not meas:  # (if meas == None)
            return ""
        if meas >= 1000.0:
            return "Inf"
        else:
            return str(meas)

    def LEDreset(self):
        for pos in self.led:
            for led in pos:
                led.setPixmap(QPixmap("images/white.png"))
        self.ui.errorLED.setPixmap(QPixmap("images/white.png"))

    def LEDchange(self, data, led):
        reset = QPixmap("images/white.png")
        failed = QPixmap("images/red.png")
        passed = QPixmap("images/green.png")

        if data == None:
            led.setPixmap(reset)
        elif data == True:
            led.setPixmap(passed)
        else:
            led.setPixmap(failed)

    def setStatus(self, status):
        pixMap = {
            "processing": QPixmap("images/yellow.png"),
            True: QPixmap("images/green.png"),
            False: QPixmap("images/red.png"),
            "reset": QPixmap("images/white.png"),
        }
        if status in pixMap.keys():
            self.ui.errorLED.setPixmap(pixMap[status])

    def displayError(self, failed: bool):
        red = QPixmap("images/red.png")
        green = QPixmap("images/green.png")
        status_color = red if failed else green
        self.ui.errorLED.setPixmap(status_color)

    #############################################################################
    # Utility
    #############################################################################
    def resetGUI(self):
        # Reset text
        for pos in range(24):
            for i in range(4):
                self.meas_input[pos][i].setText("")

        # Data Lists
        self.measurements = [[None for i in range(4)] for pos in range(24)]
        self.old_measurements = [[None for i in range(4)] for pos in range(24)]
        self.bools = [[None for i in range(4)] for pos in range(24)]
        self.old_bools = [[None for i in range(4)] for pos in range(24)]

        # self.resistanceMeter = Resistance()
        self.multiMeter = None

        self.strawIDs = [None for i in range(24)]

        self.palletNumber = None
        self.straw1ID = None
        self.palletInfoVerified = False
        self.calledInitializePallet = False

        self.clean_data = [[None for i in range(4)] for pos in range(24)]
        self.saveFile = ""
        for el in self.straw_ID_labels:
            el.setText("St#####")
        for box in self.box:
            box.setEnabled(True)
        self.LEDreset()

        # Measurement status
        self.collectData_counter = 0
        self.measureByHand_ = 0
        self.dataRecorded = False

        # Reset buttons
        self.enableButtons()

    def closeEvent(self, event):
        event.accept()
        self.DP.handleClose()
        self.close()
        sys.exit(0)

    ############################################################################
    # Deprecated
    ############################################################################
    # temp-humid not important for resistance measurements
    def getTempHumid(self):
        directory = GetProjectPaths()["temp_humid_data"] / "464B"
        D = os.listdir(directory)
        filename = ""
        for entry in D:
            if entry.startswith("464B_" + datetime.now().strftime("%Y-%m-%d")):
                filename = entry
        with open(directory / filename) as file:
            data = csv.reader(file)
            i = "first"
            for row in data:
                if i == "first":
                    i = "not first"
                    continue
                else:
                    temperature = float(row[1])
                    humidity = float(row[2])
        return temperature, humidity


def except_hook(exctype, exception, tb):
    """
    except_hook(exctype, exception, traceback)

    Description: Enables exception handling that is more intuitive. By default, uncaught exceptions
                 cause PyQt GUIs to hang and then display the "Python has encountered and error and
                 needs to close" box. By defining this function (and setting sys.excepthook = except_hook
                 in the main function), uncaught exceptions immediately close the GUI, and display the
                 error message on screen (like a normal python script).

    Parameter: exctype - The class of the uncaught exception
    Parameter: exception - Exception object that went uncaught.
    Parameter: tb - The traceback of the exception that specifies where and why it happened.
    """
    logger.error("Logging an uncaught exception", exc_info=(exctype, exception, tb))
    sys.exit()


def run():
    sys.excepthook = except_hook  # crash, don't hang when an exception is raised
    app = QApplication(sys.argv)
    paths = GetProjectPaths()
    ctr = StrawResistanceGUI(paths, app)
    ctr.show()
    app.exec_()


if __name__ == "__main__":
    run()
