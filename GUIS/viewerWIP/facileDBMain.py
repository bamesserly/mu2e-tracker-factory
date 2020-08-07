import sys, time, csv, tkinter, tkinter.messagebox  # for creating app, time formatting, saving to csv, popup dialogs

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
from PyQt5.QtGui import QBrush

# for GUI widget management^
from PyQt5.QtCore import Qt, QRect, QObject  # for gui window management
from datetime import datetime  # for time formatting
from facileDB import Ui_MainWindow  # import raw UI

# - -    --   - - /|_/|          .-------------------.
# _______________| @.@|         /                     )
# (______         >\_W/<     ---/    I'm a cat :3     /
#  -   / ______  _/____)      (                     /
# -   / /\ \   \ \             `-------------------'
#  - (_/  \_) - \_)

# Main class for a gui to make interacting with the DB easier.
# Adam Arnett
# Created 5-28-2020
# Last update 6-19-2020
# improvements to be made:
# differentiate between 5 day panels and 7 day panels
# improve on the measurement display
# some procedures get logged twice (two pan3s, for example) and one might not have wire tension data while the other does.
#     This is an issue with the database, not this gui.  But, this gui doesn't have a way to figure out which procedure to read.
# add modification stuff???
# next steps:
# add procedures to important tables
# check procedures to find best data, completion, etc
# add full report, what other data is needed?
# everything...


class facileDBGUI(QMainWindow):

    #  ██▓ ███▄    █  ██▓▄▄▄█████▓ ██▓ ▄▄▄       ██▓     ██▓▒███████▒▓█████
    # ▓██▒ ██ ▀█   █ ▓██▒▓  ██▒ ▓▒▓██▒▒████▄    ▓██▒    ▓██▒▒ ▒ ▒ ▄▀░▓█   ▀
    # ▒██▒▓██  ▀█ ██▒▒██▒▒ ▓██░ ▒░▒██▒▒██  ▀█▄  ▒██░    ▒██▒░ ▒ ▄▀▒░ ▒███
    # ░██░▓██▒  ▐▌██▒░██░░ ▓██▓ ░ ░██░░██▄▄▄▄██ ▒██░    ░██░  ▄▀▒   ░▒▓█  ▄
    # ░██░▒██░   ▓██░░██░  ▒██▒ ░ ░██░ ▓█   ▓██▒░██████▒░██░▒███████▒░▒████▒
    # ░▓  ░ ▒░   ▒ ▒ ░▓    ▒ ░░   ░▓   ▒▒   ▓▒█░░ ▒░▓  ░░▓  ░▒▒ ▓░▒░▒░░ ▒░ ░
    #  ▒ ░░ ░░   ░ ▒░ ▒ ░    ░     ▒ ░  ▒   ▒▒ ░░ ░ ▒  ░ ▒ ░░░▒ ▒ ░ ▒ ░ ░  ░
    #  ▒ ░   ░   ░ ░  ▒ ░  ░       ▒ ░  ░   ▒     ░ ░    ▒ ░░ ░ ░ ░ ░   ░
    #  ░           ░  ░            ░        ░  ░    ░  ░ ░    ░ ░       ░  ░
    #                                                       ░

    # initializer, takes ui parameter from the .ui file
    def __init__(self, ui_layout):
        # setup UI
        QMainWindow.__init__(self)  # initialize superclass
        self.ui = ui_layout  # make ui member
        ui_layout.setupUi(self)  # apply ui to window
        self.tkRoot = tkinter.Tk()  # make tkinter root for popup messages
        self.tkRoot.withdraw()  # hide root, it's necessary for popups to work, but it's just a blank window otherwise

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

        self.ringsSetupWidgetList = [  # list of line edits for rings
            self.ui.ringsBasePlateLE,
            self.ui.ringsMIRLE,
            self.ui.ringsBIRLE,
            self.ui.ringsPLALE,
            self.ui.ringsPLBLE,
            self.ui.ringsPLCLE,
            self.ui.ringsPRALE,
            self.ui.ringsPRBLE,
            self.ui.ringsPRCLE,
            self.ui.ringsALF1LE,
            self.ui.ringsALF2LE,
        ]

        # link widgets and things
        self.ui.submitPB.clicked.connect(
            self.findPanel
        )  # bind function for submit button
        self.ui.wireExportButton.clicked.connect(
            self.exportWireMeasurements
        )  # bind function for export wire tension stuff
        self.ui.plotWireDataButton.clicked.connect(
            self.plotWireData
        )  # bind function for wire plot button
        self.ui.strawExportButton.clicked.connect(
            self.exportStrawMeasurements
        )  # bind function for export straw tension data
        self.ui.plotStrawDataButton.clicked.connect(
            self.plotStrawData
        )  # bind function for plot straw tension data
        self.ui.hvExportButton.clicked.connect(
            self.exportHVMeasurements
        )  # bind funciton for export HV data
        self.ui.plotHVDataButton.clicked.connect(
            self.plotHVData
        )  # bind function for plot HV data

    # make engine, connection, and metadata objects to interact with database
    def connectToDB(self):

        # override connect to return a read-only DB connection, MUST use path starting at C drive
        # more on this: https://github.com/sqlalchemy/sqlalchemy/issues/4863
        tkinter.messagebox.showinfo(
            title="Connecting", message=f"Connecting to network database..."
        )

        def connectSpecial():
            return sqlite3.connect(
                "file:Z:\Production_Environment\Data\database.db?mode=ro", uri=True
            )
            # return sqlite3.connect("file:/spa-mu2e-network/Files/Production_Environment/Database/database.db?mode=ro", uri=True)

        self.engine = sqla.create_engine(
            "sqlite:///../../Data/database.db/", creator=connectSpecial
        )  # create engine

        # try to use read only mode
        # If the path above is wrong, read-only will fail.  I could see a mergedown or misplaced file easily screwing up the path.
        # If read-only fails, it'll use the regular SQLAlchemy connection.  The regular connection shouldn't write to the DB, but
        # having read-only mode is a good safety net.
        try:
            self.connection = self.engine.connect()  # connect engine with DB
        except:
            tkinter.messagebox.showerror(
                title="Error",
                message=f"Read-only mode failed.  The network is not mapped as the Z drive.  Contact a member of the software team for help.",
            )  # show error message
            self.connection = self.engine.connect()  # connect engine with DB

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

    #  ██▀███  ▓█████ ▄▄▄      ▓█████▄  ██▓ ███▄    █   ▄████      █████▒██▀███   ▒█████   ███▄ ▄███▓   ▓█████▄  ▄▄▄▄
    # ▓██ ▒ ██▒▓█   ▀▒████▄    ▒██▀ ██▌▓██▒ ██ ▀█   █  ██▒ ▀█▒   ▓██   ▒▓██ ▒ ██▒▒██▒  ██▒▓██▒▀█▀ ██▒   ▒██▀ ██▌▓█████▄
    # ▓██ ░▄█ ▒▒███  ▒██  ▀█▄  ░██   █▌▒██▒▓██  ▀█ ██▒▒██░▄▄▄░   ▒████ ░▓██ ░▄█ ▒▒██░  ██▒▓██    ▓██░   ░██   █▌▒██▒ ▄██
    # ▒██▀▀█▄  ▒▓█  ▄░██▄▄▄▄██ ░▓█▄   ▌░██░▓██▒  ▐▌██▒░▓█  ██▓   ░▓█▒  ░▒██▀▀█▄  ▒██   ██░▒██    ▒██    ░▓█▄   ▌▒██░█▀
    # ░██▓ ▒██▒░▒████▒▓█   ▓██▒░▒████▓ ░██░▒██░   ▓██░░▒▓███▀▒   ░▒█░   ░██▓ ▒██▒░ ████▓▒░▒██▒   ░██▒   ░▒████▓ ░▓█  ▀█▓
    # ░ ▒▓ ░▒▓░░░ ▒░ ░▒▒   ▓▒█░ ▒▒▓  ▒ ░▓  ░ ▒░   ▒ ▒  ░▒   ▒     ▒ ░   ░ ▒▓ ░▒▓░░ ▒░▒░▒░ ░ ▒░   ░  ░    ▒▒▓  ▒ ░▒▓███▀▒
    #   ░▒ ░ ▒░ ░ ░  ░ ▒   ▒▒ ░ ░ ▒  ▒  ▒ ░░ ░░   ░ ▒░  ░   ░     ░       ░▒ ░ ▒░  ░ ▒ ▒░ ░  ░      ░    ░ ▒  ▒ ▒░▒   ░
    #   ░░   ░    ░    ░   ▒    ░ ░  ░  ▒ ░   ░   ░ ░ ░ ░   ░     ░ ░     ░░   ░ ░ ░ ░ ▒  ░      ░       ░ ░  ░  ░    ░
    #    ░        ░  ░     ░  ░   ░     ░           ░       ░              ░         ░ ░         ░         ░     ░
    #                           ░                                                                        ░            ░

    # called upon hitting submit (does a lot of stuff)
    def findPanel(self):
        # first get rid of any existing data
        self.panelDatabaseID = -1  # reset panel database ID
        for widget in self.comListWidgetList:  # clear comments from list widgets
            widget.clear()
        for widget in self.ringsSetupWidgetList:  # erase all part IDs
            widget.setText("")
        for (
            key
        ) in self.panelProcedureIDs:  # "rip up" the dictionary (keep keys of course)
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
            self.panelProcedureIDs[toop[1]] = toop[
                0
            ]  # assign procedure ID to the corresponding station
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
                self.panelsTable.columns.number,
                panelPartUsage.columns.panel_part,
                panelPartUsage.columns.panel,
                panelPartUsage.columns.left_right,  # ALF L/R
                panelPartActual.columns.type,  # type of part (MIR, PIR, ALF, etc.)
                panelPartActual.columns.number,  # part number
                panelPartActual.columns.left_right,  # PIR l/R
                panelPartActual.columns.letter,  # PIR A/B/C
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
        # print("setup",resultSet2)

        for partTuple in resultSet2:
            self.sortPanelParts(partTuple)

    # get HV, straw tension, and wire tension data
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
        pass

    # ▓█████ ▒██   ██▒ ██▓███   ▒█████   ██▀███  ▄▄▄█████▓ ██▓ ███▄    █   ▄████
    # ▓█   ▀ ▒▒ █ █ ▒░▓██░  ██▒▒██▒  ██▒▓██ ▒ ██▒▓  ██▒ ▓▒▓██▒ ██ ▀█   █  ██▒ ▀█▒
    # ▒███   ░░  █   ░▓██░ ██▓▒▒██░  ██▒▓██ ░▄█ ▒▒ ▓██░ ▒░▒██▒▓██  ▀█ ██▒▒██░▄▄▄░
    # ▒▓█  ▄  ░ █ █ ▒ ▒██▄█▓▒ ▒▒██   ██░▒██▀▀█▄  ░ ▓██▓ ░ ░██░▓██▒  ▐▌██▒░▓█  ██▓  (exporting)
    # ░▒████▒▒██▒ ▒██▒▒██▒ ░  ░░ ████▓▒░░██▓ ▒██▒  ▒██▒ ░ ░██░▒██░   ▓██░░▒▓███▀▒
    # ░░ ▒░ ░▒▒ ░ ░▓ ░▒▓▒░ ░  ░░ ▒░▒░▒░ ░ ▒▓ ░▒▓░  ▒ ░░   ░▓  ░ ▒░   ▒ ▒  ░▒   ▒
    #  ░ ░  ░░░   ░▒ ░░▒ ░       ░ ▒ ▒░   ░▒ ░ ▒░    ░     ▒ ░░ ░░   ░ ▒░  ░   ░
    #    ░    ░    ░  ░░       ░ ░ ░ ▒    ░░   ░   ░       ▒ ░   ░   ░ ░ ░ ░   ░
    #    ░  ░ ░    ░               ░ ░     ░               ░           ░       ░
    #

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

    #   ▄████  ██▀███   ▄▄▄       ██▓███   ██░ ██  ██▓ ███▄    █   ▄████
    #  ██▒ ▀█▒▓██ ▒ ██▒▒████▄    ▓██░  ██▒▓██░ ██▒▓██▒ ██ ▀█   █  ██▒ ▀█▒
    # ▒██░▄▄▄░▓██ ░▄█ ▒▒██  ▀█▄  ▓██░ ██▓▒▒██▀▀██░▒██▒▓██  ▀█ ██▒▒██░▄▄▄░
    # ░▓█  ██▓▒██▀▀█▄  ░██▄▄▄▄██ ▒██▄█▓▒ ▒░▓█ ░██ ░██░▓██▒  ▐▌██▒░▓█  ██▓
    # ░▒▓███▀▒░██▓ ▒██▒ ▓█   ▓██▒▒██▒ ░  ░░▓█▒░██▓░██░▒██░   ▓██░░▒▓███▀▒
    #  ░▒   ▒ ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░▒▓▒░ ░  ░ ▒ ░░▒░▒░▓  ░ ▒░   ▒ ▒  ░▒   ▒
    #   ░   ░   ░▒ ░ ▒░  ▒   ▒▒ ░░▒ ░      ▒ ░▒░ ░ ▒ ░░ ░░   ░ ▒░  ░   ░
    # ░ ░   ░   ░░   ░   ░   ▒   ░░        ░  ░░ ░ ▒ ░   ░   ░ ░ ░ ░   ░
    #       ░    ░           ░  ░          ░  ░  ░ ░           ░       ░
    #

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

    #  ███▄ ▄███▓ ██▓  ██████  ▄████▄
    # ▓██▒▀█▀ ██▒▓██▒▒██    ▒ ▒██▀ ▀█
    # ▓██    ▓██░▒██▒░ ▓██▄   ▒▓█    ▄
    # ▒██    ▒██ ░██░  ▒   ██▒▒▓▓▄ ▄██▒
    # ▒██▒   ░██▒░██░▒██████▒▒▒ ▓███▀ ░
    # ░ ▒░   ░  ░░▓  ▒ ▒▓▒ ▒ ░░ ░▒ ▒  ░
    # ░  ░      ░ ▒ ░░ ░▒  ░ ░  ░  ▒
    # ░      ░    ▒ ░░  ░  ░  ░
    #        ░    ░        ░  ░ ░
    #                         ░

    # function to help sift through partsQuery results, also displays found data (helper for findPanelParts)
    def sortPanelParts(self, partTuple):
        # I apologise for this abhorrent block of code with 15 too many if/elif statements
        # this could potentially be avoided with a dictionary?
        # having PIR and ALF before others in the if statements it a tiny bit more efficient
        if partTuple[4] == "PIR":
            if partTuple[6] == "L":
                if partTuple[7] == "A":
                    self.ui.ringsPLALE.setText(str(partTuple[5]))
                elif partTuple[7] == "B":
                    self.ui.ringsPLBLE.setText(str(partTuple[5]))
                elif (
                    partTuple[7] == "C"
                ):  # this could be just else, but checking prevents garbage data from being displayed
                    self.ui.ringsPLCLE.setText(str(partTuple[5]))
            if partTuple[6] == "R":
                if partTuple[7] == "A":
                    self.ui.ringsPRALE.setText(str(partTuple[5]))
                elif partTuple[7] == "B":
                    self.ui.ringsPRBLE.setText(str(partTuple[5]))
                elif partTuple[7] == "C":
                    self.ui.ringsPRCLE.setText(str(partTuple[5]))
        elif partTuple[4] == "ALF":
            if partTuple[3] == "L":
                self.ui.ringsALF1LE.setText(str(partTuple[5]))
            elif partTuple[3] == "R":
                self.ui.ringsALF2LE.setText(str(partTuple[5]))
        elif partTuple[4] == "BASEPLATE":
            self.ui.ringsBasePlateLE.setText(str(partTuple[5]))
        elif partTuple[4] == "MIR":
            self.ui.ringsMIRLE.setText(str(partTuple[5]))
        elif partTuple[4] == "BIR":
            self.ui.ringsBIRLE.setText(str(partTuple[5]))

    # put measurement data on the gui
    def displayMeasurement(self):
        # ensure data exists
        extantWireData = (
            False  # booleans to represent if data exists for each measurement type
        )
        extantStrawData = False
        extantHVData = False
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

    # override close button event
    def closeEvent(self, event):
        sys.exit()  # kill program
        # this is necessary since using the pyplot.show() makes python think there's another app running, so closing the gui
        # won't close the program if you used the plot button (so you'd have a python process still running in the background
        # doing nothing).  Overriding the closeEvent to exit the program makes sure the whole process is dead when the user
        # clicks the X in the upper right corner


if __name__ == "__main__":
    app = QApplication(sys.argv)  # make an app
    # app.setStyleSheet(qdarkstyle.load_stylesheet())    # darkmodebestmode
    print("Starting...")
    window = facileDBGUI(Ui_MainWindow())  # make a window
    window.connectToDB()  # link to database
    window.setWindowTitle("Database Viewer")
    window.showMaximized()  # open in maximized window (using show() would open in a smaller one with weird porportions)

    app.exec_()  # run the app!
