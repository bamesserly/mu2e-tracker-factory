
#   Update: 10/23/18 by Joe Dill
#   Incorporated Credentials Class

#   Update: 10/24/18 by Ben Hiltbrand
#   Added upload to Mu2e Hardware database

import pyautogui
import time
import datetime
import os
import csv
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from pynput.keyboard import Key, Controller
from pathlib import Path
from co2 import Ui_MainWindow  ## edit via Qt Designer
from dataProcessor import MultipleDataProcessor as DataProcessor

#os.chdir(os.path.dirname(__file__))
os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(__file__) + '/../Remove')
from removeStraw import *

#os.chdir(os.path.dirname(__file__))
os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(__file__) + '/../Upload')
from masterUpload import *

os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(__file__) + '/../Check Straw')
from checkstraw import *

sys.path.insert(0, str(Path(Path(__file__).resolve().parent.parent.parent.parent / 'Data')))
from workers.credentials.credentials import Credentials

pyautogui.FAILSAFE = True #Move mouse to top left corner to abort script

# to change hitting enter to hitting tab
keyboard = Controller()

######## Global variables ##########
# Set each true/false to save the data collected when this gui is run to that platform.
# Note: Both can be true.
SAVE_TO_TXT = True
SAVE_TO_SQL = True

# Indicate which data processor you want to use for data-checking (ex: checkCredentials)
#PRIMARY_DP =   'TXT'
PRIMARY_DP  =   'SQL'

##Upload to Fermi Lab database, two modes: 'prod' and 'dev'
upload_mode = 'dev'

class CO2(QMainWindow):
    def __init__(self, webapp=None, parent=None):
        super(CO2,self).__init__(parent) 
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.workerDirectory = os.path.dirname(__file__) + '/../../../Data/workers/straw workers/CO2 endpiece insertion/'
        self.palletDirectory = os.path.dirname(__file__) + '/../../../Data/Pallets/' 
        self.epoxyDirectory = os.path.dirname(__file__) + '/../../../Data/CO2 endpiece data/'
        self.boardPath = os.path.dirname(__file__) + '/../../../Data/Status Board 464/'
        self.ui.PortalButtons.buttonClicked.connect(self.Change_worker_ID)
        self.stationID = 'C-O2'
        self.credentialChecker = Credentials(self.stationID)
        self.Current_workers = [self.ui.Current_worker1, self.ui.Current_worker2, self.ui.Current_worker3, self.ui.Current_worker4]
        self.portals = [self.ui.portal1,self.ui.portal2,self.ui.portal3,self.ui.portal4]
        self.ui.start.clicked.connect(self.initialData)
        self.ui.finishInsertion.clicked.connect(self.timeUp)
        self.ui.finish.clicked.connect(self.finish)
        self.ui.viewButton.clicked.connect(self.editPallet)

        self.ui.palletNumInput.returnPressed.connect(self.scan)
        self.ui.epoxyBatchInput.returnPressed.connect(self.scan)
        self.ui.DP190BatchInput.returnPressed.connect(self.scan)

        self.setTabOrder(self.ui.palletNumInput, self.ui.epoxyBatchInput)
        self.setTabOrder(self.ui.epoxyBatchInput, self.ui.DP190BatchInput)
        self.setTabOrder(self.ui.DP190BatchInput, self.ui.start)

        self.palletID = ''
        self.palletNum = ''
        self.epoxyBatch = ''
        self.DP190Batch = ''
        self.straws = []
        self.sessionWorkers = []

        self.timing = False
        self.startTime = None

        self.ui.sec_disp.setNumDigits(2)
        self.ui.sec_disp.setSegmentStyle(2)
        self.ui.min_disp.setNumDigits(2)
        self.ui.min_disp.setSegmentStyle(2)
        self.ui.hour_disp.setNumDigits(2)
        self.ui.hour_disp.setSegmentStyle(2)
        self.justLogOut = ''

        # Data Processor
        self.DP = DataProcessor(
            gui         =   self,
            save2txt    =   SAVE_TO_TXT,
            save2SQL    =   SAVE_TO_SQL,
            sql_primary =   bool(PRIMARY_DP == 'SQL')
        )
        self.DP.saveWorkers()

        # Progression Information
        self.dataSaved = False

    def Change_worker_ID(self, btn):
        label = btn.text()
        portalNum = 0
        if label == 'Log In':
            portalNum = int(btn.objectName().strip('portal')) - 1
            Current_worker, ok = QInputDialog.getText(self, 'Worker Log In', 'Scan your worker ID:')
            if not ok:
                return
            if self.credentialChecker.checkCredentials(Current_worker) == False:
                QMessageBox.question(self, 'WRONG WORKER ID','Did you type in the correct worker ID?', QMessageBox.Retry)
                return
            Current_worker = Current_worker.upper()
            self.sessionWorkers.append(Current_worker)
            self.DP.saveLogin(Current_worker)
            self.Current_workers[portalNum].setText(Current_worker)
            print('Welcome ' + self.Current_workers[portalNum].text() + ' :)')
            btn.setText('Log Out')
            #self.ui.tab_widget.setCurrentIndex(1)
        elif label == 'Log Out':
            portalNum = int(btn.objectName().strip('portal')) - 1
            self.justLogOut = self.Current_workers[portalNum].text().upper()
            self.sessionWorkers.remove(self.Current_workers[portalNum].text().upper())
            self.DP.saveLogout(self.Current_workers[portalNum].text().upper())
            print('Goodbye ' + self.Current_workers[portalNum].text() + ' :(')
            Current_worker = ''
            self.Current_workers[portalNum].setText(Current_worker)
            btn.setText('Log In')
        self.DP.saveWorkers()
        self.justLogOut = ''
        

    def lockGUI(self):
        self.ui.tab_widget.setTabText(1, 'CO2 Endpiece')
        if not self.DP.checkCredentials():
            self.resetGUI()
            self.ui.tab_widget.setCurrentIndex(0)
            self.ui.tab_widget.setTabText(1, 'CO2 Endpiece *Locked*')

    def updateBoard(self):
        status = []
        try:
            with open(self.boardPath + 'Progression Status.csv') as readfile:
                data = csv.reader(readfile)
                for row in data:
                    for pallet in row:
                        status.append(pallet)
            status[int(self.palletID[6:]) - 1] == 22
            with open(self.boardPath + 'Progression Status.csv', 'w') as writefile:
                i = 0
                for pallet in status:
                    writefile.write(pallet)
                    if i != 23:
                        writefile.write(',')
                    i = i + 1
        except IOError:
            print('Could not update board due to board file being accessed concurrently')

    def initialData(self):

        valid = [bool() for i in range(4)]

        # Get inputs
        self.palletNum  = self.ui.palletNumInput.text().strip().upper()
        self.epoxyBatch = self.ui.epoxyBatchInput.text().strip().upper()
        self.DP190Batch = self.ui.DP190BatchInput.text().strip().upper()

        # Verify inputs
        valid[1] = self.verifyPalletNumber(self.palletNum)
        valid[2] = self.verifyEpoxyBatch(self.epoxyBatch)
        valid[3] = self.verifyDP190Batch(self.DP190Batch)

        # Verify that pallet number corresponds to a CPALID
        valid[0] = False
        for palletid in os.listdir(self.palletDirectory):
            for pallet in os.listdir(self.palletDirectory + palletid + '\\'):
                if self.palletNum + '.csv' == pallet:
                    self.palletID = palletid
                    valid[0] = True

        # Update StyleSheets
        if valid[1]:
            self.ui.palletNumInput.setStyleSheet('')
            self.ui.palletNumInput.setText(self.palletNum)
            self.ui.viewButton.setEnabled(True)
        else:
            self.ui.palletNumInput.setStyleSheet('background-color:rgb(255, 0, 0)')
        
        if valid[2]:
            self.ui.epoxyBatchInput.setStyleSheet('')
            self.ui.epoxyBatchInput.setText(self.epoxyBatch)
        else:
            self.ui.epoxyBatchInput.setStyleSheet('background-color:rgb(255, 0, 0)')

        if valid[3]:
            self.ui.DP190BatchInput.setStyleSheet('')
            self.ui.DP190BatchInput.setText(self.DP190Batch)
        else:
            self.ui.DP190BatchInput.setStyleSheet('background-color:rgb(255, 0, 0)')

        if all(valid):
            try:
                check = Check()
                check.check(self.palletNum, ['prep','ohms'])
                self.ui.palletNumInput.setDisabled(True)
                self.ui.epoxyBatchInput.setDisabled(True)
                self.ui.DP190BatchInput.setDisabled(True)
                self.ui.start.setDisabled(True)
                self.ui.viewButton.setEnabled(True)
                #self.ui.finishInsertion.setEnabled(True)
                self.stopWatch()
            except StrawFailedError as error:
                QMessageBox.critical(self, "Testing Error", "Unable to test this pallet:\n" + error.message)
                self.editPallet()

    def scan(self):

        # Get current lineEdit
        lineEdit = self.focusWidget()

        string = lineEdit.text().strip().upper()

        verify = {
            self.ui.palletNumInput: self.verifyPalletNumber(string),
            self.ui.epoxyBatchInput: self.verifyEpoxyBatch(string),
            self.ui.DP190BatchInput: self.verifyDP190Batch(string)
        }
        
        if verify[lineEdit]:
            lineEdit.setText(string)
            lineEdit.setStyleSheet('')
            self.tab()

            if lineEdit == self.ui.palletNumInput:
                self.palletNum = string
                self.ui.viewButton.setEnabled(True)

        else:
            lineEdit.setFocus()
            lineEdit.selectAll()
            lineEdit.setStyleSheet('background-color:rgb(255, 0, 0)')

    def tab(self):
        keyboard.press(Key.tab)

    def verifyPalletNumber(self,pallet_num):
        #Verifies that the given pallet id is of a valid format
        verify = True
        
        # check that last 4 characters of ID are integers
        if len(pallet_num) == 8:
            verify = (pallet_num[4:7].isnumeric()) # makes sure last four digits are numbers
        else:
            verify = False # fails if palled_num

        if not pallet_num.upper().startswith('CPAL'):
            verify = False

        return verify
    
    def verifyEpoxyBatch(self,eb):
        
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
            if not int(eb[6:8]) in range(1,32):
                return False
            # Year
            if not int(eb[8:10]) in range(17,(datetime.datetime.now().year-2000)+1): # Max: current year
                return False
        if not eb[10] == '.':
            return False
        if not eb[11:13].isnumeric():
            return False
        
        return True

    def verifyDP190Batch(self,string):

        string = string.upper().strip()

        if len(string) == 9:
            return (string.startswith("DP190.") and string[6:9].isnumeric())
        else:
            return False

    def stopWatch(self):
        self.startTime = time.time()
        self.DP.saveStart()
        self.timing = True

        self.ui.finishInsertion.setEnabled(True)
        self.ui.finish.setDisabled(True)
            
    def timeUp(self):
        self.timing = False
        self.DP.saveFinish()
        self.ui.finishInsertion.setDisabled(True)
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

    def uploadData(self):
        QMessageBox.about(self, "Upload", "Now attempting data upload.")

        uploadWorker = self.sessionWorkers[0]
        uploader = getUploader(self.stationID)(upload_mode)
        passed = True
        
        for straw in self.straws:
            if straw != '_______':
                try:
                    uploader.beginUpload(straw, uploadWorker, self.epoxyBatch, self.palletNum)
                except UploadFailedError as error:
                    passed = False
                    lastMessage = error.message

        if passed:
            QMessageBox.about(self, "Upload", "All data uploaded successfully!")
        else:
            QMessageBox.warning(self, "Upload Error", "Some Uploads Failed\n\n" + lastMessage + "\n\nCheck 'errors.txt' for a complete list")
                
    def resetGUI(self):
        self.palletID = ''
        self.palletNum = ''
        self.epoxyBatch = ''
        self.DP190Batch = ''
        self.straws = []
        self.ui.palletNumInput.setEnabled(True)
        self.ui.epoxyBatchInput.setEnabled(True)
        self.ui.DP190BatchInput.setEnabled(True)
        self.ui.palletNumInput.setText('')
        self.ui.epoxyBatchInput.setText('')
        self.ui.DP190BatchInput.setText('')
        self.ui.commentBox.document().setPlainText('')
        self.ui.start.setEnabled(True)
        self.ui.hour_disp.display(0)
        self.ui.min_disp.display(0)
        self.ui.sec_disp.display(0)
        self.ui.viewButton.setDisabled(True)
        self.ui.finishInsertion.setDisabled(True)
        self.ui.finish.setDisabled(True)
        """for i in range(len(self.Current_workers)):
            if self.Current_workers[i].text() != '':
                self.Change_worker_ID(self.portals[i])
        self.sessionWorkers = []"""

    def editPallet(self):
        rem = removeStraw(self.sessionWorkers)
        rem.palletDirectory = self.palletDirectory
        CPAL, lastTask, straws, passfail = rem.getPallet(self.palletNum)
        rem.displayPallet(CPAL, lastTask, straws, passfail)
        rem.exec_()

    def finish(self):
        self.saveData()
        self.uploadData()
        self.resetGUI()

    def closeEvent(self, event):
        event.accept()
        sys.exit(0)
        
    def main(self):
        while True:

            if self.timing:
                running = time.time() - self.startTime
                self.ui.hour_disp.display(int(running/3600))
                self.ui.min_disp.display(int(running/60)%60)
                self.ui.sec_disp.display(int(running)%60)

            self.lockGUI()
            time.sleep(.01)
            app.processEvents()
        
def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)
    sys.exit()                            
            
if __name__=="__main__":
     sys.excepthook = except_hook
     app = QApplication(sys.argv)
     ctr = CO2()
     ctr.show()
     ctr.main()
     app.exec_()
