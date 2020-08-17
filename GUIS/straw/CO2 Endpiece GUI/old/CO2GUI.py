import pyautogui
import time
import os
import csv
import sys
from datetime import datetime
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from co2 import Ui_MainWindow  ## edit via Qt Designer

sys.path.insert(0, '\\\\MU2E-CART1\\Users\\Public\\Database Backup\\Remove')
from removeStraw import *

sys.path.insert(0, '\\\\MU2E-CART1\\Users\\Public\\Database Backup\\workers\\credentials')
from credentials import Credentials

pyautogui.FAILSAFE = True #Move mouse to top left corner to abort script


class CO2(QMainWindow):
    def __init__(self, webapp=None, parent=None):
        super(CO2,self).__init__(parent) 
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.palletDirectory = '\\\\MU2E-CART1\\Users\\Public\\Database Backup\\Pallets\\'
        self.workerDirectory = '\\\\MU2E-CART1\\Users\\Public\\Database Backup\\workers\\straw workers\\CO2 endpiece insertion\\'
        self.epoxyDirectory = '\\\\MU2E-CART1\\Users\\Public\\Database Backup\\CO2 endpiece data\\'
        self.boardPath = '\\\\MU2E-CART1\\Users\\Public\\Database Backup\\Status Board 464\\'
        self.ui.PortalButtons.buttonClicked.connect(self.Change_worker_ID)
        self.Current_workers = [self.ui.Current_worker1, self.ui.Current_worker2, self.ui.Current_worker3, self.ui.Current_worker4]
        self.portals = [self.ui.portal1,self.ui.portal2,self.ui.portal3,self.ui.portal4]
        self.ui.start.clicked.connect(self.initialData)
        self.ui.finishInsertion.clicked.connect(self.timeUp)
        self.ui.finish.clicked.connect(self.saveData)
        self.ui.viewButton.clicked.connect(self.editPallet)
        self.palletID = ''
        self.palletNum = ''
        self.epoxyBatch = ''
        self.DP190Batch = ''
        self.straws = []
        self.sessionWorkers = []
        self.temp = True
        self.ui.sec_disp.setNumDigits(2)
        self.ui.sec_disp.setSegmentStyle(2)
        self.ui.min_disp.setNumDigits(2)
        self.ui.min_disp.setSegmentStyle(2)
        self.ui.hour_disp.setNumDigits(2)
        self.ui.hour_disp.setSegmentStyle(2)
        self.justLogOut = ''
        self.saveWorkers()
        
    def Change_worker_ID(self, btn):
        label = btn.text()
        portalNum = int(btn.objectName().strip('portal')) - 1
        if label == 'Log In':
            Current_worker, ok = QInputDialog.getText(self, 'Worker Log In', 'Scan your worker ID:')
            if not ok:
                return
            self.sessionWorkers.append(Current_worker)
            self.Current_workers[portalNum].setText(Current_worker)
            print('Welcome ' + self.Current_workers[portalNum].text() + ' :)')
            btn.setText('Log Out')
            self.ui.tabWidget.setCurrentIndex(1)
        elif label == 'Log Out':
            self.justLogOut = self.Current_workers[portalNum].text()
            self.sessionWorkers.remove(self.Current_workers[portalNum].text())
            print('Goodbye ' + self.Current_workers[portalNum].text() + ' :(')
            Current_worker = ''
            self.Current_workers[portalNum].setText(Current_worker)
            btn.setText('Log In')
        self.saveWorkers()
        self.justLogOut = ''
        
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
        credentials = False
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
                        if qualification == 'CO2':
                            credentials = True
        return credentials

    def lockGUI(self, credentials):
        self.ui.tabWidget.setTabText(1, 'CO2 Endpiece')
        if not credentials:
            self.ui.tabWidget.setCurrentIndex(0)
            self.ui.tabWidget.setTabText(1, 'CO2 Endpiece *Locked*')

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
        self.palletNum = self.ui.palletNumInput.text()
        self.epoxyBatch = self.ui.epoxyBatchInput.text()
        self.DP190Batch = self.ui.DP190BatchInput.text()
        valid = [True,True,True,True]
        if not self.palletNum.startswith('CPAL'):
            valid[1] = False
            self.ui.palletNumInput.setStyleSheet('background-color:rgb(255, 0, 0)')
        try:
            if not int(self.palletNum[4:]) < 10000:
                valid[1] = False
                self.ui.palletNumInput.setStyleSheet('background-color:rgb(255, 0, 0)')
        except ValueError:
            valid[1] = False
            self.ui.palletNumInput.setStyleSheet('background-color:rgb(255, 0, 0)')
        valid[0] = False
        for palletid in os.listdir(self.palletDirectory):
            for pallet in os.listdir(self.palletDirectory + palletid + '\\'):
                if self.palletNum + '.csv' == pallet:
                    self.palletID = palletid
                    valid[0] = True
        if not self.epoxyBatch.startswith('CO2.') or not self.epoxyBatch[10] == '.':
            valid[2] = False
            self.ui.epoxyBatchInput.setStyleSheet('background-color:rgb(255, 0, 0)')
            if self.epoxyBatch == '':
                self.ui.epoxyBatchInput.setStyleSheet('background-color:rgb(149, 186, 255)')
        if not self.DP190Batch.startswith('DP190'):
            self.ui.DP190BatchInput.setStyleSheet('background-color:rgb(255, 0, 0)')
            valid[3] = False
        if self.DP190Batch == '':
            self.ui.DP190BatchInput.setStyleSheet('background-color:rgb(149, 186, 255)')
            valid[3] = False
        if valid[1] == True:
            self.ui.palletNumInput.setStyleSheet('')
        if valid[2] == True:
            self.ui.epoxyBatchInput.setStyleSheet('')
        if valid[3] == True:
            self.ui.DP190BatchInput.setStyleSheet('')
        if all(valid):
            if not self.palletPass(self.palletNum , 'ohms') or not self.palletPass(self.palletNum , 'prep'):
                msg = QMessageBox()
                msg.setText('At least one straw in this pallet has either failed an earlier step of production or was not tested/processed at all. Either complete this previous step or remove the failed straw.')
                msg.setWindowTitle('Quality Control Eror')
                msg.exec_()
                return
            self.ui.palletNumInput.setDisabled(True)
            self.ui.epoxyBatchInput.setDisabled(True)
            self.ui.DP190BatchInput.setDisabled(True)
            self.ui.start.setDisabled(True)
            self.ui.viewButton.setEnabled(True)
            self.ui.finishInsertion.setEnabled(True)
            self.stopWatch()

    def stopWatch(self):
        begin = time.time()
        while self.temp:
            running = time.time() - begin
            self.ui.hour_disp.display(int(running/3600))
            self.ui.min_disp.display(int(running/60)%60)
            self.ui.sec_disp.display(int(running)%60)
            credentials = self.checkCredentials()
            self.lockGUI(credentials)
            app.processEvents()
            time.sleep(.1)
        self.temp = True
        self.ui.finishInsertion.setDisabled(True)
        self.ui.finish.setEnabled(True)
            
    def timeUp(self):
        self.temp = False
        
    def saveData(self):
        if os.path.exists(self.palletDirectory + self.palletID + '\\' + self.palletNum + '.csv'):
            with open(self.palletDirectory + self.palletID + '\\' + self.palletNum + '.csv') as palletFile:
                dummy = csv.reader(palletFile)
                pallet = []
                for line in dummy:
                    pallet.append(line)
                for row in range(len(pallet)):
                    if row == len(pallet) - 1:
                        for entry in range(len(pallet[row])):
                            if entry > 1 and entry < 50:
                                if entry%2 == 0:
                                    self.straws.append(pallet[row][entry])
            with open(self.palletDirectory + self.palletID + '\\' + self.palletNum + '.csv', 'a') as palletWrite:
                palletWrite.write('\n')
                palletWrite.write(datetime.now().strftime('%Y-%m-%d_%H:%M') + ',')
                palletWrite.write('C-O2,')
                for straw in self.straws:
                    palletWrite.write(straw)
                    palletWrite.write(',')
                    if straw != '':
                        palletWrite.write('P')
                    palletWrite.write(',')
                i = 0
                for worker in self.sessionWorkers:
                    palletWrite.write(worker)
                    if i != len(self.sessionWorkers) - 1:
                        palletWrite.write(',')
                    i = i + 1
        with open(self.epoxyDirectory + self.palletNum + '.csv', 'w+') as file:
            header = 'Timestamp, Pallet ID, Epoxy Batch #, DP190 Batch #, CO2 endpiece insertion time (H:M:S), workers ***NEWLINE: Comments (optional)***\n'
            file.write(header)
            file.write(datetime.now().strftime('%Y-%m-%d_%H:%M') + ',')
            file.write(self.palletID + ',' + self.epoxyBatch + ',' + self.DP190Batch + ',')
            file.write(str(self.ui.hour_disp.intValue()) + ':' + str(self.ui.min_disp.intValue()) + ':' + str(self.ui.sec_disp.intValue()) + ',')
            i = 0
            for worker in self.sessionWorkers:
                file.write(worker)
                if i != len(self.sessionWorkers) - 1:
                    file.write(',')
                i = i + 1
            if self.ui.commentBox.document().toPlainText() != '':
                file.write('\n' + self.ui.commentBox.document().toPlainText())
        self.resetGUI()
                
    def resetGUI(self):
        self.palletID = ''
        self.palletNum = ''
        self.epoxyBatch = ''
        self.DP190Batch = ''
        self.straws = []
        self.sessionWorkers = []
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
        for i in range(len(self.Current_workers)):
            if self.Current_workers[i].text() != '':
                self.Change_worker_ID(self.portals[i])

    def editPallet(self):
        rem = removeStraw()
        rem.palletDirectory = self.palletDirectory
        rem.sessionWorkers = self.sessionWorkers
        CPAL, lastTask, straws, passfail = rem.getPallet(self.palletNum)
        rem.displayPallet(CPAL, lastTask, straws, passfail)
        rem.exec_()

    def strawPass(self, CPAL, straw, step):
        PASS = False
        for palletid in os.listdir(self.palletDirectory):
            for pallet in os.listdir(self.palletDirectory + palletid + '\\'):
                if CPAL + '.csv' == pallet:
                    with open(self.palletDirectory + palletid + '\\' + pallet, 'r') as file:
                        dummy = csv.reader(file)
                        history = []
                        for line in dummy:
                            if line != []:
                                history.append(line)
                        for line in history:
                            if line[1] == step:
                                for index in range(len(line)):
                                    if line[index] == straw and line[index + 1] == 'P':
                                        PASS = True
                            if line[1] == 'adds':
                                for index in range(len(line)):
                                    if line[index] == straw and line[index + 1].startswith('CPAL'):
                                        PASS = self.strawPass(line[index + 1], straw, step)
                                    if line[index] == straw and line[index + 1].startswith('ST'):
                                        PASS = self.strawPass(CPAL, line[index + 1], step)
        return PASS

    def palletPass(self, CPAL, step):
        PASS = False
        results = []
        straws = []
        for palletid in os.listdir(self.palletDirectory):
            for pallet in os.listdir(self.palletDirectory + palletid + '\\'):
                if CPAL + '.csv' == pallet:
                    with open(self.palletDirectory + palletid + '\\' + pallet, 'r') as file:
                        dummy = csv.reader(file)
                        history = []
                        for line in dummy:
                            if line != []:
                                history.append(line)
                        for entry in history[len(history ) - 1]:
                            if entry.startswith('ST'):
                                straws.append(entry)
        for straw in straws:
            results.append(self.strawPass(CPAL, straw, step))
        if results == []:
            return False
        return all(results)
    
    def main(self):
        while True:
            credentials = self.checkCredentials()
            self.lockGUI(credentials)
            time.sleep(.01)
            app.processEvents()
        
                            
            
if __name__=="__main__":
     app = QApplication(sys.argv)
     ctr = CO2()
     ctr.show()
     ctr.main()
     app.exec_()
