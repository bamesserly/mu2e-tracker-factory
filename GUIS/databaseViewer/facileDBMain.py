#  - -    --   - - /|_/|          .-----------------------.
#  _______________| @.@|         /  Written by Adam Arnett )
# (______         >\_W/<  ------/  Created 05/28/2020     /
#  -   / ______  _/____)       /  Last Update 11/24/2020 /
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
import pandas as pd # even more plotting
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
from panelData import PanelData # import class for data organization


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
        self.setWindowIcon(QIcon(f'{dir_path}\\mu2e.jpg'))

        # link buttons/menu items to functions
        self.initInputWidgets()
        self.initMenusActions()

        # initialize widget lists
        self.initWidgetLists()

        # create panelData member, pretty much all data is stored here
        # would it be more efficient to store data in the widgets?
        self.data = PanelData()
        


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

    # initialize lists of widgets for organization and easy access
    def initWidgetLists(self):
        # tuple of comment QListWidgets
        # index = pro number -1
        self.comWidgetList = (  
            (self.ui.ringsComList, self.ui.pan1TimeList),
            (self.ui.strawsComList, self.ui.pan2TimeList),
            (self.ui.senseComList, self.ui.pan3TimeList),
            (self.ui.pinsComList, self.ui.pan4TimeList),
            (self.ui.highComList, self.ui.pan5TimeList),
            (self.ui.manifoldComList, self.ui.pan6TimeList),
            (self.ui.floodingComList, self.ui.pan7TimeList)
        )

        #for toop in self.comWidgetList:
        #   toop[0].setStyleSheet("background-image: url(mu2e_logo.png)")

        # tuple of procedure timing/session QLineEdit widgets
        # each tuple in the tuple has the form: (<start time>, <end time>, <total time>)
        # index = pro number -1
        self.timeWidgetList = (
            (self.ui.pan1STime,self.ui.pan1ETime,self.ui.pan1TTime),
            (self.ui.pan2STime,self.ui.pan2ETime,self.ui.pan2TTime),
            (self.ui.pan3STime,self.ui.pan3ETime,self.ui.pan3TTime),
            (self.ui.pan4STime,self.ui.pan4ETime,self.ui.pan4TTime),
            (self.ui.pan5STime,self.ui.pan5ETime,self.ui.pan5TTime),
            (self.ui.pan6STime,self.ui.pan6ETime,self.ui.pan6TTime),
            (self.ui.pan7STime,self.ui.pan7ETime,self.ui.pan7TTime)
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
            self.ui.partMIDDLERIB_2LE
        )

    # link buttons with respective funcitons and panel line edit enter
    def initInputWidgets(self):
        # link widgets and things
        # bind function for entering panel id
        self.ui.panelLE.returnPressed.connect(self.findPanel)
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
        # buttons get re-enabled later if data is present for the corresponding data type
        self.disableButtons()

    # disable plot/export buttons
    def disableButtons(self):
        # disables all the buttons
        # useful for avoiding out of bounds exceptions when no data is present in lists
        self.ui.wireExportButton.setDisabled(True)
        self.ui.plotWireDataButton.setDisabled(True)
        self.ui.strawExportButton.setDisabled(True)
        self.ui.plotStrawDataButton.setDisabled(True)
        self.ui.hvExportButton.setDisabled(True)
        self.ui.plotHVDataButton.setDisabled(True)
        self.ui.heatExportButton.setDisabled(True)
        self.ui.plotHeatDataButton.setDisabled(True)
        self.ui.heatProBox.setDisabled(True)

    # link menus/actions to functions
    # some get disabled since they dont have any finished function yet
    def initMenusActions(self):
        pass
    #    # file
    #    self.ui.menuExport_Graph.setDisabled(True)
    #    self.ui.menuExport.setDisabled(True)
    #    self.ui.actionExport_Panel_Report.setDisabled(True)

    #    # edit
    #    self.ui.actionGraph_Settings.setDisabled(True)
    #    self.ui.actionExport_Location.setDisabled(True)
    #    self.ui.actionDatabase_Location.setDisabled(True)

    #    # view
    #    self.ui.menuColor_Scheme.setDisabled(True)

    #    # help
    #    self.ui.actionSend_Feedback_Issue.setDisabled(True)
    #    #self.ui.actionLatest_Changes.triggered.connect(self.latestChanges)


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

        # Clear any saved data
        self.data.clearPanel()

        # Clear all widgets except the panel entry line edit
        self.clearWidgets()

        # Set new human id
        self.data.humanID = self.ui.panelLE.text()
        
        # Set label at top
        self.ui.label_2.setText(f"MN{str(self.data.humanID).zfill(3)}")

        # Set new database id
        self.data.dbID = self.findPanelDatabaseID()
        
        # if no database id found
        if self.data.dbID == -1:
            # show error message
            tkinter.messagebox.showerror(  
                title="Error",
                message=f"No data for MN{str(self.data.humanID).zfill(3)} was found.",
            )
            # and return, no point in looking for data that doesn't exist
            # (and it's not possible w/o the database id)
            return

        # Set new procedure ids
        # calling the function sets them
        # if nothing gets returned then abort, no procedures exist
        if not self.findProcedures():
            # show error
            tkinter.messagebox.showerror(  
                title="Error",
                message=f"No data for MN{str(self.data.humanID).zfill(3)} was found.",
            )
            return

        if self.findProTiming():
            self.displayTiming()
        # no "else -> no data found" since display htiming takes care of it

        # FIND COMMENTS AND TIMING HERE
        self.findComments()

        # Find part human IDs
        if self.findParts():
            self.displayParts()
        # no "else -> no data found" since display parts takes care of it

        # Find heat data -- debug mode
        if self.findHeat() is not []:
            self.displayHeat()
        # no "else -> no data found" since display heat takes care of it

        
        # Find wire tension data
        if self.findWires():
            self.displayWires()
        else:
            self.ui.wireListWidget.addItem("No data found :(")

        # Find straw tension data
        if self.findStraws():
            self.displayStraws()
        else:
            self.ui.strawListWidget.addItem("No data found :(")

        # Find high voltage data
        if self.findHV():
            self.displayHV()
        else:
            self.ui.hvListWidget.addItem("No data found :(")

    # Query to find database ID (straw_location id) for panel
    # returns either the id or a -1 to indicate no panel found
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
        resultSet = (resultProxy.fetchall())  

        # if nothing returned,
        if len(resultSet) == 0:
            # the panel doesn't exist!
            return -1  
        else:
            # since resultSet is a list of tuples, add [0][0] to get an int
            return resultSet[0][0]  

    # query to get all procedure IDs for the panel (self.data.proIDs)
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
        panelProcedures = (resultProxy.fetchall())

        # go through results from procedures query
        for toop in panelProcedures:  
            self.data.proIDs[toop[1]] = toop[0] 
            # assign procedure ID to the corresponding station (above line)
            # self.data.proIDs is a dictionary with the name of each station as keys
        
        return not ([toop[0] for toop in panelProcedures] is None)

    # query to find procedure timestamps
    def findProTiming(self):

        # make table for procedure_timestamp
        timing = sqla.Table("procedure_timestamp", self.metadata, autoload=True, autoload_with=self.engine)  

        def proSpecificQuery(self, pro):
            
            # don't waste any time on a procudure that doesn't exist yet
            if self.data.proIDs[pro] == -1:
                return tuple('f')

            timingQuery = sqla.select(
                [
                    timing.columns.procedure,
                    timing.columns.event,
                    timing.columns.timestamp
                ]
            ).where(
                # where procedure = database id for pro parameter
                # ex. 5 gets passed in, procedure = this panel's pro 5 id
                timing.columns.procedure == self.data.proIDs[pro]
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
                return tuple('f')
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
                    self.data.timingLists[key].append([toop[1],toop[2]])

            # sort by timestamp in ascending order
            self.data.timingLists[key] = sorted(
                self.data.timingLists[key],
                key = lambda x: x[1]
            )

        return (retList is not None)

    # move displaying of comments to seperate functions
    # get and display comments for selected panel (TODO: efficiency could be improved... ?)
    def findComments(self):
        # make table
        comments = sqla.Table("comment", self.metadata, autoload=True, autoload_with=self.engine)

        # make query, it first selects:
        #   self.panelsTable.number where number = self.data.humanID (panel number)
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
        ).where(self.panelsTable.columns.number == self.data.humanID)
        # since the first select only picked entries from self.panelsTable whose number = self.data.humanID, then we're getting the selected info where
        #   the comment's procedure is one whose panel number is the what the user typed in
        comQuery = comQuery.select_from(
            self.panelsTable.join(
                self.proceduresTable,
                self.panelsTable.columns.id
                == self.proceduresTable.columns.straw_location,
            ).join(comments, self.proceduresTable.columns.id == comments.columns.procedure)
        )

        resultProxy = self.connection.execute(comQuery)  # execute query
        resultSet = resultProxy.fetchall()  # get all results as list of tuples
        # tuples have the form: (<panel Number>, <process number>, <comment text>, <comment timestamp in epoch time>)

        # now lets plug the comments into the lists!
        for i, listWidgetToop in enumerate(self.comWidgetList):
            for commentTuple in resultSet:
                # if process number string index 3 == current list widget process number
                if int(commentTuple[1][3]) == (i + 1):  
                    realTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(commentTuple[3]))
                    listWidgetToop[0].addItem(f"{realTime}\n{commentTuple[2]}")

        #for key in self.data.comLists:

    # for getting the part number, type, and PIR details (L/R, A/B/C), panel_part has all you need. (TODO: Needs comments)
    def findParts(self):
        # panel_part_use    --> panelPartUsage
        panelPartUsage = sqla.Table("panel_part_use", self.metadata, autoload=True, autoload_with=self.engine)  
        # panel_part        --> panelPartActual
        panelPartActual = sqla.Table("panel_part", self.metadata, autoload=True, autoload_with=self.engine)  

        partsQuery = sqla.select(
            [   # why are the first three in here??
                self.panelsTable.columns.number,    # panel number
                panelPartUsage.columns.panel_part,  # panel part ID
                panelPartUsage.columns.panel,   # panel straw_location ID
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

        # (<panelnum>, <part id>, <straw_loc>, <ALF L/R>, <type (MIR, ALF, etc)>, <part num>, <PIR l/R>, PIR,PAAS A/B/C>)
        for partTuple in resultSet:
            self.sortAndRefinePart(partTuple)
            retList.append(partTuple)

        #return retList -- returning the list could be useful for debugging...
        return (retList is not None)

    # get straw data
    def findStraws(self):
        # straw_tension
        strawTensions = sqla.Table(
            "measurement_straw_tension",
            self.metadata,
            autoload=True,
            autoload_with=self.engine,
        )

        # check if we have data for pro 2 --> straw tension
        if self.data.proIDs["pan2"] != -1:
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
                    self.data.strawData[toop[0]] = toop

            #return retList
            return (retList is not None)

    # get high voltage data
    def findHV(self):

        if int(self.data.humanID) < 34:  # if the panel is too old for HV data
            labelBrush = QBrush(Qt.red)  # make a red brush
            labelItem = QListWidgetItem(
                "This panel was created before HV data was recorded in the database"
            )
            # make a list item with text ^
            labelItem.setBackground(labelBrush)  # paint the list item background red
            self.ui.hvListWidget.addItem(labelItem)  # add the item to the list

            # return early, no data to look for
            return []


        hvCurrents = sqla.Table(
            "measurement_pan5", self.metadata, autoload=True, autoload_with=self.engine
        )
        # check if we have data for pro 5 --> pan5 measurement
        if self.data.proIDs["pan5"] != -1:
            hvCurrentsQuery = sqla.select(
                [  # select
                    hvCurrents.columns.position,  # wire/straw position
                    hvCurrents.columns.current_left,  # left current
                    hvCurrents.columns.current_right,  # right current
                    hvCurrents.columns.is_tripped,  # trip status
                    hvCurrents.columns.timestamp,  # timestamp
                ]
            ).where( # where procedure = this panels pan5 procedure
                hvCurrents.columns.procedure == self.data.proIDs["pan5"]
            )
            # fetching from this query will give list of tuples: (<POS>, <L_AMPS>, <R_AMPS>, <TRIP>, <TIME>)

            resultProxy = self.connection.execute(hvCurrentsQuery)  # make proxy
            rawHVData = resultProxy.fetchall()  # get all the data from the query

            self.data.hvData = []  # ensure hvData is clear
            for x in range(96):  # for x = 0 to 96
                self.data.hvData += [
                    (x, "No Data", "No Data", "No Data", 0)
                ]  # assign "data" to wireTensionData
            # this loop filters out old data, there's a better explaination for the analagous loop for strawTensionData
            # it also replaces None types with "No Data" so that an absence of data is consistent with other measurement types
            retList = []

            for toop in rawHVData:
                retList.append(toop)
                if self.data.hvData[toop[0]][4] < toop[4]:
                    self.data.hvData[toop[0]] = list(toop)
                    if self.data.hvData[toop[0]][1] == None:
                        self.data.hvData[toop[0]][1] = "No Data"
                    if self.data.hvData[toop[0]][2] == None:
                        self.data.hvData[toop[0]][2] = "No Data"


            return (retList is not None)

    # get wire tension data
    def findWires(self):
        # wire_tension
        wireTensions = sqla.Table(
            "measurement_wire_tension",
            self.metadata,
            autoload=True,
            autoload_with=self.engine,
        )

        # check if we have data for pro 3 --> wire tension
        if self.data.proIDs["pan3"] != -1:
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
            rawWireData = (
                resultProxy3.fetchall()
            )  # fetchall and send to class member, list of tuples: (<POS>, <TEN>, <TIMER>, <CALIB>, <TIME>)

            self.data.wireData = []  # ensure wireTensionData is clear
            for x in range(96):  # for x = 0 to 96
                self.data.wireData += [
                    (x, "No Data", "No Data", 0, 0)
                ]  # assign "data" to wireTensionData
            # this loop filters out old data, there's a better explaination for the analagous loop for strawTensionData
            
            retList = []

            for toop in rawWireData:
                retList.append(retList)
                if self.data.wireData[toop[0]][4] < toop[4]:
                    self.data.wireData[toop[0]] = toop

            #return retList
            return (retList is not None)

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

        self.pro1AStats = []
        self.pro1BCStats = []
        self.pro1HeatTime = []
        self.pro2AStats = []
        self.pro2BCStats = []
        self.pro2HeatTime = []
        self.pro6AStats = []
        self.pro6BCStats = []
        self.pro6HeatTime = []

        # if a pro 1 exists, get the data!
        if self.data.proIDs["pan1"] != -1:
            pro1HeatQuery = sqla.select(
                [
                    panelHeats.columns.timestamp,   # time temp taken
                    panelHeats.columns.temp_paas_a, # PAAS A temp
                    panelHeats.columns.temp_paas_bc,# PAAS BC temp
                    panelHeats.columns.procedure
                ]
            ).where(panelHeats.columns.procedure == self.data.proIDs["pan1"])
            # where the procedure for the entry is the procedure for this panel
            resultProxy = self.connection.execute(pro1HeatQuery) # make proxy
            rawPro1HeatData = resultProxy.fetchall()    # get data from db
            if rawPro1HeatData is not []:   # check if we actually have data
                self.pro1HeatData = True # we do! huzzah!

        # if a pro 2 exists, get the data!
        if self.data.proIDs["pan2"] != -1:
            pro2HeatQuery = sqla.select(
                [
                    panelHeats.columns.timestamp,   # time temp taken
                    panelHeats.columns.temp_paas_a, # PAAS A temp
                    panelHeats.columns.temp_paas_bc # PAAS BC temp
                ]
            ).where(panelHeats.columns.procedure == self.data.proIDs["pan2"])
            # where the procedure for the entry is the procedure for this panel
            resultProxy = self.connection.execute(pro2HeatQuery) # make proxy
            rawPro2HeatData = resultProxy.fetchall()    # get data from db
            if rawPro2HeatData is not []:   # check if we actually have data
                self.pro2HeatData = True # we do! noice!

        # if a pro 6 exists, get the data!
        if self.data.proIDs["pan6"] != -1:
            pro6HeatQuery = sqla.select(
                [
                    panelHeats.columns.timestamp,   # time temp taken
                    panelHeats.columns.temp_paas_a, # PAAS A temp
                    panelHeats.columns.temp_paas_bc # PAAS BC temp
                ]
            ).where(panelHeats.columns.procedure == self.data.proIDs["pan6"])
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
            
            # make lists of temps for paas A and B/C
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
                self.pro1HeatTime = timedelta(seconds=rawHeatTime)

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
                self.pro2HeatTime = timedelta(seconds=rawHeatTime)

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
                self.pro6HeatTime = timedelta(seconds=rawHeatTime)

        # stats lists are of the form: [mean, min, max, std dev, upper std dev, lower std dev]

        self.displayHeat()


# fmt: off
# ███████╗██╗  ██╗██████╗  ██████╗ ██████╗ ████████╗██╗███╗   ██╗ ██████╗ 
# ██╔════╝╚██╗██╔╝██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝██║████╗  ██║██╔════╝ 
# █████╗   ╚███╔╝ ██████╔╝██║   ██║██████╔╝   ██║   ██║██╔██╗ ██║██║  ███╗
# ██╔══╝   ██╔██╗ ██╔═══╝ ██║   ██║██╔══██╗   ██║   ██║██║╚██╗██║██║   ██║
# ███████╗██╔╝ ██╗██║     ╚██████╔╝██║  ██║   ██║   ██║██║ ╚████║╚██████╔╝
# ╚══════╝╚═╝  ╚═╝╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝╚═╝  ╚═══╝ ╚═════╝ 
# Functions responsible for writing data to CSV files, these all need more comments
# fmt: on

    # export wire data to CSV file
    def exportWireMeasurements(self):
        if len(self.data.wireData) == 0:
            tkinter.messagebox.showerror(
                title="Error",
                message=f"No wire tension data found for MN{self.data.humanID}",
            )
            return
        with open(
            f"MN{self.data.humanID}_wire_tension_data.csv", "w", newline=""
        ) as csvFile:
            csvWriter = csv.writer(csvFile)
            csvWriter.writerow([f"MN{self.data.humanID} Wire Tension Data"])
            csvWriter.writerow(
                ["Position", "Tension", "Wire Timer", "Calibration Factor"]
            )
            csvWriter.writerows(self.data.wireData)
            tkinter.messagebox.showinfo(
                title="Data Exported",
                message=f"Data exported to MN{self.data.humanID}_wire_tension_data.csv",
            )

    # export straw tension data to CSV (TODO: NEEDS COMMENTS)
    def exportStrawMeasurements(self):
        if len(self.data.strawData) == 0:
            tkinter.messagebox.showerror(
                title="Error",
                message=f"No straw tension data found for MN{self.data.humanID}",
            )
            return
        with open(
            f"MN{self.data.humanID}_straw_tension_data.csv", "w", newline=""
        ) as csvFile:
            csvWriter = csv.writer(csvFile)
            csvWriter.writerow([f"MN{self.data.humanID} Straw Tension Data"])
            csvWriter.writerow(["Position", "Tension", "Uncertainty", "Timestamp"])
            csvWriter.writerows(self.data.strawData)
            tkinter.messagebox.showinfo(
                title="Data Exported",
                message=f"Data exported to MN{self.data.humanID}_straw_tension_data.csv",
            )

    # export HV data to CSV (TODO: NEEDS COMMENTS)
    def exportHVMeasurements(self):
        # (<POS>, <L_AMPS>, <R_AMPS>, <TRIP>, <TIME>)
        if len(self.data.hvData) == 0:
            tkinter.messagebox.showerror(
                title="Error", message=f"No HV data found for MN{self.data.humanID}"
            )
            return
        with open(f"MN{self.data.humanID}_HV_data.csv", "w", newline="") as csvFile:
            csvWriter = csv.writer(csvFile)
            csvWriter.writerow([f"MN{self.data.humanID} HV Data"])
            csvWriter.writerow(
                [
                    "Position",
                    "Left Current",
                    "Right Current",
                    "Trip Status",
                    "Timestamp",
                ]
            )
            csvWriter.writerows(self.data.hvData)
            tkinter.messagebox.showinfo(
                title="Data Exported",
                message=f"Data exported to MN{self.data.humanID}_HV_data.csv",
            )
    
    # export heat data to CSV
    def exportHeatMeasurements(self):
        # get the current pro
        curPro = self.ui.heatProBox.currentText()[8]

        if len(self.getHeatData(curPro, "HeatData")) == 0:
            tkinter.messagebox.showerror(
                title="Error", message=f"No heat data found for MN{self.data.humanID}"
            )
            return

        with open(f"MN{self.data.humanID}_pro_{curPro}_heat_data.csv", "w", newline="") as csvFile:
            csvWriter = csv.writer(csvFile)
            csvWriter.writerow([f"MN{self.data.humanID} heat Data"])
            csvWriter.writerow(
                [
                    "Time (Human)",
                    "Time (Epoch)",
                    "PAAS A Temp",
                    "PAAS B/C Temp"
                ]
            )
            csvWriter.writerows(self.getHeatData(curPro, "HeatData"))
            tkinter.messagebox.showinfo(
                title="Data Exported",
                message=f"Data exported to MN{self.data.humanID}_pro_{curPro}_heat_data.csv",
            )


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
        # self.data.wireData = [(pos,ten,...), (pos,ten,...),...]
        xData = list(range(96))  # string positions: 0 to 95
        sctrYData = []  # give this list data in for loop
        for toop in self.data.wireData:  # go through wireTensionData
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
        # self.data.strawData = [(pos, ten, unc, time),...]
        xData = list(range(96))
        sctrYDataPoints = []
        sctrYDataUncs = []
        for toop in self.data.strawData:
            if toop[1] != "No Data" and toop[2] != "No Data":
                sctrYDataPoints += [toop[1]]
                sctrYDataUncs += [toop[2]]
            else:
                sctrYDataPoints += [None]  # source of a bug???
                sctrYDataUncs += [None]

        plt.subplot(211)
        # plt.figure(figsize=(12,8))
        
        try:
            plt.errorbar(
                        xData, sctrYDataPoints, yerr=sctrYDataUncs, fmt="o"
                    )  # make a scatterplot out of the x and y data
        except:
            print("Insufficient data to plot error bars.")
            
        plt.axis([0, 100, 0, 1000])  # set the bounds of the graph
        plt.xlabel("Wire Position", fontsize=20)  # set x axis label
        plt.ylabel("Straw Tension", fontsize=20)  # set y axis label
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
        for toop in self.data.hvData:
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
        for toop in self.data.hvData:
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
        # get the current pro
        curPro = self.ui.heatProBox.currentText()[8]

        # make x data list by converting raw timesamps to matplotlib dates
        xData = [
            mpl.dates.epoch2num(toop[1]) for toop in self.getHeatData(curPro, "HeatData")
        ]

        if len(xData) <3 : # <3
            tkinter.messagebox.showerror(
                title="Error",
                message=f"Too little or no heat data was found for MN{self.data.humanID}, process {curPro}.",
            )
            return

        # make y data sets
        yDataA = [
            toop[2] for toop in self.getHeatData(curPro, "HeatData")
        ]
        yDataBC = [
            toop[3] for toop in self.getHeatData(curPro, "HeatData")
        ]
        #yColorBC = [(heat - 5) for heat in yDataBC]
        

        # make subplot for PAAS A
        plt.subplot(211)
        plt.plot_date(xData, yDataA) # make plot
        mpl.dates.HourLocator()
        plt.xlabel("Time", fontsize=20)  # set x axis label
        plt.ylabel("Temperature of PAAS A (°C)", fontsize=20)  # set y axis label

        # make subplot for PAAS A
        plt.subplot(212)
        plt.plot_date(xData, yDataBC) # make plot
        mpl.dates.HourLocator()
        plt.xlabel("Time", fontsize=20)  # set x axis label
        plt.ylabel("Temperature of PAAS B/C (°C)", fontsize=20)  # set y axis label
        
        '''
        This adds color(sick as frick), but the x ticks are in days since 0001...
        # make subplot for PAAS B/C
        plt.subplot(212)
        plt.scatter(xData, yDataBC, c=yColorBC, s=10, cmap=plt.cm.jet) # make plot
        mpl.dates.HourLocator()
        plt.xlabel("Time", fontsize=20)  # set x axis label
        plt.ylabel("Temperature of PAAS B/C (°C)", fontsize=20)  # set y axis label
        '''

        plt.tight_layout()
        plt.show()


# fmt: off
# ██████╗  █████╗ ██████╗ ███████╗███████╗    ██████╗  █████╗ ████████╗ █████╗ 
# ██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔════╝    ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗
# ██████╔╝███████║██████╔╝███████╗█████╗      ██║  ██║███████║   ██║   ███████║
# ██╔═══╝ ██╔══██║██╔══██╗╚════██║██╔══╝      ██║  ██║██╔══██║   ██║   ██╔══██║
# ██║     ██║  ██║██║  ██║███████║███████╗    ██████╔╝██║  ██║   ██║   ██║  ██║
# ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝
# Functions that put data onto the GUI
# findComments() should be split into findComments() and displayComments(), same w/ findMeasurements()
# fmt: on

    # put panel part IDs (human IDs not database IDs)
    def displayParts(self):
        
        # function to get widgets w/ string
        def getPartWidget(self, widget):
            return getattr(self.ui, f"part{widget}LE")

        # for each type of part,
        for key in self.data.parts:
            # set the corresponding widget to the key's number
            if self.data.parts[key] > -1:
                getPartWidget(self, key).setText(
                    str(self.data.parts[key])
                    )
            else:
                getPartWidget(self, key).setText("Not found")

    # put hv data on gui
    def displayHV(self):
        extantHVData = False
        # make sure data exists
        # look through data to look for a number
        for toop in self.data.hvData:
            if toop[1] != "No Data":
                extantHVData = True
        
        # if hv data exists
        if extantHVData:
            self.ui.hvExportButton.setEnabled(True)
            self.ui.plotHVDataButton.setEnabled(True)
            trippedBrush = QBrush(Qt.red)
            self.ui.hvListWidget.addItem(
                f'{str("Position").ljust(14)}{str("L μA").ljust(18)}{str("R μA").ljust(18)}'
            )
            for toop in self.data.hvData:  # for each tuple in self.data.hvData
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


    # put wire tension data on gui
    def displayWires(self):
        extantWireData = False

        for toop in self.data.wireData:  # for each tuple in self.data.wireData
            if toop[1] != "No Data":  # if it isn't "No Data"
                extantWireData = True  # then data exists!

        if extantWireData:  # if wire data exists
            self.ui.wireExportButton.setEnabled(True)
            self.ui.plotWireDataButton.setEnabled(True)
            self.ui.wireListWidget.addItem(
                "Position      Tension"
            )  # add wire tension header
            for toop in self.data.wireData:  # for each tuple in wire data
                self.ui.wireListWidget.addItem(
                    f"{str(toop[0]).ljust(18)}{toop[1]}"
                )  # add position and tension to list TODO: use string fill?


    # put straw tension data on gui
    def displayStraws(self):
        extantStrawData = False

        for toop in self.data.strawData:
            if toop[1] != "No Data":
                extantStrawData = True

        if extantStrawData:
            self.ui.strawExportButton.setEnabled(True)
            self.ui.plotStrawDataButton.setEnabled(True)
            self.ui.strawListWidget.addItem("Position     Tension     Uncertainty")
            for toop in self.data.strawData:  # for each tuple in strawTensionData
                self.ui.strawListWidget.addItem(
                    f"{str(toop[0]).ljust(18)}{str(toop[1]).ljust(18)}{str(toop[2]).ljust(18)}"
                )  # add position, tension, and uncertainty to list

    
    # put heat statistics on the gui
    def displayHeat(self):

        # clear out the current data
        self.ui.heatListWidget.clear()

        

        # get the current pro
        curPro = self.ui.heatProBox.currentText()[8]


        if isinstance(self.getHeatData(curPro, "HeatData"), list):
            self.ui.heatListWidget.addItem(f'{len(self.getHeatData(curPro, "HeatData"))} measurements found for process {curPro}.')
            self.ui.heatListWidget.addItem(f'Total Heat Time: {self.getHeatData(curPro,"HeatTime")}' if (self.getHeatData(curPro,"HeatTime") is not []) else "No Heat Time Data Found")

            self.ui.heatExportButton.setEnabled(True)
            self.ui.plotHeatDataButton.setEnabled(True)

            self.ui.heatListWidget.addItem(f'PAAS A Stats' if len(self.getHeatData(curPro,"AStats")) > 0 else "No PAAS A Data Found :(")
            if len(self.getHeatData(curPro,"AStats")) > 0:
                paasAItemsToAdd = [
                    f'PAAS A Mean Temperature: {round(self.getHeatData(curPro,"AStats")[0], 2)}' if len(self.getHeatData(curPro,"AStats")) > 0 else "None",
                    f'PAAS A Maximum Temperature: {self.getHeatData(curPro,"AStats")[2]}' if len(self.getHeatData(curPro,"AStats")) > 0 else "None",
                    f'PAAS A Minimum Temperature: {self.getHeatData(curPro,"AStats")[1]}' if len(self.getHeatData(curPro,"AStats")) > 0 else "None",
                    f'PAAS A Standard Deviation: {round(self.getHeatData(curPro,"AStats")[3], 2)}' if len(self.getHeatData(curPro,"AStats")) > 0 else "None"
                ]
                self.ui.heatListWidget.addItems(paasAItemsToAdd)
            else:
                self.ui.heatListWidget.addItem("No PAAS A data found :(")

            self.ui.heatListWidget.addItem(f'PAAS B/C Stats' if len(self.getHeatData(curPro,"BCStats")) > 0 else "No PAAS B/C Data Found :(")
            if len(self.getHeatData(curPro,"BCStats")) > 0:
                paasBItemsToAdd = [
                    f'PAAS B/C Mean Temperature: {round(self.getHeatData(curPro,"BCStats")[0], 2)}' if len(self.getHeatData(curPro,"BCStats")) > 0 else "None",
                    f'PAAS B/C Maximum Temperature: {self.getHeatData(curPro,"BCStats")[2]}' if len(self.getHeatData(curPro,"BCStats")) > 0 else "None",
                    f'PAAS B/C Minimum Temperature: {self.getHeatData(curPro,"BCStats")[1]}' if len(self.getHeatData(curPro,"BCStats")) > 0 else "None",
                    f'PAAS B/C Standard Deviation: {round(self.getHeatData(curPro,"BCStats")[3], 2)}' if len(self.getHeatData(curPro,"BCStats")) > 0 else "None"
                ]
                self.ui.heatListWidget.addItems(paasBItemsToAdd)
            else:
                self.ui.heatListWidget.addItem("No PAAS B/C data found :(")
        else:
            self.ui.heatListWidget.addItem(f'0 measurements found for process {curPro}')

        # enabled no matter what to allow switching between pros
        self.ui.heatProBox.setEnabled(True)

    # put procedure timestamps (in human readable form) on the gui
    def displayTiming(self):

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
                        self.getTimeWidget(key,"L").addItem(
                            f"START:  {time.strftime('%a, %d %b %Y %H:%M:%S', (time.localtime(event[1])))}"
                        )
                    elif event[0] == "stop":
                        stopTime = event[1]
                        totalTime += (event[1] - lastTime)
                        self.getTimeWidget(key,"L").addItem(
                            f"END:  {time.strftime('%a, %d %b %Y %H:%M:%S', (time.localtime(event[1])))}"
                        )
                    elif event[0] == "pause":
                        totalTime += (event[1] - lastTime)
                        self.getTimeWidget(key,"L").addItem(
                            f"PAUSE:  {time.strftime('%a, %d %b %Y %H:%M:%S', (time.localtime(event[1])))}"
                        )
                    elif event[0] == "resume":
                        self.getTimeWidget(key,"L").addItem(
                            f"RESUME:  {time.strftime('%a, %d %b %Y %H:%M:%S', (time.localtime(event[1])))}"
                        )
                        lastTime = event[1]

                # start time
                if startTime > 0:
                    self.getTimeWidget(key, 'S').setText(
                        time.strftime("%a, %d %b %Y %H:%M:%S", (time.localtime(startTime)))
                    )
                else:
                    self.getTimeWidget(key, 'S').setText(
                        "Not found"
                    )

                # end time
                if stopTime > 0:
                    self.getTimeWidget(key, 'E').setText(
                        time.strftime("%a, %d %b %Y %H:%M:%S", (time.localtime(stopTime)))
                    )
                else:
                    self.getTimeWidget(key, 'E').setText(
                        "Not found"
                    )
                # total/elapsed time
                if totalTime > 0:
                    prefix = "Estimate: " if stopTime <= 0 else ""
                    self.getTimeWidget(key, 'T').setText(
                        # totalTime = total time in seconds
                        # hours = totalTime//3600
                        # minutes = (totalTime%3600)//60
                        # seconds = totalTime%60
                        f"{prefix}{totalTime//3600}:{(totalTime%3600)//60}:{totalTime%60}"
                    )
                else:
                    self.getTimeWidget(key, 'T').setText(
                        "Not found"
                    )
                





    # remove data from all widgets
    def clearWidgets(self):

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

        # clear part widgets
        # widget type: QLineEdit
        for widget in self.partSetupWidgetList:
            widget.setText("")

        # clear measurement widgets
        # widget type: QListWidget
        self.ui.strawListWidget.clear()
        self.ui.wireListWidget.clear()
        self.ui.hvListWidget.clear()
        self.ui.heatListWidget.clear()
        
        
# fmt: off
# ███╗   ███╗██╗███████╗ ██████╗
# ████╗ ████║██║██╔════╝██╔════╝
# ██╔████╔██║██║███████╗██║     
# ██║╚██╔╝██║██║╚════██║██║     
# ██║ ╚═╝ ██║██║███████║╚██████╗
# ╚═╝     ╚═╝╚═╝╚══════╝ ╚═════╝
# The isle of misfit functions
# fmt: on

    # a function to get heat related member variables from facileDBGUI by name
    # takes a pro and type of data you want (should be one of AStats, BCStats, HeatData, HeatTime)
    # and returns a pointer to the member you indicated (ex, get(2,AStats) returns self.pro2AStats)
    # I should make one of these that can get any data from anywhere in the GUI...  maybe later!
    def getHeatData(self, pro, data):
        return getattr(self, f"pro{pro}{data}")

    # similar to getHeatData, except it gets a specific widget
    # pro = process station type (pan1, pan2, etc)
    # event = 'S', 'E', 'T', or "L" s = start, e = end, t = total, l = list
    def getTimeWidget(self, pro, event):
        if event == "L":
            return getattr(self.ui, f"{pro}TimeList")
        else:
            return getattr(self.ui, f"{pro}{event}Time")

    # override close button event (see comments in function)
    def closeEvent(self, event):
        sys.exit()  # kill program
        # this is necessary since using the pyplot.show() makes python think there's another app running, so closing the gui
        # won't close the program if you used the plot button (so you'd have a python process still running in the background
        # doing nothing).  Overriding the closeEvent to exit the program makes sure the whole process is dead when the user
        # clicks the X in the upper right corner.
        # It's not called anywhere because having it here overwrites a QMainWindow method.
        # Killing it with sys.exit() will not hurt the database.
    
    # takes a tuple (from the query for part data), filters out the junk, saves to self.data.parts
    # and returns a part tuple minus the junk
    def sortAndRefinePart(self, part):
        
        # parameter part:
        #   0           1           2           3           4                       5           6               7
        #(<panelnum>, <part id>, <straw_loc>, <ALF L/R>, <type (MIR, ALF, etc)>, <part num>, <PIR l/R>, <PIR,PAAS A/B/C>)
        # retPart:
        #   0           1                       2           3           4
        #(<ALF L/R>, <type (MIR, ALF, etc)>, <part num>, <PIR l/R>, <PIR,PAAS A/B/C>)
        retPart = ["","","","",""]

        for i in range(3,8):
            if part[i] is not None:
                retPart[i-3] = part[i]
        
        # build a string to function as a dict key (for self.data.parts dict)
        # some of the pieces will be "", some will be a string like "PIR", "L", "A", etc.
        self.data.parts[f'{retPart[1]}{retPart[3]}{retPart[4]}{retPart[0]}'] = retPart[2]

        return retPart


    '''
    def latestChanges(self):
        tkinter.messagebox.showinfo(
                title="Latest Changes",
                message= """

                """
            )
    '''

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
    print(getpass.getuser())
    app = QApplication(sys.argv)  # make an app
    # app.setStyleSheet(qdarkstyle.load_stylesheet())    # darkmodebestmode
    window = facileDBGUI(Ui_MainWindow())  # make a window
    if ISLAB:
        window.connectToNetwork()  # link to database
        window.setWindowTitle("Database Viewer, Network Connection") # change from default window title
    else:
        window.connectToLocal() #link to database
        window.setWindowTitle("Database Viewer, Local Connection")
        # make sure you can tell the difference between local and network connections
    window.showMaximized()  # open in maximized window (using show() would open in a smaller one with weird porportions)

    app.exec_()  # run the app!
