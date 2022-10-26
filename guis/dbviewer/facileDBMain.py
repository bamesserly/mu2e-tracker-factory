#  - -    --   - - /|_/|          .-----------------------.
#  _______________| @.@|         /  Written by Adam Arnett )
# (______         >\_W/<  ------/  Created 05/28/2020     /
#  -   / ______  _/____)       /  Last Update 10/25/2022 /
# -   / /\ \   \ \            (  PS: Meow! :3           /
#  - (_/  \_) - \_)            `-----------------------'

import sys, time, csv, os, tkinter, tkinter.messagebox, itertools, statistics

# for creating app, time formatting, saving to csv, finding local db, popup dialogs, longest_zip iteration function, stat functions
from datetime import timedelta

import logging
from matplotlib import cm
from matplotlib.lines import Line2D

logger = logging.getLogger("root")

# time formatting

# import qdarkstyle  # commented out since most machines don't have this and it has to be installed with pip
import sqlalchemy as sqla  # for interacting with db
import sqlite3  # for connecting with db
import matplotlib.pyplot as plt  # for plotting (in popups)
import matplotlib as mpl  # also for plotting (in popups)
import numpy as np  # for multiple things, mostly plotting (in gui)
import pyqtgraph as pg  # for plotting (in gui)

from PyQt5.QtWidgets import (
    QApplication,
    QListWidgetItem,
    QMainWindow,
    QLabel,
    QMessageBox,
    QStyleFactory,
)

# mostly for gui window management, QPen and QSize are for plotting
from PyQt5.QtGui import QBrush, QIcon, QPen
from PyQt5.QtCore import Qt, QPointF

# for time formatting
from datetime import datetime

# all for plotting apparently...
import sip
import qwt

from guis.dbviewer.facileDB import Ui_MainWindow  # import raw UI
from guis.dbviewer.panelData import PanelData  # import class for data organization

# Load resources manager
try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources
import data, resources

# for plotting heat data, qwt doesn't come with a convinient way to
# use time as the x-axis label (unless you want to use epoch time)
class TimeScaleDraw(qwt.QwtScaleDraw):
    def __init__(self, baseTime, *args):
        qwt.QwtScaleDraw.__init__(self, *args)
        self.baseTime = baseTime

    def label(self, value):
        timeStr = time.strftime("%m/%d, %H:%M", time.localtime(value))
        return qwt.QwtText(timeStr)


# fmt: off
# ██████╗  █████╗ ████████╗ █████╗ ██████╗  █████╗ ███████╗███████╗    ██╗   ██╗██╗███████╗██╗    ██╗███████╗██████╗
# ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔════╝    ██║   ██║██║██╔════╝██║    ██║██╔════╝██╔══██╗
# ██║  ██║███████║   ██║   ███████║██████╔╝███████║███████╗█████╗      ██║   ██║██║█████╗  ██║ █╗ ██║█████╗  ██████╔╝
# ██║  ██║██╔══██║   ██║   ██╔══██║██╔══██╗██╔══██║╚════██║██╔══╝      ╚██╗ ██╔╝██║██╔══╝  ██║███╗██║██╔══╝  ██╔══██╗
# ██████╔╝██║  ██║   ██║   ██║  ██║██████╔╝██║  ██║███████║███████╗     ╚████╔╝ ██║███████╗╚███╔███╔╝███████╗██║  ██║
# ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝      ╚═══╝  ╚═╝╚══════╝ ╚══╝╚══╝ ╚══════╝╚═╝  ╚═╝

# Main class for a gui to make interacting with the database easy, and worry free (no fear of accidentally deleting anything)
# Gets the QMainWindow class from facileDB.py


# the "fmt" comments prevent the black autoformatter from messing with comments and section headers



class facileDBGUI(QMainWindow):

    # fmt: off
    # ██╗███╗   ██╗██╗████████╗██╗ █████╗ ██╗     ██╗███████╗███████╗
    # ██║████╗  ██║██║╚══██╔══╝██║██╔══██╗██║     ██║╚══███╔╝██╔════╝
    # ██║██╔██╗ ██║██║   ██║   ██║███████║██║     ██║  ███╔╝ █████╗
    # ██║██║╚██╗██║██║   ██║   ██║██╔══██║██║     ██║ ███╔╝  ██╔══╝
    # ██║██║ ╚████║██║   ██║   ██║██║  ██║███████╗██║███████╗███████╗
    # ╚═╝╚═╝  ╚═══╝╚═╝   ╚═╝   ╚═╝╚═╝  ╚═╝╚══════╝╚═╝╚══════╝╚══════╝
    # Functions called by main, or by other functions under this section for the purpose of starting up the GUI.
    # fmt: on

    # initializer, takes ui parameter from the .ui file
    # parameters: no parameters
    # returns: nothing returned
    def __init__(self, ui_layout):
        # initialize superclass
        QMainWindow.__init__(self)
        # make ui member
        self.ui = ui_layout
        # apply ui to window
        ui_layout.setupUi(self)
        # make tkinter root for popup messages
        self.tkRoot = tkinter.Tk()
        # hide root, it's necessary for popups to work, but it's just a blank window otherwise
        self.tkRoot.withdraw()

        # put icon in upper left
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QIcon(f"{dir_path}\\mu2e.jpg"))

        # link buttons/menu items to functions
        self.initInputWidgets()

        # initialize widget lists
        self.initWidgetLists()

        # initialize menu bar actions
        self.initMenuActions()

        # create panelData member, pretty much all data is stored here
        # would it be more efficient to store data only in the widgets?
        # it might not be feasible, all the heat measurements would have
        # to go somewhere, and nobody cares about individual heat measurements
        self.data = PanelData()

        # happy 4th of July :)
        if datetime.today().month == 7 and datetime.today().day < 5:
            self.changeColor((255,255,255), (10,49,97),(179,25,66), (179,25,66))

    # override close button event (see comments in function)
    # parameters: event = close window button clicked signal(?)
    # returns: nothing returned
    def closeEvent(self, event):
        sys.exit()  # kill program
        # this is necessary since using the pyplot.show() makes python think there's another app running, so closing the gui
        # won't close the program if you used the plot button (so you'd have a python process still running in the background
        # doing nothing).  Overriding the closeEvent to exit the program makes sure the whole process is dead when the user
        # clicks the X in the upper right corner.
        # It's not called anywhere because having it here overwrites a QMainWindow method.
        # Killing it with sys.exit() will not hurt the database.

    # make engine, connection, and metadata objects to interact with database
    # parameters: database = file object that points to the database
    # returns: nothing returned
    def connectToDatabaseRO(self, database):

        # override connect to return a read-only DB connection, MUST use path starting at C drive (or any drive, X, Z, etc.)
        # more on this: https://github.com/sqlalchemy/sqlalchemy/issues/4863
        # this function returns a read only connection to the .db file at the secified location
        # getpass.getuser() fetches the current username
        # double backslashes are necessary because \U is a unicode escape, but \\U is not
        def connectSpecial(dbPath):
            print("Attempting connection to database:", database)
            ro_sql3_connection_uri = "file:" + str(database) + "?mode=ro"
            return sqlite3.connect(
                ro_sql3_connection_uri,
                uri=True,
            )

        # The first argument of create_engine is usually
        # dialect:pathtodatabase. Ultimately, pathtodatabase gets passed
        # through os.path.abspath(), so you're not allowed to add URI
        # ("?mode=ro") to the end of pathtodatabase.
        #
        # We get around this through the creator arg, to which we can pass an
        # arbitrary (function that returns an) connection, which will bipass
        # that abspath call. Note: you must still specify the dialect (sqlite)
        # in the first arg.
        self.engine = sqla.create_engine(
            "sqlite:///", creator=connectSpecial
        )  # create engine

        self.connection = self.engine.connect()  # connect engine with DB

        # Test RO mode. This SHOULD throw an exception.
        try:
            # although a write command, I think it does NOTHING
            bad_query = "PRAGMA user_version=0"
            self.connection.execute(bad_query)
        except sqla.exc.OperationalError:  # "attempt to write a readonly database"
            # RO mode working as expected
            pass
        else:
            tkinter.messagebox.showerror(
                title="Local Error",
                message=f"Local read-only mode failed.  Contact a member of the software team for help.",
            )  # show error message
            sys.exit()

        self.metadata = sqla.MetaData()  # create metadata
        self.initSQLTables()  # create important tables
        self.disableButtons() # disable all input except panel entry/submit

    # initialize important tables
    # parameters: no parameters
    # returns: nothing returned
    def initSQLTables(self):
        # straw_location (panels)
        self.panelsTable = sqla.Table(
            "straw_location", self.metadata, autoload=True, autoload_with=self.engine
        )
        # procedure (each different pro for each panel pro3 for mn100, pro6 for mn050, etc)
        self.proceduresTable = sqla.Table(
            "procedure", self.metadata, autoload=True, autoload_with=self.engine
        )

    # initialize lists of widgets for organization and easy access
    # parameters: no parameters
    # returns: nothing returned
    def initWidgetLists(self):
        # tuple of tuples of comment QListWidgets
        # each tuple in the tuple has the form: (<comment list>, <start/stop time list>)
        # pro number = index + 1
        self.comWidgetList = (
            (self.ui.pan1ComList, self.ui.pan1TimeList),
            (self.ui.pan2ComList, self.ui.pan2TimeList),
            (self.ui.pan3ComList, self.ui.pan3TimeList),
            (self.ui.pan4ComList, self.ui.pan4TimeList),
            (self.ui.pan5ComList, self.ui.pan5TimeList),
            (self.ui.pan6ComList, self.ui.pan6TimeList),
            (self.ui.pan7ComList, self.ui.pan7TimeList),
            (self.ui.pan8ComList, self.ui.pan8TimeList),
        )

        # tuple of tuples of procedure timing/session QLineEdit widgets
        # each tuple in the tuple has the form: (<start time>, <end time>, <total time>)
        # pro number = index + 1
        self.timeWidgetList = (
            (self.ui.pan1STimeLE, self.ui.pan1ETimeLE, self.ui.pan1TTimeLE),
            (self.ui.pan2STimeLE, self.ui.pan2ETimeLE, self.ui.pan2TTimeLE),
            (self.ui.pan3STimeLE, self.ui.pan3ETimeLE, self.ui.pan3TTimeLE),
            (self.ui.pan4STimeLE, self.ui.pan4ETimeLE, self.ui.pan4TTimeLE),
            (self.ui.pan5STimeLE, self.ui.pan5ETimeLE, self.ui.pan5TTimeLE),
            (self.ui.pan6STimeLE, self.ui.pan6ETimeLE, self.ui.pan6TTimeLE),
            (self.ui.pan7STimeLE, self.ui.pan7ETimeLE, self.ui.pan7TTimeLE),
            (self.ui.pan8STimeLE, self.ui.pan8ETimeLE, self.ui.pan8TTimeLE),
        )

        # tuple of QLineEdit widgets for parts
        self.partSetupWidgetList = (
            self.ui.partBASEPLATELE,
            self.ui.partMIRLE,
            self.ui.partBIRLE,
            self.ui.partPIRLALE,
            self.ui.partPIRLBLE,
            self.ui.partPIRLCLE,
            self.ui.partPIRRALE,
            self.ui.partPIRRBLE,
            self.ui.partPIRRCLE,
            self.ui.partALFLLE,
            self.ui.partALFRLE,
            self.ui.partPAASALE,
            self.ui.partPAASBLE,
            self.ui.partPAASCLE,
            self.ui.partFRAMELE,
            self.ui.partMIDDLERIB_1LE,
            self.ui.partMIDDLERIB_2LE,
            self.ui.partlpal_top_LE,
            self.ui.partlpal_top_LE
        )

    # link buttons with respective funcitons and panel line edit enter
    # parameters: no parameters
    # returns: nothing returned
    def initInputWidgets(self):
        # submit push button
        self.ui.submitPB.clicked.connect(self.submitClicked)
        self.ui.panelLE.returnPressed.connect(self.submitClicked)

        # finalQC leak test double click
        self.ui.leakTestsLW.itemDoubleClicked.connect(self.graphLeak)

        # heat buttons
        self.ui.heatExportButton.clicked.connect(
            lambda: self.exportData(
                f'Process_{self.ui.heatProBox.currentText()[8]}_Heat_Data',
                getattr(self.data,f'p{self.ui.heatProBox.currentText()[8]}HeatData'),
                ("Human timestamp", "Epoch timestamp", "PAAS A temp", "PAAS B/C temp")
            )
        )
        self.ui.heatExportButton_2.clicked.connect(
            lambda: self.exportData(
                f'Process_{self.ui.heatProBox_2.currentText()[8]}_Heat_Data',
                getattr(self.data,f'p{self.ui.heatProBox.currentText()[8]}HeatData'),
                ("Human timestamp", "Epoch timestamp", "PAAS A temp", "PAAS B/C temp")
            )
        )
        self.ui.heatPlotButton.clicked.connect(
            lambda: self.graphComboPressed(
                self.ui.heatProBox.currentText()
            )
        )
        self.ui.heatPlotButton_2.clicked.connect(
            lambda: self.graphComboPressed(
                self.ui.heatProBox_2.currentText()
            )
        )

        # hv buttons
        self.ui.hvExportButton.clicked.connect(
            lambda: self.exportData(
                f'{self.ui.hvProBox.currentText()}_HV_Data',
                getattr(
                    self.data,
                    f'hv1{self.ui.hvProBox.currentText()[12]}00P{self.ui.hvProBox.currentText()[8]}' if self.ui.hvProBox.currentText()[8] != 5 else "hvXXXXP5"
                ),
                ("Position", "Current (micro amps)", "Trip Status", "Side", "Epoch Timestamp")
            )
        )
        self.ui.hvExportButton_2.clicked.connect(
            lambda: self.exportData(
                f'{self.ui.hvProBox_2.currentText()}_HV_Data',
                getattr(
                    self.data,
                    f'hv1{self.ui.hvProBox_2.currentText()[12]}00P{self.ui.hvProBox_2.currentText()[8]}' if self.ui.hvProBox_2.currentText()[8] != 5 else "hvXXXXP5"
                ),
                ("Position", "Current (micro amps)", "Trip Status", "Side", "Epoch Timestamp")
            )
        )
        self.ui.hvPlotButton.clicked.connect(
            lambda: self.graphComboPressed(
                self.ui.hvProBox.currentText()
            )
        )
        self.ui.hvPlotButton_2.clicked.connect(
            lambda: self.graphComboPressed(
                self.ui.hvProBox_2.currentText()
            )
        )

        # tb buttons
        self.ui.tbExportButton.clicked.connect(
            lambda: self.exportData(
                f'{self.ui.tbProBox.currentText()}_TB_Data',
                getattr(self.data, f'p{self.ui.tbProBox.currentText()[8]}tbData'),
                ("Position","Length","Pulse Frequency","Pulse Width","Tension","Straw/Wire","Epoch Timestamp")
            )
        )
        self.ui.tbExportButton_2.clicked.connect(
            lambda: self.exportData(
                f'{self.ui.tbProBox_2.currentText()}_TB_Data',
                getattr(self.data, f'p{self.ui.tbProBox_2.currentText()[8]}tbData'),
                ("Position","Length","Pulse Frequency","Pulse Width","Tension","Straw/Wire","Epoch Timestamp")
            )
        )
        self.ui.tbPlotButton.clicked.connect(
            lambda: self.graphComboPressed(
                self.ui.tbProBox.currentText()
            )
        )
        self.ui.tbPlotButton_2.clicked.connect(
            lambda: self.graphComboPressed(
                self.ui.tbProBox_2.currentText()
            )
        )

        # straw buttons
        self.ui.strawExportButton.clicked.connect(
            lambda: self.exportData(
                "Straw_tension_data",
                self.data.strawData,
                ["Position", "Tension", "Epoch Timestamp", "Uncertainty"]
            )
        )
        self.ui.strawExportButton.clicked.connect(
            lambda: self.exportData(
                "Straw_tension_data",
                self.data.strawData,
                ["Position", "Tension", "Epoch Timestamp", "Uncertainty"]
            )
        )
        
        self.ui.strawPlotButton.clicked.connect(
            lambda: self.graphSimple(
                self.data.strawData,
                "Tension (g)"
            )
        )
        self.ui.strawPlotButton_2.clicked.connect(
            lambda: self.graphSimple(
                self.data.strawData,
                "Tension (g)"
            )
        )
    

        # wire buttons
        self.ui.wireExportButton.clicked.connect(
            lambda: self.exportData(
                "Wire_tension_data",
                self.data.wireData,
                ["Position", "Tension", "Epoch Timestamp"]
            )
        )
        self.ui.wireExportButton.clicked.connect(
            lambda: self.exportData(
                "Wire_tension_data",
                self.data.wireData,
                ["Position", "Tension", "Epoch Timestamp"]
            )
        )
        self.ui.wirePlotButton.clicked.connect(
            lambda: self.graphSimple(
                self.data.wireData,
                "Tension (g)"
            )
        )
        self.ui.wirePlotButton_2.clicked.connect(
            lambda: self.graphSimple(
                self.data.wireData,
                "Tension (g)"
            )
        )

        # heat combo boxes
        self.ui.heatProBox.currentIndexChanged.connect(
            lambda: self.comboBoxChanged(self.ui.heatProBox.currentText())
        )
        self.ui.heatProBox_2.currentIndexChanged.connect(
            lambda: self.comboBoxChanged(self.ui.heatProBox_2.currentText())
        )

        # hv combo boxes
        self.ui.hvProBox.currentIndexChanged.connect(
            lambda: self.comboBoxChanged(self.ui.hvProBox.currentText())
        )
        self.ui.hvProBox_2.currentIndexChanged.connect(
            lambda: self.comboBoxChanged(self.ui.hvProBox_2.currentText())
        )

        # tb combo boxes
        self.ui.tbProBox.currentIndexChanged.connect(
            lambda: self.comboBoxChanged(self.ui.tbProBox.currentText())
        )
        self.ui.tbProBox_2.currentIndexChanged.connect(
            lambda: self.comboBoxChanged(self.ui.tbProBox_2.currentText())
        )

    # link menu actions (settings in upper left) with corrsponding funcitons
    # parameters: no parameters
    # returns: nothing returned
    def initMenuActions(self):
        self.ui.actionDefaultColor.triggered.connect(
            lambda: self.changeColor(0,0,default=True)
        )
        self.ui.actionDarkColor.triggered.connect(
            lambda: self.changeColor((25,25,25),(200,200,200))
        )
        self.ui.actionCyberpunkColor.triggered.connect(
            lambda: self.changeColor((25,25,25),(0,255,159),(214,0,255),(214,0,255))
        )
        self.ui.actionGopher_PrideColor.triggered.connect(
            lambda: self.changeColor((122, 0, 25), (255, 204, 51))
        )
        self.ui.actionForestColor.triggered.connect(
            lambda: self.changeColor((3,37,2), (84,34,34), (84,34,34), (130,105,69))
        )
        self.ui.actionPatrioticColor.triggered.connect(
            lambda: self.changeColor((255,255,255), (10,49,97),(179,25,66), (179,25,66))
        )
        self.ui.actionOceanColor.triggered.connect(
            lambda: self.changeColor((29,162,216),(222,243,246))
        )
        self.ui.actionVolcanicColor.triggered.connect(
            lambda: self.changeColor((10,10,10),(255,87,51), (255,215,0))
        )

        #self.ui.actionHide_False_Data.toggled.connect(self.submitClicked)

    # utility, get any widget by name
    # parameters: widgetName, name of the desired widget as a string
    # returns: requested widget, will always be a child of self.ui
    def getWid(self, widgetName,):
        return getattr(self.ui, widgetName)

    # disable plot/export buttons
    # parameters: no parameters
    # returns: nothing returned
    def disableButtons(self):
        # disables all the buttons and combo boxes
        # useful for avoiding out of bounds exceptions when no data is present in lists
        self.ui.wireExportButton.setDisabled(True)
        self.ui.wirePlotButton.setDisabled(True)
        self.ui.strawExportButton.setDisabled(True)
        self.ui.strawPlotButton.setDisabled(True)
        self.ui.hvExportButton.setDisabled(True)
        self.ui.hvPlotButton.setDisabled(True)
        self.ui.heatExportButton.setDisabled(True)
        self.ui.heatPlotButton.setDisabled(True)
        self.ui.heatProBox.setDisabled(True)
        self.ui.hvProBox.setDisabled(True)
        self.ui.wireExportButton_2.setDisabled(True)
        self.ui.wirePlotButton_2.setDisabled(True)
        self.ui.strawExportButton_2.setDisabled(True)
        self.ui.strawPlotButton_2.setDisabled(True)
        self.ui.hvExportButton_2.setDisabled(True)
        self.ui.hvPlotButton_2.setDisabled(True)
        self.ui.heatExportButton_2.setDisabled(True)
        self.ui.heatPlotButton_2.setDisabled(True)
        self.ui.heatProBox_2.setDisabled(True)
        self.ui.hvProBox_2.setDisabled(True)
        self.ui.tbExportButton.setDisabled(True)
        self.ui.tbExportButton_2.setDisabled(True)
        self.ui.tbPlotButton.setDisabled(True)
        self.ui.tbPlotButton_2.setDisabled(True)
        self.ui.tbProBox.setDisabled(True)
        self.ui.tbProBox_2.setDisabled(True)

    # remove data from all widgets
    # parameters: no parameters
    # returns: nothing returned
    def clearWidgets(self):
        # clear measurement widgets
        # widget type: QListWidget
        self.ui.strawListWidget.clear()
        self.ui.wireListWidget.clear()
        self.ui.hvListWidget.clear()
        self.ui.heatListWidget.clear()
        self.ui.strawListWidget_2.clear()
        self.ui.wireListWidget_2.clear()
        self.ui.hvListWidget_2.clear()
        self.ui.heatListWidget_2.clear()

        # clear comment list widgets
        # widget type: QListWidget
        for toop in self.comWidgetList:
            for widget in toop:
                widget.clear()

        # clear timing widgets
        # widget type: QLineEdit
        for toop in self.timeWidgetList:
            for widget in toop:
                widget.setText("")

        # clear pro 8 wdgets
        self.ui.leaksLW.clear()
        self.ui.badStrawsLW.clear()
        self.ui.badWiresLW.clear()
        self.ui.left_coverLE.setText("")
        self.ui.left_ringLE.setText("")
        self.ui.right_coverLE.setText("")
        self.ui.right_ringLE.setText("")
        self.ui.center_coverLE.setText("")
        self.ui.center_ringLE.setText("")

    # submitClicked does this stuff:
    # - checks to see if the text in self.ui.panelLE is a panel with data
    # - if not it shows an error and returns early
    # - removes all data from widgets and self.data
    # - calls findPanelData to get data from DB
    # - if findPanelData returns false it shows an error and returns early
    # - calls displayPanelData to put data on the gui
    # parameters: no parameters
    # returns: nothing returned
    def submitClicked(self):
        # get new human readable panel id, if a bad id was entered
        # show an error and return
        try:
            # any non-numerical characters in int() will
            # raise an invalid literal exception
            self.data.humanID = int(self.ui.panelLE.text())
        except:
            tkinter.messagebox.showerror(
                title="Error",
                message=f"MN{(self.ui.panelLE.text()).zfill(3)} is not a valid panel ID.",
            )
            return
        # change label at top of gui
        self.ui.label_2.setText(f"MN{str(self.data.humanID).zfill(3)}")

        # clear self.data, but leave ids intact
        self.data.clearPanel(dbOnly=True)
        # clear all widgets except entry widget
        self.clearWidgets()

        # call self.findPanelData to attempt to get data
        # if no data is found show an error and return early
        if not self.findPanelData():
            tkinter.messagebox.showerror(
                title="Error",
                message=f"No data was found for MN{(self.ui.panelLE.text()).zfill(3)}.",
            )
            return

        # put data on the gui
        self.displayPanelData()

        self.ui.hvProBox.setEnabled(True)
        self.ui.hvProBox_2.setEnabled(True)
        self.ui.heatProBox.setEnabled(True)
        self.ui.heatProBox_2.setEnabled(True)
        self.ui.tbProBox.setEnabled(True)
        self.ui.tbProBox_2.setEnabled(True)

    # parameters: ???
    # returns: nothing returned
    def graphComboPressed(self,text):
        # local function to call function to graph hv
        def graphHV(self,dataType):
            try:
                self.graphSimple(
                    dataType,
                    "Current (μA)"
                )
                return 0
            except:
                return 1
        # local funciton to call function to graph heat
        def graphHeat(self,pro):
            try:
                self.graphSpecificHeat(pro)
                return 0
            except:
                return 1

        # local funciton to graph tubriculosis
        def graphTB(self, data):
            ##  initialize subplots

            fig, (ax1, ax2) = plt.subplots(2,1)
            ax1.set_ylabel("straw tension (g)", fontweight = "bold")
            ax1.yaxis.label.set_color("b")

            ax2.set_ylabel("wire tension (g)", fontweight = "bold")
            ax2.yaxis.label.set_color("r")

            ##   define datasets
            straw_x_data = [x[0] for x in data if x[5] == "straw"]
            straw_y_data = [x[4] for x in data if x[5] == "straw"]
            straw_order = [x[7] for x in data if x[5] == "straw"]
            
            wire_x_data = [x[0] for x in data if x[5] == "wire"]
            wire_y_data = [x[4] for x in data if x[5] == "wire"]
            wire_order = [x[7] for x in data if x[5] == "wire"]

            ##  define plotting function
            def plot(axis, x_data, y_data, label, order):
                for i in range(len(x_data)):
                    colors = ['r','g','b','k']
                    if y_data[i] is not None: # determine which order measurement it is and ensure proper color
                        try:
                            if order[i] == 0:
                                axis.plot(x_data[i],y_data[i],marker='o',markersize=4,color=colors[order[i]])
                            elif order[i] <= 3:
                                axis.plot(x_data[i],y_data[i],marker='o',markersize=3,color=colors[order[i]])
                            else:
                                axis.plot(x_data[i],y_data[i],marker='o',markersize=3,color=colors[3])
                        except:
                            pass
                
                # add legend
                dots = [
                    Line2D([0], [0], marker='o', color='r', label='Nth Measurement', markersize=3),
                    Line2D([0], [0], marker='o', color='g'),
                    Line2D([0], [0], marker='o', color='b'),
                    Line2D([0], [0], marker='o', color='k'),
                ]
                axis.legend(dots,['Nth Measurement', 'Nth-1 Measurement', 'Nth-2 Measurement', 'Earlier'],fontsize = 'x-small')
                
                
                # set graph limits, first get list of y values without nones
                y_WOnone = []
                for i in y_data:
                    if i != None:
                        y_WOnone.append(i)
                if len(y_WOnone) == 0:
                    y_WOnone = [0]
                    
                # finds and sets ideal x and y bounds for the graph
                lower_bound = min(y_WOnone)-((max(y_WOnone) - min(y_WOnone)) * 0.2)
                upper_bound = max(y_WOnone)+((max(y_WOnone) - min(y_WOnone)) * 0.2)
                if lower_bound != upper_bound:
                    axis.set_ylim([lower_bound,upper_bound])
                axis.set_xlim([-5,100])
                
                for i in range(len(y_data)):  # go through x and y values to label all points
                    if y_data[i] is not None and order[i]==0:
                        axis.text(x_data[i],y_data[i],str(x_data[i]),fontsize='xx-small')

            # plot the data
            plot(ax1, straw_x_data, straw_y_data, "straw", straw_order)
            plot(ax2, wire_x_data, wire_y_data, "wire", wire_order)

            plt.show()

        callDict = {
            "Process 3, 1100V"  : (lambda: graphHV(self, self.data.hv1100P3)),
            "Process 3, 1500V"  : (lambda: graphHV(self, self.data.hv1500P3)),
            "Process 4, 1500V"  : (lambda: graphHV(self, self.data.hv1500P4)),
            "Process 5"         : (lambda: graphHV(self, self.data.hvXXXXP5)),
            "Process 6, 1500V"  : (lambda: graphHV(self, self.data.hv1500P6)),
            "Process 1, Inner Rings": (lambda: graphHeat(self, 1)),
            "Process 2, Straws"     : (lambda: graphHeat(self, 2)),
            "Process 6, Manifold"   : (lambda: graphHeat(self, 6)),
            "Process 3"             : (lambda: graphTB(self, self.data.p3tbData)),
            "Process 6"             : (lambda: graphTB(self, self.data.p6tbData)),
            "Select"                : (lambda: 0)
        }
        boool = callDict[text]()
        if boool:
            tkinter.messagebox.showerror(
                title="Error",
                message=f'An error was encountered while attempting to graph {text}.',
            )

    # called when a combo box index changes, calls functions to update relevant data
    # parameters:   type, a string either "hv" or "heat"
    #               index, the new index of the comboBox
    # returns: nothing returned
    def comboBoxChanged(self, text):
        callDict = {
            "Process 3, 1100V"  : (lambda: self.updateCombo(3,1100)),
            "Process 3, 1500V"  : (lambda: self.updateCombo(3,1500)),
            "Process 4, 1500V"  : (lambda: self.updateCombo(4,1500)),
            "Process 5"         : (lambda: self.updateCombo(5,1)),
            "Process 6, 1500V"  : (lambda: self.updateCombo(6,1500)),
            "Process 1, Inner Rings": (lambda: self.updateCombo(1,0)),
            "Process 2, Straws"     : (lambda: self.updateCombo(2,0)),
            "Process 6, Manifold"   : (lambda: self.updateCombo(6,0)),
            "Process 3"         : (lambda: self.updateCombo(3,-1)),
            "Process 6"         : (lambda: self.updateCombo(6,-1)),
            "Select"            : (lambda: 0)
        }
        boool = callDict[text]()
        if boool:
            tkinter.messagebox.showerror(
                title="Error",
                message=f'An error was encountered while fetching data for {text}.',
            )
            return

    # called in comboBoxChanged.  Does the heavy lifting when it comes to showing the
    # correct data in the list widgets and graphs.
    # parameters:   pro, int representing the process being shown
    #               volts, int representing the voltage for hv, if updating heat volts = 0, tb volts = -1
    # returns: 0 if success, 1 if failure
    def updateCombo(self, pro, volts):
        if volts == 0:
            # update heat
            self.displaySpecificHeat(
                pro,
                self.ui.heatListWidget,
                (self.ui.heatExportButton, self.ui.heatPlotButton)
            )
            self.displaySpecificHeat(
                pro,
                self.ui.heatListWidget_2,
                (self.ui.heatExportButton_2, self.ui.heatPlotButton_2),
                self.ui.heatGraphLayout
            )
            return 0
        elif volts == -1:
            self.displayOnLists(
                pro,
                getattr(self.data,f'p{pro}tbData'),
                [("Position",18),("Length",13),("Pulse Freq",13),("Pulse Wid",13),("Tension",13),("S/W",0),("timestamp",-1)],
                [self.ui.tbListWidget, self.ui.tbListWidget_2],
                [self.ui.tbExportButton, self.ui.tbExportButton_2, self.ui.tbPlotButton, self.ui.tbPlotButton_2]
            )
            return 0
        else:
            if volts < 1000:
                volts = "XXXX"
            # update hv
            self.displayOnLists(
                pro,
                getattr(self.data,f'hv{volts}P{pro}'),
                [("Position",18),("Current",13),("Trip Status",0)],
                (self.ui.hvListWidget,self.ui.hvListWidget_2),
                (
                    self.ui.hvExportButton,self.ui.hvExportButton_2,
                    self.ui.hvPlotButton,self.ui.hvPlotButton_2
                )
            )
            self.displayOnGraph(
                getattr(self.data,f'hv{volts}P{pro}'),
                "Position",0,
                "Current (μA)",1,
                self.ui.hvGraphLayout,
                microScale=True
            )
            return 0

    # used to change the color of the gui.  Adapted from the function in pangui
    # parameters:   background_color, int tuple that represents a color via RGB value
    #               text_color, int tuple that represents a color via RGB value
    #               third_color, optional int tuple that represents a color via RGB value
    #               fourth_color, optional int tuple that represents a color via RGB value
    #               default, bool that's true if resetting to default black on white colors
    # returns: nothing
    def changeColor(self, background_color, text_color, third_color=False, fourth_color=False, default=False, third_back=False):
        if default:
            self.stylesheet = ""
            self.setStyleSheet(self.stylesheet)
            return

        tuple_min = lambda t: tuple(min(x, 255) for x in t)
        tuple_max = lambda t: tuple(max(x, 0) for x in t)
        tuple_add = lambda t, i: tuple((x + i) for x in t)
        invert = lambda t: tuple(255 - x for x in t)

        lighter = tuple_min(tuple_add(background_color, 20))
        darker = tuple_max(tuple_add(background_color, -11))

        text_color_invert = invert(text_color)
        background_color_invert = invert(background_color)

        self.stylesheet = (
            "QMainWindow, QDialog, QMessageBox, QMenuBar { background-color: rgb"
            + f"{background_color}; color: rgb{text_color};"
            + " }\n"
            "QWidget#summaryTab { background-color: rgb"
            + f"{background_color}; color: rgb{text_color};"
            + " }\n"
            "QLineEdit, QPlainTextEdit, QTextEdit, QScrollArea, QListWidget { "
            + f"color: rgb{text_color if not fourth_color else fourth_color}; background-color: rgb{lighter if not third_back else third_color};"
            + " }\n"
            "QLabel { " + f"color: rgb{text_color};" + " }\n"
            "QGroupBox, QTabWidget, QTabBar, QScrollBar { "
            + f"color: rgb{text_color}; background-color: rgb{darker};"
            + " }\n"
            "QPushButton { "
            + f"color: rgb{text_color if not fourth_color else fourth_color}; background-color: rgb{darker if not third_back else third_color};"
            + " }\n"
            "QCheckBox { color: "
            + f"rgb{text_color}"
            + "; "
            + f"background-color: rgb{darker}"
            + "; }\n"
            "QLCDNumber { color: white; }\n"
            "QComboBox, QComboBox QAbstractItemView { "
            + f"color: rgb{text_color if not third_color else third_color}; background-color: rgb{background_color}; selection-color: rgb{background_color_invert}; selection-background-color: rgb{text_color_invert};"
            + " }"
            f'QStatusBar {"{"}color: rgb{text_color}{"}"}'
        )

        self.setStyleSheet(self.stylesheet)

    # ███████╗██╗███╗   ██╗██████╗     ██████╗  █████╗ ████████╗ █████╗
    # ██╔════╝██║████╗  ██║██╔══██╗    ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗
    # █████╗  ██║██╔██╗ ██║██║  ██║    ██║  ██║███████║   ██║   ███████║
    # ██╔══╝  ██║██║╚██╗██║██║  ██║    ██║  ██║██╔══██║   ██║   ██╔══██║
    # ██║     ██║██║ ╚████║██████╔╝    ██████╔╝██║  ██║   ██║   ██║  ██║
    # ╚═╝     ╚═╝╚═╝  ╚═══╝╚═════╝     ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝

    # findPanelData fetches data from the DB and puts it into self.data
    # it does NOT put data into the widgets, displayPanelData does that
    # parameters: no parameters
    # returns: bool, true if any data was found for the panel
    def findPanelData(self):

        # find new database ID
        self.data.dbID = self.findPanelDatabaseID()

        # if no database id found return False
        # without a database id, nothing else can be found
        if self.data.dbID == -1:
            return False

        # call findProcedures to get an id for each procedure
        # it will return true if at least one procedure is found
        # if it's false then return False
        # if there are no procedures yet, the panel doesn't have any data
        if not self.findProcedures():
            return False


        # make a bool to represent if any data a user would like
        # to see has been found (I doubt they care about database ids)
        # at this point no useful data has been found
        # if any of the following "find" funciton calls return true
        # then hasData will be true by the end
        hasData = False
        # funcRet stores return from "find" functions
        funcRet = False

        # find pro timing (events like start, pause, etc.)
        funcRet = self.findProTiming()
        # find comments
        funcRet = self.findComments()
        hasData = hasData or funcRet
        # find parts
        funcRet = self.findParts()
        hasData = hasData or funcRet
        # find straw tension data
        funcRet = self.findStraws()
        hasData = hasData or funcRet
        # find wire tension data
        funcRet = self.findWires()
        hasData = hasData or funcRet
        # find hv data
        funcRetI = self.findSpecificHV(3,1100)
        funcRetII = self.findSpecificHV(3,1500)
        funcRetIII = self.findSpecificHV(4,1500)
        funcRetIV = self.findSpecificHV(6,1500)
        hasData = hasData or funcRetI or funcRetII or funcRetIII or funcRetIV
        # find heat data
        funcRetI = self.findSpecificHeat(1)
        funcRetII = self.findSpecificHeat(2)
        funcRetIII = self.findSpecificHeat(6)
        hasData = hasData or funcRetI or funcRetII or funcRetIII
        # find heat data
        funcRetI = self.findSpecificTB(3)
        funcRetII = self.findSpecificTB(6)
        hasData = hasData or funcRetI or funcRetII
        # find pro 8 data
        funcRet = self.findPro8()
        hasData = hasData or funcRet

        return hasData

    # takes in heatdata, and then analyzes it, returning pertinent values to the dbviewer for display
    # parameters: self, heatdata
    # returns: paasATemps, paasBTemps, time_begin_above_50_paasA, time_end_above_50_paasA, time_begin_above_50_paasB, time_end_above_50_paasB, elapsed_time_above_50_paasA, elapsed_time_above_50_paasB
    def process_heatdata(self, heatdata):
        # initialize assorted variables
        paasATemps=[]
        paasBTemps=[]
        time_begin_above_50_paasA=None
        time_end_above_50_paasA=None
        time_begin_above_50_paasB=None
        time_end_above_50_paasB=None
        
        elapsed_time_above_50_paasA=None
        elapsed_time_above_50_paasB=None
        
        # iterate through all heat datapoints
        for datapoint in heatdata:
            # only analyze datapoint if it has the proper number of values
            if len(datapoint) == 5:
                temp_paasA=datapoint[2]
                temp_paasB=datapoint[3]
                
                # ensure that the temperature points are reasonable
                if 0 < temp_paasA < 100 and 0 < temp_paasB < 100:
                    
                    # put datapoints into individual temporary variables
                    temp_paasA=datapoint[2]
                    temp_paasB=datapoint[3]
                    timestamp=datapoint[1]
                    
                    # append temperature values to lists
                    paasATemps.append(temp_paasA)
                    paasBTemps.append(temp_paasB)
                    
                    # if the begin time above 50 C for paas A hasn't been acquired yet, acquire it
                    if time_begin_above_50_paasA is None and temp_paasA >=50:
                        time_begin_above_50_paasA = timestamp
                    
                    # if the begin time above 50 C for paas B hasn't been acquired yet, acquire it
                    if time_begin_above_50_paasB is None and temp_paasB >=50:
                        time_begin_above_50_paasB = timestamp
                    
                    # if proper, acquire last time above 50 C for paas A
                    if time_begin_above_50_paasA is not None and temp_paasA < 50:
                        time_end_above_50_paasA = timestamp

                    # if proper, acquire last time above 50 C for paas B
                    if time_begin_above_50_paasB is not None and temp_paasB < 50:
                        time_end_above_50_paasB = timestamp

        # acquire the elapsed time for paas A above 50 C
        if time_begin_above_50_paasA is not None:
            if time_end_above_50_paasA is not None:
                elapsed_time_above_50_paasA = time_end_above_50_paasA - time_begin_above_50_paasA
                elapsed_time_above_50_paasA = round(elapsed_time_above_50_paasA / 3600, 2)
            else:
                elapsed_time_above_50_paasA = processed_heatdata[-1]['timestamp'] - time_begin_above_50_paasA
        
        # acquire the elapsed time for paas B above 50 C
        if time_begin_above_50_paasB is not None:
            if time_end_above_50_paasB is not None:
                elapsed_time_above_50_paasB = time_end_above_50_paasB - time_begin_above_50_paasB
                elapsed_time_above_50_paasB = round(elapsed_time_above_50_paasB / 3600, 2)
            else:
                elapsed_time_above_50_paasB = processed_heatdata[-1]['timestamp'] - time_begin_above_50_paasB
        
        # convert assorted times to human friendly format for display in dbviewer
        if time_begin_above_50_paasA is not None:
            time_begin_above_50_paasA = datetime.fromtimestamp(time_begin_above_50_paasA)
        if time_end_above_50_paasA is not None:
            time_end_above_50_paasA = datetime.fromtimestamp(time_end_above_50_paasA)
        if time_begin_above_50_paasB is not None:
            time_begin_above_50_paasB = datetime.fromtimestamp(time_begin_above_50_paasB)
        if time_end_above_50_paasB is not None:
            time_end_above_50_paasB = datetime.fromtimestamp(time_end_above_50_paasB)
        
        # return all pertinent values
        return paasATemps, paasBTemps, time_begin_above_50_paasA, time_end_above_50_paasA, time_begin_above_50_paasB, time_end_above_50_paasB, elapsed_time_above_50_paasA, elapsed_time_above_50_paasB
                 
    # finds and returns the database id for the panel in question
    # the database id is a really long int, usually 16 characters
    # parameters: no parameters
    # returns: int, the database id or -1 to indicate failure
    def findPanelDatabaseID(self):
        panelIDQuery = (
            # select panel ids
            sqla.select([self.panelsTable.columns.id])
            # where number = user input panel number
            .where(self.panelsTable.columns.number == self.data.humanID)
            # and where location type = MN (we don't want LPALs)
            .where(self.panelsTable.columns.location_type == "MN")
        )

        # make proxy
        resultProxy = self.connection.execute(panelIDQuery)
        # fetch from proxy, which gives [(<PANEL ID>,)]
        resultSet = resultProxy.fetchall()

        # if nothing returned,
        if len(resultSet) == 0:
            # the panel doesn't exist!
            return -1
        else:
            # since resultSet is a list of tuples, add [0][0] to get an int
            return resultSet[0][0]

    # finds procedure ids and stores them in the self.data.proIDs dict
    # parameters: no parameters
    # returns: bool, true if at least one procedure found, false otherwise
    def findProcedures(self):
        proceduresQuery = sqla.select(
            # select pro ids and stations
            [
                self.proceduresTable.columns.id,
                self.proceduresTable.columns.station,
                self.proceduresTable.columns.timestamp,
            ]
            # where straw_location = db panel ID
        ).where(self.proceduresTable.columns.straw_location == self.data.dbID)

        # make proxy
        resultProxy = self.connection.execute(proceduresQuery)

        # fetch from proxy, gives list of tuples: (<PRO ID>, <STATION>)
        panelProcedures = resultProxy.fetchall()

        # go through results from procedures query
        for toop in panelProcedures:
            self.data.proIDs[toop[1]] = toop[0]
            # assign procedure ID to the corresponding station (above line)
            # self.data.proIDs is a dictionary with the name of each station as keys

        return not ([toop[0] for toop in panelProcedures] is None)

    # finds procedure timing data and stores it in the self.data.timingLists dict
    # parameters: no parameters
    # returns: bool, true if any data found, false otherwise
    def findProTiming(self):
        # make table for procedure_timestamp
        timing = sqla.Table(
            "procedure_timestamp", self.metadata, autoload=True, autoload_with=self.engine,
        )

        # function to get specific process data
        # it will be used once for each pro
        def proSpecificQuery(self, pro):
            # don't waste any time on a procudure that doesn't exist yet
            if self.data.proIDs[pro] == -1:
                return tuple("f")

            timingQuery = sqla.select(
                [
                    timing.columns.procedure,
                    timing.columns.event,
                    timing.columns.timestamp,
                ]
            ).where(
                # where procedure = database id for pro parameter
                # ex. 5 gets passed in, procedure = this panel's pro 5 id
                timing.columns.procedure
                == self.data.proIDs[pro]
            )

            # make proxy, get data
            resultProxy = self.connection.execute(timingQuery)
            resultSet = resultProxy.fetchall()

            # resultSet = a list of tuples of the form:
            #   (<procedure ID>, <event>, <timestamp>)

            # return results
            # would it be more efficient to sort data inside this function?
            # that way the potentially large list stays in one frame on the stack?
            # or is this function's frame inside findProTiming's frame so it doesn't matter?
            if resultSet is None:
                return tuple("f")
            else:
                return resultSet

        retList = []

        # for each procedure one to seven...
        for key in self.data.proIDs:
            # for each tuple (time event for procedure)...
            for toop in proSpecificQuery(self, key):
                # add the event to the list associated with this procedure
                # only add the first and second index, we don't need the procedure now
                # (did we ever really need the procedure?  is it necessary for the query?)
                if toop[0] != "f":
                    retList.append(toop)
                    self.data.timingLists[key].append([toop[1], toop[2]])

            # sort by timestamp in ascending order
            self.data.timingLists[key] = sorted(
                self.data.timingLists[key], key=lambda x: x[1]
            )

        return retList is not None

    # finds comments for each procedure and stores it in self.data.comLists
    # parameters: no parameters
    # returns: bool, true if any data found, false otherwise
    def findComments(self):
        # make table
        comments = sqla.Table(
            "comment", self.metadata, autoload=True, autoload_with=self.engine
        )
        # make query
        comQuery = sqla.select(
            [
                self.panelsTable.columns.number,
                self.proceduresTable.columns.station,
                comments.columns.text,
                comments.columns.timestamp,
            ]
        ).where(self.panelsTable.columns.number == self.data.humanID)
        comQuery = comQuery.select_from(
            self.panelsTable.join(
                self.proceduresTable,
                self.panelsTable.columns.id == self.proceduresTable.columns.straw_location,
            ).join(
                comments,
                self.proceduresTable.columns.id == comments.columns.procedure
            )
        )
        resultProxy = self.connection.execute(comQuery)  # execute query
        resultSet = resultProxy.fetchall()  # get all results as list of tuples
        # tuples have the form: (<panel Number>, <process number>, <comment text>, <comment timestamp in epoch time>)
        # now lets plug the comments into the lists!
        for toop in resultSet:
            # append comment to appropriate list in comLists dictionary
            self.data.comLists[toop[1]].append(
                (toop[2],toop[3])
            )
        # return bool, true if any comments found
        hasData = False
        for key in self.data.comLists:
            if len(self.data.comLists[key]) > 0:
                hasData = True
        return hasData

    # finds parts for the panel and stores the data in self.data.parts
    # calls self.findLPALs, since LPALs are parts
    # parameters: no parameters
    # returns: bool, true if any data found, false otherwise
    def findParts(self):
        # panel_part_use    --> panelPartUsage
        panelPartUsage = sqla.Table(
            "panel_part_use", self.metadata, autoload=True, autoload_with=self.engine
        )
        # panel_part        --> panelPartActual
        panelPartActual = sqla.Table(
            "panel_part", self.metadata, autoload=True, autoload_with=self.engine
        )

        partsQuery = sqla.select(
            [  # why are the first three in here??
                self.panelsTable.columns.number,  # panel number
                panelPartUsage.columns.panel_part,  # panel part ID
                panelPartUsage.columns.panel,  # panel straw_location ID
                panelPartUsage.columns.left_right,  # ALF L/R
                panelPartActual.columns.type,  # type of part (MIR, PIR, ALF, etc.)
                panelPartActual.columns.number,  # part number
                panelPartActual.columns.left_right,  # PIR l/R
                panelPartActual.columns.letter,  # PIR A/B/C, PAAS A/B/C
            ]
        ).where(self.panelsTable.columns.number == self.data.humanID)

        partsQuery = partsQuery.select_from(
            self.panelsTable.join(
                panelPartUsage,
                self.panelsTable.columns.id == panelPartUsage.columns.panel,
            ).join(
                panelPartActual,
                panelPartUsage.columns.panel_part == panelPartActual.columns.id,
            )
        )

        resultProxy = self.connection.execute(partsQuery)
        resultSet = resultProxy.fetchall()

        retList = []

        # takes a tuple (from the query for part data), filters out the junk, saves to self.data.parts
        # and returns a part tuple minus the junk
        # parameter part:
            #   0           1           2           3           4                       5           6               7
            # (<panelnum>, <part id>, <straw_loc>, <ALF L/R>, <type (MIR, ALF, etc)>, <part num>, <PIR l/R>, <PIR,PAAS A/B/C>)
        def sortAndRefinePart(self, part):
            # retPart:
            #   0           1                       2           3           4
            # (<ALF L/R>, <type (MIR, ALF, etc)>, <part num>, <PIR l/R>, <PIR,PAAS A/B/C>)
            retPart = ["", "", "", "", ""]
            for i in range(3, 8):
                if part[i] is not None:
                    retPart[i - 3] = part[i]
            # build a string to function as a dict key (for self.data.parts dict)
            # some of the pieces will be "", some will be a string like "PIR", "L", "A", etc.
            self.data.parts[f"{retPart[1]}{retPart[3]}{retPart[4]}{retPart[0]}"]=retPart[2]
            return retPart


        # (<panelnum>, <part id>, <straw_loc>, <ALF L/R>, <type (MIR, ALF, etc)>, <part num>, <PIR l/R>, PIR,PAAS A/B/C>)
        for partTuple in resultSet:
            sortAndRefinePart(self, partTuple)
            retList.append(partTuple)

        # lpals are slightly different, so they have their own function
        self.findLPALs()
        self.findSpool()

        # return bool
        return (len(retList) > 0)

    # finds LPALs and stores them in self.data.parts, called by findParts
    # LPALs have their own find function because they are different than the other parts
    # parameters: no parameters
    # returns: nothing returned
    def findLPALs(self):
        # LPALs are found differently than regular parts
        # straw_location(MN type) --> procedures(this panel) -->
        #   pan1_procedure(this panels procedure) --> straw_location(LPAL type)

        # procedure_details_pan1        --> pan1Pros
        pan1Pros = sqla.Table(
            "procedure_details_pan1", self.metadata, autoload=True, autoload_with=self.engine
        )

        lpal1Query = sqla.select([self.panelsTable.columns.number]
        ).select_from(
            pan1Pros.join(
                self.panelsTable,
                sqla.or_(
                    pan1Pros.columns.lpal_top == self.panelsTable.columns.id,
                    pan1Pros.columns.lpal_bot == self.panelsTable.columns.id
                )
            )
        ).where(pan1Pros.columns.procedure == self.data.proIDs["pan1"])
        resultProxy = self.connection.execute(lpal1Query)
        resultSet = resultProxy.fetchall()
        # if we have stuff for pro 1, set that as the lpal data and return
        if len(resultSet ) > 0:
            if resultSet[0][0] is not None:
                self.data.parts["lpal_top_"] = resultSet[0][0]
            if len(resultSet) > 1:
                if resultSet[1][0] is not None:
                    self.data.parts["lpal_bot_"] = resultSet[1][0]
        # if both LPALs have been found, return early
        if self.data.parts["lpal_bot_"] != [] and self.data.parts["lpal_top_"] != []:
            return

        # otherwise repeat for pro 2
        # procedure_details_pan2        --> pan2Pros
        pan2Pros = sqla.Table(
            "procedure_details_pan2", self.metadata, autoload=True, autoload_with=self.engine
        )

        lpal2Query = sqla.select([self.panelsTable.columns.number]
        ).select_from(
            pan2Pros.join(
                self.panelsTable,
                sqla.or_(
                    pan2Pros.columns.lpal_top == self.panelsTable.columns.id,
                    pan2Pros.columns.lpal_bot == self.panelsTable.columns.id
                )
            )
        ).where(pan2Pros.columns.procedure == self.data.proIDs["pan2"])

        resultProxy = self.connection.execute(lpal2Query)
        resultSet = resultProxy.fetchall()

        if len(resultSet ) > 0:
            if resultSet[0][0] is not None and self.data.parts["lpal_top_"] == []:
                self.data.parts["lpal_top_"] = resultSet[0][0]
            if resultSet[1][0] is not None and self.data.parts["lpal_bot_"] == []:
                self.data.parts["lpal_bot_"] = resultSet[1][0]

    # finds wire spool id and weights and stores them in self.data.parts, called by findParts
    # wire spool stuff has its own find function because it's different than the other parts
    # parameters: no parameters
    # returns: nothing returned
    def findSpool(self):
        # check if pro 3 exists
        if self.data.proIDs["pan3"] == -1:
            return False

        pan3Pros = sqla.Table(
            "procedure_details_pan3", self.metadata, autoload=True, autoload_with=self.engine
        )

        spoolQuery = sqla.select([
            pan3Pros.columns.wire_spool,
            pan3Pros.columns.wire_weight_initial,
            pan3Pros.columns.wire_weight_final
            ]
        ).where(pan3Pros.columns.procedure == self.data.proIDs["pan3"])

        resultProxy = self.connection.execute(spoolQuery)
        resultSet = resultProxy.fetchall()

        if len(resultSet) != 1:
            return

        if resultSet[0][0] is not None:
            self.data.parts["wire_spool"] = resultSet[0][0]
        if resultSet[0][1] is not None:
            self.data.parts["wire_weight_initial"] = resultSet[0][1]
        if resultSet[0][2] is not None:
            self.data.parts["wire_weight_final"] = resultSet[0][2]

    # finds straw tension data and stores it in self.data.strawData
    # parameters: no parameters
    # returns: bool, true if any data found, false otherwise
    def findStraws(self):
        # check if pro 2 exists
        if self.data.proIDs["pan2"] == -1:
            return False
        strawTensions = sqla.Table(
            "measurement_straw_tension",
            self.metadata,
            autoload=True,
            autoload_with=self.engine,
        )

        strawTensionQuery = sqla.select(
            [  # select
                strawTensions.columns.position,  # straw position
                strawTensions.columns.tension,  # straw tension
                strawTensions.columns.uncertainty,  # measurement uncertainty
                strawTensions.columns.timestamp,  # measurement timestamp
            ]
        ).where(
            strawTensions.columns.procedure == self.data.proIDs["pan2"]
        )  # where procedure = pro 2 id

        resultProxy4 = self.connection.execute(
            strawTensionQuery
        )  # make proxy (do I need a different proxy every time??  Probably not)
        rawStrawData = resultProxy4.fetchall()  # fetch all and send to class member
        # list of tuples:  (<POS>, <TEN>, <UNCERTAINTY>, <TIME>)
        self.data.strawData = []  # enure strawTensionData is clear
        
        preliminary = [[] for i in range(96)] # initialize preliminary
        
        # sort rawStrawData into preliminary
        for i in rawStrawData:
            # put data into readable variables
            index, measurement, timestamp, uncertainty = i[0], i[1], i[3], i[2]
            # ensure that the straw measurement isn't bogus
            if measurement >= 200 and measurement <= 1000:
                preliminary[index].append([index, measurement, timestamp, None, uncertainty])
                
        # assign order to measurements with same positions
        for i in range(len(preliminary)):
            sort_list = preliminary[i]
            # sort the list by timestamp
            sort_list = sorted(sort_list, key=lambda x: x[2], reverse=True)
            # set order value for each item
            for y in range(len(sort_list)):
                sort_list[y][3] = y
            preliminary[i] = sort_list
            
        
        # go through preliminary list and put into a 1d output list
        self.data.strawData = []
        for i in range(96):
            if len(preliminary[i]) == 0:
                self.data.strawData.append([i, "No Data", 0, None, None])
            else:
                for y in preliminary[i]:
                    self.data.strawData.append(y)
        
        retList = self.data.strawData
        
        
        
        
        # return retlist found or not
        return (len(retList) > 0)

    # finds wire tension data and stores it in self.data.wireData
    # parameters: no parameters
    # returns: bool, true if any data found, false otherwise
    def findWires(self):
        # check if pro 3 exists
        if self.data.proIDs["pan3"] == -1:
            return False

        wireTensions = sqla.Table(
            "measurement_wire_tension",
            self.metadata,
            autoload=True,
            autoload_with=self.engine,
        )

        wireTensionQuery = sqla.select(
            [  # select:
                wireTensions.columns.position,  # wire position
                wireTensions.columns.tension,  # wire tension
                wireTensions.columns.wire_timer,  # wire timer (whatever that is)
                wireTensions.columns.calibration_factor,  # calibration factor
                wireTensions.columns.timestamp,
            ]
        ).where(
            wireTensions.columns.procedure == self.data.proIDs["pan3"]
        )  # where procedure = db pro 3 id

        resultProxy3 = self.connection.execute(wireTensionQuery)  # make proxy
        rawWireData = resultProxy3.fetchall()
    
        # rawWireData = list of tuples: (<POS>, <TEN>, <TIMER>, <CALIB>, <TIME>)

        preliminary = [[] for i in range(96)] # initialize preliminary
        
        # sort wire rawWireData into preliminary
        for i in rawWireData:
            # put data into readable variables
            index, measurement, timestamp = i[0], i[1], i[4]
            # ensure that the wire measurement isn't bogus
            if measurement >= 40 and measurement <= 100:
                preliminary[index].append([index, measurement, timestamp, None])
        
        # assign order to measurements with same positions
        for i in range(len(preliminary)):
            sort_list = preliminary[i]
            # sort the list by timestamp
            sort_list = sorted(sort_list, key=lambda x: x[2], reverse=True)
            
        
            # set order value for each item
            for y in range(len(sort_list)):
                sort_list[y][3] = y
            preliminary[i] = sort_list
            
            
        # go through preliminary list and put into a 1d output list
        self.data.wireData = []
        for i in range(96):
            if len(preliminary[i]) == 0:
                self.data.wireData.append([i, "No Data", 0, None])
            else:
                for y in preliminary[i]:
                    self.data.wireData.append(y)
                
        retList = self.data.wireData

        # return retList found or not
        return (len(retList) > 0)

    # finds hv data for a specific pro and voltage
    # parameters: pro, int that specifies procedure (3 or 6)
    #             volts, int that specifies voltage (1100 or 1500)
    # returns: bool, true if any data found, false otherwise
    # TODO: add pro 5 compatability
    def findSpecificHV(self, pro, volts):
        # first check if procedure exists
        if self.data.proIDs[f'pan{pro}'] == -1:
            return False

        hvTable = sqla.Table(
            "measurement_pan5",
            self.metadata,
            autoload=True,
            autoload_with=self.engine,
        )

        hvQuery = sqla.select(          # get...
            [
                hvTable.columns.position,     # position,
                hvTable.columns.current_left, # left current,
                hvTable.columns.current_right,# right current,
                hvTable.columns.is_tripped,   # trip status,
                hvTable.columns.timestamp     # timestamp
            ]
        ).where(                        # where...
            sqla.and_(
                hvTable.columns.procedure == self.data.proIDs[f'pan{pro}'], # pro is this procedure
                hvTable.columns.voltage == volts  # voltage is the voltage we want
            )
        )

        resultProxy = self.connection.execute(hvQuery)  # make proxy
        rawHVData = resultProxy.fetchall()
        # rawHVData = list of tuples:
        # (<position>, <L amps>, <R amps>, <trip status>, <epoch timestamp>)

        # initialize preliminary list
        preliminary = [[] for i in range(96)]
        
        # sort rawHVData into preliminary
        for i in rawHVData:
            # put data into readable variables
            # source of bug, is_tripped is never used after the next line and never makes it into self.data
            index, left_current, right_current, is_tripped, timestamp = i[0], i[1], i[2], i[3], i[4]
            # ensure that the hv measurement isn't bogus
            if right_current != None:
                preliminary[index].append([index, right_current, timestamp, None, 'R'])
            if left_current != None:
                preliminary[index].append([index, left_current, timestamp, None, "L"])
        
        # assign order to measurements with same positions
        for i in range(len(preliminary)):
            sort_list = preliminary[i]
            # sort the list by timestamp
            sort_list = sorted(sort_list, key=lambda x: x[2], reverse=True)
            # set order value for each item
            for y in range(len(sort_list)):
                sort_list[y][3] = y
            preliminary[i] = sort_list
        
        # go through preliminary list and put into a 1d output list
        retList = []
        for i in range(96):
            if len(preliminary[i]) == 0:
                retList.append([i, "No Data", 0, None, None])
            else:
                for y in preliminary[i]:
                    retList.append(y)
        
        
        # assign targetList values
        targetList = getattr(self.data, f'hv{volts}P{pro}')
        targetList += retList

        # return retList found or not
        return (len(retList) > 0)

    # finds heat data and stores it in ____
    # parameters: int, pro is the process to find data for (1,2, or 6)
    # returns: bool, true if any data found, false otherwise
    def findSpecificHeat(self, pro):
        # check if desired pro exists
        if self.data.proIDs[f'pan{pro}'] == -1:
            return False

        panelHeats = sqla.Table(
            "panel_heat", self.metadata, autoload=True, autoload_with=self.engine
        )

        heatQuery = sqla.select(
            [
                panelHeats.columns.timestamp,  # time temp taken
                panelHeats.columns.temp_paas_a,  # PAAS A temp
                panelHeats.columns.temp_paas_bc,  # PAAS BC temp
                panelHeats.columns.procedure,
            ]
        ).where(panelHeats.columns.procedure == self.data.proIDs[f'pan{pro}'])

        resultProxy = self.connection.execute(heatQuery)  # make proxy
        rawHeatData = resultProxy.fetchall()  # get data from db

        # go through the raw data and build a list with it
        # list is list of tuples:
        # (<human timestamp>, <epoch timestamp>, <PAAS A temp>, <PAAS B/C temp>)
        heatList = []
        for toop in rawHeatData:
            appendMe = []
            if toop[0] is not None:
                appendMe.append(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(toop[0])))
            for thing in toop:
                if thing != None:
                    appendMe.append(thing)
            if appendMe[0] is not None and appendMe[1] is not None and appendMe[2] is not None:
                heatList.append(appendMe)

        # assign built list to self.data
        listPointer = getattr(self.data,f'p{pro}HeatData')
        listPointer += heatList

        return (len(heatList) > 0)

    # finds tuberculosis and puts it in self.data.pXtbData
    # parameters: int, pro is the process to find data for (3 or 6)
    # returns: bool, true if any data found, false otherwise
    def findSpecificTB(self, pro):
        # check if desired pro exists
        if self.data.proIDs[f'pan{pro}'] == -1:
            return False

        panelTension = sqla.Table(
            "measurement_tensionbox", self.metadata, autoload=True, autoload_with=self.engine
        )

        tbQuery = sqla.select(
            [
                panelTension.columns.position,      # position on panel
                panelTension.columns.length,        # length of...?
                panelTension.columns.frequency,     # pulse frequency
                panelTension.columns.pulse_width,   # pulse width I guess
                panelTension.columns.tension,       # the actual tension measurement
                panelTension.columns.straw_wire,    # straw/wire designation
                panelTension.columns.timestamp      # time measurement taken
            ]
        ).where(panelTension.columns.procedure == self.data.proIDs[f'pan{pro}'])

        resultProxy = self.connection.execute(tbQuery)  # make proxy
        rawTBData = resultProxy.fetchall()  # get data from db

        # make a pointer to the self.data.pXtbData and fill it
        tbDataPointer = getattr(self.data,f'p{pro}tbData')
        # initialize preliminary
        preliminary = [[] for i in range(96)]
        
        
        # sort rawTBData into preliminary
        for i in rawTBData:
            # put data into readable variables
            index, length, frequency, pulse_width, tension, straw_wire, timestamp = i[0], i[1], i[2], i[3], i[4], i[5], i[6]
            # ensure that the tension measurements aren't bogus
            try: # due to potential NoneTypes in list
                if straw_wire == 'straw' and tension >= 200 and tension <= 1000:
                    preliminary[index].append([index, length, frequency, pulse_width, tension, straw_wire, timestamp, None])
                elif tension >= 40 and tension <= 100:
                    preliminary[index].append([index, length, frequency, pulse_width, tension, straw_wire, timestamp, None])
            except:
                pass
                
        # initialize preliminary_cut
        preliminary_cut = [[] for i in range(96)]
        
        # assign order to measurements with same positions
        for i in range(len(preliminary)):
            sort_list = preliminary[i]
            # sort the list by timestamp
            sort_list = sorted(sort_list, key=lambda x: x[6], reverse=True)
            
            num_straw=0
            num_wire=0
            for y in range(len(sort_list)):
                if (y % 3) == 0:
                    if sort_list[y][5] == "straw":
                        sort_list[y][7]=num_straw
                        num_straw+=1
                    elif sort_list[y][5] == "wire":
                        sort_list[y][7]=num_wire
                        num_wire+=1
                    sort_list[y][7]
                    preliminary_cut[i].append(sort_list[y])
                    
                    
                    
                    
        # set order value for each item, additionally select 1 entry from each set of 3 data points
        #sort_list[y][7] = len(preliminary_cut[i])
        
                
            
        
                    

        # go through preliminary list and put into a 1d output list
        for i in range(96):
            if len(preliminary_cut[i]) == 0:
                tbDataPointer.append([i,None,None,None,None,None,None,None])
            else:
                for y in preliminary_cut[i]:
                    tbDataPointer.append(y)
        
        try:
            assert len(tbDataPointer) > 0
        except AssertionError:
            logger.error("Neither straw nor wire TB data could not be found.")

        return 0

    # finds QC data and puts it into panelData.
    # parameters: none
    # returns: bool, true if any data found, false otherwise
    def findPro8(self):

        # check if desired pro exists
        if self.data.proIDs['pan8'] == -1:
            return False

        # make necessary tables
        badSW = sqla.Table(
            "bad_wire_straw", self.metadata, autoload=True, autoload_with=self.engine
        )
        methaneLeak = sqla.Table(
            "leak_final_form", self.metadata, autoload=True, autoload_with=self.engine
        )
        pro8Parts = sqla.Table(
            "procedure_details_pan8", self.metadata, autoload=True, autoload_with=self.engine
        )
        leakDetails = sqla.Table(
            "panel_leak_test_details", self.metadata, autoload=True, autoload_with=self.engine
        ) # should be called leekDeets

        # bad straws and wires
        badSWQuery = sqla.select(
            [
                badSW.columns.position,     # position on panel
                badSW.columns.failure,      # comment
                badSW.columns.wire,         # bool, true if wire failed
                badSW.columns.timestamp     # time measurement taken
            ]
        ).where(badSW.columns.procedure == self.data.proIDs['pan8'])
        resultProxy = self.connection.execute(badSWQuery)  # make proxy
        rawSWData = resultProxy.fetchall()  # get data from db

        for toop in rawSWData:
            # if wire failed
            if toop[2]:
                # add to bad wires list
                self.data.badWires += [toop]
            else:
                self.data.badStraws += [toop]

        # methane leak testing data
        methaneLeakQuery = sqla.select(
            [
                methaneLeak.columns.cover_reinstalled, # covers/rings reinstalled
                methaneLeak.columns.inflated,       # reinflated
                methaneLeak.columns.leak_location,  # location of leak (str)
                methaneLeak.columns.leak_size,      # size of leak (float)
                methaneLeak.columns.resolution,     # what was done to fix the leak
                methaneLeak.columns.timestamp       # when form was submitted
            ]
        ).where(methaneLeak.columns.procedure == self.data.proIDs['pan8'])
        resultProxy = self.connection.execute(methaneLeakQuery)  # make proxy
        rawMethData = resultProxy.fetchall()  # get data from db

        for toop in rawMethData:
            self.data.methane += [toop]

        # pro8 parts
        pro8Query = sqla.select(
            [
                pro8Parts.columns.left_cover,
                pro8Parts.columns.right_cover,
                pro8Parts.columns.center_cover,
                pro8Parts.columns.left_ring,
                pro8Parts.columns.right_ring,
                pro8Parts.columns.center_ring,
                pro8Parts.columns.stage,
                pro8Parts.columns.leak_rate
            ]
        ).where(pro8Parts.columns.procedure == self.data.proIDs['pan8'])
        resultProxy = self.connection.execute(pro8Query)  # make proxy
        rawPro8Data = resultProxy.fetchall()  # get data from db

        # leek deets
        leakDetailsQuery = sqla.select(
            [
                leakDetails.columns.tag,               # tag name
                leakDetails.columns.elapsed_days,      # elapsed time
                leakDetails.columns.id,                # id (foreign key in measurement table)
                leakDetails.columns.timestamp          # time of... completion?
            ]
        ).where(leakDetails.columns.procedure == self.data.proIDs['pan8'])
        resultProxy = self.connection.execute(leakDetailsQuery)  # make proxy
        rawLDData = resultProxy.fetchall()  # get data from db

        for toop in rawLDData:
            self.data.leakTests += [toop]

        # if it's > 1 then it found two procedures and needs to go home bc it's drunk
        if len(rawPro8Data) > 1:
            return False

        try:
            self.data.qcParts["left_cover"] = rawPro8Data[0][0]
            self.data.qcParts["right_cover"] = rawPro8Data[0][1]
            self.data.qcParts["center_cover"] = rawPro8Data[0][2]
            self.data.qcParts["left_ring"] = rawPro8Data[0][3]
            self.data.qcParts["right_ring"] = rawPro8Data[0][4]
            self.data.qcParts["center_ring"] = rawPro8Data[0][5]
            self.data.qcParts["stage"] = rawPro8Data[0][6]
            self.data.qcParts["leak_rate"] = rawPro8Data[0][7]
        except IndexError as e:
            logger.warning("No pro8 parts data. This shouldn't be throwing an error. TODO for Ben.")

        return True

    # ██████╗ ██╗███████╗██████╗ ██╗      █████╗ ██╗   ██╗    ██████╗  █████╗ ████████╗ █████╗
    # ██╔══██╗██║██╔════╝██╔══██╗██║     ██╔══██╗╚██╗ ██╔╝    ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗
    # ██║  ██║██║███████╗██████╔╝██║     ███████║ ╚████╔╝     ██║  ██║███████║   ██║   ███████║
    # ██║  ██║██║╚════██║██╔═══╝ ██║     ██╔══██║  ╚██╔╝      ██║  ██║██╔══██║   ██║   ██╔══██║
    # ██████╔╝██║███████║██║     ███████╗██║  ██║   ██║       ██████╔╝██║  ██║   ██║   ██║  ██║
    # ╚═════╝ ╚═╝╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝   ╚═╝       ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝

    # displayPanelData puts data from self.data into the GUI's widgets
    # also enables buttons for data types that have enough data
    # parameters: no parameters
    # returns: nothing returned
    def displayPanelData(self):
        self.displayProTiming()
        self.displayComments()
        self.displayParts()
        self.displayPro8()
        self.displayOnLists(
            3,
            self.data.wireData,
            [("Position",18),("Tension",0)],
            (self.ui.wireListWidget,self.ui.wireListWidget_2),
            (
                self.ui.wireExportButton,self.ui.wireExportButton_2,
                self.ui.wirePlotButton,self.ui.wirePlotButton_2
            )
        )
        self.displayOnGraph(
            self.data.wireData,
            "Position",0,
            "Tension",1,
            self.ui.wireGraphLayout
        )
        self.displayOnLists(
            2,
            self.data.strawData,
            [("Position",18),("Tension",13),("timestamp",-1),("Uncertainty",0)],
            (self.ui.strawListWidget,self.ui.strawListWidget_2),
            (
                self.ui.strawExportButton,self.ui.strawExportButton_2,
                self.ui.strawPlotButton,self.ui.strawPlotButton_2
            )
        )
        self.displayOnGraph(
            self.data.strawData,
            "Position",0,
            "Tesnion",1,
            self.ui.strawGraphLayout,
            errorBars=True,
            eIndex=3
        )
        return

    # puts part IDs on the gui
    # parameters: no parameters
    # returns: nothing returned
    def displayProTiming(self):
        # helper to get widgets by name
        def getTimeWidget(self, pro, event):
            if event == "L":
                return self.getWid(f"{pro}TimeList")
            else:
                return self.getWid(f"{pro}{event}TimeLE")

        for key in self.data.timingLists:
            if self.data.timingLists[key] is not []:
                startTime = -1
                stopTime = -1
                lastTime = -1
                totalTime = 0
                # how this'll work:
                # the list of time events is in ascending order, so start to finish
                # a sequence of events should only be able to be one of the following:
                #   start
                #   start;pause
                #   start;stop
                #   start;resume
                #   start;pause;...  ...;resume;stop
                # I'm sure there's some way to get a different pattern...

                for event in self.data.timingLists[key]:
                    if event[0] == "start":
                        startTime = event[1]
                        lastTime = event[1]
                        getTimeWidget(self, key, "L").addItem(
                            f"START:  {time.strftime('%a, %d %b %Y %H:%M:%S', (time.localtime(event[1])))}"
                        )
                    elif event[0] == "stop":
                        stopTime = event[1]
                        totalTime += event[1] - lastTime
                        getTimeWidget(self, key, "L").addItem(
                            f"END:  {time.strftime('%a, %d %b %Y %H:%M:%S', (time.localtime(event[1])))}"
                        )
                    elif event[0] == "pause":
                        totalTime += event[1] - lastTime
                        getTimeWidget(self, key, "L").addItem(
                            f"PAUSE:  {time.strftime('%a, %d %b %Y %H:%M:%S', (time.localtime(event[1])))}"
                        )
                    elif event[0] == "resume":
                        getTimeWidget(self, key, "L").addItem(
                            f"RESUME:  {time.strftime('%a, %d %b %Y %H:%M:%S', (time.localtime(event[1])))}"
                        )
                        lastTime = event[1]

                # start time
                if startTime > 0:
                    getTimeWidget(self, key, "S").setText(
                        time.strftime(
                            "%a, %d %b %Y %H:%M:%S", (time.localtime(startTime))
                        )
                    )
                else:
                    getTimeWidget(self, key, "S").setText("Not found")

                # end time
                if stopTime > 0:
                    getTimeWidget(self, key, "E").setText(
                        time.strftime(
                            "%a, %d %b %Y %H:%M:%S", (time.localtime(stopTime))
                        )
                    )
                else:
                    getTimeWidget(self, key, "E").setText("Not found")
                # total/elapsed time
                if totalTime > 0:
                    prefix = "Estimate: " if stopTime <= 0 else ""
                    getTimeWidget(self, key, "T").setText(
                        # totalTime = total time in seconds
                        # hours = totalTime//3600
                        # minutes = (totalTime%3600)//60
                        # seconds = totalTime%60
                        f"{prefix}{totalTime//3600}:{(totalTime%3600)//60}:{totalTime%60}"
                    )
                else:
                    getTimeWidget(self, key, "T").setText("Not found")

    # puts comments on the gui
    # parameters: no parameters
    # returns: nothing returned
    def displayComments(self):
        '''
        labelBrush = QBrush(Qt.red)  # make a red brush
            labelItem = QListWidgetItem(
                "This panel was created before HV data was recorded in the database"
            )
            # make a list item with text ^
            labelItem.setBackground(labelBrush)  # paint the list item background red
            self.ui.hvListWidget.addItem(labelItem)  # add the item to the list
        '''
        # make brush to highlight failures
        failBrush = QBrush(Qt.red)
        # goes through each pro and adds each pro's comments to the
        # corresponding list widget
        for key in self.data.comLists:
            listWidget = self.getWid(f'{key}ComList')
            for comment in self.data.comLists[key]:
                newItem = QListWidgetItem(
                    f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(comment[1]))}\n{comment[0]}'
                )
                if self.ui.actionFailures.isChecked():
                    if "Failure:" in comment[0]:
                        newItem.setBackground(failBrush)
                listWidget.addItem(newItem)

    # puts part IDs on the gui
    # parameters: no parameters
    # returns: nothing returned
    def displayParts(self):
        # this helper takes widget name, returns pointer to that widget
        def getPartWidget(self, widget):
            try:
                return self.getWid(f"part{widget}LE")
            except:
                if widget not in ["wire_weight_initial","wire_weight_final"]:
                    tkinter.messagebox.showerror(
                        title="Error",
                        message=f'Key Error: No part found with name "{widget}".\nPerhaps an L/R or A/B/C was not found in the database?',
                    )
                    logger.error(f'Key Error: No part found with name "{widget}".\nPerhaps an L/R or A/B/C was not found in the database?')
                    return self.ui.error_label
                else:
                    return self.ui.error_label

        # for each type of part,
        for key in self.data.parts:
            # make sure we actually have an id
            if self.data.parts[key] == [] or self.data.parts[key] == None:
                # if not, let it know we don't
                self.data.parts[key] = -1
            # set the corresponding widget to the key's number
            if self.data.parts[key] > -1:
                getPartWidget(self, key).setText(str(self.data.parts[key]))
                self.ui.label_2.setText(f"MN{str(self.data.humanID).zfill(3)}")
            else:
                getPartWidget(self, key).setText("Not found")
                self.ui.label_2.setText(f"MN{str(self.data.humanID).zfill(3)}")

        # special case: wire spool weights
        boolList = [
            self.data.parts["wire_weight_initial"] != [],
            self.data.parts["wire_weight_initial"] != None,
            self.data.parts["wire_weight_initial"] != -1,
            self.data.parts["wire_weight_final"] != [],
            self.data.parts["wire_weight_final"] != None,
            self.data.parts["wire_weight_final"] != -1
        ]
        if not False in boolList:
            weightUsed = str(float(self.data.parts["wire_weight_initial"]) - float(self.data.parts["wire_weight_final"]))
            self.ui.partWireWeightLE.setText(f'{weightUsed[:5]}g')
        else:
            self.ui.partWireWeightLE.setText("Not found")

    # puts pro8 relevant info on the gui
    # parameters: no parameters
    # returns: nothing returned
    def displayPro8(self):
        self.ui.badStrawsLW.clear()
        self.ui.badWiresLW.clear()
        self.ui.leaksLW.clear()
        self.ui.leakTestsLW.clear()

        # check if desired pro exists
        if self.data.proIDs['pan8'] == -1:
            return

        # start with serial numbers
        for key in self.data.qcParts:
            # get correct widget (keys correspond to widget names) and set the text
            self.getWid(f'{key}LE').setText(
                str(self.data.qcParts[key])
            )

            if self.getWid(f'{key}LE').text() in ["000001Jan00000000000Z", "None"]:
                self.getWid(f'{key}LE').setText("Not Found")

        # leaks next
        for toop in self.data.methane:
            descStr = ""
            descStr += str(time.strftime("%a, %d %b %Y %H:%M", (time.localtime(toop[5]))))
            descStr += f'\nLeak at {toop[2]}\n'
            descStr += f'Size: {toop[3]}\n'
            descStr += "Inflated: Yes\n" if toop[1] else "Inflated: No\n"
            descStr += "O-Rings reinstalled\n" if "O" in toop[0] else ""
            descStr += "Left cover reinstalled\n" if "L" in toop[0] else ""
            descStr += "Right cover reinstalled\n" if "R" in toop[0] else ""
            descStr += "Center cover reinstalled\n" if "C" in toop[0] else ""
            descStr += f'Resolution: {toop[4]}\n'
            self.ui.leaksLW.addItem(descStr)

        # leak tests
        if len(self.data.leakTests) > 0:
            self.ui.leakTestsLW.addItem("Double click an entry to view it's data on a graph.")
        for toop in self.data.leakTests:
            newItem = QListWidgetItem()
            newItem.setText(f'Tag Name: {toop[0]}\nTime Elapsed: {toop[1]} days')
            newItem.setToolTip(f'Double click to open graph for {toop[0]}')
            self.ui.leakTestsLW.addItem(newItem)

        # lastly straws and wires
        for toop in self.data.badStraws:
            descStr = ""
            descStr += str(time.strftime("%a, %d %b %Y %H:%M", (time.localtime(toop[3]))))
            descStr += f'\nPosition: {toop[0]}\n'
            descStr += f'Comment: {toop[1]}\n'
            self.ui.badStrawsLW.addItem(descStr)

        for toop in self.data.badWires:
            descStr = ""
            descStr += str(time.strftime("%a, %d %b %Y %H:%M", (time.localtime(toop[3]))))
            descStr += f'\nPosition: {toop[0]}\n'
            descStr += f'Comment: {toop[1]}\n'
            self.ui.badWiresLW.addItem(descStr)


    # put data into QListWidgets
    # parameters:   pro, int representing which pro to check for data in
    #               dataType, list of tuples (like self.data.strawData)
    #               dataCols, list of tuples (string, int): col name, space needed, space = -1 to exclude
    #               listWidgets, tuple of QListWidgets on gui to put data in
    #               buttons, tuple of QPushButtons: the export/plot buttons under lists
    #               hV, bool that's true if displaying HV measurements
    # returns: nothing returned
    def displayOnLists(self,pro,dataType,dataCols,listWidgets,buttons,hV=False):
        # clear the list, disable buttons
        for lst in listWidgets:
            lst.clear()
        for button in buttons:
            button.setDisabled(True)

        # check if relevant procedure exists, if not return
        if self.data.proIDs[f'pan{pro}'] == -1:
            for lst in listWidgets:
                lst.addItem("No data found :(")
            return

        for button in buttons:
            button.setEnabled(True)

        # add line to show side if using HV
        if hV:
            try:
                if dataType[0][3] == "L":
                    for lst in listWidgets:
                        lst.addItem(f'***Using Left Side Measurements***')
                elif dataType[0][3] == "R":
                    for lst in listWidgets:
                        lst.addItem(f'***Using Right Side Measurements***')
                else:
                    raise NameError("No HV Measurement Side Found")
            except:
                for lst in listWidgets:
                    lst.addItem(f'HV Measurement side not found')

        # make header out of data columns
        headerString = ""
        for toop in dataCols:
            if toop[1] != -1:
                headerString += f'{str(toop[0])}      ' # note the 6 spaces

        # add header string
        for lst in listWidgets:
            lst.addItem(headerString)

        # make brush to highlight "No Data"s
        failBrush = QBrush(Qt.red)
        highlight = self.ui.actionMissing_Data.isChecked()

        noData = True
        for dataToop in dataType:  # for each tuple in data
            itemString = "" # build a string
            # for each piece of data (position, tension, etc.)
            for i in range(len(dataCols)):
                if dataCols[i][1] != -1:
                    trimmed = str(dataToop[i])[:8]
                    itemString += f'{trimmed.ljust(dataCols[i][1])}'
            # if data is good, mark that we have data and make the new item
            if "No Data" not in itemString:
                noData = False
                newItem = QListWidgetItem(itemString)
            # otherwise highlight that we have a no data
            else:
                newItem = QListWidgetItem(itemString)
                if highlight:
                    newItem.setBackground(failBrush)
            # add new item to each list
            for lst in listWidgets:
                lst.addItem(newItem)

        # check if no data was added or all data is "No Data"
        # if so, only display "No data found :("
        badItem = QListWidgetItem("No data found :(")
        if highlight:
            badItem.setBackground(failBrush)
        for lst in listWidgets:
            if lst.count() == 0:
                lst.addItem(badItem)
            if noData:
                lst.clear()
                lst.addItem(badItem)
                for button in buttons:
                    button.setDisabled(True)

    # general function to graph any data on the main window
    def displayOnGraph(self,dataType,xAxis,xIndex,yAxis,yIndex,targetLayout,errorBars=False,eIndex=0,microScale=False):
        # clear current plot
        for i in reversed(range(targetLayout.count())):
            targetLayout.itemAt(i).widget().setParent(None)

        # new plot
        plot = pg.plot()
        plot.setLabel("bottom",xAxis)
        plot.setLabel("left",yAxis)

        numPoints = 0
        xs = []
        ys = []
        erTops = []
        erBots = []
        for toop in dataType:
            if toop[yIndex] != "No Data" and toop[yIndex] != None:
                numPoints += 1
                xs.append(float(toop[xIndex]))
                ys.append(float(toop[yIndex]))

        if errorBars:
            for toop in dataType:
                if toop[yIndex] != "No Data" and toop[yIndex] != None:
                    if toop[eIndex] != None:
                        erTops.append(toop[eIndex])
                        erBots.append(toop[eIndex])
            xs = np.array(xs)
            ys = np.array(ys)
            erTops = np.array(erTops)
            erBots = np.array(erBots)
            errorPlot = pg.ErrorBarItem(x=xs,y=ys,top=erTops,bottom=erBots)

        plotToAdd = pg.ScatterPlotItem(
            size = 10,
            brush=pg.mkBrush(255,255,255,190)
        )
        points = [{'pos': [xs[z],ys[z]], 'data':1} for z in range(numPoints)]
        plotToAdd.addPoints(points, hoverable=True)

        plot.addItem(plotToAdd)
        if errorBars:
            plot.addItem(errorPlot)
        plot.setXRange(0,96)
        if microScale:
            plot.setYRange(0,0.01)
        plot.showGrid(x=True,y=True)

        targetLayout.addWidget(plot)
        #targetLayout.addWidget(QLabel("Graph coming soon!"))
        return

    # puts heat data in the gui
    # parameters:   pro, int representing which pro to get data for (1,2,or 6)
    #               listWidget, QListWidget to put data in
    #               listWidget, tuple of QPushButtons: the export/plot buttons under the list
    #               targetLayout, QVBoxLayout to put graph or "error" label in
    # returns: nothing returned
    def displaySpecificHeat(self, pro, listWidget=None, buttons=None, targetLayout=None):
        # check if relevant procedure exists, if not display errors
        noPro = False
        if self.data.proIDs[f'pan{pro}'] == -1:
            noPro = True
        # disable buttons
        for button in buttons:
            button.setDisabled(True)
        # get list of data to use (self.data.p2HeatData if pro = 2)
        heatData = getattr(self.data, f'p{pro}HeatData')


        # add data to list widget
        if listWidget is not None:
            #Logistic sorts of things:
            ###################################################
            # clear list
            listWidget.clear()
            # check for presence of data
            if noPro:
                listWidget.addItem("No data found :(")
                return
            # enable buttons
            for button in buttons:
                button.setEnabled(True)
            ###################################################
            # make lists of temps for paas A and B/C in order to calculate
            # statistics. Remove Nones for this purpose.        
            paasATemps, paasBCTemps, time_begin_above_50_paasA, time_end_above_50_paasA, time_begin_above_50_paasB, time_end_above_50_paasB, elapsed_time_above_50_paasA, elapsed_time_above_50_paasB = self.process_heatdata(heatData)
            
            if len(paasATemps) > 1:  # if paas A data exits
                # make a list of stats
                paasAStats = [
                    "PAAS A Statistics",
                    f'Mean: {str(round(statistics.mean(paasATemps),1))[:8]}',  # mean of paas A
                    f'Max: {str(round(max(paasATemps),1))[:8]}',  # max of paas A
                    f'First time above 50 C: {str(time_begin_above_50_paasA)}', # first time paas A went above 50 C
                    f'Last time above 50 C: {str(time_end_above_50_paasA)}', # last time paas A dipped below 50 C
                    f'Elapsed time above 50 C (hours): {str(elapsed_time_above_50_paasA)}', # time between first going above and finally dipping below 50 C
                ]
            else:
                paasAStats = []
            if len(paasBCTemps) > 1 and pro != 1:  # if paas B/C exists
                # make a list of stats
                paasBCStats = [
                    '', # empty line
                    f'PAAS {"B" if pro == 2 else "C"} Statistics',
                    f'Mean: {str(round(statistics.mean(paasBCTemps),1))[:8]}',  # mean of paas BC
                    f'Max: {str(round(max(paasBCTemps),1))[:8]}',  # max of paas BC
                    f'First time above 50 C: {str(time_begin_above_50_paasB)}', # first time paas BC went above 50 C
                    f'Last time above 50 C: {str(time_end_above_50_paasB)}', # last time paas BC dipped below 50 C
                    f'Elapsed time above 50 C (hours): {str(elapsed_time_above_50_paasB)}', # time between first going above and finally dipping below 50 C
                ]
            else:
                paasBCStats = []

            # make a list of heat timestamps
            heatTimes = [toop[1] for toop in heatData if (toop[2] or toop[3])]
            # if we have that data
            if len(heatTimes) > 0:
                # find the total time it took
                rawHeatTime = max(heatTimes) - min(heatTimes)
                heatTotalTime = timedelta(seconds=rawHeatTime)
                listWidget.addItem(f'Total heating time: {heatTotalTime}')
                for item in paasAStats:
                    listWidget.addItem(item)
                if pro != 1:
                    for item in paasBCStats:
                        listWidget.addItem(item)

            # add stuff to list
            listWidget.addItem(f'{len(paasATemps)} measurements found for PAAS A')
            if pro != 1:
                listWidget.addItem(f'{len(paasBCTemps)} measurements found for PAAS BC')

        # make graph
        if targetLayout is not None:
            #Logistic sorts of things:
            ###################################################
            # clear layout
            for i in reversed(range(targetLayout.count())):
                targetLayout.itemAt(i).widget().setParent(None)
            # check for presence of data
            #if noPro:
            #    listWidget.addItem("No data found :(")
            ###################################################
            # add graph
            self.displayOnGraphHEAT(pro)
        return

    # popup(?) with heat data graph  (I don't think this actually makes a popup)
    # parameters:   pro, int representing which pro to get data for (1,2,or 6)
    # returns: nothing returned
    def displayOnGraphHEAT(self,pro):
        # clear current plot
        for i in reversed(range(self.ui.heatGraphLayout.count())):
            self.ui.plotLayout.itemAt(i).widget().setParent(None)

        # check if there's data to use
        if len(getattr(self.data,f'p{pro}HeatData')) == 0:
            self.ui.heatGraphLayout.addWidget(QLabel("Insufficient Data."))
            return
        else:
            localHeat = getattr(self.data,f'p{pro}HeatData')

        # create plot, make the bottom axis datetime based
        plot = pg.PlotWidget(axisItems = {'bottom': pg.DateAxisItem()})
        # set left label as temp in C
        plot.setLabel("left","Temperature (°C)")

        # organize data
        # keep track of number of valid data points
        numPoints = 0
        # hold data for paas A and b/c respectively
        paasaYs = []
        paasbcYs = []
        # hold x data (timestamps)
        xs = []

        hide = self.ui.actionHide_False_Data.isChecked()
        # for each piece of data
        for toop in localHeat:
            # if there's a paas A measurement that's not None or...
            # if we want to hide false data (-255 or whatever) then it can't be < 1
            # (if toop[2] == None then it will be cast as 0 as an int, hence the < 1)
            if not(toop[2] == None or (hide and (toop[2] < 1))):
                # append it, the time, and add one to num data points
                paasaYs.append(float(toop[2]))
                numPoints += 1
                xs.append(float(toop[1]))
            # if there's a paas B/C measurement that meets the same criteria as before
            if not(toop[3] == None or (hide and (toop[3] < 1))):
                # append it, and the time if there was no paas A measurement
                paasbcYs.append(float(toop[3]))
                if toop[2] == None or (hide and (toop[2] < 1)):
                    numPoints += 1
                    xs.append(int(toop[1]))
        # choose colormap for paas A
        if pro == 1:
            cMapA = pg.colormap.get('CET-L8')
        else:
            cMapA = pg.colormap.get('CET-L4')
        # make pen for paas A
        brushA = QBrush(cMapA.getGradient(p1=QPointF(0.,15.0), p2=QPointF(0.,60.0)))
        penA = QPen(brushA,3.0)
        penA.setCosmetic(True)

        # make a legend item
        theLegend27 = pg.LegendItem(pen=QPen(Qt.white)) # I think I'm funny
        # make curve for paas A
        curveA = pg.PlotDataItem(x=xs,y=paasaYs, pen=penA, hoverable=True)
        # add paas A curve to plot
        plot.addItem(curveA)

        # if we need to do stuff for paas B/C too...
        if pro != 1:
            # make a pen
            cMapB = pg.colormap.get('CET-L7')
            brushB = QBrush(cMapB.getGradient(p1=QPointF(0.,15.0), p2=QPointF(0.,60.0)))
            penB = QPen(brushB,3.0)
            penB.setCosmetic(True)
            # make a curve
            curveB = pg.PlotDataItem(x=xs,y=paasbcYs,pen=penB,hoverable=True)
            # add curve
            plot.addItem(curveB)
            # add curve for paas A to legend
            theLegend27.addItem(curveA, "PAAS A - Red/Yellow")
            # add curve for paas B to legend
            theLegend27.addItem(curveB, f'PAAS {"B" if pro == 2 else "C"} - Blue/Pink')
        else:
            # add curve for paas A to legend
            theLegend27.addItem(curveA, "PAAS A")

        # add legend to plot
        theLegend27.setParentItem(plot.getPlotItem())
        # show the grid on the plot
        plot.showGrid(x=True,y=True)

        # put the plot into the gui!
        self.ui.heatGraphLayout.addWidget(plot)


    #  ██████╗ ██████╗  █████╗ ██████╗ ██╗  ██╗    ██████╗  █████╗ ████████╗ █████╗
    # ██╔════╝ ██╔══██╗██╔══██╗██╔══██╗██║  ██║    ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗
    # ██║  ███╗██████╔╝███████║██████╔╝███████║    ██║  ██║███████║   ██║   ███████║
    # ██║   ██║██╔══██╗██╔══██║██╔═══╝ ██╔══██║    ██║  ██║██╔══██║   ██║   ██╔══██║
    # ╚██████╔╝██║  ██║██║  ██║██║     ██║  ██║    ██████╔╝██║  ██║   ██║   ██║  ██║
    #  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝

    # graph straws, wires, or specific hv data in a popup window
    # parameters:   dataType, a list of tuples with the first two elements of each tuple
    #                           being the x and y values
    #               yAxis, a string that will be the y axis label
    #               yUpperBound, an int that will be the upper bound of the y axis
    #               errorBars, a bool that makes error bars if true; the third element
    #                           in each tuple from dataType is the uncertainty
    #               type, string telling the function which type of data is being graphed
    # returns: nothing returned
    def graphSimple(self,dataType,yAxis,errorBars=False):
        # xData length will vary based on the number of duplicate/missing position measurements
        xData = []
        for i in range(len(dataType)): # iterate through data appending proper index values to xData
            xData.append(dataType[i][0])
        
        # make list for y values
        sctrYDataPoints = []
        # make list for y value uncertainties
        sctrYDataUncs = []
        # for each point, add it to
        for toop in dataType:
            if toop[1] != "No Data":
                sctrYDataPoints += [toop[1]]
            else:
                sctrYDataPoints += [None]  # source of a bug???
            if errorBars:
                if toop[2] != "No Data":
                    sctrYDataUncs += [toop[2]]
                else:
                    sctrYDataUncs += [None]
        
        fig = plt.figure()
        ax1 = fig.add_subplot(211)
        # plt.figure(figsize=(12,8))
        if errorBars:
            try:
                plt.errorbar(
                    xData, sctrYDataPoints, yerr=sctrYDataUncs, fmt="o"
                )  # make a scatterplot out of the x and y data
            except:
                tkinter.messagebox.showwarning(
                    title="Warning",
                    message=f"Insufficient data to plot error bars.",
                )
        else:
            #ax1.scatter(xData, sctrYDataPoints)  # make a scatterplot out of the x and y data
            for i in range(len(xData)):
                colors = ['r','g','b','k']
                if sctrYDataPoints[i] is not None: # determine which order measurement it is and ensure proper color
                    if dataType[i][3] == 0:
                        ax1.plot(xData[i],sctrYDataPoints[i],marker='o',markersize=4,color=colors[dataType[i][3]])
                    elif dataType[i][3] <= 3:
                        ax1.plot(xData[i],sctrYDataPoints[i],marker='o',markersize=3,color=colors[dataType[i][3]])
                    else:
                        ax1.plot(xData[i],sctrYDataPoints[i],marker='o',markersize=3,color=colors[3])
                    
        # add legend
        dots = [
            Line2D([0], [0], marker='o', color='r', label='Nth Measurement', markersize=3),
            Line2D([0], [0], marker='o', color='g'),
            Line2D([0], [0], marker='o', color='b'),
            Line2D([0], [0], marker='o', color='k'),
        ]
        ax1.legend(dots,['Nth Measurement', 'Nth-1 Measurement', 'Nth-2 Measurement', 'Earlier'],fontsize = 'x-small')
        
        # set graph limits, first get list of y values without nones, also used for frequency histogram
        y_WOnone = []
        for i in sctrYDataPoints:
            if i != None:
                y_WOnone.append(i)
        # finds and sets ideal y bounds for the graph
        lower_bound = min(y_WOnone)-((max(y_WOnone) - min(y_WOnone)) * 0.2)
        upper_bound = max(y_WOnone)+((max(y_WOnone) - min(y_WOnone)) * 0.2)
        if lower_bound == upper_bound:
            lower_bound,upper_bound = -0.05,0.05
        ax1.set_ylim([lower_bound,upper_bound])
        
        plt.xlabel("Position", fontsize=20)  # set x axis label
        plt.ylabel(yAxis, fontsize=20)  # set y axis label
        
        for i in range(len(sctrYDataPoints)):  # go through x and y values to label all points
            if sctrYDataPoints[i] is not None and dataType[i][3]==0:  # if y exists and is too low...??? wat
                ax1.text(xData[i],sctrYDataPoints[i],str(xData[i]),fontsize='xx-small')

        plt.subplot(212)  # make subplot 2

        n, bins, patches = plt.hist(y_WOnone, 20)  # plot histogram
        plt.xlabel(yAxis, fontsize=20)  # set x axis label
        plt.ylabel("Frequency", fontsize=20)  # set y axis label

        plt.tight_layout()
        plt.show()

    # graph heat data in pop up window
    # parameters: pro, an int for which procedure (1, 2, or 6)
    # returns: nothing returned
    def graphSpecificHeat(self, pro):
        heatData = getattr(self.data,f'p{pro}HeatData')

        #heatData[:] = [i for i in heatData if (-100. < i[2] < 150. and -100. < i[3] < 150.)]

        # make x data list by converting raw timesamps to matplotlib dates
        xData = [
            mpl.dates.epoch2num(toop[1])
            for toop in heatData
        ]

        if len(xData) <3 :  # <3 <3 <3
            tkinter.messagebox.showerror(
                title="Error",
                message=f"Too little or no heat data was found for MN{self.data.humanID}, process {pro}.",
            )
            return

        # make y data sets
        yDataA = [toop[2] for toop in heatData]
        yDataBC = [toop[3] for toop in heatData]
        # yColorBC = [(heat - 5) for heat in yDataBC]

        # make subplot for PAAS A
        labelAddOn = "of PAAS A " if pro == 1 else ""
        plt.subplots(1,1,figsize=(12,7))
        plt.grid(color='k', linestyle='-', linewidth=1)
        plt.plot_date(xData, yDataA, label="PAAS A", markersize=2)  # make plot
        mpl.dates.HourLocator()
        plt.xlabel("Time", fontsize=20)  # set x axis label
        plt.ylabel(f'Temperature {labelAddOn}(°C)', fontsize=20)  # set y axis label
        plt.ylim(0.,65.)

        if pro > 1:
            letter = "B" if pro == 2 else "C"
            plt.plot_date(xData, yDataBC, label=f'PAAS {letter}', markersize=2)  # make plot
            plt.legend(loc="upper left")

        plt.tight_layout()
        plt.show()

    # graph leak data in pop up window
    # parameters: listItem, a QListWidgetItem from self.ui.leakTestsLW
    # returns: nothing returned
    def graphLeak(self, listItem):
        # if they clicked the list item at the top with instructions return early
        if len(listItem.toolTip()) == 0:
            return
        # name of tag clicked is the ending of the tooltip string for that item
        # see the leak tests loop in displayPro8() for how tooltip is set
        # if the actual name of the tag starts with whitespace a bug could arise
        tagName = ((listItem.toolTip())[30:]).lstrip()

        # do a stupid inefficient search that could probably be avoided with better signals
        testID = -1
        for toop in self.data.leakTests:
            if toop[0] == tagName:
                testID = toop[2]
        
        # if can't find id then bail
        if testID == -1:
            tkinter.messagebox.showerror(
                title="Error",
                message=f"Couldn't find an id for the leak test with tag {tagName}.",
            )
            logger.error(f'Couldnt find an id for the leak test with tag {tagName}')
            return

        # this next part will likely cause a bit of lag
        # next is setting up a database table and getting a the relevant data
        # can be up to if not more than 8000 tuples with 7 data points each
        # doesn't have a find data function because of the sheer amount of data required
        # don't want to have to take up space on ram unnecessarily

        leakTable = sqla.Table(
            "measurement_panel_leak", self.metadata, autoload=True, autoload_with=self.engine
        )

        leakQuery = sqla.select(
            [
                leakTable.columns.elapsed_days,   # time in days
                leakTable.columns.pressure_diff,  # deltaP
                leakTable.columns.temp_box,       # temp of box
                leakTable.columns.temp_room,      # ambient temp
                leakTable.columns.pressure_ref,   # room air pressure?
                leakTable.columns.pressure_fill   # leak pressure? idk im not physicist
            ]
        ).where(leakTable.columns.trial == testID)

        #perfMeasure = time.perf_counter() # how fast is it going? not essential
        resultProxy = self.connection.execute(leakQuery)  # make proxy
        rawLeakData = resultProxy.fetchall()  # get data from db
        #perfMeasure = time.perf_counter() - perfMeasure # how fast? not essential

        #print(f'{len(rawLeakData)} measurements found in {perfMeasure} seconds.')

        # if no data then don't bother
        if len(rawLeakData) == 0:
            tkinter.messagebox.showerror(
                title="Error",
                message=f"Couldn't find any data for the leak test with tag {tagName}.",
            )
            return
        
        # if small amount of data, tell the user
        if len(rawLeakData) < 60:
            tkinter.messagebox.showinfo(
                title="Few data points found",
                message=f"Only {len(rawLeakData)} measurements were found.",
            )


        # make lists for each group of data, x values are common for all
        # could be written in half the lines but that would be like 6 big loops
        xData = []
        yPDiff = []
        yTBox = []
        yTRoom = []
        yPRef = []
        yPFill = []
        for toop in rawLeakData:
            xData += [toop[0]]
            yPDiff += [toop[1]]
            yTBox += [toop[2]]
            yTRoom += [toop[3]]
            yPRef += [toop[4]]
            yPFill += [toop[5]]


        fig, ax2 = plt.subplots(2,1) # create figure, top subplot is ax2[0], bottom is ax2[1]
        fig.suptitle(f'Panel MN{self.data.humanID} Leak Test (Tag: {tagName})', fontsize=25) # big title
        ax1 = ax2[0].twinx() # add "second" y-axis to right side
        ax2[0].set_xlabel("Time, Elapsed Days", fontsize=20)
        ax2[0].tick_params(axis='x', labelsize=15) # change tick font size

        ax1.set_ylabel("Temperature (°C)", fontsize=20)
        ax1.plot(xData, yTBox, c="#20fc03", markersize=2, label = "Temp. Box") # plot box temp
        ax1.plot(xData, yTRoom, c="#0313fc", markersize=2, label = "Temp. Room") # plot room temp
        ax1.tick_params(axis='y', labelsize=15)
        ax1.legend(["Temp. Box", "Temp. Room"], loc = "lower left") # create legend for temps

        # since ax1 is the return value of ax2[0].twinx() and not subplots() no indexing needed
        ax2[0].set_xlabel("Elapsed Days", fontsize=20)
        ax2[0].set_ylabel("Diff Pressure (PSI)", color="#fc0303", fontsize=20)
        ax2[0].plot(xData, yPDiff, c="#fc0303", markersize=2, label="P Diff") # plot pressure diff
        ax2[0].tick_params(axis='y', labelcolor="#fc0303", labelsize=15)

        # second subplot
        ax2[1].set_xlabel("Elapsed Days", fontsize=20)
        ax2[1].tick_params(axis='x', labelsize=15)
        ax2[1].set_ylabel("Pressure (PSI)", fontsize=20)
        ax2[1].plot(xData, yPRef, c="#fc0303", markersize=2, label= "P ref") # plot P ref
        ax2[1].plot(xData, yPFill, c="#0313fc", markersize=2, label= "P fill") # plot P fill
        ax2[1].legend(["$P_{Ref}$", "$P_{Fill}$"], loc = "lower left", fontsize=15) # funky syntax for subscript
        
        ax2[0].grid(color="#fc0303")
        ax2[1].grid()

        fig.tight_layout()
        plt.show()


    # ███████╗██╗  ██╗██████╗  ██████╗ ██████╗ ████████╗    ██████╗  █████╗ ████████╗ █████╗
    # ██╔════╝╚██╗██╔╝██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝    ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗
    # █████╗   ╚███╔╝ ██████╔╝██║   ██║██████╔╝   ██║       ██║  ██║███████║   ██║   ███████║
    # ██╔══╝   ██╔██╗ ██╔═══╝ ██║   ██║██╔══██╗   ██║       ██║  ██║██╔══██║   ██║   ██╔══██║
    # ███████╗██╔╝ ██╗██║     ╚██████╔╝██║  ██║   ██║       ██████╔╝██║  ██║   ██║   ██║  ██║
    # ╚══════╝╚═╝  ╚═╝╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝       ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝

    # graph heat data in pop up window
    # parameters:   dataName, string used in making file name
    #               dataType, pointer to whatever self.data list is being used
    #               dataCols, tuple of strings to name columns in csv
    # returns: nothing returned
    def exportData(self,dataName,dataType,dataCols):
        # if there are very few data points...
        if len(dataType) == 0:
            tkinter.messagebox.showerror(
                title="Error",
                message="No data points found, unable to export data.",
            )
            return
        if len(dataType) < 10:
            # make a question popup
            qM = QMessageBox()
            answer = qM.question(
                self,'',f'{len(dataType)} data point(s) were found.  Do you still want to export the data?', qM.Yes | qM.No
            )
            # if the user doesn't want to plot len(dataType) points, then don't!
            if answer == qM.No:
                return

        filePath = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        dataName.replace(" ","_")
        filePath += f"\MN{self.data.humanID}_{dataName}.csv"
        with open(
            filePath, "w", newline=""
        ) as csvFile:
            csvWriter = csv.writer(csvFile)
            dataName.replace("_"," ")
            csvWriter.writerow([f"MN{self.data.humanID} {dataName}"])
            csvWriter.writerow(dataCols)
            csvWriter.writerows(dataType)
            tkinter.messagebox.showinfo(
                title="Data Exported",
                message=f"Data exported to {filePath}",
            )


# fmt: off
# ███╗   ███╗ █████╗ ██╗███╗   ██╗
# ████╗ ████║██╔══██╗██║████╗  ██║
# ██╔████╔██║███████║██║██╔██╗ ██║
# ██║╚██╔╝██║██╔══██║██║██║╚██╗██║
# ██║ ╚═╝ ██║██║  ██║██║██║ ╚████║
# ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝
# DEFINITELY NOT the thing that starts up the program
# fmt: on


def run():
    app = QApplication(sys.argv)  # make an app
    app.setStyle(QStyleFactory.create("Fusion"))  # aestetics
    window = facileDBGUI(Ui_MainWindow())  # make a window

    # Read from the 'network' database
    database = None
    try:
        database = pkg_resources.read_text(resources, "dbvDatabasePath.txt")
    except FileNotFoundError:
        print(
            "Can't find resources/dbvDatabasePath.txt.\n"
            "Running the python setup.py will (re)make it."
        )
        sys.exit()

    database = database.rstrip()

    try:
        window.connectToDatabaseRO(database)  # link to database
    except sqla.exc.OperationalError:  # unable to open database file
        print(
            "Problem accessing database,",
            database,
            "\nMake sure that the " "DB exists.",
        )
        sys.exit()

    window.setWindowTitle("Database Viewer, Connected to " + str(database))
    window.showMaximized()  # open in maximized window (using show() would open in a smaller one with weird porportions)

    app.exec_()  # run the app!


if __name__ == "__main__":
    run()
