# for creating app, using paths, writing/reading csvs, fetting current date
import sys, os, inspect, getpass, csv, datetime, numpy as np

from tkinter import messagebox, Tk

import pyqtgraph as pg

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
    QLineEdit,
    QMessageBox,
    QStyleFactory
)

# for GUI label and upper left icon management
from PyQt5.QtGui import QBrush, QIcon, QRegExpValidator, QPen

# for GUI window management
from PyQt5.QtCore import Qt, QRect, QRegExp

import qwt

# import UI
from guis.panel.hv.hvGUI import (
    Ui_MainWindow,
)

import logging

logger = logging.getLogger("root")

from guis.common.getresources import GetProjectPaths


"""
LIST OF IMPORTANT WIDGETS:
    Initialized in .setupUi
    Panel input                 --> panelNumLE
    Voltage input               --> voltageBox
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

    > These will be used to store all the data, rather than a
        big list or something.
    JK.  I'm adding a list, self.currentLists which contains lists
        of measurements for each channel since we want to be
        displaying ALL measurements, including those that aren't
        the most current ones.  self.currentLists is init'ed in
        the same function as self.current, _init_scroll().

    The current list can have it's text accessed by .text()
        and it can be changed with .setText(<string>)
    The trip checkbox list can have the boolean value of a box
        returned with .isChecked() and the value can be changed
        with .setChecked(<bool>)

    However!  there are set/get methods for doing those things
        to make code more readable.  See setAmp, getAmp,
        setTrip, and getTrip

"""


class highVoltageGUI(QMainWindow):
    def __init__(
        self,
        parent=None,
        ui_layout=Ui_MainWindow,
        saveMethod=None,
        loadMethod=None,
        panel=None,
    ):
        # setup ui
        # init window
        super(highVoltageGUI, self).__init__(parent)
        # create ui member
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # member to allow popup to exist for more than a millisecond
        self.pop = None

        # Go gophers!
        self.ui.centralwidget.setStyleSheet(
            """QMainWindow, QWidget#centralwidget, QWidget#scrollContents { background-color: rgb(122, 0, 25); }
            QLineEdit { color: rgb(255, 204, 51); background-color: rgb(142, 20, 45); }QLabel { color: rgb(255, 204, 51); }
            QSpinBox { color: rgb(255, 204, 51); background-color: rgb(111, 0, 14); }
            QPushButton, QScrollArea { color: rgb(255, 204, 51); background-color: rgb(111, 0, 14) }
            QCheckBox { color: rgb(255, 204, 51); background-color: rgb(111, 0, 14); }
            QComboBox, QComboBox QAbstractItemView { color: rgb(255, 204, 51); background-color: rgb(122, 0, 25);
                selection-color: rgb(133, 255, 230); selection-background-color: rgb(0, 51, 204); }
            QStatusBar {color: rgb(255, 204, 51)}"""
        )

        # set other members from parameters
        # save/load methods ("DB" or "CSV")
        self.saveMethod = saveMethod
        self.loadMethod = loadMethod
        # panel id (MNXXX)
        self.panel = panel
        # current straw (initial is 0)
        self.straw = 0

        # set icon in upper left
        self.setWindowIcon(QIcon(str(GetProjectPaths()["hvguiicon"])))

        # set save mode (DB or CSV), changes at the end of this function
        self.saveMode = ""

        # bind save functions
        # hitting enter while at amps line edit or clicking submit
        # straw button triggers save
        self.ui.ampsLE.returnPressed.connect(self.nextStraw)
        self.ui.subStrawButton.clicked.connect(self.nextStraw)

        # bind typed change of spin box to strawChanged()
        self.ui.positionBox.valueChanged.connect(self.strawChanged)
        # turn off keyboard tracking so that value changed is
        # only emitted when enter is pressed or the widget loses focus
        self.ui.positionBox.setKeyboardTracking(False)

        # set validator for amps input
        regexp = QRegExp("[+-]?[0-9]+\.[0-9]+|null|NULL")
        ampValidator = QRegExpValidator(regexp)
        self.ui.ampsLE.setValidator(ampValidator)

        # bind function to submit panel button
        self.ui.subPanelButton.clicked.connect(self.submitPanel)

        # disable straw data entry widgets
        self.ui.positionBox.setDisabled(True)
        self.ui.ampsLE.setDisabled(True)
        self.ui.tripBox.setDisabled(True)

        # setup graph
        self._init_plot()

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

        # create list of lists for additional data storage
        self.currentLists = []

        # disable everything and populate currentLists
        for i in range(96):
            self.current[i].setReadOnly(True)
            self.isTripped[i].setDisabled(True)

            self.currentLists.append([])

        

    # input validation.  TODO
    def _init_validation(self):
        pass

            # graph on right side

    # graph on right
    def _init_plot(self):
        self.plot = pg.plot()

        self.scatterMain = pg.ScatterPlotItem(
            size=10,
            brush=pg.mkBrush(255, 255, 255, 120)
        )
        self.scatterLatest = pg.ScatterPlotItem(
            size=10,
            brush=pg.mkBrush(255, 255, 255, 255),
            symbol='t1'
        )

        self.plot.addItem(self.scatterMain)
        self.plot.addItem(self.scatterLatest)
        self.ui.graphLayout.addWidget(self.plot)
        self.plot.setYRange(-0.05,1)

    # update graph
    def replot(self):
        self.scatterMain.clear()

        # L indicates "latest", all the most recent measurements
        numPoints = 0
        numPointsL = 0
        xs = []
        ys = []
        xsL = []
        ysL = []
        for z in range(96):
            #if self.getAmp(z) != "":
            #    numPoints += 1
            #    xs.append(float(self.getAmp(z)))
            #    ys.append(float(z))
            
            #if len(self.currentLists[z]) > 0:
            for a in range(len(self.currentLists[z])):
                # get current
                if float(self.getAmp(self.currentLists[z][a][4])) != float(self.currentLists[z][a][0]):
                    xs.append(float(self.currentLists[z][a][0]))
                    # get channel number (position)
                    ys.append(float(self.currentLists[z][a][4]))
                    # for other indexes in the contents of self.currentLists look
                    #   at the function loadHVMeasurements().
                    # add one to number of points collected
                    numPoints += 1
                else:
                    # do all the same but for the lists for the latest stuff
                    xsL.append(float(self.currentLists[z][a][0]))
                    ysL.append(float(self.currentLists[z][a][4]))
                    numPointsL += 1
            

        points = [{'pos': [ys[z],xs[z]], 'data':1} for z in range(numPoints)]
        pointsL = [{'pos': [ysL[z],xsL[z]], 'data':1} for z in range(numPointsL)]

        for z in range(numPoints):
            x = float(xs[z])
            y = float(ys[z])
            label = pg.TextItem(
                text = f'{int(ys[z])}'
            )
            label.setPos(y,x)
            self.plot.addItem(label)

        for z in range(numPointsL):
            x = float(xsL[z])
            y = float(ysL[z])
            label = pg.TextItem(
                text = f'{int(ysL[z])}'
            )
            label.setPos(y,x)
            self.plot.addItem(label)

        self.scatterMain.addPoints(points)
        self.scatterLatest.addPoints(pointsL)

    # linked to the submit panel button
    def submitPanel(self):
        # set panel member as current panel
        self.panel = self.ui.panelNumLE.text()

        # return if id isn't complete
        if len(self.panel) < 5:
            # show error and return early
            self.givePop("Please enter a panel ID in the format MN***")
            return

        # return if voltage isn't chosen
        if self.ui.voltageBox.currentIndex() == 0:
            # show error and return early
            self.givePop("Please choose a voltage option")
            return

        # enable data entry widgets
        self.ui.positionBox.setEnabled(True)
        self.ui.ampsLE.setEnabled(True)
        self.ui.tripBox.setEnabled(True)
        self.ui.subStrawButton.setEnabled(True)

        # disable panel entry widgets
        self.ui.voltageBox.setDisabled(True)
        self.ui.panelNumLE.setDisabled(True)
        self.ui.subPanelButton.setDisabled(True)

        # initialize scroll area
        self._init_Scroll()

        # disable everything in scroll area
        # done earlier, but somehow launching from pangui undos it
        for i in range(95):
            self.current[i].setReadOnly(True)
            self.isTripped[i].setDisabled(True)

        # if launching from pangui, utilize load method
        self.loadHVMeasurements()

        # show plot
        self.replot()


    # connected to the return pressed event for the
    # amps line edit and submit straw button
    # saves data to scroll area
    def nextStraw(self):
        # save straw
        self.saveHVMeasurement(
            self.straw,
            "Left",
            self.ui.ampsLE.text(),
            self.ui.voltageBox.currentText(),
            self.ui.tripBox.currentIndex(),
        )
        # increment position
        self.ui.positionBox.setValue(self.ui.positionBox.value() + 1)
        # self.strawChanged() gets called, since positionBox.value() changed

    # called after moving from one straw to another
    # makes sure all displayed data is up to date
    def strawChanged(self):
        # first ensure that the new straw is in bounds
        if self.ui.positionBox.value() > 95:
            # if not, undo the change and return early
            self.ui.positionBox.setValue(self.straw)
            return
        # update current straw
        self.straw = self.ui.positionBox.value()
        # update entry widgets
        self.ui.ampsLE.setText(self.current[self.straw].text())
        self.ui.tripBox.setCurrentIndex(
            1 if self.isTripped[self.straw].isChecked() else 0
        )
        self.ui.ampsLE.setFocus()
        self.replot()

    # Save to DB, takes one position at a time, or saves a CSV
    def saveHVMeasurement(self, index, side, current, volts, isTrip):
        # launched by PANGUI
        if self.saveMethod is not None and self.saveMode == "DB":
            # pangui passes self.DP.saveHVMeasurement
            if current.lower() == "null":
                current = -78857676  # ascii code for NULL, 78=N 85=U, 76=L
            # save!
            self.saveMethod(index, side, current, volts, isTrip)
        else:
            self.saveCSV(index, side, current, volts, isTrip)

        # ensure that list and scroll area is updated
        print(self.currentLists)
        self.currentLists[index].append(
            [current,None,volts,isTrip,index,int(datetime.datetime.now().timestamp())]
        )
        self.setAmp(index, current)
        self.setTrip(index, isTrip)

    # Load from DB, and put data into scroll area
    def loadHVMeasurements(self):
        # launched by PANGUI
        if self.loadMethod is not None and self.saveMode == "DB":
            # return PANGUI --> self.DP.loadHVMeasurements()
            # returns list of tuples of the form:
            # (current_left0, current_right0, voltage0, is_tripped0, position0, timestamp0)
            #  float^           float^       float??^       bool^       int^      int^
            # one of the current vars will be None and if no measurement exists for the
            #   position then the whole tuple will be (None,None,None,None,None,None)
            bigList = self.loadMethod()()
            # figure out side and voltage
            # Side is hardcoded to left
            side = 0
            volt = self.getVolt()
            # adjust volt to match int from db
            volt = 1500 if volt else 1100

            # this list keeps track of timestamps of loaded data
            # each index corresponds to the same number straw position
            # if an index is None, no data loaded yet
            # if an index is an int (a timestamp) thats the time the loaded
            # data for that posiiton was recorded
            tSList = [None for _ in range(96)]

            # toop[side] refers to index 0 or 1, the left or right current
            # toop[2] = voltage (1100 or 1500)
            # toop[3] = trip status (bool)
            # toop[4] = position (int between 0 and 95 inclusive)
            # toop[5] = timestamp (int, epoch time)
            for toop in bigList:
                # if correct side and voltage
                if (toop[side] is not None) and (toop[2] == volt):
                    # if no data present yet or toop is newer data
                    if (tSList[toop[4]] is None) or (tSList[toop[4]] < toop[5]):
                        # need to update
                        tSList[toop[4]] = toop[5]
                        self.setAmp(toop[4], str(toop[side]))
                        self.setTrip(toop[4], toop[3])
                    # either way, add to the main list
                    self.currentLists[toop[4]].append(toop)
            

    # Save one HV measurement, append CSV file
    def saveCSV(self, position, side, current, voltage, is_tripped):
        headers = ["Position", "Current", "Side", "Voltage", "IsTripped", "Timestamp"]
        outdir = GetProjectPaths()["hvdata"]
        today = datetime.datetime.today().strftime("%Y%m%d")
        outfilename = self.panel + "_hv_data_" + today + ".csv"
        outfile = outdir / outfilename
        self.ui.statusbar.showMessage(f"CSV saved at: {outfile}")
        print("Saving HV current data to", str(outfile))
        file_exists = outfile.exists()
        outfile.parent.mkdir(exist_ok=True, parents=True)
        try:
            with open(outfile, "a+") as f:
                writer = csv.DictWriter(
                    f, delimiter=",", lineterminator="\n", fieldnames=headers
                )
                if not file_exists:
                    writer.writeheader()  # file doesn't exist yet, write a header
                writer.writerow(
                    {
                        "Position": position,
                        "Current": current,
                        "Side": side,
                        "Voltage": voltage,
                        "IsTripped": str(is_tripped),
                        "Timestamp": datetime.datetime.now().isoformat(),
                    }
                )
        except PermissionError:
            print(
                "HV data CSV file is locked. Probably open somewhere. Close and try again."
            )
            print("HV data is not being saved to CSV files.")

    # Load from CSV, currently broken X_X
    def loadCSV(self):
        return
        # ensure correct save mode
        if not self.saveMode == "CSV":
            return
        # open file for reading
        with open(self.fileLocation, "r") as csvF:
            # make reader object
            reader = csv.reader(csvF)

            # skip first line (header)
            next(reader)

            for row in reader:
                if row[1] != "":
                    self.setAmp(1, int(row[0]), row[1])
                elif row[2] != "":
                    self.setAmp(0, int(row[0]), row[2])
                self.setTrip(int(row[0]), row[4])

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
    # accounts for how null is saved
    def setAmp(self, position, amps):
        if amps == "-78857676.0":
            amps = "null"
        self.current[position].setText(amps)

    # sets a bool in scroll area
    # position = straw position
    # boool = new checkbox value
    def setTrip(self, position, boool):
        self.isTripped[position].setChecked(bool(boool))

    # gets the current voltage in voltage combo box represented as an int
    # 0 = 1100V, 1 = 1500V
    def getVolt(self):
        # index of 1100 is 1, index of 1500 is 2, so subtract 1
        return (self.ui.voltageBox.currentIndex()) - 1

    # takes a message (string) and returns warning popup with the message
    # return a popup
    def givePop(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Warning")
        self.pop = msg
        self.pop.show()


def run():

    # make app
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    # make window, give it "blank" window to use
    window = highVoltageGUI()
    # set window name
    window.setWindowTitle("High Voltage Data Recording")
    # show window on desktop
    window.show()

    # run it!
    app.exec()


# main
if __name__ == "__main__":
    run()
