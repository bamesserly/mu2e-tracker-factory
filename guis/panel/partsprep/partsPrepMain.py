import sys, datetime, tkinter
from time import time
from os.path import exists

from guis.common.getresources import GetProjectPaths # import paths for saving CSVs
from guis.panel.partsprep.partsPrepUI import Ui_MainWindow  # import raw UI

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QStyleFactory,
    QCheckBox,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QInputDialog,
    QMessageBox,
)

from PyQt5.QtGui import QPixmap, QRegularExpressionValidator


from PyQt5.QtCore import Qt, QRegularExpression


class partsPrepGUI(QMainWindow):

    def __init__(self, ui_layout):
        # initialize superclass
        QMainWindow.__init__(self)
        # make ui member
        self.ui = ui_layout
        # apply ui to window
        ui_layout.setupUi(self)

        self.saveDir = GetProjectPaths()["partsprepdata"]

        self.workers = {}

        self.initStartStopButtons()
        self.initCheckboxes()
        self.initMenuButtons()
        self.initImageButtons()
        self.initValidators()
        self.initOthers()

 
    # get a list of all checkboxes that are a child, 
    # grandchild, great-grandchild, etc. of a widget
    def getCheckboxes(self,parent):
        retList = []
        for wid in parent.children():
            # base case
            if isinstance(wid, QCheckBox):
                retList += [wid]
            elif (
                isinstance(wid, QGridLayout) or
                isinstance(wid, QVBoxLayout) or
                isinstance(wid, QHBoxLayout)
                ):
                #            YEAH RECURSION >:D
                retList += self.getCheckboxes(wid)
        return retList

    # connect menu buttons up top to correct functions
    def initMenuButtons(self):

        self.ui.actionAddWorker.triggered.connect(
            self.addWorker
        )
        
        self.ui.actionbir2_3.triggered.connect(
            lambda : self.diagramPopup("bir2_3")
        )
        self.ui.actionbir6_4.triggered.connect(
            lambda : self.diagramPopup("bir6_4")
        )

        self.ui.actionbp1_2.triggered.connect(
            lambda : self.diagramPopup("bp1_2")
        )
        self.ui.actionbp4_2.triggered.connect(
            lambda : self.diagramPopup("bp4_2")
        )
        self.ui.actionbp7_2.triggered.connect(
            lambda : self.diagramPopup("bp7_2")
        )
        
        return

    # connect image push buttons to funciton
    def initImageButtons(self):
        self.ui.birImage2_3PB.clicked.connect(
            lambda: self.diagramPopup("bir2_3")
        )
        self.ui.birImage6_4PB.clicked.connect(
            lambda: self.diagramPopup("bir6_4")
        )
        self.ui.bpImage1_2.clicked.connect(
            lambda: self.diagramPopup("bp1_2")
        )
        self.ui.bpImage4_2.clicked.connect(
            lambda: self.diagramPopup("bp4_2")
        )
        self.ui.bpImage7_2.clicked.connect(
            lambda: self.diagramPopup("bp7_2")
        )
        self.ui.frImage1_3.clicked.connect(
            lambda: self.diagramPopup("fr1_3")
        )
        self.ui.frImage4_2.clicked.connect(
            lambda: self.diagramPopup("fr4_2")
        )
        self.ui.frImage4_3.clicked.connect(
            lambda: self.diagramPopup("fr4_3")
        )
        self.ui.mrImage3_10.clicked.connect(
            lambda: self.diagramPopup("mr3_10")
        )
        self.ui.mirImage5_4.clicked.connect(
            lambda: self.diagramPopup("mir5_4")
        )
        self.ui.mrImage5_4.clicked.connect(
            lambda: self.diagramPopup("mr5_4")
        )



    # connect checkbox state chenged to below funciton
    def initCheckboxes(self):
        
        # connect BIR checkboxes
        for box in self.getCheckboxes(self.ui.bir):
            stepText = box.text()
            box.stateChanged.connect(
                lambda state, stepText=stepText: self.checkboxReaction("bir",stepText)
            )

        # connect BP checkboxes
        for box in self.getCheckboxes(self.ui.bp):
            stepText = box.text()
            box.stateChanged.connect(
                lambda state, stepText=stepText: self.checkboxReaction("bp",stepText)
            )

        for box in self.getCheckboxes(self.ui.fr):
            stepText = box.text()
            box.stateChanged.connect(
                lambda state, stepText=stepText: self.checkboxReaction("fr",stepText)
            )

        for box in self.getCheckboxes(self.ui.mir):
            stepText = box.text()
            box.stateChanged.connect(
                lambda state, stepText=stepText: self.checkboxReaction("mir",stepText)
            )

        for box in self.getCheckboxes(self.ui.mr):
            stepText = box.text()
            box.stateChanged.connect(
                lambda state, stepText=stepText: self.checkboxReaction("mr",stepText)
            )

        # connect <OTHER PART TYPE> checkboxes
        #for box in self.getCheckboxes(self.ui.<OTHERPART>):
        #    stepText = box.text()
        #    box.stateChanged.connect(
        #        lambda state, stepText=stepText: self.checkboxReaction("<OTHERPART>",stepText)
        #    )

        return


    # connect start/stop buttons to appropriate funcitons
    def initStartStopButtons(self):
        # bir start button
        self.ui.birStartPB.clicked.connect(
            lambda: self.startStopButton("bir",True)
            )
        # bir stop button
        self.ui.birStopPB.clicked.connect(
            lambda: self.startStopButton("bir",False)
            )
        # bp start button
        self.ui.bpStartPB.clicked.connect(
            lambda: self.startStopButton("bp",True)
        )
        # bp stop button
        self.ui.bpStopPB.clicked.connect(
            lambda: self.startStopButton("bp",False)
        )

        # fr start button
        self.ui.frStartPB.clicked.connect(
            lambda: self.startStopButton("fr",True)
        )
        # fr stop button
        self.ui.frStopPB.clicked.connect(
            lambda: self.startStopButton("fr",False)
        )

        # mir start button
        self.ui.mirStartPB.clicked.connect(
            lambda: self.startStopButton("mir",True)
        )
        # mir stop button
        self.ui.mirStopPB.clicked.connect(
            lambda: self.startStopButton("mir",False)
        )

        # mr start button
        self.ui.mrStartPB.clicked.connect(
            lambda: self.startStopButton("mr",True)
        )
        # mr stop button
        self.ui.mrStopPB.clicked.connect(
            lambda: self.startStopButton("mr",False)
        )

        return

    def initValidators(self):
        validator = lambda string: QRegularExpressionValidator(
            QRegularExpression(string)
        )
        # bir validator
        self.ui.birLE.setValidator(validator('(BIR)\d{3}'))
        # bp validator
        self.ui.bpLE.setValidator(validator('(BP)\d{3}'))
        # f validator
        self.ui.frLE.setValidator(validator('(F)\d{3}'))
        # mir validator
        self.ui.mirLE.setValidator(validator('(MIR)\d{3}'))
        # mr validator
        self.ui.mrLE.setValidator(validator('(MR)\d{3}'))


    # connect other things to approprite funcitons
    def initOthers(self):
        self.ui.birComEntryPB.clicked.connect(
            lambda: self.submitComment("bir")
        )
        self.ui.bpComEntryPB.clicked.connect(
            lambda: self.submitComment("bp")
        )
        self.ui.frComEntryPB.clicked.connect(
            lambda: self.submitComment("fr")
        )
        self.ui.mirComEntryPB.clicked.connect(
            lambda: self.submitComment("mir")
        )
        self.ui.mrComEntryPB.clicked.connect(
            lambda: self.submitComment("mr")
        )

    # for each box make it:
    # - launch a picture if the next step (TODO)
    #   has a picture and auto open is on
    # - make it read only once checked (TODO)
    # - trigger a save 
    def checkboxReaction(self, partType, step):
        # save
        self.writeToCSV(partType, step)

        # launch next pic if desired
        if self.ui.actionAutomatically_Open.isChecked():
            # some string/list sorcery to get the format "<part type><step>_<substep>""
            # I bring dishonor upon myself for the following code, but it works.
            # get part type+step and substep
            stepMod = partType + step[0:3]
            # replace the "." between step and substep with "_"
            stepMod = stepMod.replace(".","_")
            # convert to list
            stepMod = list(stepMod)
            # increment substep
            inc = int(stepMod[-1:][0])
            stepMod[-1:][0] = str((inc+1))
            # back to string
            stepMod = "".join(stepMod)
            # check if there's a picture to display
            if exists(f'guis/panel/partsprep/partsPrepImages/{str(stepMod)}.png'):
                # launch it
                self.diagramPopup(stepMod)

        return

    # adds a new worker
    def addWorker(self):
        # get worker name and bool for when done
        name, done = QInputDialog.getText(
            self,
            "New Worker",
            "Enter the ID of the new worker."
        )

        if done:
            # make a new QAction under workers menu
            newAction = self.ui.menuWorkers.addAction(f'Remove {name}')
            # connect it to appropriate function
            newAction.triggered.connect(
                lambda: self.removeWorker(name)
            )
            # add to dictionary
            self.workers[name] = newAction
        return

    # removes a worker
    def removeWorker(self, name):
        # remove action from menu
        self.ui.menuWorkers.removeAction(self.workers[name])
        # delete from dictionary
        del self.workers[name]
        return

    # return string of workers
    # used in writeToCSV
    def getWorkers(self):
        workerStr = ""
        for key in self.workers:
            workerStr += key
            workerStr += " "
        return workerStr
    

    # write progress to a csv file
    def writeToCSV(self, partType, stepname):
        timestamp = str(datetime.datetime.now())
        
        # f string below will be part type + the parts ID
        filepath = str(self.saveDir) + f'\{getattr(self.ui,f"{partType}LE").text()}.csv'
        if exists(filepath):
            with open(filepath, 'a') as csv:
                csv.write(stepname+","+timestamp+","+self.getWorkers()+"\n")
        else:
            with open(filepath, 'w') as csv:
                csv.write(stepname+","+timestamp+","+self.getWorkers()+"\n")
        return

    # pulled straight from pangui with minimal modification
    def diagramPopup(self, diagram):
        buffer = 50
        wOpt = tkinter.Tk().winfo_screenwidth() - buffer
        hOpt = tkinter.Tk().winfo_screenheight() - buffer

        self._diagram = QLabel()

        pixmap = QPixmap()
        pixmap.load(f'guis/panel/partsprep/partsPrepImages/{diagram}')

        w = pixmap.width()
        h = pixmap.height()

        if not w == 0 and not h == 0:
            if w > wOpt or h > hOpt:
                self._diagram.setPixmap(
                    pixmap.scaled(wOpt - 20, hOpt - 20, Qt.KeepAspectRatio)
                )
                self._diagram.resize(wOpt, hOpt)
            else:
                self._diagram.setPixmap(pixmap.scaled(w, h, Qt.KeepAspectRatio))
                self._diagram.resize(w + 20, h + 20)

            self._diagram.setAlignment(Qt.AlignCenter)
            self._diagram.show()

    # do start and stop things
    # does start button things if starting == True
    #   else does stop button things
    def startStopButton(self, partType, starting):
        startingNoID = False
        # if starting verify that there are workers
        if starting:
            if len(self.workers) == 0:
                QMessageBox.warning(
                    self,
                    "No Workers",
                    "To begin please add a worker using the tab in the upper left."
                )
                return
            
            if len(getattr(self.ui, f"{partType}LE").text()) <3 :   # <3 <3 <3
                
                # no ID found
                reply = QMessageBox.question(self,
                    "No ID entered",
                    "No ID has been entered for this part.  If you choose to continue, the part will be referred to as the first worker's name plus today's date.  This can be changed later.\nDo you wish to continue?",
                    QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    # get first worker
                    first = ""
                    for action in self.ui.menuWorkers.children():
                        if action.text() != "Workers":
                            first = action.text()
                    # get todays date
                    now = datetime.datetime.now()
                    today = f'{now.day:02d}{now.month:02d}{now.year}'
                    # allow for weird ID
                    getattr(self.ui, f'{partType}LE').setValidator(None)
                    # set new ID
                    getattr(self.ui, f'{partType}LE').setText(
                        f'{first[6:]}-{today}'
                    )
                    startingNoID = True
                if reply == QMessageBox.StandardButton.No:
                    return

        for box in self.getCheckboxes(getattr(self.ui, partType)):
            box.setEnabled(starting)

        # line edit for id - disable if starting unless starting w/ no id
        getattr(self.ui,f"{partType}LE").setDisabled(starting and not startingNoID)
        # start button
        getattr(self.ui,f"{partType}StartPB").setDisabled(starting)
        # stop button
        getattr(self.ui,f"{partType}StopPB").setEnabled(starting)
        # comment button
        getattr(self.ui, f'{partType}ComEntryPB').setEnabled(starting)

        # add a "step" to the CSV
        self.writeToCSV(
            partType,
            "Session Initialized " if starting else "Session Terminated "
        )

        return

    # submit comment from entry text edit widget (triggered by submit comment button)
    def submitComment(self,partType):
        # get comment text
        text = getattr(self.ui, f'{partType}ComEntryTE').toPlainText()
        # save to CSV
        self.writeToCSV(partType, text)
        # clear entry widget
        getattr(self.ui, f'{partType}ComEntryTE').clear()
        # add to comment list
        getattr(self.ui, f'{partType}ComDisplayTE').append(text)

        return
        






def run():
    app = QApplication(sys.argv)  # make an app
    app.setStyle(QStyleFactory.create("Fusion"))  # aestetics
    window = partsPrepGUI(Ui_MainWindow())  # make a window

    window.show()
    app.exec_()

    

if __name__ == "__main__":
    run()