import sys
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

    # connecting funcitons
    # connect menu buttons up top to correct functions
    def initMenuButtons(self):
        return

    # connect checkbox state chenged to below funciton
    def initCheckboxes(self):
        return

    # connect start/stop buttons to appropriate funcitons
    def initStartStopButtons(self):
        return





    # connected functions

    # for each box make it:
    # - launch a picture if the next step
    #   has a picture and auto open is on
    # - make it read only once checked
    def checkboxReaction(self):
        return
    
    # write progress to a csv file
    def writeToCSV(self, partType):
        
        # f string below will be part type + the parts ID
        filepath = self.saveDir + f'{partType}{getattr(self.ui,f"{partType}LE").text()}'

        if exists(filepath):
            with open(filepath, 'a') as csv:
                #print statement is a placeholder
                print("already exists")
        else:
            with open(filepath, 'w') as csv:
                #print statement is a placeholder
                print("doesn't exist yet")

        return

    # display a picture
    def launchPicture(self,pic):
        return

    def startButton(self, partType):
        for box in self.getCheckboxes(getattr(self.ui, partType)):
            box.setEnabled(True)

        getattr(self.ui,f"{partType}LE").setDisabled(True)

        return






def run():
    app = QApplication(sys.argv)  # make an app
    app.setStyle(QStyleFactory.create("Fusion"))  # aestetics
    window = partsPrepGUI(Ui_MainWindow())  # make a window

    window.show()
    app.exec_()

    

if __name__ == "__main__":
    run()