# for creating app, using paths, writing/reading csvs, fetting current date
import sys , os, inspect, getpass, csv, datetime

from tkinter import messagebox, Tk
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
from PyQt5.QtCore import Qt, QRect

# Add GUIS/panel/current to sys.path
sys.path.insert(0, str(Path(Path(__file__).resolve().parent.parent.parent)))
# import UI
from tension_devices.hv_gui.hvGUI import (
    Ui_MainWindow,
) 


'''
LIST OF IMPORTANT WIDGETS:
    Initialized in .setupUi
    Panel input                 --> panelNumLE
    Voltage input               --> voltageBox
    Panel side input            --> sideBox
    Straw position              --> positionBox
    Amps input                  --> ampsLE
    Trip status input           --> tripBox
    

    Initialized in _init_scroll
    List of right current boxes --> self.currentRight
    List of left current boxes  --> self.currentLeft
    List of trip check boxes    --> self.isTripped
    (to access the right current for straw 50,
        use self.currentRight[50])

HOW DATA IS STORED:
    After the scroll area is init'ed, the following members
        self.current
        and
        self.isTripped
        are lists of the widgets in the scroll area.
    These will be used to store all the data, rather than a
        big list or something.

    The current list can have it's text accessed by .text()
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
        # save/load methods ("DB" or "CSV")
        self.saveMethod = saveMethod
        self.loadMethod = loadMethod
        # panel id (MNXXX)
        self.panel = panel
        # current straw (initial is 0)
        self.straw = 0

        # set icon in upper left
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QIcon(f'{dir_path}\\mu2e.jpg'))

        # set save mode, changes at the end of this function
        self.saveMode = ""

        # bind functions to next straw
        self.ui.ampsLE.returnPressed.connect(self.nextStraw)
        self.ui.subStrawButton.clicked.connect(self.nextStraw)

        # bind typed change of spin box to strawChanged()
        self.ui.positionBox.valueChanged.connect(self.strawChanged)

        # bind function to submit panel button
        self.ui.subPanelButton.clicked.connect(self.submitPanel)

        # disable straw data entry widgets
        self.ui.ampsLE.setDisabled(True)
        self.ui.tripBox.setDisabled(True)

        # disable panel line edit if launched from gui
        if panel is not None:
            self.ui.panelNumLE.setText(panel)
            self.ui.panelNumLE.setDisabled(True)
            self.saveMode = "DB"
        else:
            self.saveMode = "CSV"



    def _init_Scroll(self):
        self.ui.hvGrid = QGridLayout()

        for i in range(96):  # loop to fill scroll area
            hvLabel = QLabel(f"{i}")  # start with straw position labels
            hvLabel.setObjectName(
                f"hvLabel_{i}"
            )  # they can't (shouldn't) all have the same name
            self.ui.hvGrid.addWidget(hvLabel, i, 0)  # add them to grid, 0th column

            # current entry widgets
            currentEntry = QLineEdit(self.ui.scrollContents)  # make line edit widget
            currentEntry.setFixedWidth(100)  # set fixed width
            currentEntry.setObjectName(
                f"current_{str(i).zfill(2)}"
            )  # name will be lCurrent_<position>, zfill pads with zeros
            self.ui.hvGrid.addWidget(
                currentEntry, i, 1, Qt.AlignHCenter
            )  # place widget in it's row, 1st column

            hvIsTripBool = QCheckBox(self.ui.scrollContents)
            hvIsTripBool.setObjectName(f"hvIsTripBool_{i}")  # use z fill?
            self.ui.hvGrid.addWidget(hvIsTripBool, i, 2, Qt.AlignHCenter)

        # lambda functions for finding widgets and returning lists of widgets
        findLineEdit = lambda name: [
            self.ui.scrollContents.findChild(QLineEdit, f"{name}_{str(i).zfill(2)}")
            for i in range(96)
        ]
        findCheck = lambda name: [
            self.ui.scrollContents.findChild(QCheckBox, f"{name}_{i}")
            for i in range(96)
        ]
        # make list of currentLeft lineEdits
        self.current = findLineEdit("current")
        # make list of trip check boxes
        self.isTripped = findCheck("hvIsTripBool")

        # add the newly created grid layout to the GUI
        self.ui.scrollContents.setLayout(self.ui.hvGrid)
        # scrollontents is made in the .ui file, and hvGrid is made in this file by the stuff above in this function

        # disable everything
        for i in range(95):
            self.current[i].setReadOnly(True)
            self.isTripped[i].setDisabled(True)

        '''
        def widgetSaveHV(index):
            # lambda returns true if testing on left side
            isLeft = lambda : self.ui.sideBox.currentText() == "Left"
            # lambda returns true if testing at 1100V
            is1100 = lambda : self.ui.voltageBox.currentText() == "1100"
            self.saveHVMeasurement(
                # current position
                index,
                # give current to parameter for left side if using left
                self.current[index].text() if isLeft else None,
                # give current to parameter for right side if using right side
                None if isLeft else self.current[index].text(),
                # pass 1100 if testing at 1100 V
                "1100" is is1100 else "1500",
                # trip value
                self.isTripped[index].isChecked()
            )
            self.saveCSV()

        # This loop binds all of the lineEdit widgets to lineSaveHV()
        # enumerate(zip(cL, cR)) -->
        #     [(0, (lC_00, rC_00)), (1, (lC_01, rC_01)), ..., (95, (lC_95, rC_95))]
        # The second for loop goes through each lineEdit widget in lineEdits and binds lineSaveHV to its textEdited signal
        # The binding makes the lineSaveHV function get called whenever the text in a lineEdit widget is changed by the user
        # using .textChanged makes it save if the program or user changes it (.textEdited = only user change triggers it)
        # Also, python will cry if you don't use a lambda function in connect()
        for i, widget in enumerate(self.current):
            widget.textChanged.connect(lambda changed, index=i: widgetSaveHV(index))
            widget.setReadOnly(True)

        # Enumerate turns the list of checkBox widgets into a list of tuples of the form (<int>, <checkBox>)
        # where the int is the index/straw position and checkBox is the checkBox widget (really a pointer to it)
        for i, box in enumerate(self.isTripped):
            box.stateChanged.connect(lambda changed, index=i: widgetSaveHV(index))
            box.setDisabled(True)
        '''

    # input validation.  TODO
    def _init_validation(self):
        pass
    
    # linked to the submit panel button
    def submitPanel(self):
        # set panel member as current panel
        self.panel = self.ui.panelNumLE.text()

        # return if id isn't complete
        if len(self.panel) < 5:
            # show error
            root = Tk()
            root.withdraw()
            messagebox.showerror(
                title="Incomplete ID",
                message="Please enter a panel ID in the format MN***",
            )
            # return early
            return

        # return if voltage isn't chosen
        if self.ui.voltageBox.currentIndex() == 0:
            # show error
            root = Tk()
            root.withdraw()
            messagebox.showerror(
                title="Voltage not chosen",
                message="Please select a voltage option: 1100V or 1500V",
            )
            # return early
            return

        # return if side isn't chosen
        if self.ui.sideBox.currentIndex() == 0:
            # show error
            root = Tk()
            root.withdraw()
            messagebox.showerror(
                title="Side not chosen",
                message="Please select a side option: Right or Left",
            )
            # return early
            return
        
        # set csv file location
        # make string to represent today (mmddyyyy)
        today = datetime.date.today().strftime('%m%d%y')
        today.replace(' ', '')
        # make string for save location
        pathString = "\\..\\..\\..\\..\\..\\Data\\Panel Data\\hv_data"
        # make string for voltage (the index -1 will be 0 if it's 1100, 1 if 1500)
        voltString = "1500V" if (self.ui.sideBox.currentIndex() - 1) else "1100V"
        # make string for csv name (with \\ in the front to save inside the hv_data folder)
        fString = f"\\{self.panel}_hv_data_{voltString}_{today}.csv"
        # put it all together
        self.fileLocation = os.path.dirname(os.path.realpath(__file__)) + pathString + fString
        # make directory for CSVs if it doesn't exist yet
        print(self.fileLocation)
        if not os.path.exists(os.path.dirname(os.path.realpath(__file__)) + pathString):
            os.mkdir(os.path.dirname(os.path.realpath(__file__)) + pathString)

        # enable data entry widgets
        self.ui.positionBox.setEnabled(True)
        
        self.ui.ampsLE.setEnabled(True)
        self.ui.tripBox.setEnabled(True)
        self.ui.subStrawButton.setEnabled(True)

        # disable panel entry widgets
        self.ui.sideBox.setDisabled(True)
        self.ui.voltageBox.setDisabled(True)
        self.ui.panelNumLE.setDisabled(True)
        self.ui.subPanelButton.setDisabled(False)

        # initialize scroll area
        self._init_Scroll()

    # connected to the return pressed event for the amps line edit and submit straw button
    # saves data to scroll area
    def nextStraw(self):
        # save data for straw we're moving from
        self.saveHVMeasurement(
            self.ui.positionBox.value(),
            self.ui.ampsLE.text(),
            self.ui.voltageBox.currentText(),
            self.ui.tripBox.currentIndex()
        )
        # increment position
        self.ui.positionBox.setValue(self.ui.positionBox.value() +1)
        self.ui.ampsLE.clear() # clear value
        self.ui.tripBox.setCurrentIndex(0) # set to not tripped
        self.ui.ampsLE.setFocus() # move keyboard cursor to amps line edit
        self.straw = self.ui.positionBox.value() # update current straw
    
    # called after moving from one straw to another
    def strawChanged(self):
        # save previous straw
        self.saveHVMeasurement(
            self.straw,
            self.ui.ampsLE.text(),
            self.ui.voltageBox.currentText(),
            self.ui.tripBox.currentIndex()
        )
        # update current straw
        self.straw = self.ui.positionBox.value()
        # update entry widgets
        self.ui.ampsLE.setText(
            self.current[self.straw].text()
        )
        self.ui.tripBox.setCurrentIndex(
            1 if self.isTripped[self.straw].isChecked() else 0
        )
        self.ui.ampsLE.setFocus()

    # Save to DB, takes one position at a time, or saves a CSV
    def saveHVMeasurement(self, index, current, volts, isTrip):
        # launched by PANGUI
        if self.saveMethod is not None and self.saveMode == "DB":
            # pangui passes self.DP.saveHVMeasurement
            self.saveMethod(index, current, volts, isTrip)
        else:
            self.saveCSV()
        
        # ensure that scroll area is updated
        self.setAmp(index, current)
        self.setTrip(index, isTrip)

    # Load from DB, and put data into scroll area
    def loadHVMeasurements(self):
        # launched by PANGUI
        if self.loadMethod is not None and self.saveMode == "DB":
            # return PANGUI --> self.DP.loadHVMeasurements()
            # returns list of the form:
            # [(current_left0, current_right0, voltage0, is_tripped0), (current_left1, current_right1, voltage1, is_tripped1), ...]
            bigList = self.loadMethod()()
            # figure out side outside of loop
            side = self.getSide()
            for pos,straw in enumerate(bigList):
                # set current
                self.setAmp(pos, straw[side])
                # if tripped, set it that way (default is not tripped)
                if straw[3]: self.setTrip(pos,True) 
    
    # Save to CSV, saves all posiitons with one call
    def saveCSV(self):
        # ensure correct save mode
        if not self.saveMode == "CSV":
            return

        # make side string to shorten write header line
        side = "RIGHT" if self.getSide() else "LEFT"
        volt = "1500" if self.getVolt() else "1100"
        now = datetime.datetime.now().strftime("%m/%d/%Y - %H:%M:%S")
        # open file, use w to overwrite
        with open(self.fileLocation, "w") as csvF:
            # write headers
            csvF.write(f'Panel {self.panel} tested at {volt}V.  Last Update: {now}\n')
            csvF.write(f'posiiton,{side} current,voltage,is tripped')

            for p in range(96):
                csvF.write("\n")
                # write each row, with data in the same order as the header
                csvF.write(f'{p},{self.getAmp(p)},{self.getTrip(p)}')

            # close the file
            csvF.close()

    # Load from CSV, currently broken X_X
    def loadCSV(self):
        print("hello1")
        # ensure correct save mode
        if not self.saveMode == "CSV":
            return
        # open file for reading
        with open(self.fileLocation, "r") as csvF:
            print("hello2")
            # make reader object
            reader = csv.reader(csvF)
            
            # skip first line (header)
            next(reader)

            for row in reader:
                if row[1] != '':
                    self.setAmp(1,int(row[0]),row[1])
                elif row[2] !='':
                    self.setAmp(0,int(row[0]),row[2])
                self.setTrip(int(row[0]),row[4])


    # gets a current value from scroll area
    # position = straw position
    def getAmp(self, position):
        return self.current[position].text()

    # gets a bool from scroll area
    # position = straw position
    def getTrip(self, position):
        return self.isTripped[position].isChecked()

    # sets a current value in scroll area
    # position = straw position
    # amps = new value
    def setAmp(self, position, amps):
        self.current[position].setText(amps)

    # sets a bool in scroll area
    # position = straw position
    # boool = new checkbox value
    def setTrip(self, position, boool):
        self.isTripped[position].setChecked(bool(boool))

    # gets the current side in side combo box represented as an int
    # 1 = right, 0 = left
    def getSide(self):
        # index of right is 1, index of left is 2, so subtract 1
        return (self.ui.sideBox.currentIndex()) % 2

    # gets the current voltage in voltage combo box represented as an int
    # 0 = 1100V, 1 = 1500V
    def getVolt(self):
        # index of 1100 is 1, index of 1500 is 2, so subtract 1
        return (self.ui.voltageBox.currentIndex()) - 1

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