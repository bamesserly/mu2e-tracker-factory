#
#   RESISTANCE TESTING v2
#
#   Author:    Joe Dill
#   Email: <dillx031@umn.edu>
#   Previous Authors:    Cole Kampa and Zach Riehl
#   Email: <kampa041@umn.edu> , <riehl046@umn.edu>
#   Institution: University of Minnesota
#   Project: Mu2e
#   Most Recent Update: 08/24/2018
#
#   Description:
#       A Python3 script using PySerial to control and read from an Arduino Uno and PCB connected to a
#       full pallet of straws. Returns the data in the in order to be displayed by the packaged GUI.
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
#   File saved locally at: \\MU2E-CART1\Database Backup\Resistance Testing
#

#FOR TESTING ONLY!!!
#DO NOT USE IN PRODUCTION!!!

import sys
import os
import csv
from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.QtGui import *
from design import Ui_MainWindow
#from resistance import Resistance
#from measureByHand import MeasureByHandPopup
from datetime import datetime
import time

class CompletionTrack(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()

        self.meas_input = self.ui.meas_input_list          #QLineEdit objects that display measurements
        self.led = self.ui.meas_led_list                  #QLabel objects whose color indicates status of corresponding measurement
        self.box = self.ui.boxlist                        #QGroupBox objects holding info for each position of resistance measurement device
        self.straw_ID_labels = self.ui.strawID_label_list #QLabel objects labeling each box with unique straw ID
        self.initialize()

        #Directories
        self.workerDirectory = '\\\\MU2E-CART1\\Users\\Public\\Database Backup\\workers\\straw workers\\straw prep\\'
        self.palletDirectory = '\\\\MU2E-CART1\\Users\\Public\\Database Backup\\Pallets\\'
        self.prepDirectory = '\\\\MU2E-CART1\\Users\\Public\\Database Backup\\Straw prep data\\'
        self.boardPath = '\\\\MU2E-CART1\\Users\\Public\\Database Backup\\Status Board 464\\'

        #Connect buttons to respective functions
        self.ui.collect_button.clicked.connect(self.collectData)
        self.ui.byHand_button.clicked.connect(self.measureByHand)
        self.ui.reset_button.clicked.connect(self.saveReset)

        #Measurement and Bool Lists
        #Prefills lists to record 4 measurements for 24 straws
        self.measurements = [[None for i in range(4)] for pos in range(24)]
        self.old_measurements = [[None for i in range(4)] for pos in range(24)]
        self.bools = [[False for i in range(4)] for pos in range(24)]
        self.old_bools = [[False for i in range(4)] for pos in range(24)]

        self.meas_type_labels = {
            0: "inside-inside",
            1: "inside-outside",
            2: "outside-inside",
            3: "outside-outside"
            } #String identifier for

        self.meas_type_eval = { #Evaluates each type of measurement
            0: lambda meas: (50.0 <= meas <= 250.0), #i-i
            1: lambda meas: (meas >= 1000.0),        #i-o
            2: lambda meas: (meas >= 1000.0),        #o-i
            3: lambda meas: (50.0 <= meas <= 250.0), #o-o
        }
        #to determine if a given measurement passes or fails:
        #   pass_fail = self.meas_type_eval[meas_type](meas)

        self.failed_measurements = [] #used in self.measureByHand()

        #Measurement classes
        #self.dataGetter = Resistance() #resistance class
        self.byHandPopup = None #Gets created later if necessary

        #IDs
        self.palletID = None
        self.straw1ID = None
        self.strawIDs = [] #list of straw IDs filled with
        self.infoCollected = False

        #Worker Info
        self.Current_workers = [self.ui.Current_worker1, self.ui.Current_worker2, self.ui.Current_worker3, self.ui.Current_worker4]
        self.sessionWorkers = []
        self.credentials = False
        self.workerID_with_cred = None

        #Worker Portal
        self.portals = [self.ui.portal1,self.ui.portal2,self.ui.portal3,self.ui.portal4]
        self.ui.portalButtons.buttonClicked.connect(self.Change_worker_ID)

        #Saving Data
        self.dataRecorded = False
        self.saveData = [[None for i in range(4)] for pos in range(24)]
        self.oldSaveData = [[None for i in range(4)] for pos in range(24)]
        self.saveFile = ''

        #Measurement Status
        self.collectData_counter = 0
        self.collectData_limit = 5
        self.measureByHand_counter = 0

        #Configure Buttons using Measurement Status
        self.enableButtons()

        #LogOut
        self.justLogOut = ''
        self.saveWorkers()

        #Keep program running
        self.run_program = True

    def saveReset(self):
        if self.measureByHand_counter <2:
            message = "There are some failed measurements. Would you like to try measuring by hand?"
            buttonReply = QMessageBox.question(self, 'Measure By-Hand', message, QMessageBox.Yes | QMessageBox.No)
            if buttonReply == QMessageBox.Yes:
                self.measureByHand()
                return
            #double-check before save/reset
        warning = "Are you sure you want to Save? You will not be able to change this data later."
        buttonReply = QMessageBox.question(self, 'Save?', warning, QMessageBox.Yes | QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            #Save data
            self.save()

            #Ask to reset
            reset_text = "Would you like to resistance test another pallet?"
            buttonReply = QMessageBox.question(self, 'Test another pallet?', reset_text, QMessageBox.Yes | QMessageBox.No)
            if buttonReply == QMessageBox.Yes:
                self.reset() #reset; user can start another pallet
            if buttonReply == QMessageBox.No:
                self.run_program = False

    def reset(self):
        #Reset text
        for pos in range(1,25):
            for i in range(4):
                self.meas_input[pos-1][i].setText("")

        #Data Lists
        self.measurements = [[None for i in range(4)] for pos in range(24)]
        self.old_measurements = [[None for i in range(4)] for pos in range(24)]
        self.bools = [[False for i in range(4)] for pos in range(24)]
        self.old_bools = [[False for i in range(4)] for pos in range(24)]
        
        #self.dataGetter = Resistance()
        self.multiMeter = None

        self.strawIDs = []

        self.palletID = None
        self.straw1ID = None
        self.infoCollected = False

        self.saveData = [[None for i in range(4)] for pos in range(24)]
        self.oldSaveData = [[None for i in range(4)] for pos in range(24)]
        self.saveFile = ''
        for el in self.straw_ID_labels:
            el.setText('St#####')
        self.LEDreset()

        self.saveData = [[None for i in range(4)] for pos in range(24)]
        self.oldSaveData = [[None for i in range(4)] for pos in range(24)]
        self.saveFile = ''

        #Measurement status
        self.collectData_counter = 0
        self.measureByHand_ = 0
        self.dataRecorded = False

        #Reset buttons
        self.enableButtons()

    def getPalletID(self):
        pallet, ok = QInputDialog.getText(self, 'Pallet ID', 'Please scan the Pallet Number (CPAL####)')
        if self.verifyPalletID(pallet):
            self.palletID = pallet
        else:
            self.getPalletID()

    def getPos1StrawID(self):
        straw1, ok = QInputDialog.getText(self, 'Position 1 Straw ID', 'Please scan the ID of the straw in Position 1 (st#####)')
        if self.verifyStraw1ID(straw1):
            self.straw1ID = straw1
            self.assignStrawIDs()
        else:
            self.getPos1StrawID()

    def Change_worker_ID(self, btn):
        label = btn.text()
        portalNum = 0
        if label == 'Log In':
            portalNum = self.portals.index(btn)
            #portalNum = int(btn.objectName().strip('portal')) - 1
            Current_worker, ok = QInputDialog.getText(self, 'Worker Log In', 'Scan your worker ID:')
            if not ok:
                return
            self.sessionWorkers.append(Current_worker.lower())
            self.Current_workers[portalNum].setText(Current_worker.lower())
            print('Welcome ' + self.Current_workers[portalNum].text() + ' :)')
            btn.setText('Log Out')
            self.ui.tab_widget.setCurrentIndex(1)
        elif label == 'Log Out':
            portalNum = self.portals.index(btn)
            self.justLogOut = self.Current_workers[portalNum].text()
            print('Goodbye ' + self.Current_workers[portalNum].text() + ' :(')
            Current_worker = ''
            self.Current_workers[portalNum].setText(Current_worker)
            btn.setText('Log In')
        self.saveWorkers()
        self.justLogOut = ''
        self.checkCredentials()

    def saveWorkers(self):
        previousWorkers = []
        activeWorkers = []
        exists = os.path.exists(self.workerDirectory + datetime.now().strftime("%Y-%m-%d") + '.csv')
        if exists:
            with open(self.workerDirectory + datetime.now().strftime("%Y-%m-%d") + '.csv','r') as previous:
                today = csv.reader(previous)
                for row in today:
                    previousWorkers = []
                    for worker in row:
                        previousWorkers.append(worker)
        for i in range(len(self.Current_workers)):
            if self.Current_workers[i].text() != '':
                activeWorkers.append(self.Current_workers[i].text())
        for prev in previousWorkers:
            already = False
            for act in activeWorkers:
                if prev == act:
                    already = True
            if not already:
                if prev != self.justLogOut:
                    activeWorkers.append(prev)
        with open(self.workerDirectory + datetime.now().strftime("%Y-%m-%d") + '.csv','a+') as workers:
            if exists:
                workers.write('\n')
            if len(activeWorkers) == 0:
                workers.write(',')
            for i in range(len(activeWorkers)):
                    workers.write(activeWorkers[i])
                    if i != len(activeWorkers) - 1:
                        workers.write(',')

    def checkCredentials(self):
        credentialsDir = '\\\\MU2E-CART1\\Users\\Public\\Database Backup\\workers\\credentials\\credentials.csv'
        self.credentials = False
        self.workerID_with_cred = None
        master = []
        with open(credentialsDir) as file:
            file.seek(0)
            fileArray = csv.reader(file)
            for element in fileArray:
                master.append(element)
        currentWorkers = []
        for dude in self.Current_workers:
            currentWorkers.append(dude.text())
        for worker in currentWorkers:
            for person in master:
                if worker == person[0]:
                    for qualification in person:
                        if qualification == 'Resistance':
                            self.credentials = True
                            self.workerID_with_cred = worker

    def lockGUI(self):
        if self.credentials:
            self.ui.tab_widget.setTabText(1, 'Resistance Test')
        else:
            self.ui.tab_widget.setCurrentIndex(0)
            self.ui.tab_widget.setTabText(1, 'Resistance Test *Locked*')

    def getLabInfo(self):
        self.infoCollected = False
        if not self.palletID:
            self.getPalletID()
        if not self.straw1ID:
            self.getPos1StrawID()
        if self.palletID and self.straw1ID:
            self.infoCollected = True

    def verifyPalletID(self,text):
        #Verifies that the given pallet id is of a valid format
        verify = True
        pallet_id = text

        correct_ending = True
        nums = ['1','2','3','4','5','6','7','8','9','0']

        # check that last 4 characters of ID are integers
        if len(pallet_id) > 4:
            for i in range (1,5):
                if (pallet_id[len(pallet_id)-i] not in nums):
                    verify = False
                    break
        else:
            verify = False

        if not pallet_id.upper().startswith('CPAL'):
            verify = False

        return verify

    def verifyStraw1ID(self,text):
        #Verifies that the given id for the straw in position 1 is of a valid format
        straw_id = text
        verify = True
        nums = ['1','2','3','4','5','6','7','8','9','0']

        # check that last 4 characters of ID are integers
        if len(straw_id) > 4:
            for i in range (1,6):
                if (straw_id[len(straw_id)-i] not in nums):
                    verify = False
                    break
        else:
            verify = False

        if not straw_id.upper().startswith('ST'):
            verify = False

        return verify


    def getTempHumid(self):
        directory = '\\\\MU2E-CART1\\Users\Public\\Database Backup\\temp_humid_data\\464B\\'
        D = os.listdir(directory)
        filename = ''
        for entry in D:
            if entry.startswith('464B_' + datetime.now().strftime("%Y-%m-%d")):
                filename = entry
        with open(directory + filename) as file:
            data = csv.reader(file)
            i = 'first'
            for row in data:
                if i == 'first':
                    i = 'not first'
                    continue
                else:
                    temperature = float(row[1])
                    humidity = float(row[2])
        return temperature, humidity

    def enableButtons(self):
            #enable/disable buttons depending on state in data collection process
        self.ui.reset_button.setEnabled(self.dataRecorded)
        self.ui.collect_button.setEnabled(self.collectData_counter < self.collectData_limit)
        self.ui.collect_button.setAutoDefault(self.collectData_counter < self.collectData_limit)
        

    def collectData(self):
            #Shoe "processing" image
        self.ui.errorLED.setPixmap(QPixmap('images/yellow.png'))
        time.sleep(.01)
        app.processEvents()
        
        if not self.infoCollected:
            self.getLabInfo()
                #If self.getLabInfo() is successful, proceeds with collectData()
                #collectData() can only be run 10 times
        if self.infoCollected and self.collectData_counter < self.collectData_limit:
            try:
                self.measurements = self.dataGetter.rMain()
                print("self.measurements: " + str(self.measurements))
                print("old.old_measurements: " + str(self.old_measurements))
            except:
                print("Arduino Error")
                self.error(False)
                return
            print("rMain() successful!")
            self.combineDATA()
                #Update bools
            for pos in range(1,25):
                for i in range(4):
                    meas = self.measurements[pos-1][i]
                    self.bools[pos-1][i] = self.meas_type_eval[i](meas)
            print("combineDATA() successful!")
            try:
                self.updateDisplay()
            except:
                print("Display Error")
                self.error(False)
                return
            print("updateLights() successful!")
            
                #save new data to old data
            for pos in range(1,25):
                for i in range(4):
                        #Get old values
                    old_meas = self.measurements[pos-1][i]
                    old_bool = self.bools[pos-1][i]
                        #Save to lists
                    self.old_measurements[pos-1][i] = old_meas
                    self.old_bools[pos-1][i] = old_bool
                    
            self.error(True)
            self.dataRecorded = True
            self.collectData_counter += 1
            self.enableButtons()

    #BY-HAND MEASUREMENT
    def measureByHand(self):
        self.getFailedMeasurements()
        print("failed measurements:")
        print(self.failed_measurements)
        if len(self.failed_measurements) > 0:
            instructions = "Turn on the Multimeter. This program will crash if you do not."
            buttonReply = QMessageBox.question(self, 'Measure By-Hand', instructions, QMessageBox.Ok | QMessageBox.Cancel)
            if buttonReply == QMessageBox.Ok:
                
                if self.byHandPopup == None:
                    self.byHandPopup = MeasureByHandPopup() #Create Popup Window

                while not self.byHandPopup.multiMeter:
                    self.byHandPopup.getMultiMeter() #Tries to connect to multimeter
                    if not self.byHandPopup.multiMeter:
                        message = "There was an error connecting to the multimeter. Make sure it is turned on and plugged into the computer, then try again"
                        QMessageBox.about(self, "Connection Error", message)

                for el in self.failed_measurements:
                    #Record measured by hand
                    self.measureByHand_counter += 1
                    #Get Specific Measurement Information
                    pos = el[0]
                    strawID = self.strawIDs[pos-1]
                    meas_type = el[1]
                    meas_type_label = self.meas_type_labels[meas_type]
                    eval_expression = self.meas_type_eval[meas_type]
                    #Prepare labels in popup display
                    self.byHandPopup.setLabels(pos,strawID,meas_type_label)
                    print("prepared labels")
                    #Get Data
                    meas, pass_fail = self.byHandPopup.byHand_main(eval_expression)
                    print("called byHand_main()")
                        #Save new data
                    self.measurements[pos-1][meas_type] = meas #save meas
                    self.bools[pos-1][meas_type] = pass_fail #save boool
                    
                        #Display new measurement
                    if meas != 0.0: #meas == 0.0 if no text if entered (user presses x in corner)
                        if meas >= 1000.0:
                            self.meas_input[pos-1][meas_type].setText("Inf")
                        else:
                            self.meas_input[pos-1][meas_type].setText(str(meas))
                        #Change LED
                        self.LEDchange(pass_fail,self.led[pos-1][meas_type])
                        #If collectData() is run again later, combineData() needs most recent measurements
                        self.old_measurements[pos-1][meas_type] = meas 
                        self.old_bools[pos-1][meas_type] = pass_fail
                    else:
                        self.measureByHand_counter -= 1 #if broken early, counter doesn't increase
                        break #user pressed x in corner, stop running measureByHand()
                
            else:
                return
        else:
            message = "Data looks good. No by-hand measurements required!"
            QMessageBox.about(self, "Measure By-Hand", message)

    def getFailedMeasurements(self):
        self.failed_measurements = list()
        for pos in range(1,25):
            for i in range(4):
                if not self.bools[pos-1][i]:
                    self.failed_measurements.append([pos,i])

    def showByHandMeasurementInstructions(self,pos,measurement_type):
        left_instructions = {
            0: "inside",
            1: "inside",
            2: "outside",
            3: "outside"
            }
        right_instructions = {
            0: "inside",
            1: "outside",
            2: "inside",
            3: "outside"
            }

        strawID = self.strawIDs[pos-1]

        #Instructions
        instructions = "Measure straw at position " + str(pos) + " (" + strawID + ").\n"
        instructions += "Person on left measure " + left_instructions[measurement_type] + " the straw.\n"
        instructions += "Person on right measure " + right_instructions[measurement_type] + " the straw.\n"

        QMessageBox.about(self, "Measure by Hand", instructions)

    def configureSaveData(self):
        pass_fail_library = {
            True: "pass",
            False: "fail"
            }
        for pos in range(1,25):
            for i in range(4):
                resistance = self.meas_input[pos-1][i].text()     #Measurement for respective position and index
                the_bool = self.bools[pos-1][i]                   #Status of respective measurement
                pass_fail = pass_fail_library[the_bool]           #Translates bool into "pass" or "fail" for the save file
                self.saveData[pos-1][i] = (resistance,pass_fail)  #Saves measurement and pass_fail as a tuple

    def assignStrawIDs(self): #takes the numbers from the first straw's ID and assigns IDs to the remaining straws
        #Note: function assumes the straws are sequential
        initial = self.straw1ID
        st = initial[0:2]
        new = initial[2:7]
        char_find = None
        for i in range(5): #splits the leading zeros from the numbers that matter
            if new[i] != "0":
                char_find = i
                break
        st = st + new[0:char_find]
        first = new[char_find:]
        first = int(first)
        self.strawIDs = []
        arbitrary_counter = 0
        while arbitrary_counter < 24: #makes the inital box values
            self.strawIDs.append(st+str(first+arbitrary_counter))
            arbitrary_counter += 1
        s = self.strawIDs
        for ite in range(len(s)): #makes sure the number has a length of 5
            if len(s[ite]) > 7:
                p1 = s[ite][0:2]
                p2 = s[ite][3:8]
                s[ite] = p1+p2
        for i in range(24):
            self.ui.strawID_label_list[i].setText(s[i])

    def updateDisplay(self):
        for pos in range(1,25):
            for i in range(4):
                self.LEDchange(self.bools[pos-1][i],self.led[pos-1][i])
                the_measurement = self.measurements[pos-1][i]
                if the_measurement >= 1000.0:
                    display_text = "Inf"
                else:
                    display_text = str(the_measurement)
                self.meas_input[pos-1][i].setText(display_text)

    def LEDreset(self):
        for pos in self.led:
            for led in pos:
                led.setPixmap(QPixmap('images/white.png'))
        self.ui.errorLED.setPixmap(QPixmap("images/white.png"))

    def LEDchange(self,data,led):
        failed = QPixmap("images/red.png")
        passed = QPixmap("images/green.png")
        if data:
            led.setPixmap(passed)
        else:
            led.setPixmap(failed)

    def initialize(self):
        default = QPixmap("images/white.png")
        for pos in range(1,25):
            for i in range(4):
                self.led[pos-1][i].setPixmap(default)

    def combineDATA(self):
        print('\n\n')
        print("---COMBINE DATA---")
        print('\n\n')
        for pos in range(1,25):
            for i in range(4):
                print("pos " + str(pos))
                new_measurement = self.measurements[pos-1][i]
                print("new: " + str(new_measurement))
                old_measurement = self.old_measurements[pos-1][i]
                print("old: " + str(old_measurement))
                if old_measurement != None: #Prevents errors during first collection
                    #Save smallest measurement
                    keep_meas = min(old_measurement,new_measurement)
                    print("keep meas: " + str(keep_meas))
                    self.measurements[pos-1][i] = keep_meas

    def error(self,boo):
        failed = QPixmap("images/red.png")
        passed = QPixmap("images/green.png")
        if not boo:
            disp = failed
        else:
            disp = passed
        self.ui.errorLED.setPixmap(disp)

    def prepareSaveFile(self):
        heading = 'Straw Number, Timestamp, Worker ID, Pallet ID, Resistance(Ohms), Temp(C), Humidity(%), Measurement Type, Pass/Fail \n'
        temperature, humidity = self.getTempHumid()
        time_stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S_")
        #Start compiling data into self.saveFile:
        self.saveFile += heading
        for pos in range(1,25):
            for i in range(4):
                strawID = self.strawIDs[pos-1]
                measurement_type = self.meas_type_labels[i]
                measurement = self.saveData[pos-1][i][0]
                pass_fail = self.saveData[pos-1][i][1]
                self.saveFile += strawID.lower() + ','
                self.saveFile += time_stamp + ','
                self.saveFile += self.workerID_with_cred.lower() + ','
                self.saveFile += self.palletID.lower() + ','
                self.saveFile += measurement.lower() + ','
                self.saveFile += str(temperature) + ','
                self.saveFile += str(humidity) + ','
                self.saveFile += measurement_type + ','
                self.saveFile += pass_fail + '\n'

    def save(self):
        self.configureSaveData()
        self.prepareSaveFile()
        #Prepare file name
        day = datetime.now().strftime("%Y-%m-%d_%H%M%S_")
        first_strawID = self.strawIDs[0]
        last_strawID = self.strawIDs[23]
        fileName = '\\\MU2E-CART1\\Users\\Public\\Database Backup\\Resistance Testing\\Straw_Resistance_' + day + '_' + first_strawID + '-' + last_strawID + '.csv'
        #Create new file on computer
        saveF = open(fileName,'a+')
        #Write self.saveFile to new file
        saveF.write(self.saveFile)
        #Close new file. Save is complete.
        saveF.close()
        QMessageBox.about(self, "Save Successful", "Data was saved successfully!")

    def main(self):
        while self.run_program:
            while not self.credentials:
                self.checkCredentials()
                self.lockGUI()
                time.sleep(.01)
                app.processEvents()
            self.lockGUI() #Calls function one last time to change tab title
            while self.credentials and not self.infoCollected and self.run_program:
                self.getLabInfo()
                time.sleep(.01)
                app.processEvents()
            time.sleep(.01)
            app.processEvents()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ctr = CompletionTrack()
    ctr.show()
    ctr.main()
    sys.exit()
