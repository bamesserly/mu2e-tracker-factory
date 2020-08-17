import time
import os
import csv
import sys
import datetime
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from removeGUI import *

class removeStraw(QMainWindow):
    def __init__(self, webapp=None, parent=None):
        super(removeStraw,self).__init__(parent) 
        self.ui = Ui_Dialogw()
        self.ui.setupUi(self)
        self.palletDirectory = os.path.dirname(__file__) + '/../../../Data/Pallets/'
        self.sessionWorkers = []
        self.palletID = ''
        self.palletNum = ''
        
        self.strawLabels = [self.ui.straw_1,self.ui.straw_2,self.ui.straw_3,self.ui.straw_4,
                            self.ui.straw_5,self.ui.straw_6,self.ui.straw_7,self.ui.straw_8,
                            self.ui.straw_9,self.ui.straw_10,self.ui.straw_11,self.ui.straw_12,
                            self.ui.straw_13,self.ui.straw_14,self.ui.straw_15,self.ui.straw_16,
                            self.ui.straw_17,self.ui.straw_18,self.ui.straw_19,self.ui.straw_20,
                            self.ui.straw_21,self.ui.straw_22,self.ui.straw_23,self.ui.straw_24]
        self.pfLabels = [self.ui.pf_1,self.ui.pf_2,self.ui.pf_3,self.ui.pf_4,
                         self.ui.pf_5,self.ui.pf_6,self.ui.pf_7,self.ui.pf_8,
                         self.ui.pf_9,self.ui.pf_10,self.ui.pf_11,self.ui.pf_12,
                         self.ui.pf_13,self.ui.pf_14,self.ui.pf_15,self.ui.pf_16,
                         self.ui.pf_17,self.ui.pf_18,self.ui.pf_19,self.ui.pf_20,
                         self.ui.pf_21,self.ui.pf_22,self.ui.pf_23,self.ui.pf_24]

        self.ui.removeButtons.buttonClicked.connect(self.delete)
        self.ui.moveButtons.buttonClicked.connect(self.moveStraw)
        self.ui.addButtons.buttonClicked.connect(self.addStraw)
        self.ui.resetButton.clicked.connect(self.reset)
        self.ui.palletID.returnPressed.connect(self.setCPALID)
        self.ui.palletNum.returnPressed.connect(self.setCPAL)

        for btn in self.ui.removeButtons.buttons():
            btn.setDisabled(True)

        for btn in self.ui.moveButtons.buttons():
            btn.setDisabled(True)

        for btn in self.ui.addButtons.buttons():
            btn.setDisabled(True)

        self.ui.palletNum.setDisabled(True)
        
    def getPallet(self, CPAL, path = ''):
        lastTask = ''
        straws = []
        passfail = []

        if path == '':
            for palletid in os.listdir(self.palletDirectory):
                for pallet in os.listdir(self.palletDirectory + palletid + '/'):
                    if CPAL + '.csv' == pallet:
                        with open(self.palletDirectory + palletid + '/' + pallet, 'r') as file:
                            dummy = csv.reader(file)
                            history = []
                            for line in dummy:
                                if line != []:
                                    history.append(line)
                            lastTask = history[len(history) - 1][1]
                            for entry in range(len(history[len(history ) - 1])):
                                if entry > 1 and entry < 50:
                                    if entry%2 == 0:
                                        if history[len(history) - 1][entry] == '_______':
                                            straws.append('Empty')
                                        else:
                                            straws.append(history[len(history) - 1][entry])
                                    else:
                                        if history[len(history) - 1][entry] == 'P':
                                            passfail.append('Pass')
                                        elif history[len(history) - 1][entry] == '_':
                                            passfail.append('Incomplete')
                                        else:
                                            passfail.append('Fail')
                        break
        else:
            with open(path, 'r') as file:
                dummy = csv.reader(file)
                history = []
                for line in dummy:
                    if line != []:
                        history.append(line)
                lastTask = history[len(history) - 1][1]
                for entry in range(len(history[len(history ) - 1])):
                    if entry > 1 and entry < 50:
                        if entry%2 == 0:
                            if history[len(history) - 1][entry] == '_______':
                                straws.append('Empty')
                            else:
                                straws.append(history[len(history) - 1][entry])
                        else:
                            if history[len(history) - 1][entry] == 'P':
                                passfail.append('Pass')
                            elif history[len(history) - 1][entry] == '_':
                                passfail.append('Incomplete')
                            else:
                                passfail.append('Fail')
        
        return CPAL, lastTask, straws, passfail
    
    def displayPallet(self, CPAL, lastTask, straws, passfail):
        steps1 = ['made','prep','ohms','C-O2','infl','leak','lasr','leng','silv']
        steps2 = ['Straw Made','Straw Prep','Resistance','CO2 End Pieces','Inflation','Leak Rate','Laser Cut','Length','Silver Epoxy']
        for pos in range(len(self.strawLabels)):
            self.strawLabels[pos].setText(straws[pos])
                
        for pos in range(len(self.pfLabels)):
            self.pfLabels[pos].setText(passfail[pos])

        for btn in self.ui.addButtons.buttons():
            btn.setDisabled(False)

        for pos, b in enumerate(self.ui.removeButtons.buttons()):
            if straws[pos] != 'Empty':
                b.setDisabled(False)

        for pos, b in enumerate(self.ui.moveButtons.buttons()):
            if straws[pos] != 'Empty':
                b.setDisabled(False)

    def delete(self, btn):
        pos = int(btn.objectName().strip('remove_')) - 1
        CPAL, lastTask, straws, passfail = self.getPallet(self.ui.palletLabel.text()[8:])
        if straws[pos] == 'Empty':
            return
        buttonReply = QMessageBox.question(self, 'Straw Removal Confirmation', "Are you sure you want to permanently remove " + straws[pos] + " from " + CPAL + " ?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply != QMessageBox.Yes:
            return
        for palletid in os.listdir(self.palletDirectory):
            for pallet in os.listdir(self.palletDirectory + palletid + '/'):
                if CPAL + '.csv' == pallet:
                    with open(self.palletDirectory + palletid + '/' + pallet, 'a') as file:
                        file.write('\n')
                        file.write(datetime.now().strftime('%Y-%m-%d_%H:%M') + ',')
                        file.write(lastTask + ',')
                        for place in range(len(straws)):
                            if place == pos:
                                file.write('_______,_,')
                                continue
                            if straws[place] == 'Empty':
                                file.write('_______,_,')
                                continue
                            file.write(straws[place] + ',')
                            if passfail[place] == 'Pass':
                                file.write('P,')
                            elif passfail[place] == 'Incomplete':
                                file.write('_,')
                            else :
                                file.write('F,')
                        ','.join(self.sessionWorkers)
                    break
                        
        CPAL, lastTask, straws, passfail = self.getPallet(CPAL)
        self.displayPallet(CPAL, lastTask, straws, passfail)

    def moveStraw(self, btn):
        pos = int(btn.objectName().strip('move_')) - 1
        CPAL, lastTask, straws, passfail = self.getPallet(self.ui.palletLabel.text()[8:])
        if straws[pos] == 'Empty':
            return
        items = ("This Pallet","Another Pallet")
        item, okPressed = QInputDialog.getItem(self, "Move Straw","Where would you like to move this straw to?", items, 0, False)
        if not okPressed:
            return
        if item == 'This Pallet':
            newpos, okPressed = QInputDialog.getInt(self, "Move Straw","New Straw Position:", pos, 0, 23, 1)
            if not okPressed:
                return
            if straws[newpos] != 'Empty':
                buttonReply = QMessageBox.critical(self, 'Move Error', "Position " + str(newpos) + " is already \
                filled by straw " + straws[newpos] + " .", QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
                return
            buttonReply = QMessageBox.question(self, 'Straw Move Confirmation', "Are you sure you want to move " + straws[pos] + " from position " + str(pos) + " to position " + str(newpos) + " ?", QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
            if buttonReply != QMessageBox.Ok:
                return
            
            found, valid, path = self.validCPAL(CPAL)
            
            with open(path, 'a') as file:
                file.write('\n')
                file.write(datetime.now().strftime('%Y-%m-%d_%H:%M') + ',')
                file.write(lastTask + ',')
                for place in range(len(straws)):
                    if place == pos:
                        file.write('_______,_,')
                        continue
                    if place == newpos:
                        file.write(straws[pos] + ',')
                        if passfail[pos] == 'Pass':
                            file.write('P,')
                        elif passfail[pos] == 'Incomplete':
                            file.write('_,')
                        else :
                            file.write('F,')
                        continue
                    if straws[place] == 'Empty':
                        file.write('_______,_,')
                        continue
                    file.write(straws[place] + ',')
                    if passfail[place] == 'Pass':
                        file.write('P,')
                    elif passfail[place] == 'Incomplete':
                        file.write('_,')
                    else :
                        file.write('F,')
                file.write(','.join(self.sessionWorkers))
                        
        if item == 'Another Pallet':
            found, valid, path = self.validCPAL(CPAL)
            newpal, okPressed = QInputDialog.getText(self, "Move Straw","Scan the pallet number of the pallet the straw will be moved to:", QLineEdit.Normal, "")

            valid = self.validateCPALNumber(newpal)
            again = True

            while not valid and again:
                newpal, again = QInputDialog.getText(self, "Add Straw","INVALID CPAL NUMBER\nCPAL numbers have the form CPAL####.\n\nScan the pallet number of the pallet the straw will be moved to:", QLineEdit().Normal, "")
                valid = self.validateStrawNumber(newstraw)

            if not valid and not again:
                return

            found, valid, newpath = self.validCPAL(newpal)
            again = True

            while not found and again:
                newpal, again = QInputDialog.getText(self, "Add Straw","INVALID CPAL NUMBER\nUnable to locate the pallet file for the CPAL specified.\n\nScan the pallet number of the pallet the straw will be moved to:", QLineEdit().Normal, "")
                found, valid, path = self.validCPAL(newpal)

            if not found and not again:
                return
            
            if not okPressed:
                return
            
            newpal, newlastTask, newstraws, newpassfail = self.getPallet(newpal, newpath)
            
            if newlastTask != lastTask:
                buttonReply = QMessageBox.critical(self, 'Move Error', "Pallet " + CPAL + " and pallet " + newpal + " are at different stages of production.", QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
                return
            
            newpos, okPressed = QInputDialog.getInt(self, "Move Straw","New Straw Position on " + newpal + ":", pos, 0, 23, 1)
            
            if not okPressed:
                return
            
            if newstraws[newpos] != 'Empty':
                buttonReply = QMessageBox.critical(self, 'Move Error', "Position " + str(newpos) + " is already filled by straw " + newstraws[newpos] + " .", QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
                return
            
            with open(newpath, 'a') as file:
                file.write('\n')
                file.write(datetime.now().strftime('%Y-%m-%d_%H:%M') + ',')
                file.write('adds,')
                for place in range(len(newstraws)):
                    if place == newpos:
                        file.write(straws[pos] + ',' + CPAL + ',')
                    else:
                        file.write('_______,_,')
                ','.join(self.sessionWorkers)
                
                file.write('\n')
                file.write(datetime.now().strftime('%Y-%m-%d_%H:%M') + ',')
                file.write(newlastTask + ',')
                for place in range(len(newstraws)):
                    if place == newpos:
                        file.write(straws[pos] + ',')
                        if passfail[pos] == 'Pass':
                            file.write('P,')
                        elif passfail[pos] == 'Incomplete':
                            file.write('_,')
                        else :
                            file.write('F,')
                        continue
                    if newstraws[place] == 'Empty':
                        file.write('_______,_,')
                        continue
                    file.write(newstraws[place] + ',')
                    if newpassfail[place] == 'Pass':
                        file.write('P,')
                    elif newpassfail[place] == 'Incomplete':
                        file.write('_,')
                    else :
                        file.write('F,')
                file.write(','.join(self.sessionWorkers))
                
                with open(path, 'a') as file:
                    file.write('\n')
                    file.write(datetime.now().strftime('%Y-%m-%d_%H:%M') + ',')
                    file.write(lastTask + ',')
                    for place in range(len(straws)):
                        if place == pos:
                            file.write('_______,_,')
                            continue
                        if straws[place] == 'Empty':
                            file.write('_______,_,')
                            continue
                        file.write(straws[place] + ',')
                        if passfail[place] == 'Pass':
                            file.write('P,')
                        elif passfail[place] == 'Incomplete':
                            file.write('_,')
                        else :
                            file.write('F,')
                    file.write(','.join(self.sessionWorkers))
            
        CPAL, lastTask, straws, passfail = self.getPallet(CPAL, path)
        self.displayPallet(CPAL, lastTask, straws, passfail)

    def addStraw(self, btn):
        add = False
        pos = int(btn.objectName().strip('add_')) - 1
        CPAL = self.ui.palletLabel.text()[8:]
        found, valid, path = self.validCPAL(CPAL)
        CPAL, lastTask, straws, passfail = self.getPallet(CPAL, path)
        passFailDict = dict(zip(straws, passfail))

        if straws[pos] == "Empty":
            add = True

        items = ("Parent Straw", "Another Pallet")
        item, okPressed = QInputDialog.getItem(self, "Add Straw","Where are you adding the straw from?", items, 0, False)

        if okPressed:
            newstraw, okPressed = QInputDialog.getText(self, "Add Straw","Scan the straw number of the new straw:", QLineEdit().Normal, "")

            if okPressed:
                valid = self.validateStrawNumber(newstraw)
                again = True

                while not valid and again:
                    newstraw, again = QInputDialog.getText(self, "Add Straw","INVALID STRAW NUMBER\nStraw numbers have the form ST#####.\n\nScan the straw number of the new straw:", QLineEdit().Normal, "")
                    valid = self.validateStrawNumber(newstraw)

                if not valid and not again:
                    return
                
                if item == items[0]:
                    parent, okPressed = QInputDialog.getText(self, "Add Straw","Scan the straw number of the parent straw:", QLineEdit.Normal, "")
                    
                    if okPressed:
                        valid = self.validateStrawNumber(parent)
                        again = True

                        while not valid and again:
                            parent, again = QInputDialog.getText(self, "Add Straw","INVALID STRAW NUMBER\nStraw numbers have the form ST#####.\n\nScan the straw number of the parent straw:", QLineEdit().Normal, "")
                            valid = self.validateStrawNumber(parent)

                        if not valid and not again:
                            return

                        valid = parent in straws
                        again =  True

                        while not valid and again:
                            parent, again = QInputDialog.getText(self, "Add Straw",f"INVALID STRAW NUMBER\nStraw {parent} was not found on {CPAL}.\n\nScan the straw number of the parent straw:", QLineEdit().Normal, "")
                            valid = parent in straws

                        if not valid and not again:
                            return
                        
                        if not add:
                            reply = QMessageBox.warning(self, "Replacing Straw", f"There is already a straw in position {pos + 1}.\n\nDo you wish to replace {straws[pos]} with {newstraw}?", QMessageBox.Yes, QMessageBox.No)

                            if reply == QMessageBox.Yes:
                                with open(path, 'a') as file:
                                    file.write('\n')
                                    file.write(datetime.now().strftime('%Y-%m-%d_%H:%M') + ',')
                                    file.write(lastTask + ',')
                                    for place in range(len(straws)):
                                        if place == pos:
                                            file.write('_______,_,')
                                            continue
                                        if straws[place] == 'Empty':
                                            file.write('_______,_,')
                                            continue
                                        file.write(straws[place] + ',')
                                        if passfail[place] == 'Pass':
                                            file.write('P,')
                                        elif passfail[place] == 'Incomplete':
                                            file.write('_,')
                                        else :
                                            file.write('F,')
                                    file.write(','.join(self.sessionWorkers))

                                    file.write('\n')
                                    file.write(datetime.now().strftime('%Y-%m-%d_%H:%M') + ',')
                                    for place in range(len(newstraws)):
                                        if place == pos:
                                            file.write(f'adds,{newstraw},{parent},')
                                        else:
                                            file.write('_______,_,')
                                    file.write(','.join(self.sessionWorkers))

                                    file.write('\n')
                                    file.write(datetime.now().strftime('%Y-%m-%d_%H:%M') + ',')
                                    file.write(lastTask + ',')
                                    for place in range(len(straws)):
                                        if place == pos:
                                            file.write(f'{newstraw},')
                                            if passFailDict[parent] == 'Incomplete':
                                                file.write('_,')
                                            else:
                                                file.write(f'{passFailDict[parent][0]},')
                                            continue
                                        if straws[place] == 'Empty':
                                            file.write('_______,_,')
                                            continue
                                        file.write(straws[place] + ',')
                                        if passfail[place] == 'Pass':
                                            file.write('P,')
                                        elif passfail[place] == 'Incomplete':
                                            file.write('_,')
                                        else :
                                            file.write('F,')
                                    file.write(','.join(self.sessionWorkers))
                        else:
                            with open(path, 'a') as file:
                                file.write('\n')
                                file.write(datetime.now().strftime('%Y-%m-%d_%H:%M') + ',')
                                for place in range(len(straws)):
                                    if place == pos:
                                        file.write(f'adds,{newstraw},{parent},')
                                    else:
                                        file.write('_______,_,')
                                file.write(','.join(self.sessionWorkers))

                                file.write('\n')
                                file.write(datetime.now().strftime('%Y-%m-%d_%H:%M') + ',')
                                file.write(lastTask + ',')
                                for place in range(len(straws)):
                                    if place == pos:
                                        file.write(f'{newstraw},')
                                        if passFailDict[parent] == 'Incomplete':
                                            file.write('_,')
                                        else:
                                            file.write(f'{passFailDict[parent][0]},')
                                        continue
                                    if straws[place] == 'Empty':
                                        file.write('_______,_,')
                                        continue
                                    file.write(straws[place] + ',')
                                    if passfail[place] == 'Pass':
                                        file.write('P,')
                                    elif passfail[place] == 'Incomplete':
                                        file.write('_,')
                                    else :
                                        file.write('F,')
                                file.write(','.join(self.sessionWorkers))
                            
                else:
                    newpal, okPressed = QInputDialog.getText(self, "Add Straw","Scan the pallet number of the pallet the straw came from:", QLineEdit.Normal, "")

                    valid = self.validateCPALNumber(newpal)
                    again = True

                    while not valid and again:
                        newpal, again = QInputDialog.getText(self, "Add Straw","INVALID CPAL NUMBER\nCPAL numbers have the form CPAL####.\n\nScan the pallet number of the pallet the straw came from:", QLineEdit().Normal, "")
                        valid = self.validateStrawNumber(newstraw)

                    if not valid and not again:
                        return

                    found, valid, newpath = self.validCPAL(newpal)
                    again = True

                    while not found and again:
                        newpal, again = QInputDialog.getText(self, "Add Straw","INVALID CPAL NUMBER\nUnable to locate the pallet file for the CPAL specified.\n\nScan the pallet number of the pallet the straw will be moved to:", QLineEdit().Normal, "")
                        found, valid, path = self.validCPAL(newpal)

                    if not found and not again:
                        return

                    found, valid, newpath = self.validCPAL(newpal, newstraw)
                    again = True

                    while not valid and again:
                        newpal, again = QInputDialog.getText(self, "Add Straw",f"INVALID CPAL NUMBER\nStraw {newstraw} not found in pallet file for {newpal}.\n\nScan the pallet number of the pallet the straw will be moved to:", QLineEdit().Normal, "")
                        found, valid, path = self.validCPAL(newpal)

                    if not valid and not again:
                        return

                    if okPressed:
                        newpal, newlastTask, newstraws, newpassfail = self.getPallet(newpal, newpath)
                        newPassFailDict = dict(zip(newstraws, newpassfail))

                        if newlastTask != lastTask:
                            buttonReply = QMessageBox.critical(self, 'Move Error', f"Pallet {CPAL} and pallet {newpal} are at different stages of production.", QMessageBox.Ok)
                        else:
                            if not add:
                                reply = QMessageBox.warning(self, "Replacing Straw", f"There is already a straw in position {pos + 1}.\n\nDo you wish to replace {straws[pos]} with {newstraw}?", QMessageBox.Yes, QMessageBox.No)

                                with open(path, 'a') as file:
                                    file.write('\n')
                                    file.write(datetime.now().strftime('%Y-%m-%d_%H:%M') + ',')
                                    file.write(lastTask + ',')
                                    for place in range(len(straws)):
                                        if place == pos:
                                            file.write('_______,_,')
                                            continue
                                        if straws[place] == 'Empty':
                                            file.write('_______,_,')
                                            continue
                                        file.write(straws[place] + ',')
                                        if passfail[place] == 'Pass':
                                            file.write('P,')
                                        elif passfail[place] == 'Incomplete':
                                            file.write('_,')
                                        else :
                                            file.write('F,')
                                    file.write(','.join(self.sessionWorkers))

                                    file.write('\n')
                                    file.write(datetime.now().strftime('%Y-%m-%d_%H:%M') + ',')
                                    for place in range(len(newstraws)):
                                        if place == pos:
                                            file.write(f'adds,{newstraw},{newpal},')
                                        else:
                                            file.write('_______,_,')
                                    file.write(','.join(self.sessionWorkers))

                                    file.write('\n')
                                    file.write(datetime.now().strftime('%Y-%m-%d_%H:%M') + ',')
                                    file.write(lastTask + ',')
                                    for place in range(len(straws)):
                                        if place == pos:
                                            file.write(f'{newstraw},')
                                            if newPassFailDict[newstraw] == 'Incomplete':
                                                file.write('_,')
                                            else:
                                                file.write(f'{newPassFailDict[newstraw][0]},')
                                            continue
                                        if straws[place] == 'Empty':
                                            file.write('_______,_,')
                                            continue
                                        file.write(straws[place] + ',')
                                        if passfail[place] == 'Pass':
                                            file.write('P,')
                                        elif passfail[place] == 'Incomplete':
                                            file.write('_,')
                                        else :
                                            file.write('F,')
                                    file.write(','.join(self.sessionWorkers))

                                with open(newpath, 'a') as file:
                                    file.write('\n')
                                    file.write(datetime.now().strftime('%Y-%m-%d_%H:%M') + ',')
                                    file.write(newlastTask + ',')
                                    for place in range(len(newstraws)):
                                        if place == pos:
                                            file.write('_______,_,')
                                            continue
                                        if newstraws[place] == 'Empty':
                                            file.write('_______,_,')
                                            continue
                                        file.write(newstraws[place] + ',')
                                        if newpassfail[place] == 'Pass':
                                            file.write('P,')
                                        elif newpassfail[place] == 'Incomplete':
                                            file.write('_,')
                                        else :
                                            file.write('F,')
                                    file.write(','.join(self.sessionWorkers))
                                    
                            else:
                                with open(path, 'a') as file:
                                    file.write('\n')
                                    file.write(datetime.now().strftime('%Y-%m-%d_%H:%M') + ',')
                                    for place in range(len(newstraws)):
                                        if place == pos:
                                            file.write(f'adds,{newstraw},{newpal},')
                                        else:
                                            file.write('_______,_,')
                                    file.write(','.join(self.sessionWorkers))

                                    file.write('\n')
                                    file.write(datetime.now().strftime('%Y-%m-%d_%H:%M') + ',')
                                    file.write(lastTask + ',')
                                    for place in range(len(straws)):
                                        if place == pos:
                                            file.write(f'{newstraw},')
                                            if newPassFailDict[newstraw] == 'Incomplete':
                                                file.write('_,')
                                            else:
                                                file.write(f'{newPassFailDict[newstraw][0]},')
                                            continue
                                        if straws[place] == 'Empty':
                                            file.write('_______,_,')
                                            continue
                                        file.write(straws[place] + ',')
                                        if passfail[place] == 'Pass':
                                            file.write('P,')
                                        elif passfail[place] == 'Incomplete':
                                            file.write('_,')
                                        else :
                                            file.write('F,')
                                    file.write(','.join(self.sessionWorkers))

                            with open(newpath, 'a') as file:
                                file.write('\n')
                                file.write(datetime.now().strftime('%Y-%m-%d_%H:%M') + ',')
                                file.write(newlastTask + ',')
                                for place in range(len(newstraws)):
                                    if place == pos:
                                        file.write('_______,_,')
                                        continue
                                    if newstraws[place] == 'Empty':
                                        file.write('_______,_,')
                                        continue
                                    file.write(newstraws[place] + ',')
                                    if newpassfail[place] == 'Pass':
                                        file.write('P,')
                                    elif newpassfail[place] == 'Incomplete':
                                        file.write('_,')
                                    else :
                                        file.write('F,')
                                file.write(','.join(self.sessionWorkers))
                                                    
            CPAL, lastTask, straws, passfail = self.getPallet(CPAL)

            if straws[pos] != 'Empty':
                self.ui.moveButtons.buttons()[pos].setDisabled(False)
                self.ui.removeButtons.buttons()[pos].setDisabled(False)
                
            self.displayPallet(CPAL, lastTask, straws, passfail)

    def validateStrawNumber(self, straw):
        firstLetter = ['s', 'S']
        secondLetter = ['t', 'T']
        valid = True
        
        if len(straw) != 7:
            valid = False

        if valid and ((straw[0] not in firstLetter) and (straw[1] not in secondLetter)):
            valid = False

        if valid and not straw[2:].isdigit():
           valid = False

        return valid

    def validateCPALNumber(self, CPAL):
        start = 'CPAL'
        valid = True
        
        if len(CPAL) != 8:
            valid = False

        if valid and CPAL[:4].upper() != start:
            valid = False

        if valid and not CPAL[4:].isdigit():
           valid = False

        return valid
    
    def validCPAL(self, CPAL, straw = "ST"):
        found = False
        valid = False
        path = ''
        
        for palletid in os.listdir(self.palletDirectory):
            for pallet in os.listdir(self.palletDirectory + palletid + '/'):
                if CPAL + '.csv' == pallet:
                    found = True
                    
                    with open(self.palletDirectory + palletid + '/' + pallet, 'r') as file:
                        path = self.palletDirectory + palletid + '/' + pallet
                        old_line = ''
                        line = file.readline()

                        while line != '\n' and line != '':
                            old_line = line
                            line = file.readline()

                        if straw in old_line:
                            valid = True
                    break
                            
        return found, valid, path

    def setCPALID(self):
        valid = True
        self.palletID = self.ui.palletID.text().upper()

        if len(self.palletID) != 8:
            valid = False

        if valid and not self.palletID[:6] == 'CPALID':
            valid = False

        if valid and not (int(self.palletID[6:]) > 0 and int(self.palletID[6:]) < 25):
            valid = False

        if not valid:
            QMessageBox.critical(self, 'Invalid CPALID', 'CPALIDs have the form CPALID##')
            self.palletID = ''
            self.ui.palletID.setText('')
        else:
            self.ui.palletID.setText(self.palletID)
            self.ui.palletID.setDisabled(True)
            self.ui.palletNum.setDisabled(False)
            self.ui.palletNum.setFocus()

    def setCPAL(self):
        valid = True
        found = True
        self.palletNum = self.ui.palletNum.text().upper()
        path = os.path.join(self.palletDirectory, self.palletID, self.palletNum + '.csv')

        if len(self.palletNum) != 8:
            valid = False

        if valid and not self.palletID[:4] == 'CPAL':
            valid = False

        if valid and not self.palletNum[4:].isdigit():
            valid = False

        if valid and not os.path.exists(path):
            found = False

        if not valid:
            QMessageBox.critical(self, 'Invalid CPAL', 'CPALs have the form CPAL####')
            self.palletNum = ''
            self.ui.palletNum.setText('')
        elif not found:
            QMessageBox.critical(self, 'Invalid CPAL', f'{self.palletID} is not associated with {self.palletNum}')
            self.palletNum = ''
            self.ui.palletNum.setText('')
        else:
            self.ui.palletNum.setText(self.palletNum)
            try:
                CPAL, lastTask, straws, passfail = self.getPallet(self.palletNum, path)
                self.displayPallet(CPAL, lastTask, straws, passfail)
                self.ui.palletNum.setDisabled(True)
            except Exception:
                QMessageBox.critical(self, 'Pallet File Error', 'Error reading pallet file. Make sure pallet file is in correct format (no blank lines).')

    def reset(self):
        for pos in range(len(self.strawLabels)):
            self.strawLabels[pos].setText('Straw')
                
        for pos in range(len(self.pfLabels)):
            self.pfLabels[pos].setText('Pass/Fail')

        for btn in self.ui.removeButtons.buttons():
            btn.setDisabled(True)

        for btn in self.ui.moveButtons.buttons():
            btn.setDisabled(True)

        for btn in self.ui.addButtons.buttons():
            btn.setDisabled(True)

        self.ui.palletID.setDisabled(False)
        self.ui.palletNum.setDisabled(True)
        self.ui.palletID.setText('')
        self.ui.palletNum.setText('')
        self.palletID = ''
        self.palletNum = ''
        self.ui.palletID.setFocus()

def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)
    sys.exit()

if __name__ == '__main__':
    sys.excepthook = except_hook
    app = QApplication(sys.argv) 
    ctr = removeStraw()
    ctr.show()
    app.exec_()
