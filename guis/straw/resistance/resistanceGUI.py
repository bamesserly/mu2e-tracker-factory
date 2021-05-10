#
#   RESISTANCE TESTING v2.2
#   Most Recent Update: 10/23/2018
#
#   Author:    Joe Dill
#   Email: <dillx031@umn.edu>
#
#   Previous Authors:    Cole Kampa and Zach Riehl
#   Email: <kampa041@umn.edu> , <riehl046@umn.edu>
#
#   Institution: University of Minnesota
#   Project: Mu2e
#
#   Description:
#       A Python3 script using PySerial to control and read from an Arduino Uno and PCB connected to a
#       full pallet of straws. Returns the data in the in order to be displayed by the packaged GUI.
#
#   Updates in v 2.1:
#       - Implements remove interface
#           - View/edit pallet button
#           - When saving, strawIDs and pass/fail written to pallet file
#           - On open, user only needs to scan CPAL Number. All other info collected
#
#   Updates in v 2.2:
#       - Implements Credentials Class
#
#   Packages: PySerial, Straw (custom wrapper class), Resistance (class controlling arduino)
#
#   General Order: arbrcrdrerfrgrhrirjrkrlrmrnrorpr
#
#   Adjusted Order: 1)erfrgrhr 2)arbrcrdr 3)mrnrorpr 4)irjrkrlr
#
#   Columns in file (for database): straw_barcode, create_time, worker_barcode, workstation_barcode,
#       resistance, temperature, humidity, test_type, pass/fail
#
#   File saved at: Mu2e-factory/Straw lab GUIs/Resistance GUI

import sys
from pathlib import Path
import os
import csv
from datetime import datetime
import time
from PyQt5.QtCore import QRect, Qt, QTimer, QMetaObject, QCoreApplication
from PyQt5.QtGui import QFont, QPalette, QColor, QBrush
from PyQt5.QtWidgets import (
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
from guis.straw.resistance.design import Ui_MainWindow
from guis.straw.resistance.resistanceMeter import Resistance
from guis.straw.resistance.measureByHand import MeasureByHandPopup
from guis.straw.removestraw import removeStraw
from data.workers.credentials.credentials import Credentials
from guis.common.getresources import GetProjectPaths

class CompletionTrack(QtWidgets.QDialog):
    def __init__(self, paths):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()

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
        self.prepDirectory = paths["prepdata"]
        self.boardPath = paths["board"]

        # Connect buttons to respective functions
        self.ui.collect_button.clicked.connect(self.collectData)
        self.ui.byHand_button.clicked.connect(self.measureByHand)
        self.ui.reset_button.clicked.connect(self.resetGUI)
        self.ui.save_button.clicked.connect(self.saveReset)
        self.ui.editPallet_button.clicked.connect(self.editPallet)

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
            0: lambda meas: (40.0 <= meas <= 250.0),  # i-i
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
        self.saveData = [[None for i in range(4)] for pos in range(24)]
        self.oldSaveData = [[None for i in range(4)] for pos in range(24)]
        self.saveFile = ""

        # Measurement Status
        self.collectData_counter = 0
        self.collectData_limit = 500
        self.measureByHand_counter = 0

        # Configure Buttons using Measurement Status
        self.enableButtons()

        # LogOut
        self.justLogOut = ""
        self.saveWorkers()

        # Keep program running
        self.run_program = True

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

        self.resistanceMeter = Resistance()
        self.multiMeter = None

        self.strawIDs = [None for i in range(24)]

        self.palletNumber = None
        self.straw1ID = None
        self.palletInfoVerified = False
        self.calledInitializePallet = False

        self.saveData = [[None for i in range(4)] for pos in range(24)]
        self.oldSaveData = [[None for i in range(4)] for pos in range(24)]
        self.saveFile = ""
        for el in self.straw_ID_labels:
            el.setText("St#####")
        for box in self.box:
            box.setEnabled(True)
        self.LEDreset()

        self.saveData = [[None for i in range(4)] for pos in range(24)]
        self.oldSaveData = [[None for i in range(4)] for pos in range(24)]
        self.saveFile = ""

        # Measurement status
        self.collectData_counter = 0
        self.measureByHand_ = 0
        self.dataRecorded = False

        # Reset buttons
        self.enableButtons()

    ### WORKER PORTAL ###
    def Change_worker_ID(self, btn):
        label = btn.text()
        portalNum = self.portals.index(btn)
        if label == "Log In":
            Current_worker, ok = QInputDialog.getText(
                self, "Worker Log In", "Scan your worker ID:"
            )
            if not ok:
                return
            self.sessionWorkers.append(Current_worker)
            self.Current_workers[portalNum].setText(Current_worker)
            print("Welcome " + self.Current_workers[portalNum].text() + " :)")
            btn.setText("Log Out")
            # self.ui.tab_widget.setCurrentIndex(1)
        elif label == "Log Out":
            self.justLogOut = self.Current_workers[portalNum].text()
            self.sessionWorkers.remove(self.Current_workers[portalNum].text())
            print("Goodbye " + self.Current_workers[portalNum].text() + " :(")
            Current_worker = ""
            self.Current_workers[portalNum].setText(Current_worker)
            btn.setText("Log In")
        self.saveWorkers()
        self.justLogOut = ""

    def saveWorkers(self):
        previousWorkers = []
        activeWorkers = []
        outfilename = datetime.now().strftime("%Y-%m-%d") + ".csv"
        outfile = self.workerDirectory / outfilename
        exists = outfile.is_file()
        if exists:
            with open(outfile, "r") as previous:
                today = csv.reader(previous)
                for row in today:
                    previousWorkers = []
                    for worker in row:
                        previousWorkers.append(worker)
        for i in range(len(self.Current_workers)):
            if self.Current_workers[i].text() != "":
                activeWorkers.append(self.Current_workers[i].text())
        for prev in previousWorkers:
            already = False
            for act in activeWorkers:
                if prev == act:
                    already = True
            if not already:
                if prev != self.justLogOut:
                    activeWorkers.append(prev)
        with open(outfile, "a+") as workers:
            if exists:
                workers.write("\n")
            if len(activeWorkers) == 0:
                workers.write(",")
            for i in range(len(activeWorkers)):
                workers.write(activeWorkers[i])
                if i != len(activeWorkers) - 1:
                    workers.write(",")

    def lockGUI(self):
        if not self.credentialChecker.checkCredentials(self.sessionWorkers):
            self.resetGUI()
            self.ui.tab_widget.setCurrentIndex(0)
            self.ui.tab_widget.setTabText(1, "Resistance *Locked*")
            self.ui.tab_widget.setTabEnabled(1, False)
        else:
            self.ui.tab_widget.setTabText(1, "Resistance")
            self.ui.tab_widget.setTabEnabled(1, True)

    ### PALLET INFO ###
    def getPalletNumber(self):

        pallet, ok = QInputDialog().getText(
            self, "Pallet Number", "Please scan the Pallet Number", text="CPAL####"
        )

        pallet = pallet.strip().upper()  # remove spaces and put in CAPS

        if ok:
            if self.verifyPalletNumber(pallet):
                self.palletNumber = pallet
            else:
                self.getPalletNumber()

    def verifyPalletNumber(self, pallet_num):
        # Verifies that the given pallet id is of a valid format
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

    def initializePallet(self):

        # Obtain pallet number
        if not self.palletNumber:
            self.getPalletNumber()

        if self.palletNumber:
            # Display Pallet Info Window
            #   - Hint that user remove all failed straws
            #   - Calls interpretEditPallet() to
            #     obtain most recent pallet info
            # self.editPallet()
            rem = removeStraw(self.sessionWorkers)
            rem.palletDirectory = self.palletDirectory
            rem.sessionWorkers = self.sessionWorkers
            CPAL, lastTask, straws, passfail = rem.getPallet(self.palletNumber)
            self.interpretEditPallet(CPAL, lastTask, straws, passfail)

        self.calledInitializePallet = True

    def editPallet(self):
        rem = removeStraw(self.sessionWorkers)
        rem.palletDirectory = self.palletDirectory
        rem.sessionWorkers = self.sessionWorkers
        CPAL, lastTask, straws, passfail = rem.getPallet(self.palletNumber)
        rem.displayPallet(CPAL, lastTask, straws, passfail)
        rem.exec_()

        CPAL, lastTask, straws, passfail = rem.getPallet(
            self.palletNumber
        )  # Run again incase changes were made (straws removed, moved, etc...)
        # After executing
        self.interpretEditPallet(CPAL, lastTask, straws, passfail)

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

        # If failed straws are present, instruct user to remove them and run editPallet() (which will call this function again)
        else:
            self.palletInfoVerified = False

            instructions = "The following straws failed Straw Prep and need to be removed before testing resistance:"
            for strawID in remove_straws:
                instructions += "\n" + strawID
            buttonreply = QMessageBox.question(
                self,
                "Remove Straws",
                instructions,
                QMessageBox.Ok | QMessageBox.Cancel,
                QMessageBox.Cancel,
            )

            if buttonreply != QMessageBox.Cancel:
                self.editPallet()

    def checkForMovedStraws(self, newStrawIDs):
        # straws_moved = False
        if self.strawIDs == ["" for i in range(24)]:
            return

        for i1 in range(24):

            if not self.strawIDs[i1] and (newStrawIDs[i1] in self.strawIDs):

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

    ### RESISTANCE METER MEASUREMENT ###
    def collectData(self):
        # Show "processing" image
        self.setStatus("processing")
        time.sleep(0.01)
        app.processEvents()

        if not self.palletInfoVerified:
            self.initializePallet()
            return
            # If self.getLabInfo() is successful, proceeds with collectData()
            # collectData() can only be run 10 times
        if (
            self.palletInfoVerified
            and self.collectData_counter < self.collectData_limit
        ):

            try:
                self.measurements = self.resistanceMeter.rMain()
            except:
                print("Arduino Error")
                self.error(False)
                return

            self.combineDATA()
            # Update bools
            for pos in range(0, 24):
                for i in range(4):
                    meas = self.measurements[pos][i]
                    self.bools[pos][i] = self.meas_type_eval[i](meas)

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

            self.error(True)
            self.dataRecorded = True
            self.collectData_counter += 1
            self.enableButtons()

    def combineDATA(self):

        for pos in range(24):
            for i in range(4):
                new_measurement = self.measurements[pos][i]
                old_measurement = self.old_measurements[pos][i]
                if old_measurement != None:  # Prevents errors during first collection
                    # Save smallest measurement
                    keep_meas = min(old_measurement, new_measurement)
                    self.measurements[pos][i] = keep_meas

    ### BY-HAND MEASUREMENT ###
    def measureByHand(self):
        self.getFailedMeasurements()
        if len(self.failed_measurements) > 0:
            instructions = (
                "Turn on the Multimeter. This program will crash if you do not."
            )
            buttonReply = QMessageBox.question(
                self,
                "Measure By-Hand",
                instructions,
                QMessageBox.Ok | QMessageBox.Cancel,
            )
            if buttonReply == QMessageBox.Ok:

                if self.byHandPopup == None:
                    self.byHandPopup = MeasureByHandPopup()  # Create Popup Window
                while not self.byHandPopup.multiMeter:
                    self.byHandPopup.getMultiMeter()  # Tries to connect to multimeter
                    if not self.byHandPopup.multiMeter:
                        message = "There was an error connecting to the multimeter. Make sure it is turned on and plugged into the computer, then try again"
                        QMessageBox.about(self, "Connection Error", message)
                        print("hit the not thing")
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

                    # Save new data
                    self.measurements[pos][meas_type] = meas  # save meas
                    self.bools[pos][meas_type] = pass_fail  # save boool

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

            else:
                return
        else:
            message = "Data looks good. No by-hand measurements required!"
            QMessageBox.about(self, "Measure By-Hand", message)

    def getFailedMeasurements(self):
        self.failed_measurements = list()
        for pos in range(24):
            for i in range(4):
                if not self.bools[pos][i]:
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

    ### GUI DISPLAY ###
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

    def error(self, boo):
        failed = QPixmap("images/red.png")
        passed = QPixmap("images/green.png")
        if not boo:
            disp = failed
        else:
            disp = passed
        self.ui.errorLED.setPixmap(disp)

    ### SAVE / RESET ###
    def getTempHumid(self):
        directory = (
            os.path.dirname(__file__) + "..\\..\\..\\Data\\temp_humid_data\\464B\\"
        )
        D = os.listdir(directory)
        filename = ""
        for entry in D:
            if entry.startswith("464B_" + datetime.now().strftime("%Y-%m-%d")):
                filename = entry
        with open(directory + filename) as file:
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

    def configureSaveData(self):
        pass_fail_library = {True: "pass", False: "fail"}
        for pos in range(24):
            for i in range(4):
                resistance = self.measurements[pos][
                    i
                ]  # Measurement for respective position and index
                if resistance > 1000:
                    resistance = float("inf")
                the_bool = self.bools[pos][i]  # Status of respective measurement
                pass_fail = pass_fail_library[
                    the_bool
                ]  # Translates bool into "pass" or "fail" for the save file
                self.saveData[pos][i] = (
                    resistance,
                    pass_fail,
                )  # Saves measurement and pass_fail as a tuple

    def prepareSaveFile(self):
        heading = "Straw Number, Timestamp, Worker ID, Pallet ID, Resistance(Ohms), Temp(C), Humidity(%), Measurement Type, Pass/Fail \n"
        # temperature, humidity = self.getTempHumid()
        temperature, humidity = 70.1, 40
        time_stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S_")

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
                    measurement = self.saveData[pos][i][0]
                    pass_fail = self.saveData[pos][i][1]
                    self.saveFile += strawID.lower() + ","
                    self.saveFile += time_stamp + ","
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

    def save(self):

        ## SAVE RESISTANCE DATA ##
        ## This is a .csv file containing all resistance measurements, pass/fail's, and the temperature and humidity
        self.configureSaveData()
        self.prepareSaveFile()
        # Prepare file name
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
        fileName = (
            os.path.dirname(__file__)
            + "..\\..\\..\\Data/Resistance Testing\\Straw_Resistance"
            + day
            + "_"
            + first_strawID
            + "-"
            + last_strawID
            + ".csv"
        )
        # Create new file on computer
        saveF = open(fileName, "a+")
        # Write self.saveFile to new file
        saveF.write(self.saveFile)
        # Close new file. Save is complete.
        saveF.close()

        ## SAVE TO PALLET FILE ##
        ## This is a .txt file logging the history of each CPAL that all GUIs write to.
        for palletid in os.listdir(self.palletDirectory):
            for pallet in os.listdir(self.palletDirectory / palletid):
                if self.palletNumber + ".csv" == pallet:
                    pfile = self.palletDirectory / palletid / pallet
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

        QMessageBox.about(self, "Save", "Data saved successfully!")

    def saveReset(self):
        if self.measureByHand_counter < 2:
            message = "There are some failed measurements. Would you like to try measuring by hand?"
            buttonReply = QMessageBox.question(
                self, "Measure By-Hand", message, QMessageBox.Yes | QMessageBox.No
            )
            if buttonReply == QMessageBox.Yes:
                self.measureByHand()
                return
            # double-check before save/reset
        warning = "Are you sure you want to Save?"
        buttonReply = QMessageBox.question(
            self, "Save?", warning, QMessageBox.Yes | QMessageBox.No
        )
        if buttonReply == QMessageBox.Yes:
            # Save data
            self.save()
            self.uploadData()
            # self.resetGUI()

            """#Ask to reset
            reset_text = "Would you like to resistance test another pallet?"
            buttonReply = QMessageBox.question(self, 'Test another pallet?', reset_text, QMessageBox.Yes | QMessageBox.No)
            if buttonReply == QMessageBox.Yes:
                self.resetGUI() #reset; user can start another pallet
            if buttonReply == QMessageBox.No:
                self.run_program = False"""

    def closeEvent(self, event):
        event.accept()
        sys.exit(0)

    def main(self):
        while True:

            if not self.calledInitializePallet:
                self.lockGUI()
                if self.ui.tab_widget.currentIndex() == 1:
                    self.initializePallet()

            self.lockGUI()
            time.sleep(0.1)
            app.processEvents()


def run():
    app = QtWidgets.QApplication(sys.argv)
    paths = GetProjectPaths()
    ctr = CompletionTrack(paths)
    ctr.show()
    ctr.main()
    sys.exit()


if __name__ == "__main__":
    run()
