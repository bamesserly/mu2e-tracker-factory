import sys, datetime
from os.path import exists

from guis.common.getresources import GetProjectPaths # import paths for saving CSVs
from guis.panel.partsprep.partsPrepUI import Ui_MainWindow  # import raw UI

from PyQt5.QtWidgets import (
    QApplication,
    QListWidgetItem,
    QMainWindow,
    QLabel,
    QMessageBox,
    QStyleFactory,
    QLineEdit,
    QCheckBox,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout
)

from PyQt5 import Qt


class partsPrepGUI(QMainWindow):

    def __init__(self, ui_layout):
        # initialize superclass
        QMainWindow.__init__(self)
        # make ui member
        self.ui = ui_layout
        # apply ui to window
        ui_layout.setupUi(self)

        self.saveDir = GetProjectPaths()["partsprepdata"]

        self.initStartStopButtons()
        self.initCheckboxes()

 
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
        # TODO
        return

    # connect checkbox state chenged to below funciton
    def initCheckboxes(self):
        
        # connect BIR checkboxes
        for box in self.getCheckboxes(self.ui.bir):
            stepText = box.text()
            box.stateChanged.connect(
                lambda state, stepText=stepText: self.checkboxReaction("bir",stepText)
            )

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

    # for each box make it:
    # - launch a picture if the next step (TODO)
    #   has a picture and auto open is on
    # - make it read only once checked (TODO)
    # - trigger a save 
    def checkboxReaction(self, partType, step):

        #save
        self.writeToCSV(partType, step)
        return
    

    # write progress to a csv file
    def writeToCSV(self, partType, stepname):
        timestamp = str(datetime.datetime.now())
        
        # f string below will be part type + the parts ID
        filepath = str(self.saveDir) + f'\{partType}{getattr(self.ui,f"{partType}LE").text()}.csv'
        if exists(filepath):
            with open(filepath, 'a') as csv:
                print(stepname)
                csv.write(stepname+","+timestamp+"\n")
        else:
            with open(filepath, 'w') as csv:
                csv.write(stepname+","+timestamp+"\n")

        return

    # display a picture
    def launchPicture(self,pic):
        #TODO
        return

    # do start and stop things
    # does start button things if starting == True
    #   else does stop button things
    def startStopButton(self, partType, starting):
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