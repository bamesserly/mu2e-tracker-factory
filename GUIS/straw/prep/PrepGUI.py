#
# PrepGUI.py
# 
# Straw Prep (Paper Pull) GUI v. 2.1
# 
# Author: Joe Dill
# email: dillx031@umn.edu
#
# Updator: Billy Haoyang Li
# email: li000400@umn.edu
#
# Updates:
#   - Easier data entry
#   - Modified prep data format (alligns strawID, batchBarcode, and PPG)
#   - Avoid duplicate prepped pallets -Billy Li
#
# Last Editted: 09/17/19
#

import pyautogui
import time
import os
import csv
import sys
from datetime import datetime
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from pynput.keyboard import Key, Controller
from pathlib import Path
from design import Ui_MainWindow  ## edit via Qt Designer
from dataProcessor import MultipleDataProcessor as DataProcessor

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, '../Upload')
from masterUpload import *

os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, str(Path(Path(__file__).resolve().parent.parent.parent.parent / 'Modules')))
import BarcodePrinter.CpalLabels.make_CPAL_labels as make_CPAL_labels

pyautogui.FAILSAFE = True #Move mouse to top left corner to abort script

# to change hitting enter to hitting tab
keyboard = Controller()

######## Global variables ##########
# Set each true/false to save the data collected when this gui is run to that platform.
# Note: Both can be true.
SAVE_TO_TXT = True
SAVE_TO_SQL = True

# Indicate which data processor you want to use for data-checking (ex: checkCredentials)
PRIMARY_DP =   'TXT'
# PRIMARY_DP =   'SQL'

##Upload to Fermi Lab database, two modes: 'prod' and 'dev'
upload_mode = 'dev'

class Prep(QMainWindow):
    def __init__(self, webapp=None, parent=None):
        super(Prep,self).__init__(parent) 
        self.ui = Ui_MainWindow()
        sys.setrecursionlimit(1800)
        self.ui.setupUi(self)
        self.workerDirectory = os.path.dirname(__file__) + '/../../../Data/workers/straw workers/straw prep/'
        self.palletDirectory = os.path.dirname(__file__) + '/../../../Data/Pallets/' 
        self.prepDirectory = os.path.dirname(__file__) + '/../../../Data/Straw Prep Data/'
        self.boardPath = os.path.dirname(__file__) + '/../../../Data/Status Board 464/'
        self.ui.PortalButtons.buttonClicked.connect(self.Change_worker_ID)
        self.ui.tab_widget.setCurrentIndex(0)
        self.Current_workers = [self.ui.Current_worker1, self.ui.Current_worker2, self.ui.Current_worker3, self.ui.Current_worker4]
        self.portals = [self.ui.portal1,self.ui.portal2,self.ui.portal3,self.ui.portal4]

        self.ui.start.clicked.connect(self.startTiming)
        self.ui.finishPull.clicked.connect(self.timeUp)
        self.ui.finish.clicked.connect(self.saveData)
        self.ui.reset.clicked.connect(self.resetGUI)

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
        self.stationID = 'prep'
        self.palletID = ""
        self.palletNumber = ""
        self.batchBarcode = "" #Use if all straws are from same batch
        self.batchBarcodes = ['' for i in range(24)] #Use if straws are from different batches
        self.pos1StrawID = "" #Use if all straws are sequential
        self.strawIDs = ['' for i in range(24)]
        self.paperPullGrades = ['' for i in range(24)]

        self.strawCount = None #will be either 23 or 24, initialy unobtained
        self.sameBatch = None #will be boolean 

        self.dataValidity = {
            "Pallet ID": False,
            "Pallet Number": False,
            "Batch Barcode": [False for i in range(24)],
            "Straw ID": [False for i in range(24)],
            "PPG": [False for i in range(24)]
        }

        self.ui.sec_disp.setNumDigits(2)
        self.ui.sec_disp.setSegmentStyle(2)
        self.ui.min_disp.setNumDigits(2)
        self.ui.min_disp.setSegmentStyle(2)
        self.ui.hour_disp.setNumDigits(2)
        self.ui.hour_disp.setSegmentStyle(2)
        self.justLogOut = ''

        # Worker Info
        self.sessionWorkers = []

        # Data Processor
        self.DP = DataProcessor(
            gui         =   self,
            save2txt    =   SAVE_TO_TXT,
            save2SQL    =   SAVE_TO_SQL,
            sql_primary =   bool(PRIMARY_DP == 'SQL')
        )


        #Progression Information
        self.calledGetUncollectedPalletInfo = False
        self.PalletInfoCollected = False
        self.dataSaved = False

        #Timing info
        self.timing = False
        self.startTime = None
        
    def upload(self):
        uploader = MakeUpload(upload_mode)
        passed = True
        i = 0
        for straw in self.strawIDs:
            try:
                if straw != "_______":
                    uploader.beginUpload(straw, self.batchBarcodes[i], self.sessionWorkers[0], self.palletNumber)
                    #print(straw, self.batchBarcodes[i], self.sessionWorkers[0], self.palletNumber)
            except UploadFailedError as error:
                last_message = error.message
                passed = False
            i = i + 1

        if passed:
            QMessageBox.about(self, "Upload", "All data uploaded successfully!")
        else:
            QMessageBox.warning(self, "Upload Error", "Some Uploads Failed\n\n" + last_message + "\n\nCheck 'errors.txt' for a complete list")
    
    def Change_worker_ID(self, btn):
        label = btn.text()
        portalNum = 0
        if label == 'Log In':
            portalNum = int(btn.objectName().strip('portal')) - 1
            Current_worker, ok = QInputDialog.getText(self, 'Worker Log In', 'Scan your worker ID:')
            if not ok:
                return
            Current_worker = Current_worker.upper()
            self.sessionWorkers.append(Current_worker)
            if PRIMARY_DP == 'SQL':
                if self.DP.validateWorkerID(Current_worker) == False:
                    QMessageBox.question(self, 'WRONG WORKER ID','Did you type in the correct worker ID?', QMessageBox.Retry)
                    return
            elif PRIMARY_DP == 'TXT':
                if self.DP.checkCredentials() == False:
                    QMessageBox.question(self, 'WRONG WORKER ID','Did you type in the correct worker ID?', QMessageBox.Retry)
                    return
            self.DP.saveLogin(Current_worker)
            self.Current_workers[portalNum].setText(Current_worker)
            print('Welcome ' + self.Current_workers[portalNum].text() + ' :)')
            btn.setText('Log Out')
        elif label == 'Log Out':
            portalNum = int(btn.objectName().strip('portal')) - 1
            self.justLogOut = self.Current_workers[portalNum].text().upper()
            self.sessionWorkers.remove(self.Current_workers[portalNum].text().upper())
            self.DP.saveLogout(self.Current_workers[portalNum].text().upper())
            print('Goodbye ' + self.Current_workers[portalNum].text() + ' :(')
            Current_worker = ''
            self.Current_workers[portalNum].setText(Current_worker)
            btn.setText('Log In')
        self.justLogOut = ''
        self.DP.saveWorkers()
        
    def lockGUI(self):
        if not self.DP.checkCredentials():
            self.resetGUI()
            self.ui.tab_widget.setCurrentIndex(0)
            self.ui.tab_widget.setTabText(1, 'Straw Prep *Locked*')
        else:
            self.ui.tab_widget.setTabText(1, 'Straw Prep')

    def updateBoard(self):
        status = []
        try:
            with open(self.boardPath + 'Progression Status.csv') as readfile:
                data = csv.reader(readfile)
                for row in data:
                    for pallet in row:
                        status.append(pallet)
            status[int(self.palletID[6:]) - 1] == 11
            with open(self.boardPath + 'Progression Status.csv', 'w') as writefile:
                i = 0
                for pallet in status:
                    writefile.write(pallet)
                    if i != 23:
                        writefile.write(',')
                    i = i + 1
        except IOError:
            print('Could not update board due to board file being accessed concurrently')

    def tab(self):
        keyboard.press(Key.tab)
    
    def getUncollectedPalletInfo(self):

        QMessageBox.question(self, 'Pallet cleaned?', "Clean the pallet with alcohol.", QMessageBox.Ok)

        reply = QMessageBox.question(self, 'Print Barcodes', 'Do you need to print barcodes?', QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            QMessageBox.question(self, 'Prepare for barcodes','Barcodes are about to print--hit ok then do not touch the mouse until finished printing!',QMessageBox.Ok)
            
            make_CPAL_labels.print_barcodes()

            QMessageBox.question(self, 'Barcodes', 'Barcodes are printing...', QMessageBox.Ok)

        QMessageBox.question(self, 'Attach barcodes', 'Attach sheet of four pallet barcodes to pallet\nand tape row of 24 straw barcodes to pallet',QMessageBox.Ok)

        self.calledGetUncollectedPalletInfo = True
        
        # Pallet ID
        c = 0 #Loop counter
        while not self.verifyPalletID() and c <= 3:

            # If invalid entry was put in manually, make lineEdit red
            if self.input_palletID.text() != '':
                self.updateLineEdit(self.input_palletID,False)

            new_id = self.askForInfo("Pallet ID")

            if new_id == '':
                return

            valid = self.verifyPalletID(new_id)
            self.updateLineEdit(self.input_palletID,valid,new_id)
            if valid:
                self.palletID = new_id
                self.dataValidity["Pallet ID"] = valid
            c += 1

        if c > 3:
            return
        
        if self.verifyPalletID():
            self.updateLineEdit(self.input_palletID,self.verifyPalletID(),self.palletID)

        # Pallet Number
        c = 0 #Loop counter
        while not self.verifyPalletNumber() and c <= 3:

            # If invalid entry was put in manually, make lineEdit red
            if self.input_palletNumber.text() != '':
                self.updateLineEdit(self.input_palletNumber,False)

            new_Number = self.askForInfo("Pallet Number")

            if new_Number == '':
                return
            
            valid = self.verifyPalletNumber(new_Number)
            self.updateLineEdit(self.input_palletNumber,valid,new_Number)
            if valid:
                self.palletNumber = new_Number
                self.dataValidity["Pallet Number"] = valid
            c += 1

        if c > 3:
            return
        
        if self.verifyPalletNumber():
            self.updateLineEdit(self.input_palletNumber,self.verifyPalletNumber(),self.palletNumber)

        #Get top Straw ID, then apply to all (sequentially)
        c = 0 #Loop counter
        while not self.verifyStrawID() and c <= 3:
            new_id = self.askForInfo("Straw ID")

            if new_id == '':
                return
                
            valid = self.verifyStrawID(new_id)
            if valid:
            #If valid, apply to all
                self.pos1StrawID = new_id
                self.assignStrawIDs() 
                for i in range(24):
                    lineEdit = self.input_strawID[i]
                    string = self.strawIDs[i] # Skips index 0 (top straw) if self.strawCount == 23
                    self.updateLineEdit(lineEdit,valid,string) #Display
                    if i == 0 and self.strawCount == 23: # Preserve 'disabled' look on top row
                        lineEdit.setStyleSheet('')
                        
                #Save Validity
                self.dataValidity["Straw ID"] = [valid for i in range(24)]
            else:
                #DisStill display bad id in top input
                self.updateLineEdit(self.input_strawID[0],valid,new_id)
            c += 1

# Get straw count
        c = 0 # loop counter
        while self.strawCount == None and c<=1:
            self.getStrawCount()
            c += 1

        # If user doesn't cooperate (and give a straw count), stop running the function
        if self.strawCount == None:
            return
        
        if c > 3:
            return

        # Batch Barcodes

        all_bbs_recorded = True
        for boolean in self.dataValidity["Batch Barcode"]:
            if not boolean:
                all_bbs_recorded = False
        
        if not all_bbs_recorded:
            message = "Are all the straws from the same batch?"
            buttonReply = QMessageBox.question(self, 'Straw Batch', message, QMessageBox.Yes | QMessageBox.No)
            if buttonReply == QMessageBox.Yes:
                self.sameBatch = True
            elif buttonReply == QMessageBox.No:
                self.sameBatch = False
            else:
                return # This indicates user pressed (x), in which case, stop looping
        
        if self.sameBatch:
            for i in range(0,24):
                if i == 0 and self.strawCount == 23:
                    break
                lineEdit = self.input_batchBarcode[i]
                lineEdit.setDisabled(True)
                lineEdit.setStyleSheet('')
                lineEdit.setText('')
                

            #Straws are sequential, get top barcode then apply to all (sequentially)
            c = 0 #Loop counter
            while not self.verifyBatchBarcode() and c <= 3:
                new_bb = self.askForInfo("Batch Barcode")

                if new_bb == '':
                    return
                
                valid = self.verifyBatchBarcode(new_bb)
                if valid:
                #If valid, apply to all
                    self.batchBarcode = new_bb
                    for index in range(len(self.batchBarcodes)):
                        self.batchBarcodes[index] = new_bb
                    #Display 
                    for i in range(24):
                        lineEdit = self.input_batchBarcode[i]
                        if i == 0 and self.strawCount == 23:
                            pass #Don't change 
                        else:
                            self.updateLineEdit(lineEdit,valid,new_bb) #Display
                    #Save Validity
                    self.dataValidity["Batch Barcode"] = [valid for i in range(24)]

                #If not valid, loop and ask for barcode again
                c += 1

            if c > 3:
                return
                
        if not self.sameBatch: # if NOT self.sameBatch, obtain and display each individually
            i = 24-self.strawCount
            loop = 0
            while i < 24 and loop <= 3:

                # Check if lineEdit doesn't already contain a valid barcode
                valid = self.verifyBatchBarcode(self.input_batchBarcode[i].text())

                if not valid:                
                    new_bb = self.askForInfo("Batch Barcode",i).upper()
                    #If user enters nothing (pressed X), stop looping.
                    if new_bb == '':
                        break

                    # Display new entry
                    valid = self.verifyBatchBarcode(new_bb)
                    lineEdit = self.input_batchBarcode[i]
                    self.updateLineEdit(lineEdit,valid,new_bb)
                    lineEdit.setEnabled(True) #Keep edittable incase mistake is made

                    if valid:
                        # If valid, save data
                        self.batchBarcodes[i] = new_bb
                        self.dataValidity["Batch Barcode"][i] = valid

                if valid:                    
                    # If valid, move onto next straw
                    i += 1
                    loop = 0
                else:
                    #Otherwise, stay on current straw
                    loop += 1

            if c > 3:
                return

            if self.strawCount == 23:
                self.input_batchBarcode[0].setText(self.input_batchBarcode[1].text())
        
        self.verifyPalletInfo() #After attempting to obtain all data, run verification

    def assignStrawIDs(self): 
        #takes the numbers from the first straw's ID and assigns IDs to the remaining straws

        # Don't run function if self.pos1strawid isn't verified
        if not self.verifyStrawID():
            return

        #Note: function assumes the straws are sequential
        initial = self.pos1StrawID
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
              
        for i in range(24): #makes the inital box values
            self.strawIDs[i] = (st+str(first+i))
            
        s = self.strawIDs
        for ite in range(len(s)): #makes sure the number has a length of 5
            if len(s[ite]) > 7:
                p1 = s[ite][0:2]
                p2 = s[ite][3:8]
                s[ite] = p1+p2

    def getStrawCount(self):
        box = QMessageBox()
        box.setIcon(QMessageBox.Question)
        box.setWindowTitle("How many straws?")
        box.setText("How many straws are on the pallet?")
        box.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
        button23 = box.button(QMessageBox.Yes)
        button23.setText("23")
        button24 = box.button(QMessageBox.No)
        button24.setText('24')
        box.exec_()
        
        if box.clickedButton() == button23:
            self.strawCount = 23
        elif box.clickedButton() == button24:
            self.strawCount = 24
        else:
            self.strawCount = None

        if self.strawCount == 23:
            # When only testing 23 straws, disable the top row of lineEdits
            inputs = [self.input_strawID,self.input_batchBarcode,self.input_paperPullGrade]
            for i in inputs:
                lineEdit = i[0] #Get first lineEdit in list
                #Disable it
                lineEdit.setDisabled(True)    
            self.input_paperPullGrade[0].setText("NO STRAW")
            self.input_batchBarcode[0].setText("NO STRAW")
            self.dataValidity["Batch Barcode"][0] = True

    def askForInfo(self,identifier,iterator=None):
        #Asks user to scan given barcode. Returns user input.
        if iterator != None:
            message = {
                "Batch Barcode": "position " + str(int(iterator)) + " batch barcode (MMDDYY.B#)",
                "Straw ID": "position " + str(int(iterator)) + " straw ID (st#####)"
            }

        else:
            message = {
                "Pallet ID": "pallet ID (CPALID##)",
                "Pallet Number": "pallet number (CPAL####)",
                "Batch Barcode": "batch barcode (MMDDYY.B#)",
                "Straw ID": "top straw ID (st#####) (even if there is no straw)"
            }           
        
        if identifier not in message.keys():
            return

        string, ok = QInputDialog.getText(self, identifier, 'Please scan ' + message[identifier])
        string=string.upper()

        return string

    def verifyPalletInfo(self):
       #This function is predominately to check if new data has been entered.
       #Pallet ID
        if self.palletID != self.input_palletID.text() or not self.dataValidity["Pallet ID"]: #If new data has been entered, or pallet ID was never verified:
            new_id = self.input_palletID.text()
            valid = self.verifyPalletID(new_id)
            if valid:
                self.palletID = new_id  #Record it
            else:
                self.palletID = "" #Set to null string
            self.updateLineEdit(self.input_palletID,valid) #And update the lineEdit background
            self.dataValidity["Pallet ID"] = valid

        #Pallet Number
        if self.palletNumber != self.input_palletNumber.text() or not self.dataValidity["Pallet Number"]: #If new data has been entered, or pallet Number was never verified:
            new_num = self.input_palletNumber.text()
            valid = self.verifyPalletNumber(new_num)
            if valid:
                self.palletNumber = new_num  #Record it
            else:
                self.palletNumber = "" #Set to null string
            self.updateLineEdit(self.input_palletNumber,valid) #And update the lineEdit background
            self.dataValidity["Pallet Number"] = valid
        
        # Batch Barcodes
        for i in range((24-self.strawCount),24):
            batch = self.input_batchBarcode[i].text()
            if (batch != self.batchBarcodes[i]) or not (self.dataValidity["Batch Barcode"][i]):
                valid = self.verifyBatchBarcode(batch)
                if valid:
                    self.batchBarcodes[i] = batch # Record if valid
                
                self.dataValidity["Batch Barcode"][i] = valid
                self.updateLineEdit(self.input_batchBarcode[i],valid) #update linEdit background

        # Straw IDs
        for i in range((24-self.strawCount),24):
            current_id = self.input_strawID[i].text()
            if (current_id != self.strawIDs[i]) or not self.dataValidity["Straw ID"][i]:
                valid = self.verifyStrawID(current_id)
                if valid:
                    self.strawIDs[i] = batch # Record if valid
                
                self.dataValidity["Straw ID"][i] = valid
                self.updateLineEdit(self.input_batchBarcode,valid) #update linEdit background

        #Summarize Booleans
        all_pass = True
        if not self.dataValidity["Pallet ID"] or not self.dataValidity["Pallet Number"]:
            all_pass = False
        for boolean in self.dataValidity["Batch Barcode"]:
            if not boolean:
                all_pass = False
        for boolean in self.dataValidity["Straw ID"]:
            if not boolean:
                all_pass = False
        
        self.PalletInfoCollected = all_pass

    def verifyPalletID(self,potential_id=None):
        
        # If no specific string is given to check as an ID, finds the most relevant string to use, and saves it.        
        if not potential_id:
            if self.palletID != self.input_palletID.text().upper():
                self.palletID = self.input_palletID.text().upper()
            potential_id = self.palletID

        potential_id = potential_id.strip().upper()

        verify = True
        if len(potential_id) != 8:
            verify = False
                
        #Starts correctly
        elif not potential_id.startswith('CPALID'):
            verify = False
                
        #Check this to prevent error checking next...
        elif not potential_id[6:].isnumeric():
            verify = False
                
        elif not int(potential_id[6:]) > 0 or not int(potential_id[6:]) <25:
            verify = False
                
        return(verify)

    def verifyPalletNumber(self,potential_num=None):

        # If no specific string is given to check as a pallet number, finds the most relevant string to use, and saves it.        
        if not potential_num:
            if self.palletNumber != self.input_palletNumber.text().upper():
                self.palletNumber = self.input_palletNumber.text().upper()
            potential_num = self.palletNumber

        potential_num = potential_num.strip().upper()
        verify = True
        if len(potential_num) != 8:
            verify = False
                
        elif not potential_num.startswith('CPAL'):
            verify = False
                
        elif not potential_num[4:].isnumeric():
            verify = False

        exist = False
        for id in range(1,24):
            path = self.palletDirectory + 'CPALID' + str(id).zfill(2) + '/' + self.palletNumber + '.csv'
            exist_tmp = os.path.exists(path)
            if exist_tmp == True:
                exist = True

        if exist ==  True:
            print(f'{self.palletNumber} has been preped.')
            verify = False
            QMessageBox.question(self, 'Duplicate CPAL Number','This pallet has been prepped!',QMessageBox.Ok)
            return(verify)
        else:
            return(verify)

    def verifyBatchBarcode(self,potential_batchID=None):

        if not potential_batchID:
            potential_batchID = self.batchBarcode

        potential_batchID = potential_batchID.strip().upper()
        verify = True
        if len(potential_batchID) != 9:
            verify = False
                
        #Starts correctly
        elif not potential_batchID[:6].isnumeric():
            verify = False

        elif not potential_batchID[8].isnumeric():
            verify = False
            
        elif not potential_batchID[6:8].upper() == '.B':
            verify = False
            
        return(verify)

    def verifyStrawID(self,potential_ID=None):
        
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
            
        return(verify)

    def verifyPaperPullGrade(self,potential_ppg):

        potential_ppg = potential_ppg.strip().upper() #Always evaluate the uppercase version of the given string with no spaces
        
        valid = True

        if potential_ppg == "DNE":
            valid = True

        elif len(potential_ppg) != 4:
            valid = False
                  
        elif not potential_ppg.startswith("PP."):
            valid = False

        elif not potential_ppg[3] in ['A','B','C','D']:
            valid = False

        return(valid)
        
    def bbScan(self):
        # Get current lineEdit
        lineEdit = self.focusWidget()

        if not lineEdit in self.input_batchBarcode: # Make sure this is a ppg lineEdit
            return
        
        potential_bb = lineEdit.text().upper()
        valid = self.verifyBatchBarcode(potential_bb)
        self.updateLineEdit(lineEdit,valid,potential_bb)
        
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

        if not lineEdit in self.input_paperPullGrade: # Make sure this is a ppg lineEdit
            return
            
        # Get PPG and evaluate
        potential_ppg = self.getPreparedPPG(lineEdit) # Get lineEdit text, convert to CAPS and no spaces, puls change letters to corresponding ppg code
        valid = self.verifyPaperPullGrade(potential_ppg)

        # Update Display
        self.updateLineEdit(lineEdit,valid,potential_ppg)
        lineEdit.setEnabled(True)
        
        # If entry is invalid, set focus to that input
        if not valid:
            lineEdit.setFocus()
            lineEdit.selectAll()

        # After all evaluations, save entry and validity
        index = self.input_paperPullGrade.index(lineEdit)
        self.paperPullGrades[index] = potential_ppg
        self.dataValidity["PPG"][index] = valid        

    def getPreparedPPG(self,lineEdit):
        # Gets the text from a given lineEdit and converts it into an evalutable PPG

        if not lineEdit in self.input_paperPullGrade:
            return ''

        # Put string in all caps, and remove spaces
        string = lineEdit.text().strip().upper()

        # For ease of use if barcode scanner isn't working, simply typing a, b, c, or d, can be converted to a ppg code:
        letterToPPGCode = {
            "A": "PP.A",
            "B": "PP.B",
            "C": "PP.C",
            "D": "PP.D",
            "X": "DNE"
        }
        # Convert entered letter to correspondig PPG Code ( letter --> PP.[letter] )
        if string in letterToPPGCode.keys():
            string = letterToPPGCode[string]

        # Double check C or D entries
        if string in ["PP.C","PP.D"]:

            # Get additional lineEdit information
            index = self.input_paperPullGrade.index(lineEdit)
            straw_ID = self.strawIDs[index]

            # Send the user a message double-checking that their input was correct
            message = "Was " + straw_ID + " actually a " + string[-1] + " grade?"
            buttonReply = QMessageBox.question(self, 'Verify Input', message, QMessageBox.Yes | QMessageBox.No)

            if buttonReply == QMessageBox.No:
                string = ''

        return string

    def updateLineEdit(self,lineEdit,boolean=None,string=None,):
        #Displays text and changes background of given Q LineEdit
        styleSheets = {
            True: 'background-color:rgb(0, 255, 51)',
            False: 'background-color:rgb(255, 0, 0)',
        }
        
        if boolean != None:
            lineEdit.setStyleSheet(styleSheets[boolean])
            lineEdit.setDisabled(boolean) # If valid data is given, disable lineEdit (and visa versa)

        if string != None:
            lineEdit.setText(string)
        # If no string argument is given, don't touch text

    def startTiming(self):
        
        if not self.PalletInfoCollected:
            self.getUncollectedPalletInfo()

        else:
            #Update GUI components (dis/en)abled
            self.ui.input_palletID.setDisabled(True)
            self.ui.input_palletNumber.setDisabled(True)
            
            for i in range((24-self.strawCount),24):
                self.ui.input_list_strawBatch[i].setEnabled(False)
                self.ui.input_list_strawID[i].setEnabled(False)
                self.ui.input_list_paperPullGrade[i].setEnabled(True)
            
            self.ui.start.setDisabled(True)
            self.ui.finishPull.setEnabled(True)
            ##Begin timing
            self.startTime = time.time()
            self.DP.saveStart()
            self.timing = True
            #Set focus to first Paper Pull Input
            self.input_paperPullGrade[24-self.strawCount].setFocus()
            
    def timeUp(self):
        # Makes sure all ppg inputs are good, then stops timing
        # all_pass = True
         
        for i in range(self.strawCount):
            if not (self.dataValidity["PPG"][23-i]): # First, check that data hasn't already been verified
                #"Scan in" all unrecorded ppg entries
                self.input_paperPullGrade[23-i].setFocus()
                self.ppgScan()

                
        all_pass = True
        
        # Evaluate all relevant ppg pass/fail's
        for i in range((24-self.strawCount),24):
            boolean = self.dataValidity["PPG"][i]
            if not boolean:
                all_pass = False
                
        # Once all ppg's have been verified...
        if all_pass:
            # Record all in self.paperPullGrades
            self.paperPullGrades = ['' for ppg in range(24)]
            for i in range(24):
                self.paperPullGrades[i] = self.input_paperPullGrade[i].text().upper()
            self.timing = False # Stop timing
            self.DP.saveFinish()
            #(Dis/En)able "Finish" Buttons
            self.ui.finishPull.setEnabled(False)
            self.ui.finish.setEnabled(True)
    
    def saveData(self):
        print("Saving data...")
        self.DP.saveData()
        print("Saving data: done")
        try:
            pass
        except Exception:
            self.generateBox('critical', 'Save Error', 'Error encountered trying to save data.')
        
        self.dataSaved = True

        print("dataSaved: " + str(self.dataSaved))

        self.ui.finish.setEnabled(False)

        QMessageBox.about(self, "Save", "Data saved successfully!")

        #QMessageBox.about(self, "Upload", "Now attempting data upload.")

        self.DP.saveComment(self.ui.commentBox.document().toPlainText())
        # call upload
        #self.upload()
        self.DP.handleClose()
        self.resetGUI()
        
    def resetGUI(self):
        #Pallet ID
        self.input_palletID.setText('')
        self.input_palletID.setPlaceholderText("CPALID##")
        self.input_palletID.setStyleSheet('')
        self.input_palletID.setEnabled(True)

        #Pallet Number
        self.input_palletNumber.setText('')
        self.input_palletNumber.setPlaceholderText("CPAL####")
        self.input_palletNumber.setStyleSheet('')
        self.input_palletNumber.setEnabled(True)

        #BatchBarcodes
        for lineEdit in self.input_batchBarcode:
            lineEdit.setText('')
            lineEdit.setPlaceholderText("MMDDYY.B#")
            lineEdit.setStyleSheet('')
            lineEdit.setEnabled(False)

        #Straw IDs
        for lineEdit in self.input_strawID:
            lineEdit.setText('')
            lineEdit.setPlaceholderText("ST#####")
            lineEdit.setStyleSheet('')
            lineEdit.setEnabled(False)

        #PPGs
        for lineEdit in self.input_paperPullGrade:
            lineEdit.setText('')
            lineEdit.setPlaceholderText("PP._")
            lineEdit.setStyleSheet('')
            lineEdit.setEnabled(False)

        #Buttons
        self.ui.finish.setEnabled(False)
        self.ui.finishPull.setEnabled(False)
        self.ui.start.setEnabled(True)

        #Time Display
        self.ui.hour_disp.display(0)
        self.ui.min_disp.display(0)
        self.ui.sec_disp.display(0)

        #Comments
        self.ui.commentBox.clear()

        # Actual data to be saved
        self.palletID = ""
        self.palletNumber = ""
        self.batchBarcode = "" #Use if all straws are from same batch
        self.batchBarcodes = ['' for i in range(24)] #Use if straws are from different batches
        self.pos1StrawID = "" #Use if all straws are sequential
        self.strawIDs = ['' for i in range(24)]
        self.paperPullGrades = ['' for i in range(24)]

        self.strawCount = None #will be either 23 or 24, initialy unobtained
        self.sameBatch = None #will be boolean 

        self.dataValidity = {
            "Pallet ID": False,
            "Pallet Number": False,
            "Batch Barcode": [False for i in range(24)],
            "Straw ID": [False for i in range(24)],
            "PPG": [False for i in range(24)]
        }
        
        self.ui.sec_disp.setNumDigits(2)
        self.ui.sec_disp.setSegmentStyle(2)
        self.ui.min_disp.setNumDigits(2)
        self.ui.min_disp.setSegmentStyle(2)
        self.ui.hour_disp.setNumDigits(2)
        self.ui.hour_disp.setSegmentStyle(2)

        self.PalletInfoCollected = False
        self.calledGetUncollectedPalletInfo = False

        #Timing info
        self.timing = False
        self.startTime = None

        # If data has been saved: also log out
        if self.dataSaved:
            self.dataSaved = False
            for i in range(len(self.Current_workers)):
                if self.Current_workers[i].text() != '':
                    self.Change_worker_ID(self.portals[i])
            self.sessionWorkers = []
            self.justLogOut = ''
            self.DP.saveWorkers()

    def closeEvent(self, event):
        self.DP.handleClose()
        event.accept()
        sys.exit()

    def getElapsedTime(self):
        return self.running

    def main(self):

        while True:

            if not self.calledGetUncollectedPalletInfo:
                self.lockGUI()
                if ((self.ui.tab_widget.currentIndex() == 1)):
                    self.getUncollectedPalletInfo()

            if self.timing:
                if self.startTime == None:
                    self.startTime = time.time()

                # Update time display
                self.running = time.time() - self.startTime
                self.ui.hour_disp.display(int(self.running/3600))
                self.ui.min_disp.display(int(self.running/60)%60)
                self.ui.sec_disp.display(int(self.running)%60)

            self.lockGUI()
            app.processEvents()
            time.sleep(.05)

if __name__=="__main__":
    app = QApplication(sys.argv) 
    ctr = Prep()
    ctr.show()
    ctr.main()
    ctr.close()
    app.exec_()
    #sys.exit(app.exec_())
