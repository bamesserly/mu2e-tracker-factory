#  - -    --   - - /|_/|          .-----------------------.
#  _______________| @.@|         /  Written by Adam Arnett )
# (______         >\_W/<  ------/  Created 05/28/2020     /
#  -   / ______  _/____)       /  Last Update 04/20/2021 /
# -   / /\ \   \ \            (  PS: Meow! :3           /
#  - (_/  \_) - \_)            `-----------------------'
import sys, time, csv, getpass, os, tkinter, tkinter.messagebox, itertools, statistics

# for creating app, time formatting, saving to csv, finding local db, popup dialogs, longest_zip iteration function, stat functions
from datetime import timedelta

# time formatting

# import qdarkstyle  # commented out since most machines don't have this and it has to be installed with pip
import sqlalchemy as sqla  # for interacting with db
import sqlite3  # for connecting with db
import matplotlib.pyplot as plt  # for plotting
import matplotlib as mpl  # also for plotting
import pandas as pd  # even more plotting

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
    QMessageBox,
)

# mostly for gui window management, QPen and QSize are for plotting
from PyQt5.QtGui import QBrush, QIcon, QPen
from PyQt5.QtCore import Qt, QRect, QObject, QDateTime, QSize

# for time formatting
from datetime import datetime

# all for plotting apparently...
import sip
import numpy as np
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
# Accesses either network (X:\Data\database.db) or local (C:\Users\{getpass.getuser()}\Desktop\production\Data\database.db)
# Using local is necessary if you're on a computer not connected to the network (personal laptop for development)
ISLAB = (getpass.getuser() == "mu2e" or getpass.getuser() == ".\mu2e")
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

        # create panelData member, pretty much all data is stored here
        # would it be more efficient to store data only in the widgets?
        # it might not be feasible, all the heat measurements would have
        # to go somewhere, and nobody cares about individual heat measurements
        self.data = PanelData()

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
            ro_sql3_connection_uri = "file:" + database + "?mode=ro"
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
                "Tension (g)",
                1000
            )
        )
        self.ui.strawPlotButton_2.clicked.connect(
            lambda: self.graphSimple(
                self.data.strawData,
                "Tension (g)",
                1000
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
                "Tension (g)",
                120
            )
        )
        self.ui.wirePlotButton_2.clicked.connect(
            lambda: self.graphSimple(
                self.data.wireData,
                "Tension (g)",
                120
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
        print("debug - submit clicked")
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

    # parameters: ???
    # returns: nothing returned
    def graphComboPressed(self,text):
        # local function to call function to graph hv
        def graphHV(self,dataType):
            try:
                self.graphSimple(
                    dataType,
                    "Current (μA)",
                    0.5,
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

        callDict = {
            "Process 3, 1100V"  : (lambda: graphHV(self, self.data.hv1100P3)),
            "Process 3, 1500V"  : (lambda: graphHV(self, self.data.hv1500P3)),
            "Process 5"         : (lambda: graphHV(self, self.data.hvXXXXP5)),
            "Process 6, 1500V"  : (lambda: graphHV(self, self.data.hv1500P6)),
            "Process 1, Inner Rings": (lambda: graphHeat(self, 1)),
            "Process 2, Straws"     : (lambda: graphHeat(self, 2)),
            "Process 6, Manifold"   : (lambda: graphHeat(self, 6)),
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
            "Process 5"         : (lambda: self.updateCombo(5,1)),
            "Process 6, 1500V"  : (lambda: self.updateCombo(6,1500)),
            "Process 1, Inner Rings": (lambda: self.updateCombo(1,0)),
            "Process 2, Straws"     : (lambda: self.updateCombo(2,0)),
            "Process 6, Manifold"   : (lambda: self.updateCombo(6,0)),
            "Select"                : (lambda: 0)
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
    #               volts, int representing the voltage for hv, if updating heat, volts = 0
    # returns: 0 if success, 1 if failure
    def updateCombo(self, pro, volts):
        if not volts:
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
            return 0

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
        funcRetIII = self.findSpecificHV(6,1500)
        hasData = hasData or funcRetI or funcRetII or funcRetIII
        # find heat data
        funcRetI = self.findSpecificHeat(1)
        funcRetII = self.findSpecificHeat(2)
        funcRetIII = self.findSpecificHeat(6)
        hasData = hasData or funcRetI or funcRetII or funcRetIII

        #print(str(self.data))
        return hasData

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

        # return bool
        return (len(retList) > 0)

    # finds LPALs and stores them in self.data.parts, called by findParts
    # LPALs have their own find function because they are different than the other parts
    # parameters: no parameters
    # returns: nothing returned (yet)
    # TODO: CHECK TO MAKE SURE THIS FINDS CORRECT DATA
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
        for x in range(96):  # for x = 0 to 96
            self.data.strawData += [
                (x, "No Data", "No Data", 0)
            ]  # assign "data" to strawTensionData

        # The following for loop goes through the raw data and puts it into self.data.strawData.  It will only put data into
        # self.data.strawData if the raw data has a timestamp newer than the existing one in self.data.strawData, in order to
        # filter out old data.  So if a tuple from rawStrawData for position 5 is found, and self.data.strawData already
        # has data for position 5, it will replace the existing data if the timestamp from the raw data is newer than the
        # already existing one.
        # self.data.strawData[toop[0]][3] gets index 3 (time) from the tuple at the index in strawTensionData equal
        # to index 0 (position) of toop (data from rawStrawData)

        retList = []

        for toop in rawStrawData:
            retList.append(toop)
            if self.data.strawData[toop[0]][3] < toop[3]:
                # tuple has form: (<position>, <tension>, <epoch timestamp>, <uncertainty>)
                self.data.strawData[toop[0]] = (toop[0],toop[1],toop[3],toop[2])

        # return true if any data found
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


        self.data.wireData = []  # ensure wireTensionData is clear
        for x in range(96):  # for x = 0 to 96
            self.data.wireData += [
                (x, "No Data", 0)
            ]  # assign "data" to wireTensionData
        # this loop filters out old data, there's a better explaination for the analagous loop for strawTensionData
        retList = []
        for toop in rawWireData:
            retList.append(retList)
            if self.data.wireData[toop[0]][2] < toop[4]:
                self.data.wireData[toop[0]] = (toop[0],toop[1],toop[4])

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

        hvList = []
        
        for x in range(96):  # for x = 0 to 96
            hvList += [
                (x, "No Data", "No Data", False, 0)
            ]  # assign "data" to hvList
        # this loop filters out old data, there's a better explaination for the analagous loop for strawTensionData
        retList = []
        for toop in rawHVData:
            retList.append(toop)
            if hvList[toop[0]][4] < toop[4]:
                hvList[toop[0]] = toop

        lCount = 0
        rCount = 0
        for lst in hvList:
            if lst[1] is not None:
                lCount += 1
            if lst[2] is not None:
                rCount += 1
        
        if lCount > rCount:
            for i,toop in enumerate(hvList):
                hvList[i] = (toop[0],toop[1],toop[3],"L",toop[4])
        else:
            for i,toop in enumerate(hvList):
                hvList[i] = (toop[0],toop[2],toop[3],"R",toop[4])

        targetList = getattr(self.data, f'hv{volts}P{pro}')

        targetList += hvList

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
            heatList.append(
                    (
                        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(toop[0])),
                        toop[0],
                        toop[1] if (0 < toop[1] and toop[1] < 150) else None,
                        toop[2] if (0 < toop[2] and toop[2] < 150) else None,
                    )
                )
        # assign built list to self.data
        listPointer = getattr(self.data,f'p{pro}HeatData')
        listPointer += heatList

        return (len(heatList) > 0)


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
        # goes through each pro and adds each pro's comments to the
        # corresponding list widget
        for key in self.data.comLists:
            listWidget = self.getWid(f'{key}ComList')
            for comment in self.data.comLists[key]:
                listWidget.addItem(
                    f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(comment[1]))}\n{comment[0]}'
                )

    # puts part IDs on the gui
    # parameters: no parameters
    # returns: nothing returned
    def displayParts(self):
        # this helper takes widget name, returns pointer to that widget
        def getPartWidget(self, widget):
            try:
                return self.getWid(f"part{widget}LE")
            except:
                tkinter.messagebox.showerror(
                    title="Error",
                    message=f'Key Error: No part found with name "{widget}".\nPerhaps an L/R or A/B/C was not found in the database?',
                )
                return self.ui.label_2
            
        # for each type of part,
        for key in self.data.parts:
            # make sure we actually have an id
            if self.data.parts[key] == []:
                # if not, let it know we don't
                self.data.parts[key] = -1
            # set the corresponding widget to the key's number
            if self.data.parts[key] > -1:
                getPartWidget(self, key).setText(str(self.data.parts[key]))
                self.ui.label_2.setText(f"MN{str(self.data.humanID).zfill(3)}")
            else:
                getPartWidget(self, key).setText("Not found")
                self.ui.label_2.setText(f"MN{str(self.data.humanID).zfill(3)}")

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

        noData = True
        for dataToop in dataType:  # for each tuple in data
            itemString = "" # build a string
            # for each piece of data (position, tension, etc.)
            for i in range(len(dataCols)):
                if dataCols[i][1] != -1:
                    itemString += f'{str(dataToop[i]).ljust(dataCols[i][1])}'
            if "No Data" not in itemString:
                noData = False
            for lst in listWidgets:
                lst.addItem(itemString)

        # check if no data was added or all data is "No Data"
        # if so, only display "No data found :("
        for lst in listWidgets:
            if lst.count() == 0:
                lst.addItem("No data found :(")
            if noData:
                lst.clear()
                lst.addItem("No data found :(")
                for button in buttons:
                    button.setDisabled(True)

    # general function to graph any data on the main window
    # TODO: actually write the function lol
    def displayOnGraph(self,dataType,xAxis,yAxis,graphType,targetLayout):
        targetLayout.addWidget(QLabel("Graph coming soon!"))
        return

    def displayOnGraphHEAT(self,pro):
        # clear current plot
        for i in reversed(range(self.ui.heatGraphLayout.count())): 
            self.ui.plotLayout.itemAt(i).widget().setParent(None)

        if len(getattr(self.data,f'p{pro}HeatData')) == 0:
            self.ui.heatGraphLayout.addWidget(QLabel("Insufficient Data."))
            return
        else:
            localHeat = getattr(self.data,f'p{pro}HeatData')

        plot = qwt.QwtPlot(self)
        plot.setTitle(f"MN{self.data.humanID} Pro {pro} Heat Data")

        plot.setAxisScaleDraw(
            qwt.QwtPlot.xBottom, TimeScaleDraw(
                QDateTime.fromMSecsSinceEpoch(localHeat[0][1])
            )
        )
        plot.setAxisTitle(0,"Temperature (°C)")
        #plot.setCanvasBackground(Qt.black)
        # y axis is temperature
        # first remove tuples where no measurements for A or B/C
        localHeat = [toop for toop in localHeat if (toop[2] or toop[3])]
        paasA = [toop[2] if toop[2] else 1 for toop in localHeat]
        paasBC = [toop[3] if toop[3] else 1 for toop in localHeat]
        time = [toop[1] for toop in localHeat]
        curveA = qwt.QwtPlotCurve("PAAS A")
        curveA.setPen(QPen(Qt.darkBlue))
        curveA.setData(time, paasA)
        curveA.attach(plot)

        if pro == 2:
            curveB = qwt.QwtPlotCurve("PAAS B")
            curveB.setPen(QPen(Qt.red))
            curveB.setData(time, paasBC)
            curveB.attach(plot)
        if pro == 6:
            curveB = qwt.QwtPlotCurve("PAAS C")
            curveB.setPen(QPen(Qt.red))
            curveB.setData(time, paasBC)
            curveB.attach(plot)

        grid = qwt.QwtPlotGrid()
        grid.attach(plot)
        grid.setPen(QPen(Qt.black, 0, Qt.DotLine))

        plot.replot()
        self.ui.heatGraphLayout.addWidget(plot)

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
            paasATemps = [toop[2] for toop in heatData if toop[2]]
            paasBCTemps = [toop[3] for toop in heatData if toop[3]]

            if len(paasATemps) > 0:  # if paas A data exits
                # make a list of stats
                paasAStats = [
                    "PAAS A (Blue on graph) Statistics",
                    f'Mean: {statistics.mean(paasATemps)}',  # mean of paas A
                    f'Min: {min(paasATemps)}',  # min of paas A
                    f'Max: {max(paasATemps)}',  # max of paas A
                    f'Std Dev: {statistics.stdev(paasATemps)}',  # standard dev of paas A
                    f'Upper σ: {statistics.mean(paasATemps)- statistics.stdev(paasATemps)}',  # upper std dev
                    f'Lower σ: {statistics.mean(paasATemps) + statistics.stdev(paasATemps)}',  # lower std dev
                ]
            if len(paasBCTemps) > 0 and pro != 1:  # if paas B/C exists
                # make a list of stats
                paasBCStats = [
                    f'\nPAAS {"B" if pro == 2 else "C"} (Red on graph) Statistics',
                    f'Mean: {statistics.mean(paasBCTemps)}',  # mean of paas BC
                    f'Min: {min(paasBCTemps)}',  # min of paas BC
                    f'Max: {max(paasBCTemps)}',  # max of paas BC
                    f'Std Dev: {statistics.stdev(paasBCTemps)}',  # standard dev of paas BC
                    f'Upper σ: {statistics.mean(paasBCTemps)- statistics.stdev(paasBCTemps)}',  # upper std dev
                    f'Lower σ: {statistics.mean(paasBCTemps) + statistics.stdev(paasBCTemps)}',  # lower std dev
                ]
            
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
    # returns: nothing returned
    def graphSimple(self,dataType,yAxis,yUpperBound,errorBars=False):
        # all "simple" data types will have 96 points
        xData = list(range(96))
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

        plt.subplot(211)
        # plt.figure(figsize=(12,8))
        if errorBars:
            try:
                plt.errorbar(
                    xData, sctrYDataPoints, yerr=sctrYDataUncs, fmt="o"
                )  # make a scatterplot out of the x and y data
            except:
                print("Insufficient data to plot error bars.")
        else:
            plt.scatter(xData, sctrYDataPoints)  # make a scatterplot out of the x and y data

        plt.axis([0, 100, 0, yUpperBound])  # set the bounds of the graph
        plt.xlabel("Position", fontsize=20)  # set x axis label
        plt.ylabel(yAxis, fontsize=20)  # set y axis label
        for x, y in enumerate(sctrYDataPoints):  # go through y data, enumerate for x
            if y is not None:  # if y exists and is too low...??? wat
                plt.annotate(f"{x}", (x, y), fontsize=8)  # annotate that point

        plt.subplot(212)  # make subplot 2
        histYData = []  # make list to filter out None types

        for y in sctrYDataPoints:  # go through scatter y data
            if y != None:  # if it's not a None type
                histYData += [y]  # add it to the new histogram y data
        n, bins, patches = plt.hist(histYData, 20)  # plot histogram
        plt.xlabel(yAxis, fontsize=20)  # set x axis label
        plt.ylabel("Frequency", fontsize=20)  # set y axis label

        plt.tight_layout()
        # mpl.rcParams['figure.dpi'] = 600        # make the graph itself bigger (deault is super smol)
        plt.show()

    # graph heat data in pop up window
    # parameters: pro, an int for which procedure (1, 2, or 6)
    # returns: nothing returned
    def graphSpecificHeat(self, pro):
        heatData = getattr(self.data,f'p{pro}HeatData')

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
        plt.subplot(211)
        plt.plot_date(xData, yDataA, label="PAAS A")  # make plot
        mpl.dates.HourLocator()
        plt.xlabel("Time", fontsize=20)  # set x axis label
        plt.ylabel(f'Temperature {labelAddOn}(°C)', fontsize=20)  # set y axis label

        if pro > 1:
            letter = "B" if pro == 2 else "C"
            plt.plot_date(xData, yDataBC, label=f'PAAS {letter}')  # make plot
            plt.legend(loc="upper left")

        plt.tight_layout()
        plt.show()


    # ███████╗██╗  ██╗██████╗  ██████╗ ██████╗ ████████╗    ██████╗  █████╗ ████████╗ █████╗ 
    # ██╔════╝╚██╗██╔╝██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝    ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗
    # █████╗   ╚███╔╝ ██████╔╝██║   ██║██████╔╝   ██║       ██║  ██║███████║   ██║   ███████║
    # ██╔══╝   ██╔██╗ ██╔═══╝ ██║   ██║██╔══██╗   ██║       ██║  ██║██╔══██║   ██║   ██╔══██║
    # ███████╗██╔╝ ██╗██║     ╚██████╔╝██║  ██║   ██║       ██████╔╝██║  ██║   ██║   ██║  ██║
    # ╚══════╝╚═╝  ╚═╝╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝       ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝

    def exportData(self,dataName,dataType,dataCols):
        # if there are very few data points...
        if len(dataType) < 10:
            # make a question popup
            qM = QMessageBox()
            answer = qM.question(
                self,'',f'{len(dataType)} data points were found.  Do you still want to export the data?', qM.Yes | qM.No
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
    # app.setStyleSheet(qdarkstyle.load_stylesheet()) # darkmodebestmode
    window = facileDBGUI(Ui_MainWindow())  # make a window
    database = ""
    # Access network DB
    if ISLAB:
        database = pkg_resources.read_text(resources, "networkDatabasePath.txt")
    # Access local DB
    else:
        with pkg_resources.path(data, "database.db") as p:
            database = p.resolve()
    window.connectToDatabaseRO(database)  # link to database
    window.setWindowTitle("Database Viewer, Connected to " + database)
    window.showMaximized()  # open in maximized window (using show() would open in a smaller one with weird porportions)

    app.exec_()  # run the app!


if __name__ == "__main__":
    run()