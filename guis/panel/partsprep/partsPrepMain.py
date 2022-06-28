import sys, datetime, tkinter
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
    QMessageBox
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
        self.initValidators()

 
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
        return

    # connect checkbox state chenged to below funciton
    def initCheckboxes(self):
        
        # connect BIR checkboxes
        for box in self.getCheckboxes(self.ui.bir):
            stepText = box.text()
            box.stateChanged.connect(
                lambda state, stepText=stepText: self.checkboxReaction("bir",stepText)
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

        return

    def initValidators(self):
        validator = lambda string: QRegularExpressionValidator(
            QRegularExpression(string)
        )
        # bir validator
        self.ui.birLE.setValidator(validator('\d{3}'))

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
        filepath = str(self.saveDir) + f'\{partType}{getattr(self.ui,f"{partType}LE").text()}.csv'
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
        # if starting verify that there are workers
        if starting:
            if len(self.workers) == 0:
                QMessageBox.warning(
                    self,
                    "No Workers",
                    "To begin please add a worker using the tab in the upper left."
                )
                return
            if len(self.ui.birLE.text()) < 3:
                return

        for box in self.getCheckboxes(getattr(self.ui, partType)):
            box.setEnabled(starting)

        # line edit for id
        getattr(self.ui,f"{partType}LE").setDisabled(starting)
        # start button
        getattr(self.ui,f"{partType}StartPB").setDisabled(starting)
        # stop button
        getattr(self.ui,f"{partType}StopPB").setEnabled(starting)

        # add a "step" to the CSV
        self.writeToCSV(
            partType,
            "Session Initialized " if starting else "Session Terminated "
        )

        return
        






def run():
    app = QApplication(sys.argv)  # make an app
    app.setStyle(QStyleFactory.create("Fusion"))  # aestetics
    window = partsPrepGUI(Ui_MainWindow())  # make a window

    window.show()
    app.exec_()

    

if __name__ == "__main__":
    run()