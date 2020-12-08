# for creating app, using paths
import sys , os, inspect
# for using paths
from pathlib import Path, PurePath
# for interacting with db
import sqlalchemy as sqla
# for GUI widget management
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QTableWidget,
    QGridLayout,
    QScrollArea,
    QWidget,
    QComboBox,
    QListWidget,
    QListWidgetItem,
    QCheckBox,
    QPushButton,
    QTableWidgetItem,
    QLineEdit
)
# for GUI label and upper left icon management
from PyQt5.QtGui import QBrush, QIcon
# for GUI window management
from PyQt5.QtCore import Qt, QRect, QObject
# ui in .py format
from hvGUI import Ui_MainWindow
sys.path.insert(
    0, str(Path(Path(__file__).resolve().parent.parent.parent))
)
from dataProcessor import MultipleDataProcessor as DataProcessor

'''
LIST OF IMPORTANT WIDGETS:
    Initialized in .setupUi
    Panel input                 --> panelNumLE
    Straw position              --> positionBox
    Panel side input            --> sideBox
    Amps input                  --> ampsLE
    Trip status input           --> tripBox

    Initialized in _init_scroll
    List of right current boxes --> self.currentRight
    List of left current boxes  --> self.currentLeft
    List of trip check boxes    --> self.isTripped
    (to access the right current for straw 50,
        use self.currentRight[50])
'''

class highVoltageGUI(QMainWindow):

    def __init__(self, ui_layout):
        # setup ui
        # init window
        QMainWindow.__init__(self)
        # create ui member
        self.ui = ui_layout
        # init widgets and stuff in ui, method in hvGUI.py
        ui_layout.setupUi(self)

        # set icon in upper left
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QIcon(f'{dir_path}\\mu2e.jpg'))

        # setup data processor
        self.pro = 5
        self.DP = DataProcessor(
            gui=self,
            save2txt=False,
            save2SQL=True,
            lab_version=True,
            sql_primary=True,
        )

        # init scroll area
        self._init_Scroll()

        # bind function to enter pressed on ampsLE
        self.ui.ampsLE.returnPressed.connect(self.nextStraw)


    #################################################################
    ##### THIS WAS COPY/PASTED FROM panelGUI._init_pro5_setup() #####
    #################################################################
    # Literally didn't even have to change variable names.
    # The fact that this works so smoothly makes me think that this program could 
    #   potentially use the same data processor as PANGUI with little effort
    def _init_Scroll(self):
        self.ui.hvGrid = QGridLayout()

        for i in range(96):  # loop to fill scroll area
            hvLabel = QLabel(f"{i}")  # start with straw position labels
            hvLabel.setObjectName(
                f"hvLabel_{i}"
            )  # they can't (shouldn't) all have the same name
            self.ui.hvGrid.addWidget(hvLabel, i, 0)  # add them to grid, 0th column

            # left current entry widgets
            lCurrentEntry = QLineEdit(self.ui.scrollContents)  # make line edit widget
            lCurrentEntry.setFixedWidth(150)  # set fixed width
            lCurrentEntry.setObjectName(
                f"lCurrent_{str(i).zfill(2)}"
            )  # name will be lCurrent_<position>, zfill pads with zeros
            self.ui.hvGrid.addWidget(
                lCurrentEntry, i, 1
            )  # place widget in it's row, 1st column

            # lCurrent entry, except RIGHT side
            rCurrentEntry = QLineEdit(self.ui.scrollContents)  # make line edit widget
            rCurrentEntry.setFixedWidth(150)  # set fixed width
            rCurrentEntry.setObjectName(
                f"rCurrent_{str(i).zfill(2)}"
            )  # name will be rCurrent_<position>, zfill pads with zeros
            self.ui.hvGrid.addWidget(
                rCurrentEntry, i, 2
            )  # place widget in it's row, 1st column

            hvIsTripBool = QCheckBox(self.ui.scrollContents)
            hvIsTripBool.setObjectName(f"hvIsTripBool_{i}")  # use z fill?
            self.ui.hvGrid.addWidget(hvIsTripBool, i, 3)

        # lambda functions for finding widgets and returning lists of widgets
        findLineEdit = lambda name: [
            self.ui.scrollContents.findChild(QLineEdit, f"{name}_{str(i).zfill(2)}")
            for i in range(96)
        ]
        findCheck = lambda name: [
            self.ui.scrollContents.findChild(QCheckBox, f"{name}_{i}")
            for i in range(96)
        ]
        self.currentLeft = findLineEdit(
            "lCurrent"
        )  # make list of currentLeft lineEdits
        self.currentRight = findLineEdit(
            "rCurrent"
        )  # make list of currentRight lineEdits
        self.isTripped = findCheck("hvIsTripBool")  # make list of trip check boxes

        self.ui.scrollContents.setLayout(
            self.ui.hvGrid
        )  # add the newly created grid layout to the GUI
        # scrollontents is made in the .ui file, and hvGrid is made in this file by the stuff above in this function

        # The following two functions are bound to signals that the widgets in pro 5 emit
        # Whenever a lineEdit or checkBox in the scroll area are changed, the corresponding function is called
        # Both save all of the data for the straw that had a widget change

        # lineSaveHV is called whenever a lineEdit widget (currentLeft or currentRight) is changed
        # We want to write NULL values, so there is no restriction on what can be written.
        def lineSaveHV(index):
            self.saveHVMeasurement(
                index,
                self.currentLeft[index].text(),
                self.currentRight[index].text(),
                self.isTripped[index].isChecked(),
            )

        # boxSaveHV is called whenever a checkBox widget is checked or unckecked.
        # This function doesn't actually need to exist, since the check boxes could be bound to saveHVMeasurement(), but
        # it would be pretty hard to read if saveHVMeasurement() was bound to the widget in a lambda function in a loop
        def boxSaveHV(index):
            self.saveHVMeasurement(
                index,
                self.currentLeft[index].text(),
                self.currentRight[index].text(),
                self.isTripped[index].isChecked(),
            )

        # This loop binds all of the lineEdit widgets to lineSaveHV()
        # enumerate(zip(cL, cR)) -->
        #     [(0, (lC_00, rC_00)), (1, (lC_01, rC_01)), ..., (95, (lC_95, rC_95))]
        # The second for loop goes through each lineEdit widget in lineEdits and binds lineSaveHV to its textEdited signal
        # The binding makes the lineSaveHV function get called whenever the text in a lineEdit widget is changed by the user
        # Also, python will cry if you don't use a lambda function in connect()
        for i, lineEdits in enumerate(zip(self.currentLeft, self.currentRight)):
            for widget in lineEdits:
                widget.textEdited.connect(lambda changed, index=i: lineSaveHV(index))

        # Enumerate turns the list of checkBox widgets into a list of tuples of the form (<int>, <checkBox>)
        # where the int is the index/straw position and checkBox is the checkBox widget (really a pointer to it)
        for i, box in enumerate(self.isTripped):
            box.stateChanged.connect(lambda changed, index=i: boxSaveHV(index))

    def saveHVMeasurement(self, position, current_left, current_right, is_tripped):
        self.DP.saveHVMeasurement(position, current_left, current_right, is_tripped)

        if self.currentLeft[position].text() != current_left:
            self.displayHVMeasurement(position, current_left, current_right)
        if self.currentRight[position].text() != current_right:
            self.displayHVMeasurement(position, current_left, current_right)

    def displayHVMeasurement(self, index, current_left, current_right, is_tripped=False):
        self.currentLeft[index].setText(str(current_left))
        self.currentRight[index].setText(str(current_right))
        self.isTripped[index].setChecked(is_tripped)

    def _init_validation(self):
        pass

    def nextStraw(self):
        # self.saveData()
        self.ui.positionBox.setValue(self.ui.positionBox.value() +1)
        self.ui.ampsLE.clear()
        self.ui.ampsLE.setFocus()

    



# main

if __name__ == "__main__":
    # make app
    app = QApplication(sys.argv)
    # make window, give it "blank" window to use
    window = highVoltageGUI(Ui_MainWindow())
    # set window name
    window.setWindowTitle("High Voltage Data Recording")
    # show window on desktop
    window.show()

    # run it!
    app.exec()