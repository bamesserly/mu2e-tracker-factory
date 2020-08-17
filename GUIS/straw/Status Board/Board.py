#### Bottom Inner Ring Installation
#### Goal1: PyQt5 GUI for collecting BIR per-panel data and saving to csv file

import sys, csv, time, os
from datetime import datetime
import pyautogui
import csv
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from Status1Board import Ui_MainWindow  ## edit via Qt Designer
from removeStraw import *

class Status(QMainWindow):
    """ GUI to collect data during BIR installation """
    def __init__(self, webapp=None, parent=None):
        super(Status,self).__init__(parent) 
        self.directory = os.path.dirname(os.path.realpath(__file__))+'\\'
        self.datafile = 'BIRinstall'
#        if not os.path.isfile(self.datafile+'.csv'): 
#            with open(self.datafile+'.csv', mode='a+') as f:
#                f.write('panel,bir,baseplate,wk1,wk2,insertiontime,\
#                        clamped,leftgap,rightgap,minradialgap,maxradialgap,\
#                        iscomplete,comment\n')
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.nextbuttons = [self.ui.next1,self.ui.next2,self.ui.next3,self.ui.next4,
                            self.ui.next5,self.ui.next6,self.ui.next7,self.ui.next8,
                            self.ui.next9,self.ui.next10,self.ui.next11,self.ui.next12,
                            self.ui.next13,self.ui.next14,self.ui.next15,self.ui.next16,
                            self.ui.next17,self.ui.next18,self.ui.next19,self.ui.next20,
                            self.ui.next21,self.ui.next22,self.ui.next23,self.ui.next24]
        self.lastbuttons = [self.ui.last1,self.ui.last2,self.ui.last3,self.ui.last4,
                            self.ui.last5,self.ui.last6,self.ui.last7,self.ui.last8,
                            self.ui.last9,self.ui.last10,self.ui.last11,self.ui.last12,
                            self.ui.last13,self.ui.last14,self.ui.last15,self.ui.last16,
                            self.ui.last17,self.ui.last18,self.ui.last19,self.ui.last20,
                            self.ui.last21,self.ui.last22,self.ui.last23,self.ui.last24]
        self.progbars = [self.ui.prog1,self.ui.prog2,self.ui.prog3,self.ui.prog4,
                         self.ui.prog5,self.ui.prog6,self.ui.prog7,self.ui.prog8,
                         self.ui.prog9,self.ui.prog10,self.ui.prog11,self.ui.prog12,
                         self.ui.prog13,self.ui.prog14,self.ui.prog15,self.ui.prog16,
                         self.ui.prog17,self.ui.prog18,self.ui.prog19,self.ui.prog20,
                         self.ui.prog21,self.ui.prog22,self.ui.prog23,self.ui.prog24]
        self.statbars = [self.ui.stat1,self.ui.stat2,self.ui.stat3,self.ui.stat4,
                         self.ui.stat5,self.ui.stat6,self.ui.stat7,self.ui.stat8]
        self.locations = [self.ui.pos1,self.ui.pos2,self.ui.pos3,self.ui.pos4,
                          self.ui.pos5,self.ui.pos6,self.ui.pos7,self.ui.pos8,
                          self.ui.pos9,self.ui.pos10,self.ui.pos11,self.ui.pos12,
                          self.ui.pos13,self.ui.pos14,self.ui.pos15,self.ui.pos16,
                          self.ui.pos17,self.ui.pos18,self.ui.pos19,self.ui.pos20,
                          self.ui.pos21,self.ui.pos22,self.ui.pos23,self.ui.pos24]
        self.ui.nextbuttons.buttonClicked.connect(self.next)
        self.ui.lastbuttons.buttonClicked.connect(self.last)
        self.lcd = [self.ui.disp1,self.ui.disp2,self.ui.disp3,self.ui.disp4,
                    self.ui.disp5,self.ui.disp6,self.ui.disp7,self.ui.disp8,
                    self.ui.disp9,self.ui.disp10,self.ui.disp11,self.ui.disp12]
        for lcd in self.lcd:
            lcd.setSegmentStyle(2)
        self.begin = time.time()
        self.oldPos = pyautogui.position()
        self.boardPath = os.path.dirname(__file__) + '/../../../Data/Status Board 464/'
        self.palletDirectory = os.path.dirname(__file__) + '/../../../Data/Pallets/' 

        currentLab, currentPallets, currentLocations = self.status()
        T, H, TB, HB = self.loadTH()
        self.displayStatus(currentLab, currentPallets, currentLocations, T, H, TB, HB)

        self.ui.palbuttons.buttonClicked.connect(self.editPallet)

        
    #changes progress bar status
    def next(self,btn):
        pallet = int(btn.objectName().strip('next')) - 1
        progress = [0,11,22,41,56,65,84,100]
        palletStatus = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        if os.path.exists(self.boardPath + 'Progression Status.csv'):
            with open(self.boardPath + 'Progression Status.csv', 'r') as file:
                pallets = csv.reader(file)
                for row in pallets:
                    temp = row
                i = 0
                for item in temp:
                    palletStatus[i] = int(item)
                    i = i + 1
                for step in progress:
                    if step == palletStatus[pallet]:
                        if step == 100:
                            palletStatus[pallet] = 0
                            break
                        else:
                            palletStatus[pallet] = progress[progress.index(step) + 1]
                            break
            with open(self.boardPath + 'Progression Status.csv', 'a') as file:
                i = 0
                file.write('\n')
                for pallet in palletStatus:
                    file.write(str(pallet))
                    if i != 23:
                        file.write(',')
                    i = i + 1

            
    def last(self,btn):
        pallet = int(btn.objectName().strip('last')) - 1
        progress = [0,11,22,41,56,65,84,100]
        palletStatus = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        if os.path.exists(self.boardPath + 'Progression Status.csv'):
            with open(self.boardPath + 'Progression Status.csv', 'r') as file:
                pallets = csv.reader(file)
                for row in pallets:
                    temp = row
                i = 0
                for item in temp:
                    palletStatus[i] = int(item)
                    i = i + 1
                for step in progress:
                    if step == palletStatus[pallet]:
                        if step == 0:
                            palletStatus[pallet] = 100
                            break
                        else:
                            palletStatus[pallet] = progress[progress.index(step) - 1]
                            break
            with open(self.boardPath + 'Progression Status.csv', 'w') as file:
                i = 0
                for pallet in palletStatus:
                    file.write(str(pallet))
                    if i != 23:
                        file.write(',')
                    i = i + 1

    
    #returns overallStatus list of number of pallets at each step and palletStatus list of steps for each pallet
    def status(self):
        steps = ['empt','prep','ohms','CO-2','leak','lasr','meas','silv']
        progress = [0,11,22,41,56,65,84,100]
        overallStatus = [0,0,0,0,0,0,0,0]
        palletStatus = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        locationStatus = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        #for index in range(len(palletStatus)):
        #    try:
        #        for palletid in os.listdir(self.palletDirectory):
        #            if int(palletid.strip('CPALID.csv')) == index + 1:
        #                CPAL = 'CPAL0000.csv'
        #                for pallet in os.listdir(self.palletDirectory + palletid + '\\'):
        #                    if int(pallet.strip('CPAL.csv')) > int(CPAL.strip('CPAL.csv')):
        #                        CPAL = pallet
        #                with open(self.palletDirectory + palletid + '\\' + CPAL, 'r') as file:
        #                    dummy = csv.reader(file)
        #                    history = []
        #                    for line in dummy:
        #                        if line != []:
        #                            history.append(line)
        #                    print(history[len(history) - 1][1])
        #                    palletStatus[index] = progress[steps.index(history[len(history) - 1][1])]
        #    except:
        #        print('Could not access CPALID' + str(index))
        if os.path.exists(self.boardPath + 'Progression Status.csv'):
            with open(self.boardPath + 'Progression Status.csv', 'r') as file:
                pallets = csv.reader(file)
                for row in pallets:
                    temp = row
                i = 0
                for item in temp:
                    palletStatus[i] = int(item)
                    i = i + 1
        for pallet in palletStatus:
            for step in progress:
                if pallet == step:
                    overallStatus[progress.index(step)] = overallStatus[progress.index(step)] + 1 
        if os.path.exists(self.boardPath + 'Location Status.csv'):
            with open(self.boardPath + 'Location Status.csv', 'r') as file:
                pallets = csv.reader(file)
                for row in pallets:
                    temp = row
                i = 0
                for item in temp:
                    locationStatus[i] = int(item)
                    i = i + 1
                    
        return overallStatus, palletStatus, locationStatus

    def displayStatus(self, currentLab, currentPallets, currentLocations, T, H, TB, HB):
        i=0
        for step in currentLab:
            self.lcd[i].display(currentLab[i])
            if step == 24:
                self.statbars[i].setValue(100)
            else:
                self.statbars[i].setValue((float(100)/24)*step)
            i = i+1
        for pallet in self.progbars:
            pallet.setValue(int(currentPallets[self.progbars.index(pallet)]))
        for pallet in self.locations:
            pallet.setCurrentIndex(currentLocations[self.locations.index(pallet)])
        self.lcd[8].display(T)
        self.lcd[9].display(H)
        self.lcd[10].display(TB)
        self.lcd[11].display(HB)
        
    def loadTH(self):
        #Temperature and Humidity for 464 Main Room
        temperature464 = 0
        humidity464 = 0
        temperature464B = 0
        humidity464B = 0
        directory = os.path.dirname(__file__) + '/../../../Data/temp_humid_data/464_main/'
        D = os.listdir(directory)
        filename = 'initialization'
        for entry in D:
            if entry.startswith('464_' + datetime.now().strftime("%Y-%m-%d")):
                filename = entry
        if os.path.exists(directory + filename):
            try:
                with open(directory + filename) as file:
                    data = csv.reader(file)
                    i = 'first'
                    for row in data:
                        if i == 'first':
                            i = 'not first'
                            continue
                        else:
                            temperature464 = float(row[1])
                            humidity464 = float(row[2])
            except:
                print('subdir 464_main\\ has been bypassed')
        #Temperature and Humidity for 464 Closet Room
        directory =  os.path.dirname(__file__) + '/../../../Data/temp_humid_data/464B/'
        D = os.listdir(directory)
        filename = 'initialization'
        for entry in D:
            if entry.startswith('464B_' + datetime.now().strftime("%Y-%m-%d")):
                filename = entry
        if os.path.exists(directory + filename):
            try:
                with open(directory + filename) as file:
                    data = csv.reader(file)
                    i = 'first'
                    for row in data:
                        if i == 'first':
                            i = 'not first'
                            continue
                        else:
                            temperature464B = float(row[1])
                            humidity464B = float(row[2])
            except:
                print('subdir 464B\\ has been bypassed')

        return temperature464, humidity464, temperature464B, humidity464B

    def setClock(self):
        hour = int(datetime.now().strftime("%H"))
        minute = int(datetime.now().strftime('%M'))
        noon = int(hour/12)
        hour = hour - noon*12
        if hour == 0:
            hour = 12
        if minute < 10:
            t = str(hour) + ':0' + str(minute)
        else:
            t = str(hour) + ':' + str(minute)
        if noon == 1:
            t = t + ' PM'
        else:
            t = t + ' AM'
        self.ui.time.setText(t)
        if noon == 1 and hour == 5 and minute >= 15 and minute < 25:
            if minute == 15:
                self.ui.gohome.setText('WOOO go home!')
            else:
                self.ui.gohome.setText('Why are you still here? Go home!')
        else:
            self.ui.gohome.setText('')

    def loadWorkers(self):
        workers = []
        tasks = []
        temp = []
        workerDir =  os.path.dirname(__file__) + '/../../../Data/workers/straw workers/'
        subDir = ['laser cutting/', 'leak testing/', 'straw prep/', 'CO2 endpiece insertion/', 'silver epoxy/', 'testing resistances/']
        for sub in subDir:
            try:
                if not os.path.exists(workerDir + sub + datetime.now().strftime('%Y-%m-%d') + '.csv'):
                    continue
                with open(workerDir + sub + datetime.now().strftime('%Y-%m-%d') + '.csv', 'a+') as file:
                    file.seek(0)
                    today = csv.reader(file)
                    for row in today:
                        temp = []
                        for worker in row:
                            if worker != '':
                                temp.append(worker)
                    for worker in temp:
                        workers.append(worker)
                        tasks.append(sub.rstrip('/'))
            except IOError:
                print('subdir ' + sub + ' has been bypassed')
        return workers, tasks

    def displayWorkers(self, workers, tasks):
        status = []
        i = 0
        for worker in workers:
            status.append(worker + ' is working on ' + tasks[i])
            i = i + 1
        self.ui.currentWorkers.setText('\n'.join(status))

    def cycle(self):
        newPos = pyautogui.position()
        if newPos != self.oldPos:  #stops tab switching for 30 seconds when mouse movement is detected
            self.begin = time.time() + 30
        self.oldPos = newPos
        if time.time() > self.begin:
            if int(time.time() - self.begin) % 60 >= 30:   #switches tabs every 30 seconds
                self.ui.tabWidget.setCurrentIndex(0)
            else:
                self.ui.tabWidget.setCurrentIndex(1)
        self.oldPos = newPos

    def editPallet(self, btn):
        pal = int(btn.objectName().strip('pal_')) - 1
        for palletid in os.listdir(self.palletDirectory):
            if int(palletid.strip('CPALID.csv')) == pal + 1:
                CPAL = 'CPAL0000.csv'
                for pallet in os.listdir(self.palletDirectory + palletid + '\\'):
                    if int(pallet.strip('CPAL.csv')) > int(CPAL.strip('CPAL.csv')):
                        CPAL = pallet[:-4]
        worker, okPressed = QInputDialog.getText(self, "Woker Identification","Scan worker ID:", QLineEdit.Normal, "")
        if not okPressed:
            return
        self.sessionWorkers = [worker]
        rem = removeStraw()
        rem.palletDirectory = self.palletDirectory
        rem.sessionWorkers = self.sessionWorkers
        try:
            CPAL, lastTask, straws, passfail = rem.getPallet(CPAL)
            rem.displayPallet(CPAL, lastTask, straws, passfail)
            rem.exec_()
        except:
            print('Pallet read error')
    def main(self):
        try:
            while True:
                currentLab, currentPallets, currentLocations = self.status()
                T, H, TB, HB = self.loadTH()
                self.displayStatus(currentLab, currentPallets, currentLocations, T, H, TB, HB)
                self.setClock()
                workers, tasks = self.loadWorkers()
                self.displayWorkers(workers, tasks)
                self.cycle()
                time.sleep(.01)
                app.processEvents()
                if datetime.now().strftime('%H-%M') == '23-55':
                    time.sleep(1200)
        except:
            print('ruh roh Raggy')
            ctr = Status()
            ctr.show()
            ctr.main()

if __name__=="__main__":
     app = QApplication(sys.argv)
     ctr = Status()
     ctr.show()
     ctr.main()
     app.exec_()
    
        
        
    

