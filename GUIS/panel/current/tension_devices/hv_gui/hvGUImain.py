# for creating app, using paths
import sys , os, inspect, getpass
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


'''
LIST OF IMPORTANT WIDGETS:
    Initialized in .setupUi
    Panel input                 --> panelNumLE
    Straw position              --> positionBox
    Panel side input            --> sideBox
    Amps input                  --> ampsLE
    Trip status input           --> tripBox
    voltage input               --> voltageBox

    Initialized in _init_scroll
    List of right current boxes --> self.currentRight
    List of left current boxes  --> self.currentLeft
    List of trip check boxes    --> self.isTripped
    (to access the right current for straw 50,
        use self.currentRight[50])

HOW DATA IS STORED:
    After the scroll area is init'ed, the following members
        self.currentRight
        self.currentLeft
        self.isTripped
        are lists of the widgets in the scroll area.
    These will be used to store all the data, rather than a
        big list or something.

    The current lists can have their text accessed by .text()
        and it can be changed with .setText(<string>)
    The trip checkbox list can have the boolean value of a box
        returned with .isChecked() and the value can be changed
        with .setChecked(<bool>)

    However!  there are set/get methods for doing those things
        to make code more readable.  See setAmp, getAmp,
        setTrip, and getTrip
    
'''

class highVoltageGUI(QMainWindow):

    def __init__(
        self,
        parent = None,
        ui_layout=Ui_MainWindow,
        saveMethod = None,
        loadMethod = None,
        panel = None
        ):
        # setup ui
        # init window
        super(highVoltageGUI, self).__init__(parent)
        # create ui member
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # set other members from parameters
        self.saveMethod = saveMethod
        self.loadMethod = loadMethod
        self.panel = panel

        # set icon in upper left
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QIcon(f'{dir_path}\\mu2e.jpg'))

        # set save mode, changes at the end of this function
        self.saveMode = ""

        # bind functions to next straw
        self.ui.ampsLE.returnPressed.connect(self.nextStraw)
        self.ui.subStrawButton.clicked.connect(self.nextStraw)

        # bind function to submit panel button
        self.ui.subPanelButton.clicked.connect(self.submitPanel)

        # disable panel input AND load if launched from gui
        if panel is not None:
            self.ui.panelNumLE.setText(f'MN{panel}')
            self.ui.panelNumLE.setDisabled(True)
            self.ui.subPanelButton.setDisabled(True)
            self.loadHVMeasurements()
            # init scroll area
            self._init_Scroll()
            # set save mode
            self.saveMode = "DB"
        else:
            self.ui.positionBox.setDisabled(True)
            self.ui.sideBox.setDisabled(True)
            self.ui.ampsLE.setDisabled(True)
            self.ui.tripBox.setDisabled(True)
            self.ui.voltageBox.setDisabled(True)
            self.ui.subStrawButton.setDisabled(True)
            # set save mode
            self.saveMode = "CSV"



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
            self.saveCSV()

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
            self.saveCSV()

        # This loop binds all of the lineEdit widgets to lineSaveHV()
        # enumerate(zip(cL, cR)) -->
        #     [(0, (lC_00, rC_00)), (1, (lC_01, rC_01)), ..., (95, (lC_95, rC_95))]
        # The second for loop goes through each lineEdit widget in lineEdits and binds lineSaveHV to its textEdited signal
        # The binding makes the lineSaveHV function get called whenever the text in a lineEdit widget is changed by the user
        # using .textChanged makes it save if the program or user changes it (.textEdited = only user change triggers it)
        # Also, python will cry if you don't use a lambda function in connect()
        for i, lineEdits in enumerate(zip(self.currentLeft, self.currentRight)):
            for widget in lineEdits:
                widget.textChanged.connect(lambda changed, index=i: lineSaveHV(index))

        # Enumerate turns the list of checkBox widgets into a list of tuples of the form (<int>, <checkBox>)
        # where the int is the index/straw position and checkBox is the checkBox widget (really a pointer to it)
        for i, box in enumerate(self.isTripped):
            box.stateChanged.connect(lambda changed, index=i: boxSaveHV(index))

    # input validation.  TODO
    def _init_validation(self):
        pass

    def submitPanel(self):
        # set panel member as current panel
        self.panel = self.ui.panelNumLE.text()
        # return if id isn't complete
        if len(self.panel) < 5:
            return
        # set csv file location
        self.fileLocation = os.path.dirname(os.path.realpath(__file__)) + f"\\..\\..\\..\\..\\..\\Data\\Panel Data\\hv_data\\{self.panel}_hv_data.csv"
        # make directory for CSVs if it doesn't exist yet
        if not os.path.exists(os.path.dirname(os.path.realpath(__file__)) + f"\\..\\..\\..\\..\\..\\Data\\Panel Data\\hv_data"):
            os.mkdir(os.path.dirname(os.path.realpath(__file__)) + f"\\..\\..\\..\\..\\..\\Data\\Panel Data\\hv_data")

        self.ui.positionBox.setEnabled(True)
        self.ui.sideBox.setEnabled(True)
        self.ui.ampsLE.setEnabled(True)
        self.ui.tripBox.setEnabled(True)
        self.ui.voltageBox.setEnabled(True)
        self.ui.subStrawButton.setEnabled(True)

        self.ui.panelNumLE.setDisabled(True)
        self.ui.subPanelButton.setDisabled(False)
    
    # connected to the return pressed event for the amps line edit and submit straw button
    # saves data to scroll area
    def nextStraw(self):
        # save data
        self.saveHVMeasurement(
            self.ui.positionBox.value(),
            self.ui.ampsLE.text() if self.getSideInput() else "",
            self.ui.ampsLE.text() if not self.getSideInput() else "",
            self.ui.tripBox.currentIndex()
        )
        # increment position
        self.ui.positionBox.setValue(self.ui.positionBox.value() +1)
        self.ui.ampsLE.clear() # clear value
        self.ui.tripBox.setCurrentIndex(0) # set to not tripped
        self.ui.ampsLE.setFocus()

    # saving every time an edit is made would require totally re-writing the csv...
    #   maybe use some kind of buffer and save every few minutes/on close?
    #   saving through pangui would avoid this.
    def saveHVMeasurement(self, index, curLeft, curRight, isTrip):
        # launched by PANGUI
        if self.saveMethod is not None and self.saveMode == "DB":
            # pangui passes self.DP.saveHVMeasurement
            self.saveMethod(index, curLeft, curRight, isTrip)
        
        # ensure that scroll area is updated
        self.setAmp(0, index, curRight)
        self.setAmp(1, index, curLeft)
        self.setTrip(index, isTrip)

    def loadHVMeasurements(self):
        # launched by PANGUI
        if self.loadMethod is not None and self.saveMode == "DB":
            # return PANGUI --> self.DP.loadHVMeasurements()
            # returns list of the form:
            # [(current_left0, current_right0, is_tripped0), (current_left1, current_right1, is_tripped1), ...]
            bigList = self.loadMethod()()
            for pos,straw in enumerate(bigList):
                # set both currents
                if straw[0] is not None:
                    self.setAmp(1,pos,str(straw[0]))
                if straw[1] is not None:
                    self.setAmp(0,pos,str(straw[1]))
                # if tripped
                if straw[2]:
                    # set it that way, default is not tripped
                    self.setTrip(pos,True)
    

    def saveCSV(self):
        # ensure correct save mode
        if not self.saveMode == "CSV":
            return
        # open file, use w to overwrite
        with open(self.fileLocation, "w") as csv:
            # write header
            csv.write("position,left current,right current,voltage,is tripped")

            for p in range(96):
                # write each row, with data in the same order as the header
                csv.write(f'{p},{self.getAmp(1,p)},{self.getAmp(0,p)},{self.getVoltInput()},{self.getTrip(p)}')

            # close the file
            csv.close()



    def loadCSV(self):
        pass


    # gets a current value from scroll area
    # side = 0 for right, 1 for left
    # position = straw position
    def getAmp(self, side, position):
        if side:
            return self.currentLeft[position].text()
        else:
            return self.currentRight[position].text()

    # gets a bool from scroll area
    # position = straw position
    def getTrip(self, position):
        return self.isTripped[position].isChecked()

    # gets the current side in side combo box represented as an int
    # 0 = right, 1 = left
    def getSideInput(self):
        # index of right is 1, index of left is 2, so subtract 1
        return (self.ui.sideBox.currentIndex()) - 1

    # gets the current voltage in voltage combo box represented as an int
    # 0 = 1100V, 1 = 1500V
    def getVoltInput(self):
        # index of 1100 is 1, index of 1500 is 2, so subtract 1
        return (self.ui.voltageBox.currentIndex()) - 1

    # sets a current value in scroll area
    # side = 0 for right, 1 for left
    # position = straw position
    # amps = new value
    def setAmp(self, side, position, amps):
        if side:
            self.currentLeft[position].setText(amps)
        else:
            self.currentRight[position].setText(amps)

    # sets a bool in scroll area
    # position = straw position
    # boool = new checkbox value
    def setTrip(self, position, boool):
        self.isTripped[position].setChecked(boool)

# main
if __name__ == "__main__":
    # make app
    app = QApplication(sys.argv)
    # make window, give it "blank" window to use
    window = highVoltageGUI()
    # set window name
    window.setWindowTitle("High Voltage Data Recording")
    # show window on desktop
    window.show()

    # run it!
    app.exec()













'''
# setup data processor
        self.pro = 5
        self.DP = DataProcessor(
            gui=self,
            save2txt=False,
            save2SQL=True,
            lab_version=True,
            sql_primary=True,
        )
sys.path.insert(
    0, str(Path(Path(__file__).resolve().parent.parent.parent))
)
from dataProcessor import MultipleDataProcessor as DataProcessor

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
'''