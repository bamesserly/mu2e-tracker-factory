import sys, time, tkinter, tkinter.messagebox # for opening new app, time formatting, auto refresh events, popup messages
from coolLabStatusGUI import Ui_MainWindow # for importing UI
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QTableWidget, 
    QGridLayout, QScrollArea, QWidget, QComboBox, QListWidget, QListWidgetItem,
    QCheckBox, QPushButton, QTableWidgetItem, QGroupBox, QLineEdit, QProgressBar)
from PyQt5.QtGui import QBrush, QFont
# for GUI widget management^
from PyQt5.QtCore import Qt, QRect, QObject, QTimer # for gui window management
from datetime import datetime   # for time formatting
import sqlalchemy as sqla   # for interacting with db
import sqlite3  # for connecting with db

# - -    --   - - /|_/|          .------------------------.
# _______________| @.@|         / GUI to show panel status )
#(______         >\_W/<     ---/   on the TV in the lab   /
#  -   / ______  _/____)      (   Author: Adam Arnett    /
# -   / /\ \   \ \             `------------------------'
#  - (_/  \_) - \_)

PRONAMES = [
    "Inner Ring",
    "Straws",
    "Sense Wire",
    "Pin Protectors",
    "High Voltage",
    "Manifold",
    "Flooding",
    "Final QC",
    "Storage"
]



class Step:
    def __init__(self, stepNumber, stepStation, stepName, nextStep):
        self.stepNumber = stepNumber    # number of step (id in the database)
        self.stepStation = stepStation  # station the step is for
        self.stepName = stepName        # name of the step (ex. apply_epoxy)
        self.nextStep = nextStep        # id of next step

class Panel:
    def __init__(self, number, location):
        self.number = number        # readable ID (MN XYZ)
        self.location = location    # database ID (really big int)
        self.proceduresFinished = 0 # number of finished procedures
        self.stepsFinished = [0,0,0,0,0,0,0]    # number of finished steps for each procedure
        self.recentUpdate = -1      # most recent timestamp
        self.currentStep = -1       # most recent step
        self.currentPro = -1        # most current procedure
    
    # is passed a string and int
    def addStep(self, stepPro, timestamp, stepNum):
        self.stepsFinished[int(stepPro[3])-1] += 1     # add one to number of steps complete for corresponding procedure
        if self.recentUpdate < timestamp:
            self.recentUpdate = timestamp
            self.currentPro = int(stepPro[3])
            self.currentStep = stepNum
    
    def checkProCompletion(self, numStepsList):
        self.proceduresFinished = 0
        for i, pro in enumerate(self.stepsFinished):
            if pro == numStepsList[i]:
                self.proceduresFinished += 1

    def __repr__(self):
        return str(self.number)



class labGUI(QMainWindow):
    def __init__(self, ui_layout):
        # setup UI
        QMainWindow.__init__(self)  # initialize superclass
        self.ui = ui_layout         # make ui member
        ui_layout.setupUi(self)     # apply ui to window
        self.tkRoot = tkinter.Tk()  # make tkinter root for popup messages
        self.tkRoot.withdraw()      # hide root, it's necessary for popups to work, but it's just a blank window otherwise
        self.panels = {}            # store panel objects
        self.numDisplayed = 0       # number of panels being displayed
        self.steps = {}             # store step objects
        self.scrollGrid = QGridLayout() # scroll area
        self.initTimer()            # start timer and refreshing

        self.colorActions = [               # list of color theme actions
            self.ui.actionBoring,
            self.ui.actionCool_Default,
            self.ui.actionDark,
            self.ui.actionLight,
            self.ui.actionUMN,
            self.ui.actionVantablack,
            self.ui.actionSurprise
        ]

    # make engine, connection, and metadata objects to interact with database
    def connectToDB(self):
        # real connection code:
        
        # override connect to return a read-only DB connection, MUST use path starting at C drive
        # more on this: https://github.com/sqlalchemy/sqlalchemy/issues/4863
        tkinter.messagebox.showinfo(
            title='Connecting',
            message=f'Connecting to network database...'
        )    
        def connectSpecial():
            return sqlite3.connect("file:Z:\Production_Environment\Database\database.db?mode=ro", uri=True)
            #return sqlite3.connect("file:/spa-mu2e-network/Files/Production_Environment/Database/database.db?mode=ro", uri=True)
        #self.engine = sqla.create_engine('sqlite://Z:/Production_Environment/Database/database.db', creator=connectSpecial)    # create engine
        self.engine = sqla.create_engine('sqlite:///../../Database/database.db/', creator=connectSpecial)    # create engine
        # try to use read only mode
        # If the path above is wrong, read-only will fail.  I could see a mergedown or misplaced file easily screwing up the path.
        # If read-only fails, it'll use the regular SQLAlchemy connection.  The regular connection shouldn't write to the DB, but
        # having read-only mode is a good safety net.
        try:
            self.connection = self.engine.connect()     # connect engine with DB
        except:
            tkinter.messagebox.showerror(
                title='Error',
                message=f'Read-only mode failed.  The network is not mapped as the Z drive.  Contact a member of the software team for help.'
            )                                           # show error message

        '''
        # fake temporary code for Adam's computer:
        self.engine = sqla.create_engine('sqlite:///../../Database/database.db')    # create engine
        self.connection = self.engine.connect()     # connect engine with DB
        '''

        self.metadata = sqla.MetaData()             # create metadata
        self.makeSQLTables()                        # make tables for later use
        
    
    def makeSQLTables(self):
        self.panelsTable = sqla.Table('straw_location', self.metadata, autoload = True, autoload_with = self.engine)    # straw_location
        self.proceduresTable = sqla.Table('procedure', self.metadata, autoload = True, autoload_with = self.engine)     # procedure
        self.stepsDefTable = sqla.Table('panel_step', self.metadata, autoload = True, autoload_with = self.engine)      # step defenitions
        self.stepsDoneTable = sqla.Table('panel_step_execution', self.metadata, autoload = True, autoload_with = self.engine)   # steps completed
        self.sessionsTable = sqla.Table('session', self.metadata, autoload = True, autoload_with = self.engine)         # work sessions
        self.workersTable = sqla.Table('worker_login', self.metadata, autoload = True, autoload_with = self.engine)     # workers

    def findStepDefs(self):
        # find step defenitions
        stepsDefQuery = sqla.select([                   # find defenitions of steps
            self.stepsDefTable.columns.id,              # get the id,
            self.stepsDefTable.columns.station,         # station
            self.stepsDefTable.columns.name,            # name of step
            self.stepsDefTable.columns.next             # id of next step
        ]).where(
            self.stepsDefTable.columns.current == 1     # include current steps
        ).where(
            self.stepsDefTable.columns.checkbox == 1    # exclude uncheckable steps
        )

        resultProxy = self.connection.execute(stepsDefQuery)    # proxy for query execution
        stepsDefResults = resultProxy.fetchall()                # get list of tuples

        self.numStepsList = [0,0,0,0,0,0,0]     # make list for number of steps for each procedure
        
        for i in range(7):                      # for i = (0,6); (i+1) = procedure number
            for step in stepsDefResults:            # for each step found earlier,
                if step[1] == f'pan{i+1}':              # if that step is for the (i+1)th procedure
                    self.numStepsList[i] += 1               # add 1 to the number of steps that procedure has
        
        for toop in stepsDefResults:    # for each step defenition
            self.steps[toop[0]] = Step(toop[0], toop[1], toop[2], toop[3])   # keep it for future referance!  as a step object

    def findPanels(self):
        start = time.time()
        
        panelsQuery = sqla.select([         # get straw_locations for panels that could be in progress
            self.panelsTable.columns.id
        ]).where(     
            self.panelsTable.columns.number >= 38       # MN036 is already complete
        ).where(                   
            self.panelsTable.columns.number <= 200      # No real panels will have an ID > something in the upper 100's
        )
        resultProxy = self.connection.execute(panelsQuery)      # execute panels query
        panelsResults = resultProxy.fetchall()                  # fetch list of straw_location ids in list of tuples: (<location>,)

        refinedPanelsResults = []                               # make empty list
        for toop in panelsResults:                              # for each tuple in the raw results
            refinedPanelsResults.append(toop[0])                # add the actual data to the list we just made


        proceduresQuery = sqla.select([         # find procedures and straw_locations for potentially in progress panels
            self.proceduresTable.columns.straw_location,
            self.proceduresTable.columns.id,
            self.proceduresTable.columns.station
        ]).where(
            self.proceduresTable.columns.straw_location.in_(refinedPanelsResults)   # eliminate procedures for already completed panels
        )
        resultProxy = self.connection.execute(proceduresQuery)  # execute procedures query
        proceduresResults = resultProxy.fetchall()              # fetch list of straw_location ids in list of tuples: (<location>, <procedureID>, <station>)

        locationResults = []                            # make empty list
        for toop in proceduresResults:                  # for each tuple in the raw results
            locationResults.append(toop[0])                 # add the actual data to the list we just made

        startedPanels = []                              # make empty list (for started panel straw_locations)
        for panelID in locationResults:                 # for each straw_location we have
            if locationResults.count(panelID) > 0:          # if it has at least one procedure
                startedPanels.append(panelID)                   # then it has been started

        #print(refinedProceduresResults)
        #print(startedPanels)
        ########################## AT THIS POINT WE HAVE THE STARTED PANELS

        recentPanelQuery = sqla.select([
            self.stepsDoneTable.columns.panel_step,     # 0 - step number
            self.stepsDoneTable.columns.timestamp,      # 1 - step timestamp
            #self.proceduresTable.columns.id,           # NA- pro ID
            self.proceduresTable.columns.station,       # 2 - pro station
            self.panelsTable.columns.id,                # 3 - panel straw_location
            self.panelsTable.columns.number             # 4 - panel number
            ]).where(self.panelsTable.columns.id.in_(startedPanels))
        
        recentPanelQuery = recentPanelQuery.select_from(
                self.panelsTable.join(
                    self.proceduresTable, self.panelsTable.columns.id == self.proceduresTable.columns.straw_location).join(
                        self.stepsDoneTable, self.stepsDoneTable.columns.procedure == self.proceduresTable.columns.id)
        )
        
        resultProxy = self.connection.execute(recentPanelQuery)
        #print(len(resultProxy.fetchall()))
        recentPanels = resultProxy.fetchall()

        for toop in recentPanels:
            if toop[4] in self.panels:  # if the corresponding panel exists,
                self.panels[toop[4]].addStep(toop[2], toop[1], toop[0])  # add step to panel object
            else:                       # if the corresponding panel doesn't exist,
                self.panels[toop[4]] = Panel(toop[4], toop[3])  # make one
                self.panels[toop[4]].addStep(toop[2], toop[1], toop[0])  # add the step

        for panelID in self.panels:
            self.panels[panelID].checkProCompletion(self.numStepsList)
        
        #print(self.panels)
        #print(self.panels[38].proceduresFinished)

        end = time.time()
        elapsedMiliseconds = round((end-start)*1000, 1)
        now = time.strftime('%H:%M', time.localtime(time.time()))
        print(f'Found panels in {elapsedMiliseconds} miliseconds')
        self.ui.statusbar.showMessage(f'Found panels in {elapsedMiliseconds} miliseconds at {now}', 600000)

    # make a layout for the scroll area
    def initScrollArea(self):
        self.scrollGrid = QGridLayout()
        self.ui.panelScrollAreaContents.setLayout(self.scrollGrid)

    # put widgets onto GUI
    def makeWidget(self, panelObj):
        newBox = QGroupBox()
        newBox.setFont(QFont("MS Shell Dlg 2", 20))
        newBox.setTitle(f'MN{str(panelObj.number).zfill(3)}')
        newBox.setMaximumSize(1000, 600)
        newBoxLayout = QGridLayout()

        # time of update
        newLabel1 = QLabel()
        newLabel1.setText("Time of Last Update")
        newLabel1.setFont(QFont("MS Shell Dlg 2", 20))
        newBoxLayout.addWidget(newLabel1,0,0)
        recentUpdateLE = QLineEdit()
        recentUpdateLE.setText(time.strftime('%a, %m-%d, %H:%M', time.localtime(panelObj.recentUpdate)))
        recentUpdateLE.setFont(QFont("MS Shell Dlg 2", 20))
        recentUpdateLE.setReadOnly(True)
        newBoxLayout.addWidget(recentUpdateLE,0,1)

        # current process
        newLabel2 = QLabel()
        newLabel2.setText("Current Process")
        newLabel2.setFont(QFont("MS Shell Dlg 2", 20))
        newBoxLayout.addWidget(newLabel2,1,0)
        currentProLE = QLineEdit()
        currentProLE.setText(PRONAMES[panelObj.currentPro - 1])
        currentProLE.setFont(QFont("MS Shell Dlg 2", 20))
        currentProLE.setReadOnly(True)
        newBoxLayout.addWidget(currentProLE,1,1)

        # last step
        newLabel3 = QLabel()
        newLabel3.setText("Last Completed Step")
        newLabel3.setFont(QFont("MS Shell Dlg 2", 20))
        newBoxLayout.addWidget(newLabel3,2,0)
        lastStepLE = QLineEdit()
        tempText = (self.steps[panelObj.currentStep].stepName).replace('_', ' ')
        tempText = tempText.title()
        lastStepLE.setText(tempText)
        lastStepLE.setFont(QFont("MS Shell Dlg 2", 20))
        lastStepLE.setReadOnly(True)
        newBoxLayout.addWidget(lastStepLE,2,1)

        # current step
        newLabel5 = QLabel()
        newLabel5.setText("Current Step")
        newLabel5.setFont(QFont("MS Shell Dlg 2", 20))
        newBoxLayout.addWidget(newLabel5,3,0)
        currentStepLE = QLineEdit()
        # the step we want is the next step after the last completed step
        # self.steps[panelObj.currentStep].stepNumber gets us the last step
        # so <that^>.nextStep will give us the current step (like the step being worked on)
        if self.steps[self.steps[panelObj.currentStep].stepNumber].nextStep is not None:
            tempText = self.steps[self.steps[self.steps[panelObj.currentStep].stepNumber].nextStep].stepName.replace('_', ' ')
            tempText = tempText.title()
            currentStepLE.setText(tempText)
        else:   # it IS None, we need to get the next procedure
            if self.steps[self.steps[panelObj.currentStep].stepNumber].stepStation != 'pan7':
                currentStepLE.setText(f'Start {PRONAMES[panelObj.currentPro]}')
            else: # a complete panel made it through, return None since it doesn't need to be displayed
                return None
        currentStepLE.setFont(QFont("MS Shell Dlg 2", 20))
        currentStepLE.setReadOnly(True)
        newBoxLayout.addWidget(currentStepLE,3,1)

        # procedure completion
        newLabel4 = QLabel(self.ui.panelScrollAreaContents)
        newLabel4.setText("Process Completion")
        '''
        if round((panelObj.stepsFinished[panelObj.currentPro-1] / self.numStepsList[panelObj.currentPro-1]) * 100) == 69:
            newLabel4.setText("nice")
        '''
        newLabel4.setFont(QFont("MS Shell Dlg 2", 20))
        newBoxLayout.addWidget(newLabel4,4,0)
        proProgBar = QProgressBar(self.ui.panelScrollAreaContents)
        proProgBar.setFont(QFont("MS Shell Dlg 2", 20))
        proProgBar.setValue(
            (panelObj.stepsFinished[panelObj.currentPro-1] / self.numStepsList[panelObj.currentPro-1]) * 100
        )
        newBoxLayout.addWidget(proProgBar, 4, 1)


        # buttons
        commentsButton = QPushButton()
        commentsButton.setText("Open Comments")
        commentsButton.setFont(QFont("MS Shell Dlg 2", 20))
        commentsButton.setDisabled(True)
        newBoxLayout.addWidget(commentsButton,5,0)
        workersButton = QPushButton()
        workersButton.setText("Open Workers")
        workersButton.setFont(QFont("MS Shell Dlg 2", 20))
        workersButton.setDisabled(True)
        newBoxLayout.addWidget(workersButton,5,1)

        newBox.setLayout(newBoxLayout)
        return newBox

    def displayPanels(self):
        self.numDisplayed = 0

        for panel in self.panels:
            newWidget = self.makeWidget(self.panels[panel])
            if newWidget is not None:
                y = int(self.numDisplayed/2)
                x = self.numDisplayed%2
                self.scrollGrid.addWidget(self.makeWidget(self.panels[panel]),y,x)
                self.numDisplayed += 1

        self.ui.panelScrollAreaContents.setLayout(self.scrollGrid)

    def changeColor(self, background_color, text_color):
        tuple_min = lambda t : tuple(min(x, 255) for x in t)
        tuple_max = lambda t : tuple(max(x, 0) for x in t)
        tuple_add = lambda t, i: tuple((x + i) for x in t)
        invert = lambda t : tuple(255 - x for x in t)

        lighter = tuple_min(tuple_add(background_color, 20))
        darker = tuple_max(tuple_add(background_color, -11))

        text_color_invert = invert(text_color)
        background_color_invert = invert(background_color)

        stylesheet =    ('QMainWindow, QWidget#centralwidget, QWidget#stepsWidget, QWidget#toolWidget, QWidget#partWidget, QWidget#supplyWidget, QWidget#moldReleaseWidget, QWidget#scrollAreaWidgetContents { background-color: rgb' + f'{background_color};' + ' }\n'
                'QLineEdit { ' + f'color: rgb{text_color}; background-color: rgb{lighter};' + ' }\n'
                'QPlainTextEdit, QTextEdit, QLabel, QProgressBar { ' + f'color: rgb{text_color};' + ' }\n'
                'QGroupBox, QTabWidget, QSpinBox { ' + f'color: rgb{text_color}; background-color: rgb{darker};' + ' }\n'
                'QPushButton, QScrollArea, QPlainTextEdit, QTextEdit { ' + f'color: rgb{text_color}; background-color: rgb{darker}' + ' }\n'
                'QCheckBox { color: ' + f'rgb{text_color}' + '; ' + f'background-color: rgb{darker}' + '; }\n'
                'QLCDNumber { color: white; }\n'
                'QComboBox, QComboBox QAbstractItemView { '  + f'color: rgb{text_color}; background-color: rgb{background_color}; selection-color: rgb{background_color_invert}; selection-background-color: rgb{text_color_invert};' + ' }'
                f'QStatusBar {"{"}color: rgb{text_color}{"}"}'
                )

        self.ui.panelScrollArea.setStyleSheet("background-color:transparent;")
        self.ui.centralwidget.setStyleSheet(stylesheet)
    
    def refresh(self):
        # delete current widgets
        for i in reversed(range(self.scrollGrid.count())):      # must go backwards, widgets shift position if you start at the beginning
            self.scrollGrid.itemAt(i).widget().setParent(None)  # cut the widget loose

        if self.ui.actionRandom_Color_On_Refresh.isChecked():
            self.ui.actionSurprise.setChecked(True)
            self.toggleSurpriseMe(True)
            self.ui.actionRandom_Color_On_Refresh.setChecked(True)

        self.panels = {}
        self.steps = {}
        self.findStepDefs()
        self.findPanels()
        self.displayPanels()
    
    def tick(self):
        now = str(time.strftime('%H:%M:%S', time.localtime(time.time())))
        self.ui.clock.setText(now)


    def initTimer(self):
        self.refreshTimer = QTimer(self)
        self.refreshTimer.timeout.connect(self.refresh)
        self.refreshTimer.start(600000)     # refresh every 10 minutes
        self.clockTimer = QTimer(self)
        self.clockTimer.timeout.connect(self.tick)
        self.clockTimer.start(1000)         # refresh every second
    
    def connectActions(self):
        self.ui.actionRefresh_Now.triggered.connect(self.refresh)

        self.ui.actionBoring.triggered.connect(self.toggleBoringTheme)
        self.ui.actionCool_Default.triggered.connect(self.toggleCoolTheme)
        self.ui.actionDark.triggered.connect(self.toggleDarkTheme)
        self.ui.actionLight.triggered.connect(self.toggleLightTheme)
        self.ui.actionUMN.triggered.connect(self.toggleUMNTheme)
        self.ui.actionSurprise.triggered.connect(self.toggleSurpriseMe)
        self.ui.actionVantablack.triggered.connect(self.toggleVantablackTheme)
  
    def toggleBoringTheme(self, checked):
        if checked:
            for action in self.colorActions:
                action.setChecked(False)
            self.ui.actionRandom_Color_On_Refresh.setChecked(False)
            self.ui.actionBoring.setChecked(True)
            stylesheet = ('')
            self.ui.panelScrollArea.setStyleSheet("background-color:transparent;")
            self.ui.centralwidget.setStyleSheet(stylesheet)
        else:
            self.toggleCoolTheme(True)

    def toggleCoolTheme(self, checked):
        if checked:
            for action in self.colorActions:
                action.setChecked(False)
            self.ui.actionRandom_Color_On_Refresh.setChecked(False)
            self.ui.actionCool_Default.setChecked(True)
            self.ui.panelScrollArea.setStyleSheet("background-color:transparent;")
            self.changeColor((0,20,255),(255,255,255))
        else:
            self.toggleCoolTheme(True)
    
    def toggleDarkTheme(self, checked):
        if checked:
            for action in self.colorActions:
                action.setChecked(False)
            self.ui.actionRandom_Color_On_Refresh.setChecked(False)
            self.ui.actionDark.setChecked(True)
            self.ui.panelScrollArea.setStyleSheet("background-color:transparent;")
            self.changeColor((35,35,35),(255,255,255))
        else:
            self.toggleCoolTheme(True)

    def toggleLightTheme(self, checked):
        if checked:
            for action in self.colorActions:
                action.setChecked(False)
            self.ui.actionRandom_Color_On_Refresh.setChecked(False)
            self.ui.actionLight.setChecked(True)
            self.ui.panelScrollArea.setStyleSheet("background-color:transparent;")
            self.changeColor((255,255,255),(0,0,0))
        else:
            self.toggleCoolTheme(True)
    
    def toggleSurpriseMe(self, checked):
        if checked:
            for action in self.colorActions:
                action.setChecked(False)
            self.ui.actionRandom_Color_On_Refresh.setChecked(False)
            self.ui.actionSurprise.setChecked(True)
            seed = int(str(datetime.now())[20:])        # semi random number generator (the current microsecond)
            seedMod = int(str(datetime.now())[17:19])   # another semi random number generator (the current second)
            backR = (seed*seedMod)%255  # back red
            backG = (seed/seedMod)%255  # back green
            backB = (seed+seedMod)%255  # back blue
            textR = (backR+175)%255     # text red; keeping all of these at +X makes sure that the text is visible against the back
            textG = (backG+175)%255     # text green
            textB = (backB+175)%255     # text blue
            self.ui.panelScrollArea.setStyleSheet("background-color:transparent;")
            self.changeColor((backR,backG,backB),(textR,textG,textB))
        else:
            self.toggleCoolTheme(True)

    def toggleUMNTheme(self, checked):
        if checked:
            for action in self.colorActions:
                action.setChecked(False)
            self.ui.actionRandom_Color_On_Refresh.setChecked(False)
            self.ui.actionUMN.setChecked(True)
            self.ui.panelScrollArea.setStyleSheet("background-color:transparent;")
            self.changeColor((122,0,25),(255,204,51))
        else:
            self.toggleCoolTheme(True)
    
    def toggleVantablackTheme(self, checked):
        if checked:
            for action in self.colorActions:
                action.setChecked(False)
            self.ui.actionRandom_Color_On_Refresh.setChecked(False)
            self.ui.actionVantablack.setChecked(True)
            self.ui.panelScrollArea.setStyleSheet("background-color:transparent;")
            self.changeColor((0,0,0),(0,255,0))
        else:
            self.toggleCoolTheme(True)




if __name__ == "__main__":
    app = QApplication(sys.argv)        # make an app


    window = labGUI(Ui_MainWindow())    # make a window
    window.connectToDB()                # connect with database
    window.connectActions()
    window.findStepDefs()
    window.findPanels()
    window.initScrollArea()
    window.displayPanels()
    window.setWindowTitle("Cool Lab Status GUI")    # rename window
    window.changeColor((0,20,255),(255,255,255))
    window.showMaximized()  # open in maximized window (using show() would open in a smaller one with weird porportions)



    app.exec_() # run the app!
