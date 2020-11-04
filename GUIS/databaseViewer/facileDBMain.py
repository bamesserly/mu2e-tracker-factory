#  - -    --   - - /|_/|          .-----------------------.
#  _______________| @.@|         /  Written by Adam Arnett )
# (______         >\_W/<  ------/  Created 5/28/2020      /
#  -   / ______  _/____)       /  Last Update 10/25/2020 /
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
)
from PyQt5.QtGui import QBrush, QIcon

# for GUI widget management^
from PyQt5.QtCore import Qt, QRect, QObject  # for gui window management
from datetime import datetime  # for time formatting
from facileDB import Ui_MainWindow  # import raw UI


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
# fmt: on




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
    def __init__(self, ui_layout):
        # setup UI
        QMainWindow.__init__(self)  # initialize superclass
        self.ui = ui_layout  # make ui member
        ui_layout.setupUi(self)  # apply ui to window
        self.tkRoot = tkinter.Tk()  # make tkinter root for popup messages
        self.tkRoot.withdraw()  # hide root, it's necessary for popups to work, but it's just a blank window otherwise

        dir_path = os.path.dirname(os.path.realpath(__file__))  # put icon in upper left
        self.setWindowIcon(QIcon(f'{dir_path}\\mu2e.jpg'))

        self.initInputWidgets()

        # panel variables
        self.panelNumber = (
            -1
        )  # Keep track of current panel being displayed (input by user)
        self.panelDatabaseID = (
            -1
        )  # Keep track of current panel's straw_location ID (query for later)
        self.panelProcedureIDs = {  # Keep track of the panels procedure IDs in the database (query for later)
            "pan1": -1,
            "pan2": -1,
            "pan3": -1,
            "pan4": -1,
            "pan5": -1,
            "pan6": -1,
            "pan7": -1,
        }
        self.comListWidgetList = [  # comment QListWidgets for easy organization
            self.ui.ringsComList,
            self.ui.strawsComList,
            self.ui.senseComList,
            self.ui.pinsComList,
            self.ui.highComList,
            self.ui.manifoldComList,
            self.ui.floodingComList,
        ]

        # more lists, because I demand control of all the RAM
        # the next three lists are filled by findMeasurements()
        self.hvData = []
        self.strawTensionData = []
        self.wireTensionData = []
        # heat lists are initialized as bools in findHeat() then changed to lists in findHeat()

        self.partSetupWidgetList = [  # list of line edits for part
            self.ui.partBasePlateLE,
            self.ui.partMIRLE,
            self.ui.partBIRLE,
            self.ui.partPLALE,
            self.ui.partPLBLE,
            self.ui.partPLCLE,
            self.ui.partPRALE,
            self.ui.partPRBLE,
            self.ui.partPRCLE,
            self.ui.partALF1LE,
            self.ui.partALF2LE,
            self.ui.partPaasALE,
            self.ui.partPaasBLE,
            self.ui.partPaasCLE
        ]


    # make engine, connection, and metadata objects to interact with NETWORK database
    def connectToNetwork(self):
        # override connect to return a read-only DB connection, MUST use path starting at C drive (or any drive, X, Z, etc.)
        # more on this: https://github.com/sqlalchemy/sqlalchemy/issues/4863
        # this function returns a read only connection to the .db file at the secified location
        def connectSpecial():
            return sqlite3.connect(
                "file:X:\Data\database.db?mode=ro", uri=True
            )

        # this create_engine call uses connectSpecial to open the sqlite database in read only
        self.engine = sqla.create_engine(
            "sqlite:///../../Data/database.db/", creator=connectSpecial
        )  # create engine

        # try to use read only mode
        # give error message to allow for quick debugging if it fails
        try:
            self.connection = self.engine.connect()  # connect engine with DB
        except:
            tkinter.messagebox.showerror(
                title="Error",
                message=f"Network read-only mode failed.  Contact a member of the software team for help.",
            )  # show error message
            sys.exit()


        self.metadata = sqla.MetaData()  # create metadata
        self.initSQLTables()  # create important tables

    # make engine, connection, and metadata objects to interact with LOCAL database
    def connectToLocal(self):
        
        # override connect to return a read-only DB connection, MUST use path starting at C drive (or any drive, X, Z, etc.)
        # more on this: https://github.com/sqlalchemy/sqlalchemy/issues/4863
        # this function returns a read only connection to the .db file at the secified location
        # getpass.getuser() fetches the current username
        # double backslashes are necessary because \U is a unicode escape, but \\U is not
        def connectSpecial(dbPath):
            return sqlite3.connect(
                f'file:C:\\Users\\{getpass.getuser()}\\Desktop\\production\\Data\\database.db?mode=ro',
                uri=True
                )

        # this create_engine call uses connectSpecial to open the sqlite database in read only
        self.engine = sqla.create_engine(
            "sqlite:///../../Data/database.db/", creator=connectSpecial
        )  # create engine

        # try to use read only mode
        # give error message to allow for quick debugging if it fails
        try:
            self.connection = self.engine.connect()  # connect engine with DB
        except:
            tkinter.messagebox.showerror(
                title="Local Error",
                message=f"Local read-only mode failed.  Contact a member of the software team for help.",
            )  # show error message
            sys.exit()


        self.metadata = sqla.MetaData()  # create metadata
        self.initSQLTables()  # create important tables

    # initialize important tables
    def initSQLTables(self):
        self.panelsTable = sqla.Table(
            "straw_location", self.metadata, autoload=True, autoload_with=self.engine
        )  # straw_location
        self.proceduresTable = sqla.Table(
            "procedure", self.metadata, autoload=True, autoload_with=self.engine
        )  # procedure

    def initInputWidgets(self):
        # link widgets and things
        # bind function for submit button
        self.ui.submitPB.clicked.connect(self.findPanel)
        # bind function for export wire tension stuff
        self.ui.wireExportButton.clicked.connect(self.exportWireMeasurements) 
        # bind function for wire plot button
        self.ui.plotWireDataButton.clicked.connect(self.plotWireData)  
        # bind function for export straw tension data
        self.ui.strawExportButton.clicked.connect(self.exportStrawMeasurements)
        # bind function for plot straw tension data
        self.ui.plotStrawDataButton.clicked.connect(self.plotStrawData)
        # bind funciton for export HV data
        self.ui.hvExportButton.clicked.connect(self.exportHVMeasurements)
        # bind function for plot HV data
        self.ui.plotHVDataButton.clicked.connect(self.plotHVData)
        # bind function for export heat data
        self.ui.heatExportButton.clicked.connect(self.exportHeatMeasurements)
        # bind function for plot heat data
        self.ui.plotHeatDataButton.clicked.connect(self.plotHeatData)

        # bind function for heat combo box change
        self.ui.heatProBox.currentIndexChanged.connect(self.displayHeat)
        
        

# fmt: off
# ██████╗ ███████╗ █████╗ ██████╗     ███████╗██████╗  ██████╗ ███╗   ███╗    ██████╗ ██████╗ 
# ██╔══██╗██╔════╝██╔══██╗██╔══██╗    ██╔════╝██╔══██╗██╔═══██╗████╗ ████║    ██╔══██╗██╔══██╗
# ██████╔╝█████╗  ███████║██║  ██║    █████╗  ██████╔╝██║   ██║██╔████╔██║    ██║  ██║██████╔╝
# ██╔══██╗██╔══╝  ██╔══██║██║  ██║    ██╔══╝  ██╔══██╗██║   ██║██║╚██╔╝██║    ██║  ██║██╔══██╗
# ██║  ██║███████╗██║  ██║██████╔╝    ██║     ██║  ██║╚██████╔╝██║ ╚═╝ ██║    ██████╔╝██████╔╝
# ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝     ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝    ╚═════╝ ╚═════╝ 
# Functions that read from the SQL database
# Find panel is a pretty important function, it's tied to the submit button and clears data
#   from the GUI, checks for the existence of the submitted panel, and changes the top text
#   label all before calling all the other "find" functions
# fmt: on

    # called upon hitting submit (does a lot of stuff)
    def findPanel(self):
        # What it does:
        # gets rid of data on the gui
        # changes the panel ID on the top of the gui
        # checks if the requested panel exists, if not gives error popup
        # finally calls all the functions that read data from the database
        #   which in turn call all the display functions (should a seperate
        #   thing call those maybe?)

        # first get rid of any existing data
        self.panelDatabaseID = -1  # reset panel database ID
        for widget in self.comListWidgetList:  # clear comments from list widgets
            widget.clear()
        for widget in self.partSetupWidgetList:  # erase all part IDs
            widget.setText("")
        for key in self.panelProcedureIDs:  # "rip up" the dictionary (keep keys of course)
            self.panelProcedureIDs[key] = -1
        # clear lists
        self.ui.hvListWidget.clear()  # clear text in widget
        self.hvData = []  # clear saved data
        self.ui.strawListWidget.clear()
        self.strawTensionData = []
        self.ui.wireListWidget.clear()
        self.wireTensionData = []

        # get new data and do stuff with it!
        self.panelNumber = self.ui.panelLE.text()  # get panel number from user input
        self.ui.label_2.setText(
            f"MN{str(self.panelNumber).zfill(3)}"
        )  # set label on top of gui (zfill because all panels have 3 numeric digits)
        self.findPanelDatabaseID()  # get the panels id in the straw_location table in the db
        if self.panelDatabaseID == -1:  # if the panel is not in the db
            tkinter.messagebox.showerror(  # show error message
                title="Error",  # name it 'Error'
                message=f"No data for MN{str(self.panelNumber).zfill(3)} was found.",  # give it this string for a message
            )
            return  # return to avoid errors (if self.panelDatabaseID == -1)
        self.findProcedures()  # get procedure IDs (get data for self.panelProcedureIDs)
        self.findComments()  # get comments, put them into list widgets
        self.findPanelParts()  # get part IDs, put them into disabled line edit widgets
        self.findMeasurements()  # get measurements, put them into class member lists and display them
        self.findHeat() # get heat measurements

    # query to assign id to GUI class member (self.panelDatabaseID)
    def findPanelDatabaseID(self):
        panelIDQuery = (
            sqla.select([self.panelsTable.columns.id])
            .where(  # select panel ids
                self.panelsTable.columns.number == self.panelNumber
            )
            .where(  # where number = user input panel number
                self.panelsTable.columns.location_type == "MN"
            )
        )  # and where location type = MN (we don't want LPALs)

        resultProxy = self.connection.execute(panelIDQuery)  # make proxy
        resultSet = (
            resultProxy.fetchall()
        )  # fetch from proxy, which gives [(<PANEL ID>,)]
        if len(resultSet) == 0:  # if nothing returned,
            self.panelDatabaseID = -1  # the panel doesn't exist!
        else:
            self.panelDatabaseID = resultSet[0][
                0
            ]  # since resultSet is a list of tuples, add [0][0] to get an int

    # query to get all procedure IDs for the panel (self.panelProcedureIDs)
    def findProcedures(self):
        proceduresQuery = sqla.select(
            [
                self.proceduresTable.columns.id,
                self.proceduresTable.columns.station,
                self.proceduresTable.columns.timestamp,
            ]
        ).where(  # select pro ids and stations
            self.proceduresTable.columns.straw_location == self.panelDatabaseID
        )  # where straw_location = db panel ID

        resultProxy = self.connection.execute(proceduresQuery)  # make proxy
        self.panelProcedures = (
            resultProxy.fetchall()
        )  # fetch from proxy, gives list of tuples: (<PRO ID>, <STATION>)

        for toop in self.panelProcedures:  # go through results from procedures query
            self.panelProcedureIDs[toop[1]] = toop[0] 
            # assign procedure ID to the corresponding station (above line)
            # self.panelProcedureIDs is a dictionary with the name of each station as keys
        # print(self.panelProcedureIDs)

    # get and display comments for selected panel (TODO: efficiency could be improved)
    def findComments(self):
        comments = sqla.Table(
            "comment", self.metadata, autoload=True, autoload_with=self.engine
        )  # make table

        # make query, it first selects:
        #   self.panelsTable.number where number = self.panelNumber (panel number)
        #   self.proceduresTable.station (process number)
        #   comments.text (comment text)
        #   comments.timestamp (time comment was made)
        comQuery = sqla.select(
            [
                self.panelsTable.columns.number,
                self.proceduresTable.columns.station,
                comments.columns.text,
                comments.columns.timestamp,
            ]
        ).where(self.panelsTable.columns.number == self.panelNumber)
        # since the first select only picked entries from self.panelsTable whose number = self.panelNumber, then we're getting the selected info where
        #   the comment's procedure is one whose panel number is the what the user typed in
        comQuery = comQuery.select_from(
            self.panelsTable.join(
                self.proceduresTable,
                self.panelsTable.columns.id
                == self.proceduresTable.columns.straw_location,
            ).join(
                comments, self.proceduresTable.columns.id == comments.columns.procedure
            )
        )

        resultProxy = self.connection.execute(comQuery)  # execute query
        resultSet = resultProxy.fetchall()  # get all results as list of tuples
        # tuples have the form: (<panel Number>, <process number>, <comment text>, <comment timestamp in epoch time>)

        # now lets plug the comments into the lists!
        for i, listWidget in enumerate(self.comListWidgetList):
            for commentTuple in resultSet:
                if int(commentTuple[1][3]) == (
                    i + 1
                ):  # if process number string index 3 == current list widget process number
                    realTime = time.strftime(
                        "%Y-%m-%d %H:%M:%S", time.localtime(commentTuple[3])
                    )
                    listWidget.addItem(f"{realTime}\n{commentTuple[2]}")

    # for getting the part number, type, and PIR details (L/R, A/B/C), panel_part has all you need. (TODO: Needs comments)
    def findPanelParts(self):
        panelPartUsage = sqla.Table(
            "panel_part_use", self.metadata, autoload=True, autoload_with=self.engine
        )  # panel_part_use    --> panelPartUsage
        panelPartActual = sqla.Table(
            "panel_part", self.metadata, autoload=True, autoload_with=self.engine
        )  # panel_part        --> panelPartActual

        partsQuery = sqla.select(
            [
                self.panelsTable.columns.number,    # panel number
                panelPartUsage.columns.panel_part,  # panel part ID
                panelPartUsage.columns.panel,   # panel straw_location ID
                panelPartUsage.columns.left_right,  # ALF L/R
                panelPartActual.columns.type,  # type of part (MIR, PIR, ALF, etc.)
                panelPartActual.columns.number,  # part number
                panelPartActual.columns.left_right,  # PIR l/R
                panelPartActual.columns.letter,  # PIR A/B/C, PAAS A/B/C
            ]
        ).where(self.panelsTable.columns.number == self.panelNumber)

        partsQuery = partsQuery.select_from(
            self.panelsTable.join(
                panelPartUsage,
                self.panelsTable.columns.id == panelPartUsage.columns.panel,
            ).join(
                panelPartActual,
                panelPartUsage.columns.panel_part == panelPartActual.columns.id,
            )
        )

        resultProxy2 = self.connection.execute(partsQuery)
        resultSet2 = resultProxy2.fetchall()

        for partTuple in resultSet2:
            self.displayPanelParts(partTuple)

    # get HV, straw tension, and wire tension data
    # THIS SHOULD BE SPLIT INTO THREE SEPERATE FUNCTIONS
    def findMeasurements(self):
        # get tables: straw_location, procedure, measurement_wire_tension, measurement_straw_tension, measurement_pan5
        wireTensions = sqla.Table(
            "measurement_wire_tension",
            self.metadata,
            autoload=True,
            autoload_with=self.engine,
        )  # wire_tension
        strawTensions = sqla.Table(
            "measurement_straw_tension",
            self.metadata,
            autoload=True,
            autoload_with=self.engine,
        )  # straw_tension
        hvCurrents = sqla.Table(
            "measurement_pan5", self.metadata, autoload=True, autoload_with=self.engine
        )  # pan5

        # check if we have data for pro 3 --> wire tension
        if self.panelProcedureIDs["pan3"] != -1:
            wireTensionQuery = sqla.select(
                [  # select:
                    wireTensions.columns.position,  # wire position
                    wireTensions.columns.tension,  # wire tension
                    wireTensions.columns.wire_timer,  # wire timer (whatever that is)
                    wireTensions.columns.calibration_factor,  # calibration factor
                    wireTensions.columns.timestamp,
                ]
            ).where(
                wireTensions.columns.procedure == self.panelProcedureIDs["pan3"]
            )  # where procedure = db pro 3 id

            resultProxy3 = self.connection.execute(wireTensionQuery)  # make proxy
            rawWireData = (
                resultProxy3.fetchall()
            )  # fetchall and send to class member, list of tuples: (<POS>, <TEN>, <TIMER>, <CALIB>, <TIME>)

            self.wireTensionData = []  # ensure wireTensionData is clear
            for x in range(96):  # for x = 0 to 96
                self.wireTensionData += [
                    (x, "No Data", "No Data", 0, 0)
                ]  # assign "data" to wireTensionData
            # this loop filters out old data, there's a better explaination for the analagous loop for strawTensionData
            for toop in rawWireData:
                if self.wireTensionData[toop[0]][4] < toop[4]:
                    self.wireTensionData[toop[0]] = toop

        # check if we have data for pro 2 --> straw tension
        if self.panelProcedureIDs["pan2"] != -1:
            strawTensionQuery = sqla.select(
                [  # select
                    strawTensions.columns.position,  # straw position
                    strawTensions.columns.tension,  # straw tension
                    strawTensions.columns.uncertainty,  # measurement uncertainty
                    strawTensions.columns.timestamp,  # measurement timestamp
                ]
            ).where(
                strawTensions.columns.procedure == self.panelProcedureIDs["pan2"]
            )  # where procedure = pro 2 id

            resultProxy4 = self.connection.execute(
                strawTensionQuery
            )  # make proxy (do I need a different proxy every time??  Probably not)
            rawStrawData = resultProxy4.fetchall()  # fetch all and send to class member
            # list of tuples:  (<POS>, <TEN>, <UNCERTAINTY>, <TIME>)
            self.strawTensionData = []  # enure strawTensionData is clear
            for x in range(96):  # for x = 0 to 96
                self.strawTensionData += [
                    (x, "No Data", "No Data", 0)
                ]  # assign "data" to strawTensionData

            # The following for loop goes through the raw data and puts it into self.strawTensionData.  It will only put data into
            # self.strawTensionData if the raw data has a timestamp newer than the existing one in self.strawTensionData, in order to
            # filter out old data.  So if a tuple from rawStrawData for position 5 is found, and self.strawTensionData already
            # has data for position 5, it will replace the existing data if the timestamp from the raw data is newer than the
            # already existing one.
            # self.strawTensionData[toop[0]][3] gets index 3 (time) from the tuple at the index in strawTensionData equal
            # to index 0 (position) of toop (data from rawStrawData)
            for toop in rawStrawData:
                if self.strawTensionData[toop[0]][3] < toop[3]:
                    self.strawTensionData[toop[0]] = toop

        if int(self.panelNumber) < 34:  # if the panel is too old for HV data
            labelBrush = QBrush(Qt.red)  # make a red brush
            labelItem = QListWidgetItem(
                "This panel was created before HV data was recorded in the database"
            )
            # make a list item with text ^
            labelItem.setBackground(labelBrush)  # paint the list item background red
            self.ui.hvListWidget.addItem(labelItem)  # add the item to the list

        # check if we have data for pro 5 --> pan5 measurement
        if self.panelProcedureIDs["pan5"] != -1:
            hvCurrentsQuery = sqla.select(
                [  # select
                    hvCurrents.columns.position,  # wire/straw position
                    hvCurrents.columns.current_left,  # left current
                    hvCurrents.columns.current_right,  # right current
                    hvCurrents.columns.is_tripped,  # trip status
                    hvCurrents.columns.timestamp,  # timestamp
                ]
            ).where(
                hvCurrents.columns.procedure == self.panelProcedureIDs["pan5"]
            )  # where procedure = this panels pan5 procedure
            # fetching from this query will give list of tuples: (<POS>, <L_AMPS>, <R_AMPS>, <TRIP>, <TIME>)

            resultProxy5 = self.connection.execute(hvCurrentsQuery)  # make proxy
            rawHVData = resultProxy5.fetchall()  # get all the data from the query

            self.hvData = []  # ensure hvData is clear
            for x in range(96):  # for x = 0 to 96
                self.hvData += [
                    (x, "No Data", "No Data", "No Data", 0)
                ]  # assign "data" to wireTensionData
            # this loop filters out old data, there's a better explaination for the analagous loop for strawTensionData
            # it also replaces None types with "No Data" so that an absence of data is consistent with other measurement types
            for toop in rawHVData:
                if self.hvData[toop[0]][4] < toop[4]:
                    self.hvData[toop[0]] = list(toop)
                    if self.hvData[toop[0]][1] == None:
                        self.hvData[toop[0]][1] = "No Data"
                    if self.hvData[toop[0]][2] == None:
                        self.hvData[toop[0]][2] = "No Data"

        self.displayMeasurement()  # show the data on the GUI!

    # find and display PAAS heating data
    def findHeat(self):
        # get heat table
        panelHeats = sqla.Table(
            "panel_heat",
            self.metadata,
            autoload=True,
            autoload_with=self.engine
        )

        # make bools to keep track of what data we have
        # originally lists were initialized here, but sqlalchemys fetchall() returns
        #   dumb lists that aren't real lists because you can't concatenate them onto normal lists
        self.pro1HeatData = False
        self.pro2HeatData = False
        self.pro6HeatData = False

        self.pro1AStats = False
        self.pro1BCStats = False
        self.pro1HeatTime = False
        self.pro2AStats = False
        self.pro2BCStats = False
        self.pro2HeatTime = False
        self.pro2AStats = False
        self.pro2BCStats = False
        self.pro2HeatTime = False

        # if a pro 1 exists, get the data!
        if self.panelProcedureIDs["pan1"] != -1:
            pro1HeatQuery = sqla.select(
                [
                    panelHeats.columns.timestamp,   # time temp taken
                    panelHeats.columns.temp_paas_a, # PAAS A temp
                    panelHeats.columns.temp_paas_bc,# PAAS BC temp
                    panelHeats.columns.procedure
                ]
            ).where(panelHeats.columns.procedure == self.panelProcedureIDs["pan1"])
            # where the procedure for the entry is the procedure for this panel
            resultProxy = self.connection.execute(pro1HeatQuery) # make proxy
            rawPro1HeatData = resultProxy.fetchall()    # get data from db
            if rawPro1HeatData is not []:   # check if we actually have data
                self.pro1HeatData = True # we do! huzzah!

        # if a pro 2 exists, get the data!
        if self.panelProcedureIDs["pan2"] != -1:
            pro2HeatQuery = sqla.select(
                [
                    panelHeats.columns.timestamp,   # time temp taken
                    panelHeats.columns.temp_paas_a, # PAAS A temp
                    panelHeats.columns.temp_paas_bc # PAAS BC temp
                ]
            ).where(panelHeats.columns.procedure == self.panelProcedureIDs["pan2"])
            # where the procedure for the entry is the procedure for this panel
            resultProxy = self.connection.execute(pro2HeatQuery) # make proxy
            rawPro2HeatData = resultProxy.fetchall()    # get data from db
            if rawPro2HeatData is not []:   # check if we actually have data
                self.pro2HeatData = True # we do! noice!

        # if a pro 6 exists, get the data!
        if self.panelProcedureIDs["pan6"] != -1:
            pro6HeatQuery = sqla.select(
                [
                    panelHeats.columns.timestamp,   # time temp taken
                    panelHeats.columns.temp_paas_a, # PAAS A temp
                    panelHeats.columns.temp_paas_bc # PAAS BC temp
                ]
            ).where(panelHeats.columns.procedure == self.panelProcedureIDs["pan6"])
            # where the procedure for the entry is the procedure for this panel
            resultProxy = self.connection.execute(pro6HeatQuery) # make proxy
            rawPro6HeatData = resultProxy.fetchall()    # get data from db
            if rawPro6HeatData is not []:   # check if we actually have data
                self.pro6HeatData = True # we do! excellent!
        
        # The tuples in the raw data lists exist in the form: (timestamp, PAAS A temp, PAAS B temp)

        # the next 3 if blocks take the raw data and refine it
        # first it changes the bool into a list, and then puts the raw data in the list, with a human
        # readable timestamp at index 0.
        # second it gets statistics from the refined data temp: min, max, mean, std dev time: total time
        if self.pro1HeatData:
            self.pro1HeatData = [] # switch bool to list

            for toop in rawPro1HeatData:    # for each tuple in list,
                # add that data to the heat data with a human readable timestamp in front
                self.pro1HeatData.append([time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(toop[0])), toop[0], toop[1], toop[2]])
            
            # make lists fo temps for paas A and B/C
            paasATemps = [toop[2] for toop in self.pro1HeatData]
            paasBCTemps = [toop[3] for toop in self.pro1HeatData]

            if len(paasATemps) > 0: # if paas A data exits
                # make a list of stats
                self.pro1AStats = [
                    statistics.mean(paasATemps),    # mean of paas A
                    min(paasATemps),    # min of paas A
                    max(paasATemps),    # max of paas A
                    statistics.stdev(paasATemps),# standard dev of paas A
                    statistics.mean(paasATemps) - statistics.stdev(paasATemps),   # upper std dev
                    statistics.mean(paasATemps) + statistics.stdev(paasATemps)    # lower std dev
                ]
            if len(paasBCTemps) > 0: # if paas B/C exists
                # make a list of stats
                self.pro1BCStats = [
                    statistics.mean(paasBCTemps),    # mean of paas BC
                    min(paasBCTemps),    # min of paas BC
                    max(paasBCTemps),    # max of paas BC
                    statistics.stdev(paasBCTemps),# standard dev of paas BC
                    statistics.mean(paasBCTemps) - statistics.stdev(paasBCTemps),   # upper std dev
                    statistics.mean(paasBCTemps) + statistics.stdev(paasBCTemps)    # lower std dev
                ]
            
            # make a list of heat timestamps
            heatTimes = [toop[1] for toop in self.pro1HeatData]
            # if we have that data
            if len(heatTimes) > 0:
                # find the total time it took
                rawHeatTime = max(heatTimes) - min(heatTimes)
                self.pro1HeatTime = timedelta(rawHeatTime)

        # SEE THE ABOVE IF BLOCK FOR COMMENTS, THIS ONE WORKS THE SAME WAY
        if self.pro2HeatData:
            self.pro2HeatData = []
            for toop in rawPro2HeatData:
                self.pro2HeatData.append([time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(toop[0])), toop[0], toop[1], toop[2]])
            paasATemps = [toop[2] for toop in self.pro2HeatData]
            paasBCTemps = [toop[3] for toop in self.pro2HeatData]
            if len(paasATemps) > 0:
                self.pro2AStats = [
                    statistics.mean(paasATemps),    # mean of paas A
                    min(paasATemps),    # min of paas A
                    max(paasATemps),    # max of paas A
                    statistics.stdev(paasATemps),# standard dev of paas A
                    statistics.mean(paasATemps) - statistics.stdev(paasATemps),   # upper std dev
                    statistics.mean(paasATemps) + statistics.stdev(paasATemps)    # lower std dev
                ]
            if len(paasBCTemps) > 0:
                self.pro2BCStats = [
                    statistics.mean(paasBCTemps),    # mean of paas BC
                    min(paasBCTemps),    # min of paas BC
                    max(paasBCTemps),    # max of paas BC
                    statistics.stdev(paasBCTemps),# standard dev of paas BC
                    statistics.mean(paasBCTemps) - statistics.stdev(paasBCTemps),   # upper std dev
                    statistics.mean(paasBCTemps) + statistics.stdev(paasBCTemps)    # lower std dev
                ]

            heatTimes = [toop[1] for toop in self.pro2HeatData]
            if len(heatTimes) > 0:
                rawHeatTime = max(heatTimes) - min(heatTimes)
                self.pro2HeatTime = timedelta(rawHeatTime)

        # SEE THE ABOVE IF BLOCK FOR COMMENTS, THIS ONE WORKS THE SAME WAY
        if self.pro6HeatData:
            self.pro6HeatData = []
            for toop in rawPro6HeatData:
                self.pro6HeatData.append([time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(toop[0])), toop[0], toop[1], toop[2]])
            
            paasATemps = [toop[2] for toop in self.pro6HeatData]
            paasBCTemps = [toop[3] for toop in self.pro6HeatData]
            if len(paasATemps) > 0:
                self.pro6AStats = [
                    statistics.mean(paasATemps),    # mean of paas A
                    min(paasATemps),    # min of paas A
                    max(paasATemps),    # max of paas A
                    statistics.stdev(paasATemps),# standard dev of paas A
                    statistics.mean(paasATemps) - statistics.stdev(paasATemps),   # upper std dev
                    statistics.mean(paasATemps) + statistics.stdev(paasATemps)    # lower std dev
                ]
            if len(paasBCTemps) > 0:
                self.pro6BCStats = [
                    statistics.mean(paasBCTemps),    # mean of paas BC
                    min(paasBCTemps),    # min of paas BC
                    max(paasBCTemps),    # max of paas BC
                    statistics.stdev(paasBCTemps),# standard dev of paas BC
                    statistics.mean(paasBCTemps) - statistics.stdev(paasBCTemps),   # upper std dev
                    statistics.mean(paasBCTemps) + statistics.stdev(paasBCTemps)    # lower std dev
                ]
            
            heatTimes = [toop[1] for toop in self.pro6HeatData]
            if len(heatTimes) > 0:
                rawHeatTime = max(heatTimes) - min(heatTimes)
                self.pro6HeatTime = timedelta(seconds = rawHeatTime)

        #print(self.pro6HeatData)
        #print(self.pro6AStats)
        #print(self.pro6BCStats)
        #print(self.pro6HeatTime)



# fmt: off
# ███████╗██╗  ██╗██████╗  ██████╗ ██████╗ ████████╗██╗███╗   ██╗ ██████╗ 
# ██╔════╝╚██╗██╔╝██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝██║████╗  ██║██╔════╝ 
# █████╗   ╚███╔╝ ██████╔╝██║   ██║██████╔╝   ██║   ██║██╔██╗ ██║██║  ███╗
# ██╔══╝   ██╔██╗ ██╔═══╝ ██║   ██║██╔══██╗   ██║   ██║██║╚██╗██║██║   ██║
# ███████╗██╔╝ ██╗██║     ╚██████╔╝██║  ██║   ██║   ██║██║ ╚████║╚██████╔╝
# ╚══════╝╚═╝  ╚═╝╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝╚═╝  ╚═══╝ ╚═════╝ 
# Functions responsible for writing data to CSV files
# fmt: on

    # export wire data to CSV file
    def exportWireMeasurements(self):
        if len(self.wireTensionData) == 0:
            tkinter.messagebox.showerror(
                title="Error",
                message=f"No wire tension data found for MN{self.panelNumber}",
            )
            return
        with open(
            f"MN{self.panelNumber}_wire_tension_data.csv", "w", newline=""
        ) as csvFile:
            csvWriter = csv.writer(csvFile)
            csvWriter.writerow([f"MN{self.panelNumber} Wire Tension Data"])
            csvWriter.writerow(
                ["Position", "Tension", "Wire Timer", "Calibration Factor"]
            )
            csvWriter.writerows(self.wireTensionData)
            tkinter.messagebox.showinfo(
                title="Data Exported",
                message=f"Data exported to MN{self.panelNumber}_wire_tension_data.csv",
            )

    # export straw tension data to CSV (TODO: NEEDS COMMENTS)
    def exportStrawMeasurements(self):
        if len(self.strawTensionData) == 0:
            tkinter.messagebox.showerror(
                title="Error",
                message=f"No straw tension data found for MN{self.panelNumber}",
            )
            return
        with open(
            f"MN{self.panelNumber}_straw_tension_data.csv", "w", newline=""
        ) as csvFile:
            csvWriter = csv.writer(csvFile)
            csvWriter.writerow([f"MN{self.panelNumber} Straw Tension Data"])
            csvWriter.writerow(["Position", "Tension", "Uncertainty", "Timestamp"])
            csvWriter.writerows(self.strawTensionData)
            tkinter.messagebox.showinfo(
                title="Data Exported",
                message=f"Data exported to MN{self.panelNumber}_straw_tension_data.csv",
            )

    # export HV data to CSV (TODO: NEEDS COMMENTS)
    def exportHVMeasurements(self):
        # (<POS>, <L_AMPS>, <R_AMPS>, <TRIP>, <TIME>)
        if len(self.hvData) == 0:
            tkinter.messagebox.showerror(
                title="Error", message=f"No HV data found for MN{self.panelNumber}"
            )
            return
        with open(f"MN{self.panelNumber}_HV_data.csv", "w", newline="") as csvFile:
            csvWriter = csv.writer(csvFile)
            csvWriter.writerow([f"MN{self.panelNumber} HV Data"])
            csvWriter.writerow(
                [
                    "Position",
                    "Left Current",
                    "Right Current",
                    "Trip Status",
                    "Timestamp",
                ]
            )
            csvWriter.writerows(self.hvData)
            tkinter.messagebox.showinfo(
                title="Data Exported",
                message=f"Data exported to MN{self.panelNumber}_HV_data.csv",
            )
    
    # export heat data to CSV
    def exportHeatMeasurements(self):
        pass

# fmt: off
#  ██████╗ ██████╗  █████╗ ██████╗ ██╗  ██╗██╗███╗   ██╗ ██████╗ 
# ██╔════╝ ██╔══██╗██╔══██╗██╔══██╗██║  ██║██║████╗  ██║██╔════╝ 
# ██║  ███╗██████╔╝███████║██████╔╝███████║██║██╔██╗ ██║██║  ███╗
# ██║   ██║██╔══██╗██╔══██║██╔═══╝ ██╔══██║██║██║╚██╗██║██║   ██║
# ╚██████╔╝██║  ██║██║  ██║██║     ██║  ██║██║██║ ╚████║╚██████╔╝
#  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝ 
# Functions that use matplotlib to make graphs from the data in scroll areas
# fmt: on

    # function to open new window with wire tension data graphed
    def plotWireData(self):
        # plt.style.use('dark_background') # darkmodebestmode
        # self.wireTensionData = [(pos,ten,...), (pos,ten,...),...]
        xData = list(range(96))  # string positions: 0 to 95
        sctrYData = []  # give this list data in for loop
        for toop in self.wireTensionData:  # go through wireTensionData
            if toop[1] != "No Data":  # if data exists...
                sctrYData += [toop[1]]  # add it to the list of y axis points
            else:  # if there isn't data...
                sctrYData += [None]  # add a None value to the list

        plt.subplot(211)  # make subplot 1
        plt.scatter(xData, sctrYData)  # make a scatterplot out of the x and y data
        plt.axis([0, 100, 0, 100])  # set the bounds of the graph
        plt.xlabel("Wire Position", fontsize=20)  # set x axis label
        plt.ylabel("Wire Tension", fontsize=20)  # set y axis label
        for x, y in enumerate(sctrYData):  # go through y data, enumerate for x
            if y is not None and y < 70:  # if y exists and is too low...
                plt.annotate(f"({x},{y})", (x, y))  # annotate that point

        plt.subplot(212)  # make subplot 2
        histYData = []  # make list to filter out None types
        # doing the histogram before the scatterplot to avoid the redundant addition then
        # removal of None types wouldn't work since you would still need to remove the strings
        for y in sctrYData:  # go through scatter y data
            if y != None:  # if it's not a None type
                histYData += [y]  # add it to the new histogram y data
        n, bins, patches = plt.hist(histYData, 20)  # plot histogram
        plt.xlabel("Wire Tension", fontsize=20)  # set x axis label
        plt.ylabel("Frequency", fontsize=20)  # set y axis label

        plt.tight_layout()  # give subplots enough space between them
        # mpl.rcParams['figure.dpi'] = 300        # make the graph itself bigger (deault is super smol)
        plt.show()  # show the graphs

    # plot straw tension data in new window (TODO: NEEDS BETTER COMMENTS)
    def plotStrawData(self):
        # self.strawTensionData = [(pos, ten, unc, time),...]
        xData = list(range(96))
        sctrYDataPoints = []
        sctrYDataUncs = []
        for toop in self.strawTensionData:
            if toop[1] != "No Data" and toop[2] != "No Data":
                sctrYDataPoints += [toop[1]]
                sctrYDataUncs += [toop[2]]
            else:
                sctrYDataPoints += [None]  # source of a bug???
                sctrYDataUncs += [None]

        plt.subplot(211)
        # plt.figure(figsize=(12,8))

        plt.errorbar(
            xData, sctrYDataPoints, yerr=sctrYDataUncs, fmt="o"
        )  # make a scatterplot out of the x and y data
        plt.axis([0, 100, 0, 1000])  # set the bounds of the graph
        plt.xlabel("Wire Position", fontsize=20)  # set x axis label
        plt.ylabel("Wire Tension", fontsize=20)  # set y axis label
        for x, y in enumerate(sctrYDataPoints):  # go through y data, enumerate for x
            if y is not None:  # if y exists and is too low...
                plt.annotate(f"{x}", (x, y), fontsize=8)  # annotate that point

        plt.subplot(212)  # make subplot 2
        histYData = []  # make list to filter out None types

        for y in sctrYDataPoints:  # go through scatter y data
            if y != None:  # if it's not a None type
                histYData += [y]  # add it to the new histogram y data
        n, bins, patches = plt.hist(histYData, 20)  # plot histogram
        plt.xlabel("Straw Tension", fontsize=20)  # set x axis label
        plt.ylabel("Frequency", fontsize=20)  # set y axis label

        plt.tight_layout()
        # mpl.rcParams['figure.dpi'] = 600        # make the graph itself bigger (deault is super smol)
        plt.show()

    # plot HV data in new window (TODO: NEEDS BETTER COMMENTS)
    def plotHVData(self):
        # (<pos>, <L current>, <R current>, <is tripped bool>, <time>)

        xData = list(range(96))  # x data can be re-used

        # left current subplots
        yData = []
        for toop in self.hvData:
            if toop[1] != "No Data":
                yData += [toop[1]]
            else:
                yData += [None]

        plt.subplot(221)
        plt.scatter(xData, yData)
        plt.xlabel("Left Current", fontsize=20)  # set x axis label
        plt.ylabel("Position", fontsize=20)  # set y axis label

        plt.subplot(223)  # make subplot 2
        histYData = []  # make list to filter out None types

        for y in yData:  # go through scatter y data
            if y != None:  # if it's not a None type
                histYData += [y]  # add it to the new histogram y data
        n, bins, patches = plt.hist(histYData, 20)  # plot histogram
        plt.xlabel("Left Current", fontsize=20)  # set x axis label
        plt.ylabel("Frequency", fontsize=20)  # set y axis label

        # right current subplots
        yData = []
        for toop in self.hvData:
            if toop[2] != "No Data":
                yData += [toop[2]]
            else:
                yData += [None]

        plt.subplot(222)
        plt.scatter(xData, yData)
        plt.xlabel("Right Current", fontsize=20)  # set x axis label

        plt.subplot(224)  # make subplot 2
        histYData = []  # make list to filter out None types

        for y in yData:  # go through scatter y data
            if y != None:  # if it's not a None type
                histYData += [y]  # add it to the new histogram y data
        n, bins, patches = plt.hist(histYData, 20)  # plot histogram
        plt.xlabel("Right Current", fontsize=20)  # set x axis label

        plt.tight_layout()
        # mpl.rcParams['figure.dpi'] = 600        # make the graph itself bigger (deault is super smol)
        plt.show()

    # plot heat data in new window
    def plotHeatData(self):
        pass
        

# fmt: off
# ██████╗  █████╗ ██████╗ ███████╗███████╗    ██████╗  █████╗ ████████╗ █████╗ 
# ██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔════╝    ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗
# ██████╔╝███████║██████╔╝███████╗█████╗      ██║  ██║███████║   ██║   ███████║
# ██╔═══╝ ██╔══██║██╔══██╗╚════██║██╔══╝      ██║  ██║██╔══██║   ██║   ██╔══██║
# ██║     ██║  ██║██║  ██║███████║███████╗    ██████╔╝██║  ██║   ██║   ██║  ██║
# ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝
# Functions that put data onto the GUI
# findComments() should be split into findComments() and displayComments()
# fmt: on

    # function to help sift through partsQuery results, also displays found data
    # this is essentially a helper for findPanelParts()
    def displayPanelParts(self, partTuple):
        # I apologise for this abhorrent block of code with 15 too many if/elif statements
        # this could potentially be avoided with a dictionary?
        # having PIR and ALF before others in the if statements it a tiny bit more efficient
        if partTuple[4] == "PIR":
            if partTuple[6] == "L":
                if partTuple[7] == "A":
                    self.ui.partPLALE.setText(str(partTuple[5]))
                elif partTuple[7] == "B":
                    self.ui.partPLBLE.setText(str(partTuple[5]))
                elif (
                    partTuple[7] == "C"
                ):  # this could be just else, but checking prevents garbage data from being displayed
                    self.ui.partPLCLE.setText(str(partTuple[5]))
            if partTuple[6] == "R":
                if partTuple[7] == "A":
                    self.ui.partPRALE.setText(str(partTuple[5]))
                elif partTuple[7] == "B":
                    self.ui.partPRBLE.setText(str(partTuple[5]))
                elif partTuple[7] == "C":
                    self.ui.partPRCLE.setText(str(partTuple[5]))
        elif partTuple[4] == "PAAS":
            if partTuple[7] == "A":
                self.ui.partPaasALE.setText(str(partTuple[5]))
            if partTuple[7] == "B":
                self.ui.partPaasBLE.setText(str(partTuple[5]))
            if partTuple[7] == "C":
                self.ui.partPaasCLE.setText(str(partTuple[5]))
        elif partTuple[4] == "ALF":
            if partTuple[3] == "L":
                self.ui.partALF1LE.setText(str(partTuple[5]))
            elif partTuple[3] == "R":
                self.ui.partALF2LE.setText(str(partTuple[5]))
        elif partTuple[4] == "BASEPLATE":
            self.ui.partBasePlateLE.setText(str(partTuple[5]))
        elif partTuple[4] == "MIR":
            self.ui.partMIRLE.setText(str(partTuple[5]))
        elif partTuple[4] == "BIR":
            self.ui.partBIRLE.setText(str(partTuple[5]))

    # put measurement data on the gui
    def displayMeasurement(self):
        # ensure data exists
        # bools to represent if data exists for each measurement type
        extantWireData = False
        extantStrawData = False
        extantHVData = False
        extantHeatData = False

        for toop in self.wireTensionData:  # for each tuple in self.wireTensionData
            if toop[1] != "No Data":  # if it isn't "No Data"
                extantWireData = True  # then data exists!
        for toop in self.strawTensionData:
            if toop[1] != "No Data":
                extantStrawData = True
        for toop in self.hvData:
            if toop[1] != "No Data":
                extantHVData = True

        if extantWireData:  # if wire data exists
            self.ui.wireListWidget.addItem(
                "Position      Tension"
            )  # add wire tension header
            for toop in self.wireTensionData:  # for each tuple in wire data
                self.ui.wireListWidget.addItem(
                    f"{str(toop[0]).ljust(18)}{toop[1]}"
                )  # add position and tension to list TODO: use string fill?
        else:  # otherwise
            self.ui.wireListWidget.addItem("No Data Found :(")  # display no data

        if extantStrawData:
            self.ui.strawListWidget.addItem("Position     Tension     Uncertainty")
            for toop in self.strawTensionData:  # for each tuple in strawTensionData
                self.ui.strawListWidget.addItem(
                    f"{str(toop[0]).ljust(18)}{str(toop[1]).ljust(18)}{str(toop[2]).ljust(18)}"
                )  # add position, tension, and uncertainty to list
        else:
            self.ui.strawListWidget.addItem("No Data Found :(")

        if extantHVData:
            trippedBrush = QBrush(Qt.red)
            self.ui.hvListWidget.addItem(
                f'{str("Position").ljust(14)}{str("L μA").ljust(18)}{str("R μA").ljust(18)}'
            )
            for toop in self.hvData:  # for each tuple in self.hvData
                if toop[3]:  # if index 3 (isTripped) is true,
                    trippedItem = QListWidgetItem(
                        f"{str(toop[0]).ljust(18)}{str(toop[1]).ljust(18)}{str(toop[2]).ljust(18)}   TRIPPED"
                    )
                    trippedItem.setBackground(trippedBrush)
                    self.ui.hvListWidget.addItem(trippedItem)  # display TRIPPED
                else:  # otherwise, it's not tripped
                    self.ui.hvListWidget.addItem(
                        f"{str(toop[0]).ljust(18)}{str(toop[1]).ljust(18)}{str(toop[2]).ljust(18)}"
                    )  # display just the data
        else:
            self.ui.hvListWidget.addItem("No Data Found :(")
        
        if extantHeatData:
            self.ui.heatListWidget.addItem(
                "Data Exists, but only the export and plot buttons work right now.  Check back in 173,000 seconds or so."
                )
        else:
            self.ui.heatListWidget.addItem("No Data Found :(")
    
    # put heat statistics on the gui
    def displayHeat(self):

        # clear out the current data
        self.ui.heatListWidget.clear()

        def get(pro, data):
            return getattr(self, f"pro{pro}{data}")

        itemsToAdd = [
            f'PAAS A Maximum Temperature: {get(6,"BCStats")[2]}' if 
        ]

        self.ui.heatListWidget.addItems(itemsToAdd)

        
        

# fmt: off
# ███╗   ███╗██╗███████╗ ██████╗
# ████╗ ████║██║██╔════╝██╔════╝
# ██╔████╔██║██║███████╗██║     
# ██║╚██╔╝██║██║╚════██║██║     
# ██║ ╚═╝ ██║██║███████║╚██████╗
# ╚═╝     ╚═╝╚═╝╚══════╝ ╚═════╝
# The isle of misfit functions
# fmt: on

    # override close button event (see comments in function)
    def closeEvent(self, event):
        sys.exit()  # kill program
        # this is necessary since using the pyplot.show() makes python think there's another app running, so closing the gui
        # won't close the program if you used the plot button (so you'd have a python process still running in the background
        # doing nothing).  Overriding the closeEvent to exit the program makes sure the whole process is dead when the user
        # clicks the X in the upper right corner.
        # It's not called anywhere because having it here overwrites a QMainWindow method.
        # Killing it with sys.exit() will not hurt the database.


# fmt: off
# ███╗   ███╗ █████╗ ██╗███╗   ██╗
# ████╗ ████║██╔══██╗██║████╗  ██║
# ██╔████╔██║███████║██║██╔██╗ ██║
# ██║╚██╔╝██║██╔══██║██║██║╚██╗██║
# ██║ ╚═╝ ██║██║  ██║██║██║ ╚████║
# ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝
# DEFINITELY NOT the thing that starts up the program
# fmt: on

if __name__ == "__main__":
    app = QApplication(sys.argv)  # make an app
    # app.setStyleSheet(qdarkstyle.load_stylesheet())    # darkmodebestmode
    window = facileDBGUI(Ui_MainWindow())  # make a window
    if ISLAB:
        window.connectToNetwork()  # link to database
        window.setWindowTitle("Database Viewer") # change from default window title
    else:
        window.connectToLocal() #link to database
        window.setWindowTitle("~~~~~~~LOCAL CONNECTION FOR DEVELOPMENT~~~~~~~")
        # make sure you can tell the difference between local and network connections
    window.showMaximized()  # open in maximized window (using show() would open in a smaller one with weird porportions)

    app.exec_()  # run the app!
