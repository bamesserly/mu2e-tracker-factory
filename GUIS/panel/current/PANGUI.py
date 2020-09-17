"""
#
#  .oooooo.    ooooo     ooo ooooo      ooo        ooooo       .o.       ooooo ooooo      ooo 
# d8P'  `Y8b   `888'     `8' `888'      `88.       .888'      .888.      `888' `888b.     `8' 
#888            888       8   888        888b     d'888      .8"888.      888   8 `88b.    8  
#888            888       8   888        8 Y88. .P  888     .8' `888.     888   8   `88b.  8  
#888    o8888o  888       8   888        8  `888'   888    .88ooo8888.    888   8     `88b.8  
#`88.    .88'   `88.    .8'   888        8    Y     888   .8'     `888.   888   8       `888  
# `Y8bood8P'      `YbodP'    o888o      o8o        o888o o88o     o8888o o888o o8o        `8  
#                                                                                                                                                                    
This file is the class definition for the panel GUI. The whole GUI is run out of this main class.
UI elements come from the file panel.py, which is generated from panel.ui, which is edited from
Qt Creator.

Using [Ctrl] + K + 0 collapses all functions and sections, making it much easier to navigate
(On VS Code at least)

Original Authors: Jacob Christy, Kate Ciampa, Ben Hiltbrand
Updated/Expanded by: Adam Arnett, Himanshu Joshi

"""

###  _____                           _
### |_   _|                         | |
###   | | _ __ ___  _ __   ___  _ __| |_ ___
###   | || '_ ` _ \| '_ \ / _ \| '__| __/ __|
###  _| || | | | | | |_) | (_) | |  | |_\__ \
###  \___/_| |_| |_| .__/ \___/|_|   \__|___/
###                | |
###                |_|
import inspect
import pyautogui
from PIL import Image
import sys, time, os, tkinter, traceback, serial, platform
from datetime import datetime
from threading import Thread, enumerate as enumerateThreads
import numpy as np
import subprocess  ## run straw and wire tensioner GUIs as subprocesses
from PyQt5.Qt import PYQT_VERSION_STR  # used for version checking
from PyQt5.QtCore import (
    QCoreApplication,
    pyqtSignal,
    Qt,
    QRegularExpression,
    QEvent,
    pyqtBoundSignal,
    pyqtSlot,
)
from PyQt5.QtGui import (
    QRegularExpressionValidator,
    QPixmap,
    QValidator,
    QDoubleValidator,
)

# pyqt5 docs: https://www.riverbankcomputing.com/static/Docs/PyQt4/classes.html
from PyQt5.QtWidgets import (
    QCheckBox,
    QLabel,
    QComboBox,
    QSizePolicy,
    QInputDialog,
    QMainWindow,
    QApplication,
    QMessageBox,
    QStyleFactory,
    QLineEdit,
    QVBoxLayout,
    QGridLayout,
)

# the next import is the class for the ui
# edit it via Qt Designer
# changing the gui color is easy using panelGUI.changeColor in the panelGUI init function
# when making changes to this file make sure that the button names and stuff match up
from panel import Ui_MainWindow

from suppliesList import SuppliesList
from dialogBox import DialogBox
from stepsList import StepList
import serial.tools.list_ports
from pathlib import Path, PurePath
from dataProcessor import MultipleDataProcessor as DataProcessor
from tension_devices.straw_tensioner.run_straw_tensioner import StrawTension
from tension_devices.wire_tensioner.wire_tension import WireTensionWindow
from tension_devices.tension_box.tensionbox_window import TensionBox
from tension_devices.panel_heater.PanelHeater import HeatControl

# Import QLCDTimer from Modules
sys.path.insert(
    0, str(Path(Path(__file__).resolve().parent.parent.parent.parent / "Modules"))
)
from timer import QLCDTimer

# import packages that are used by other files (data processor, straw tensioner, etc.)
# this 'should' slightly speed up the program while it's running, with a tiny bit of time added to starting it up
# also allows for checking the packages right off the bat
import cycler, kiwisolver, matplotlib, pyparsing, pyrect, pyscreeze, pytweening, scipy, setuptools, six, sqlalchemy


###  _____ _       _           _   _____ _          __  __
### |  __ \ |     | |         | | /  ___| |        / _|/ _|
### | |  \/ | ___ | |__   __ _| | \ `--.| |_ _   _| |_| |_
### | | __| |/ _ \| '_ \ / _` | |  `--. \ __| | | |  _|  _|
### | |_\ \ | (_) | |_) | (_| | | /\__/ / |_| |_| | | | |
###  \____/_|\___/|_.__/ \__,_|_| \____/ \__|\__,_|_| |_|
###

# Global Debug flag, set to True when debugging
# Disables enforcing worker-id input and supplies list check-off
# Make sure to set to False for production
DEBUG = True

# Global variables.
# Set each true/false to save the data collected when this gui is run to that platform.
# Note: Both can be true.
SAVE_TO_TXT = True
SAVE_TO_SQL = True

# Indicate which data processor you want to use for data-checking (ex: checkCredentials)
# PRIMARY_DP =   'TXT'
PRIMARY_DP = "SQL"

# set LAB_VERSION=True for lab path references and python/pythonw subprocesses
# for stand alone compiled version, set LAB_VERSION=False
# LAB_VERSION = False
LAB_VERSION = True


class panelGUI(QMainWindow):
    """
    class panelGUI5

    Description: The main class for the panel GUI. This class handles all of the pros, as well as saving and loading data.
                 The class inherhits from QMainWindow in order to function as a proper GUI.
    """

    ###  ___       _ _   _       _ _
    ### |_ _|_ __ (_) |_(_) __ _| (_)_______ _ __ ___
    ###  | || '_ \| | __| |/ _` | | |_  / _ \ '__/ __|
    ###  | || | | | | |_| | (_| | | |/ /  __/ |  \__ \
    ### |___|_| |_|_|\__|_|\__,_|_|_/___\___|_|  |___/

    # Definition of signals, which are used for UI updates from threads other than the Main thread
    LockGUI = pyqtSignal(bool)
    SaveStep = pyqtSignal(str)
    SaveData = pyqtSignal()
    Timer_0 = pyqtSignal()
    Timer_1 = pyqtSignal()
    Timer_2 = pyqtSignal()
    Timer_3 = pyqtSignal()
    Timer_4 = pyqtSignal()
    Timer_5 = pyqtSignal()
    Timer_6 = pyqtSignal()
    Timer_7 = pyqtSignal()
    Timer_8 = pyqtSignal()
    Timer_9 = pyqtSignal()
    Timer_10 = pyqtSignal()
    Timer_11 = pyqtSignal()
    Timer_12 = pyqtSignal()
    Timer_13 = pyqtSignal()
    Timer_14 = pyqtSignal()
    Timer_15 = pyqtSignal()
    Timer_16 = pyqtSignal()
    Timer_17 = pyqtSignal()
    Timer_18 = pyqtSignal()
    Save_Straw_Tensioner_Data = pyqtSignal(int, float, float)

    """
    __init__(self, paths, parent=None)

        Function: __init__

        Description: Class initializer. Sets up the UI and initializes variables. Also, connects appropriate signals to slots.

        Parameter: parent - Specifies a parent widget, None by default

        Note: self is a required argument for all class methods, and will be omitted from all method comments
    """

    def __init__(self, paths, parent=None):
        super(panelGUI, self).__init__(parent)

        ## File paths
        self.paths = paths
        self.imagePath = Path(self.paths["imagePath"]).resolve()

        ## Setup UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowState(Qt.WindowMaximized)
        self.resizeGUI()
        self.application = QCoreApplication.instance()

        # COLOR OPTION
        self.changeColor(
            (122, 0, 25), (255, 204, 51)
        )  # 122/0/25 = UMN MAROON,255/204/51 == UMN GOLD
        self.ui.scrollArea.setStyleSheet("background-color: rgb(122, 0, 25);")
        self.ui.scrollAreaHV.setStyleSheet("background-color: rgb(122, 0, 25);")

        """
        # if it's outside of working hours use dark mode
        if datetime.now().hour > 19 or datetime.now().hour < 8:
            self.changeColor((26,26,26),(255,255,255)) # 26/26/26 = 10% brightness,255/255/255 = 100% brightness (white)
        """

        # Data Processor
        self.DP = None  # Defined in openGUi

        ## Default Indexes
        self.ui.proSelection.setCurrentIndex(1)
        self.ui.tabWidget.setCurrentIndex(0)
        self.ui.suppliesList.setCurrentIndex(0)

        # Tension pop-up windows
        self._init_deviceWindows()

        # Worker Portal
        self._init_worker_portal()

        # Panel Input
        self._init_panel_input()

        # Setup each pro
        self._init_pro1_setup()
        self._init_pro2_setup()
        self._init_pro3_setup()
        self._init_pro4_setup()  # process 4: pin protector
        self._init_pro5_setup()  # process 5: high voltage tests
        self._init_pro6_setup()
        self._init_pro7_setup()
        self._init_failure_setup()

        # Grouping common elements by pro to make accessing more general
        self._init_widget_lists()

        self._init_connect()

        self._init_validators()

        # Data lists
        self._init_data_lists()

        # Finish Button
        self._init_finish_button()

        # Variable to measure time since last automatic write
        self.writeInterval = 600

        # Supplies list class instance
        self.suppliesList = SuppliesList(
            Tools=self.ui.Tools,
            Parts=self.ui.Parts,
            Supplies=self.ui.Supplies,
            MoldRelease=self.ui.MoldRelease,
        )
        self.suppliesList.setDiagramPopup(self.diagram_popup)

        # All timers
        self._init_timers()

        # Steps List
        self.stepsList = None

        # Initialize elapsed time to 0
        self.elapsedTime = 0

        # Removes Unwanted Highlighting
        self._init_highlighting()

        # Start GUI default locked
        self.pro = 0
        self.LockGUI.emit(DEBUG)

    def _init_data_lists(self):

        ## pro DATA
        # Initialize data lists
        self.data = []

        # Specify number of data values collected for each pro
        data_count = {1: 23, 2: 9, 3: 3, 4: 13, 5: 1, 6: 14, 7: 5}

        # Make a list of Nones for each pro (a list of lists, one list for each pro)
        for pro in data_count:
            self.data.append([None for _ in range(data_count[pro])])


    def _init_deviceWindows(self):
        self.strawTensionWindow = None
        self.wireTensionWindow = None
        self.tensionBoxWindow = None
        self.panelHeaterWindow = None

    def _init_worker_portal(self):
        self.Current_workers = [
            self.ui.Current_worker1,
            self.ui.Current_worker2,
            self.ui.Current_worker3,
            self.ui.Current_worker4,
        ]
        self.portals = [
            self.ui.portal1,
            self.ui.portal2,
            self.ui.portal3,
            self.ui.portal4,
        ]
        self.ui.PortalButtons.buttonClicked.connect(self.Change_worker_ID)

    def _init_pro1_setup(self):
        ## Connect
        self.ui.panelInput1.installEventFilter(self)
        self.ui.epoxy_mixed1.clicked.connect(self.pro1part2)
        self.ui.epoxy_applied1.clicked.connect(self.pro1CheckEpoxySteps)
        self.ui.pro1PanelHeater.clicked.connect(self.panelHeaterPopup)
        self.ui.validateStraws.clicked.connect(self.checkLPALs)
        self.ui.picone1.clicked.connect(lambda: self.diagram_popup("PAAS_A_C.png"))
        self.ui.picone2.clicked.connect(lambda: self.diagram_popup("d2_mix_epoxy.png"))
        self.ui.picone3.clicked.connect(lambda: self.diagram_popup("d1_BIRgroove.png"))
        self.ui.picone4.clicked.connect(
            lambda: self.diagram_popup("d1_BIR hole positions.png")
        )
        self.ui.picone5.clicked.connect(
            lambda: self.diagram_popup("d1_ALF Placement.gif")
        )
        self.ui.barcode.clicked.connect(
            lambda: self.diagram_popup("barcode_placement.png")
        )
        self.ui.paas_attach.clicked.connect(
            lambda: self.diagram_popup("d2_paas_attach.png")
        )
        self.ui.paas_attach_2.clicked.connect(
            lambda: self.diagram_popup("d2_paas_attach.png")
        )
        self.ui.paas_attach_3.clicked.connect(
            lambda: self.diagram_popup("d2_paas_attach.png")
        )

    def _init_pro2_setup(self):
        ## Connect
        self.ui.panelInput2.installEventFilter(self)

        self.ui.timer_instructions.clicked.connect(
            lambda: self.diagram_popup("d2_timer.png")
        )
        self.ui.picone2_2.clicked.connect(
            lambda: self.diagram_popup("d2_mix_epoxy.png")
        )
        self.ui.epoxy_mixed.clicked.connect(self.pro2part2)
        self.ui.heat_start.clicked.connect(self.pro2Heating)
        self.ui.epoxy_inject2.clicked.connect(self.pro2part2_3)
        self.ui.epoxy_mixed_2.clicked.connect(self.pro2part2_2)
        self.ui.epoxy_inject1.clicked.connect(self.pro2EpoxyInjected)
        self.ui.heat_finished.clicked.connect(self.pro2CheckTemp)

        ## Timers
        self.pro2TimerNum1 = [self.ui.hour_disp, self.ui.min_disp, self.ui.sec_disp]
        self.pro2TimerNum2 = [
            self.ui.hour_disp_2,
            self.ui.min_disp_2,
            self.ui.sec_disp_2,
        ]
        self.pro2TimerNum3 = [
            self.ui.hour_disp_3,
            self.ui.min_disp_3,
            self.ui.sec_disp_3,
        ]
        self.pro2Timers = [self.pro2TimerNum1, self.pro2TimerNum2, self.pro2TimerNum3]

        # Disable Widgets
        disabled_widgets = [
            self.ui.epoxy_batch,
            self.ui.epoxy_batch_2,
            self.ui.temp4,
            self.ui.temp4_2,
            self.ui.launch_straw_tensioner,
            self.ui.epoxy_inject1,
            self.ui.epoxy_inject2,
            self.ui.epoxy_mixed,
            self.ui.epoxy_mixed_2,
            self.ui.heat_finished,
            self.ui.paasBInput,
        ]
        self.setWidgetsDisabled(disabled_widgets)

        ## Launch vernier straw tensioner connected to self.DP
        self.ui.launch_straw_tensioner.clicked.connect(self.strawTensionPopup)
        self.ui.pro2PanelHeater.clicked.connect(self.panelHeaterPopup)
        self.ui.launch_wire_tensioner.clicked.connect(self.wireTensionPopup)
        self.ui.launch_tension_box.clicked.connect(self.tensionboxPopup)

    def _init_pro3_setup(self):
        ## Connect
        self.ui.panelInput3.installEventFilter(self)

        ## Disable Widgets
        self.ui.wireInput.setDisabled(False)

        ## Setup pro 3 drop down menus
        rcItems = [
            "Select",
            "Pass: No Continuity",
            "Fail: Right Continuity",
            "Fail: Left Continuity",
            "Fail: Both Continuity",
        ]
        lcItems = ["Select", "Top 1/3", "Middle 1/3", "Lower 1/3"]

        """
        listAssign(list, index, value)

            Description: Simple assignment function that assigns an index of a list a specified value. Used in lambdas
            where direct assignment is not allowed.

            Parameter: l - A list to be modified
            Parameter: index - int giving the list index to modify
            Parameter: value - Value that is assigned to list index
        """

        for i in range(96):
            label = QLabel(self.ui.scrollAreaWidgetContents)
            label.setText(f"{i}:")
            label.setObjectName(f"position_{i}")
            label.setFixedWidth(16)

            menu1 = QComboBox(self.ui.scrollAreaWidgetContents)
            menu1.addItems(rcItems)
            menu1.setObjectName(f"continuity_{str(i).zfill(2)}")
            menu1.setFixedWidth(185)
            menu1.currentIndexChanged.connect(
                lambda changed, index=i: checkSaveContinuity(index)
            )
            sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(menu1.sizePolicy().hasHeightForWidth())
            menu1.setSizePolicy(sizePolicy)

            menu2 = QComboBox(self.ui.scrollAreaWidgetContents)
            menu2.addItems(lcItems)
            menu2.setObjectName(f"wire_position_{str(i).zfill(2)}")
            menu2.setFixedWidth(184)
            menu2.currentIndexChanged.connect(
                lambda changed, index=i: checkSaveContinuity(index)
            )

            sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(menu2.sizePolicy().hasHeightForWidth())
            menu2.setSizePolicy(sizePolicy)

            self.ui.gridLayout.setHorizontalSpacing(2)
            self.ui.gridLayout.addWidget(label, i, 0)
            self.ui.gridLayout.addWidget(menu1, i, 1)
            self.ui.gridLayout.addWidget(menu2, i, 2)

        # Assemble widget lists
        findWidgets = lambda name: [
            self.ui.scrollAreaWidgetContents.findChild(
                QComboBox, f"{name}_{str(i).zfill(2)}"
            )
            for i in range(96)
        ]
        self.cont_pos = findWidgets("position")  # label
        self.continuity = findWidgets("continuity")  # continuity
        self.wire_pos = findWidgets("wire_position")  # wire position

        # Connect drop downs to save continuity when changed:
        # Define the method
        def checkSaveContinuity(index):
            if (
                self.continuity[index].currentIndex() != 0
                and self.wire_pos[index].currentIndex() != 0
            ):
                self.saveContinuityMeasurement(
                    position=index,
                    continuity_str=self.continuity[index].currentText(),
                    wire_pos_str=self.wire_pos[index].currentText(),
                )

        # Connect all widgets to this method using the proper index
        for i, widgets in enumerate(zip(self.continuity, self.wire_pos)):
            for widg in widgets:
                widg.currentIndexChanged.connect(
                    lambda changed, index=i: checkSaveContinuity(index)
                )

        # Disable all
        self.setWidgetsDisabled(self.continuity + self.wire_pos)
        self.ui.launch_wire_tensioner.setDisabled(True)

        [
            combo.installEventFilter(self) for combo in self.continuity + self.wire_pos
        ]  ## prevent value change from scroll

    def _init_pro4_setup(self):
        self.ui.panelInput4.installEventFilter(self)

        self.ui.epoxyMixedLP.clicked.connect(self.mixEpoxyLPP)
        self.ui.epoxyInjectedLP.clicked.connect(self.applyEpoxyLPP)
        self.ui.epoxyFinishedLP.clicked.connect(self.cureEpoxyLPP)

        self.ui.epoxyMixedRP.clicked.connect(self.mixEpoxyRPP)
        self.ui.epoxyInjectedRP.clicked.connect(self.applyEpoxyRPP)
        self.ui.epoxyFinishedRP.clicked.connect(self.cureEpoxyRPP)

        self.ui.epoxyMixedLOP.clicked.connect(self.mixEpoxyLOP)
        self.ui.epoxyAppliedLOP.clicked.connect(self.applyEpoxyLOP)
        self.ui.epoxyCuredLOP.clicked.connect(self.cureEpoxyLOP)

        self.ui.epoxyMixedROP.clicked.connect(self.mixEpoxyROP)
        self.ui.epoxyAppliedROP.clicked.connect(self.applyEpoxyROP)
        self.ui.epoxyCuredROP.clicked.connect(self.cureEpoxyROP)

        self.pro4Timer1 = [
            self.ui.hour_disp_5,
            self.ui.min_disp_5,
            self.ui.sec_disp_5,
        ]  # LP
        self.pro4Timer2 = [
            self.ui.hour_disp_7,
            self.ui.min_disp_7,
            self.ui.sec_disp_7,
        ]  # RP
        self.pro4Timer3 = [
            self.ui.hour_disp_11,
            self.ui.min_disp_11,
            self.ui.sec_disp_11,
        ]  # LOP
        self.pro4Timer4 = [
            self.ui.hour_disp_13,
            self.ui.min_disp_13,
            self.ui.sec_disp_13,
        ]  # ROP
        self.pro4Timers = [
            self.pro4Timer1,
            self.pro4Timer2,
            self.pro4Timer3,
            self.pro4Timer4,
        ]

        disabled_widgets = [
            self.ui.epoxyMixedLP,
            self.ui.epoxyMixedLOP,
            self.ui.epoxyMixedRP,
            self.ui.epoxyMixedROP,
            self.ui.epoxyInjectedLP,
            self.ui.epoxyInjectedRP,
            self.ui.epoxyFinishedLP,
            self.ui.epoxyFinishedRP,
            self.ui.epoxyAppliedLOP,
            self.ui.epoxyAppliedROP,
        ]
        self.setWidgetsDisabled(disabled_widgets)

        # TODO Add any image buttons for pro 4 here

    def _init_pro5_setup(self):
        self.ui.panelInput5.installEventFilter(self)

        """
        This method is confusing, but here's how it works:
        The .ui file contains a scroll area (scrollAreaHV) and that has a child
        widget (scrollContents).  With just those, there's nothing in the scroll
        area.  This method adds the stuff (labels, boxes, etc) to the scroll area.
        self.ui.hvGrid = QGridLayout() makes a qt layout that all of the stuff
        will be put into.  A loop creates all of the stuff, row by row, adding each
        widget as it's created.
        self.ui.scrollContents.setLayout(self.ui.hvGrid) sets the newly created
        hvGrid as the layout for the scrollContents.
        """

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

    def _init_pro6_setup(self):
        self.ui.panelInput6.installEventFilter(self)

        ## Connect Triggers
        # Progression between parts
        self.ui.epoxy_mixed41.clicked.connect(self.pro6part2)
        self.ui.epoxy_mixed42.clicked.connect(self.pro6part3)
        self.ui.heat_start4.clicked.connect(self.pro6part4)
        self.ui.epoxy_applied41.clicked.connect(self.pro6part2_2)
        self.ui.epoxy_applied42.clicked.connect(self.pro6part3_2)
        self.ui.heat_finished4.clicked.connect(self.pro6CheckTemp)
        self.ui.pro6PanelHeater.clicked.connect(self.panelHeaterPopup)

        # Images
        self.ui.picfour1.clicked.connect(lambda: self.diagram_popup("PAAS_A_C.png"))
        self.ui.picfour2.clicked.connect(lambda: self.diagram_popup("d2_mix_epoxy.png"))
        self.ui.picfour3.clicked.connect(lambda: self.diagram_popup("d2_heater.png"))
        self.ui.picfive1.clicked.connect(lambda: self.diagram_popup("d2_mix_epoxy.png"))

        ## Disable Widgets
        disabled_widgets = [
            self.ui.epoxy_batch41,
            self.ui.epoxy_batch42,
            self.ui.epoxy_batch42_2,
            self.ui.temp4_4,
            self.ui.temp4_5,
            self.ui.bpmirgapL,
            self.ui.bpmirgapR,
            self.ui.heat_start,
        ]
        self.setWidgetsDisabled(disabled_widgets)

    def _init_pro7_setup(self):
        self.ui.panelInput7.installEventFilter(self)
        self.ui.epoxy_mixed5_2.clicked.connect(self.pro7part2)
        self.ui.epoxy_applied5_2.clicked.connect(self.pro7part2_2)
        self.ui.epoxy_mixed5_3.clicked.connect(self.pro7part3)
        self.ui.epoxy_applied5_3.clicked.connect(self.pro7part3_2)

    def _init_timers(self):
        self.timers = [
            # Main timer
            QLCDTimer(
                self.ui.hour_left,
                self.ui.min_left,
                self.ui.sec_left,
                lambda: self.Timer_0.emit(),
                max_time=28800,
            ),  # 0 - Main Timer: Turns red after 8 hours
            QLCDTimer(
                self.ui.hour_disp_6,
                self.ui.min_disp_6,
                self.ui.sec_disp_6,
                lambda: self.Timer_1.emit(),
            ),  # 1
            QLCDTimer(
                self.ui.hour_disp,
                self.ui.min_disp,
                self.ui.sec_disp,
                lambda: self.Timer_2.emit(),
            ),  # 2
            QLCDTimer(
                self.ui.hour_disp_2,
                self.ui.min_disp_2,
                self.ui.sec_disp_2,
                lambda: self.Timer_3.emit(),
            ),  # 3
            QLCDTimer(
                self.ui.hour_disp_3,
                self.ui.min_disp_3,
                self.ui.sec_disp_3,
                lambda: self.Timer_4.emit(),
            ),  # 4
            QLCDTimer(
                self.ui.hour_disp_13,
                self.ui.min_disp_13,
                self.ui.sec_disp_13,
                lambda: self.Timer_5.emit(),
            ),  # 5 -> vestigial, use one that isn't associated with pro 3 to keep stuff moving
            QLCDTimer(
                self.ui.hour_disp_8,
                self.ui.min_disp_8,
                self.ui.sec_disp_8,
                lambda: self.Timer_6.emit(),
            ),  # 6
            QLCDTimer(
                self.ui.hour_disp_9,
                self.ui.min_disp_9,
                self.ui.sec_disp_9,
                lambda: self.Timer_7.emit(),
            ),  # 7
            QLCDTimer(
                self.ui.hour_disp_16,
                self.ui.min_disp_16,
                self.ui.sec_disp_16,
                lambda: self.Timer_8.emit(),
            ),  # 8
            QLCDTimer(
                self.ui.hour_disp_10,
                self.ui.min_disp_10,
                self.ui.sec_disp_10,
                lambda: self.Timer_9.emit(),
            ),  # 9
            QLCDTimer(
                self.ui.hour_disp_12,
                self.ui.min_disp_12,
                self.ui.sec_disp_12,
                lambda: self.Timer_10.emit(),
            ),
            QLCDTimer(
                self.ui.hour_disp_5,
                self.ui.min_disp_5,
                self.ui.sec_disp_5,
                lambda: self.Timer_11.emit(),
            ),
            QLCDTimer(
                self.ui.hour_disp_5,
                self.ui.min_disp_5,
                self.ui.sec_disp_5,
                lambda: self.Timer_12.emit(),
            ),
            QLCDTimer(
                self.ui.hour_disp_7,
                self.ui.min_disp_7,
                self.ui.sec_disp_7,
                lambda: self.Timer_13.emit(),
            ),
            QLCDTimer(
                self.ui.hour_disp_7,
                self.ui.min_disp_7,
                self.ui.sec_disp_7,
                lambda: self.Timer_14.emit(),
            ),
            QLCDTimer(
                self.ui.hour_disp_11,
                self.ui.min_disp_11,
                self.ui.sec_disp_11,
                lambda: self.Timer_15.emit(),
            ),
            QLCDTimer(
                self.ui.hour_disp_13,
                self.ui.min_disp_13,
                self.ui.sec_disp_13,
                lambda: self.Timer_16.emit(),
            ),
            QLCDTimer(
                self.ui.hour_disp_11,
                self.ui.min_disp_11,
                self.ui.sec_disp_11,
                lambda: self.Timer_17.emit(),
            ),
            QLCDTimer(
                self.ui.hour_disp_13,
                self.ui.min_disp_13,
                self.ui.sec_disp_13,
                lambda: self.Timer_18.emit(),
            ),
        ]

        # Connect all timer signals to the corresponding timer's display method
        self.Timer_0.connect(self.timers[0].display)
        self.Timer_1.connect(self.timers[1].display)
        self.Timer_2.connect(self.timers[2].display)
        self.Timer_3.connect(self.timers[3].display)
        self.Timer_4.connect(self.timers[4].display)
        self.Timer_5.connect(self.timers[5].display)
        self.Timer_6.connect(self.timers[6].display)
        self.Timer_7.connect(self.timers[7].display)
        self.Timer_8.connect(self.timers[8].display)
        self.Timer_9.connect(self.timers[9].display)
        self.Timer_10.connect(self.timers[10].display)
        self.Timer_11.connect(self.timers[11].display)
        self.Timer_12.connect(self.timers[12].display)
        self.Timer_13.connect(self.timers[13].display)
        self.Timer_14.connect(self.timers[14].display)
        self.Timer_15.connect(self.timers[15].display)
        self.Timer_16.connect(self.timers[16].display)
        self.Timer_17.connect(self.timers[17].display)
        self.Timer_18.connect(self.timers[18].display)

        self.startTimer = lambda index: self.timers[index].start()
        self.stopTimer = lambda index: self.timers[index].stop()
        self.stopAllTimers = lambda: [t.stop() for t in self.timers]
        self.resetAllTimers = lambda: [t.reset() for t in self.timers]
        self.mainTimer = self.timers[0]
        self.running = (
            lambda: self.mainTimer.isRunning()
        )  # Returns True if main timer is running

    def _init_failure_setup(self):
        self.failMode = [
            self.ui.anchorFail,
            self.ui.anchorFail,
            self.ui.strawFail,
            self.ui.pinFail,
        ]
        self.ui.failureComments.setDisabled(True)
        self.ui.failureComments.textChanged.connect(
            lambda: self.ui.failureComments.setStyleSheet("")
        )
        # Failures
        self.ui.failSelect.currentIndexChanged.connect(
            lambda: self.setFailIndex(f"{self.ui.failSelect.currentText().lower()}Fail")
        )
        self.ui.failSelect.currentIndexChanged.connect(self.enableAdditionalFailure)
        self.ui.submitFailure.clicked.connect(self.failure)

    def _init_connect(self):
        set_focus = (
            lambda index: self.panelInput[self.pro_index].setFocus()
            if (index == 2 and self.getCurrentPanel() == "")
            else None
        )
        self.ui.tabWidget.currentChanged.connect(set_focus)
        self.SaveStep.connect(self.saveStep)
        self.LockGUI.connect(self.lockGUI)
        self.SaveData.connect(self.saveData)
        self.Save_Straw_Tensioner_Data.connect(
            lambda position, tension, uncertainty: self.DP.saveStrawTensionMeasurement(
                position, tension, uncertainty
            )
        )

        self.ui.proSelectButtons.buttonClicked.connect(self.openGUI)

        # Save buttons
        for btn in self.ui.saveButtons.buttons():
            btn.setDisabled(True)
            btn.clicked.connect(lambda: [self.saveData(), self.saveComments()])
            # When the save button is pressed, self.saveData and self.saveComments will be called.

        # pro select back button
        self.ui.proReturnButton.clicked.connect(self.backToproSelect)

        # Supplies list change page buttons
        supply_tabs = 2
        self.ui.nextButton.clicked.connect(
            lambda: self.ui.suppliesList.setCurrentIndex(
                (self.ui.suppliesList.currentIndex() + 1) % supply_tabs
            )
        )
        self.ui.nextButton_2.clicked.connect(
            lambda: self.ui.suppliesList.setCurrentIndex(
                (self.ui.suppliesList.currentIndex() + 1) % supply_tabs
            )
        )
        self.ui.previousButton.clicked.connect(
            lambda: self.ui.suppliesList.setCurrentIndex(
                (self.ui.suppliesList.currentIndex() - 1) % supply_tabs
            )
        )
        self.ui.previousButton_2.clicked.connect(
            lambda: self.ui.suppliesList.setCurrentIndex(
                (self.ui.suppliesList.currentIndex() - 1) % supply_tabs
            )
        )

        for input in self.panelInput:
            input.editingFinished.connect(self.loadpro)
            input.editingFinished.connect(lambda: input.setEnabled(False))
            input.returnPressed.connect(lambda: None)

    def _init_validators(self):
        # Lambda expressions to create and set expression validators
        validator = lambda string: QRegularExpressionValidator(
            QRegularExpression(string)
        )

        set_validator = lambda obj, string: obj.setValidator(validator(string))

        # Create then set text validators to constrain allowed text input
        # Strings passed to validator() are regular expressions
        #   text inside the parentheses is treated as normal required text
        #   the \d{X} requires X digits, so \d{3} requires any 3 numbers to be vaild

        valid_panel = validator("(MN)\d{3}")
        for input in self.panelInput:
            input.setValidator(valid_panel)

        valid_epoxy = validator("(EP)\d{4}")
        self.ui.epoxy_batch.setValidator(valid_epoxy)
        self.ui.epoxy_batch1.setValidator(valid_epoxy)
        self.ui.epoxy_batch41.setValidator(valid_epoxy)
        self.ui.epoxy_batch42.setValidator(valid_epoxy)
        self.ui.epoxy_batch42_2.setValidator(valid_epoxy)
        self.ui.epoxy_batch5_2.setValidator(valid_epoxy)
        self.ui.epoxy_batch5_3.setValidator(valid_epoxy)
        self.ui.epoxy_batch_2.setValidator(valid_epoxy)
        self.ui.epoxy_batch_3.setValidator(valid_epoxy)
        self.ui.epoxy_batch_4.setValidator(valid_epoxy)
        self.ui.epoxy_batch_5.setValidator(valid_epoxy)
        self.ui.epoxy_batch_6.setValidator(valid_epoxy)

        set_validator(self.ui.mirInput, "(MIR)\d{3}")
        set_validator(self.ui.birInput, "(BIR)\d{3}")

        valid_pir = validator("(PIR)\d{4}")
        self.ui.pirInputLA.setValidator(valid_pir)
        self.ui.pirInputLB.setValidator(valid_pir)
        self.ui.pirInputLC.setValidator(valid_pir)
        self.ui.pirInputRA.setValidator(valid_pir)
        self.ui.pirInputRB.setValidator(valid_pir)
        self.ui.pirInputRC.setValidator(valid_pir)

        valid_alf = validator("(ALF)\d{3}")
        self.ui.alfInput.setValidator(valid_alf)
        self.ui.alfInput_2.setValidator(valid_alf)

        valid_paasA = validator("(PAAS A-)\d{2}")
        self.ui.paasAInput.setValidator(valid_paasA)
        valid_paasB = validator("(PAAS B-)\d{2}")
        self.ui.paasBInput.setValidator(valid_paasB)
        valid_paasC = validator("(PAAS C-)\d{2}")
        self.ui.paasCInput.setValidator(valid_paasC)

        set_validator(self.ui.baseInput1, "(BP)\d{3}")

        valid_lpal = validator("(LPAL)\d{4}")
        self.ui.pallet1code.setValidator(valid_lpal)
        self.ui.pallet2code.setValidator(valid_lpal)

        set_validator(self.ui.frameInput, "(F)\d{3}")

        valid_mr = validator("(MR)\d{3}")
        self.ui.mrInput1.setValidator(valid_mr)
        self.ui.mrInput2.setValidator(valid_mr)

        valid_temp = QDoubleValidator(bottom=50.0, top=99.9, decimals=1)
        self.ui.temp4.setValidator(valid_temp)
        self.ui.temp4_2.setValidator(valid_temp)
        self.ui.temp4_4.setValidator(valid_temp)
        self.ui.temp4_5.setValidator(valid_temp)

        set_validator(self.ui.wireInput, "(WIRE\.)\d{6}")

    def _init_widget_lists(self):
        # Start buttons
        self.startButtons = [
            self.ui.startbutton1,
            self.ui.startbutton2,
            self.ui.startbutton3,
            self.ui.startButton4,
            self.ui.startButton5,
            self.ui.startButton6,
            self.ui.startButton7,
        ]

        # without the loop it would look like self.ui.startButton1.clicked.connect(self.pro1part1)
        for btn in self.startButtons:
            btn.clicked.connect(
                lambda: {
                    1: self.pro1part1,
                    2: self.pro2part1,
                    3: self.pro3part1,
                    4: self.pro4part0,
                    5: self.pro5part0,
                    6: self.pro6part1,
                    7: self.pro7part1,
                }[self.pro]()
            )

        """
        The widgets in the following lists have a specific order; ValidateInput() takes indicies
        as an argument and finds widgets with those indicies in one of these lists.
        """

        self.widgets = [
            # pro 1 Widgets
            [
                self.ui.panelInput1,
                self.ui.baseInput1,
                self.ui.mirInput,
                self.ui.birInput,
                self.ui.pirInputLA,
                self.ui.pirInputLB,
                self.ui.pirInputLC,
                self.ui.pirInputRA,
                self.ui.pirInputRB,
                self.ui.pirInputRC,
                self.ui.alfInput,
                self.ui.alfInput_2,
                self.ui.leftgap,
                self.ui.rightgap,
                self.ui.mingap,
                self.ui.maxgap,
                self.ui.epoxy_batch1,
                self.ui.paasAInput,
                self.ui.paasCInput,
                self.ui.pallet1code,
                self.ui.pallet2code
            ],
            # pro 2 Widgets
            [
                self.ui.panelInput2,
                self.ui.epoxy_batch,
                self.ui.epoxy_inject1,
                self.ui.epoxy_batch_2,
                self.ui.epoxy_inject2,
                self.ui.temp4,
                self.ui.temp4_2,
                self.ui.heat_finished,
                self.ui.paasBInput,
            ],
            # pro 3 Widgets
            [self.ui.panelInput3, self.ui.wireInput],
            # Pro 4 Widgets --> can't be entered randomly
            [
                self.ui.panelInput4,
                self.ui.epoxy_batch_3,
                self.ui.epoxy_batch_4,
                self.ui.epoxy_batch_5,
                self.ui.epoxy_batch_6,
                self.ui.epoxyMixedLP,
                self.ui.epoxyInjectedLP,
                self.ui.epoxyFinishedLP,
                self.ui.epoxyMixedRP,
                self.ui.epoxyInjectedRP,
                self.ui.epoxyFinishedRP,
                self.ui.epoxyMixedLOP,
                self.ui.epoxyAppliedLOP,
                self.ui.epoxyAppliedROP,
                self.ui.epoxyCuredLOP,
                self.ui.epoxyCuredROP,
            ],
            # pro 5 Widgets
            [self.ui.panelInput5],
            # pro 6 Widgets
            [
                self.ui.panelInput6,
                self.ui.frameInput,
                self.ui.mrInput1,
                self.ui.mrInput2,
                self.ui.bpmirgapL,
                self.ui.bpmirgapR,
                self.ui.epoxy_batch41,
                self.ui.epoxy_applied41,
                self.ui.epoxy_batch42,
                self.ui.epoxy_batch42_2,
                self.ui.epoxy_applied42,
                self.ui.temp4_4,
                self.ui.temp4_5,
                self.ui.heat_finished4,
            ],
            # pro 7 Widgets
            [
                self.ui.panelInput7,
                self.ui.epoxy_batch5_2,
                self.ui.epoxy_applied5_2,
                self.ui.epoxy_batch5_3,
                self.ui.epoxy_applied5_3,
            ],
        ]

    def _init_panel_input(self):
        self.panelInput = [
            self.ui.panelInput1,
            self.ui.panelInput2,
            self.ui.panelInput3,
            self.ui.panelInput4,
            self.ui.panelInput5,
            self.ui.panelInput6,
            self.ui.panelInput7,
        ]

        # Lambda expression that gets text from the panel input line.
        self.getCurrentPanel = lambda: self.panelInput[self.pro_index].text()

    def _init_finish_button(self):
        self.finishButton = self.ui.FinishButton
        self.finishButton.setDisabled(True)
        self.finishButton.clicked.connect(lambda: self.suppliesList.clearMoldRelease())
        self.finishButton.clicked.connect(
            lambda: self.timers[5].stop()
            if self.stepsList.allStepsChecked() and self.pro == 3
            else None
        )  # Stop the pro 3 timer when finish button is pushed     TODO: for pro 5?
        self.finishButton.clicked.connect(
            lambda clicked: self.stopRunning(self.finishButton.text() == "Pause")
        )

    def _init_highlighting(self):
        # Removes highlighting when line edit edited
        for edit in self.ui.centralwidget.findChildren(QLineEdit):
            edit.textChanged.connect(lambda text, widget=edit: widget.setStyleSheet(""))

        # Removes highlighting from combobox menus when selected
        for box in self.ui.centralwidget.findChildren(QComboBox):
            box.activated.connect(lambda index, widget=box: widget.setStyleSheet(""))

        # Removes highlighting when combo box selected
        self.ui.failSelect.highlighted.connect(
            lambda index: self.ui.failSelect.setStyleSheet("")
        )
        self.ui.anchorFail.highlighted.connect(
            lambda: self.ui.anchorFail.setStyleSheet("")
        )
        self.ui.pinFail.highlighted.connect(lambda: self.ui.pinFail.setStyleSheet(""))
        self.ui.strawFail.highlighted.connect(
            lambda: self.ui.strawFail.setStyleSheet("")
        )
        self.ui.positionSelect.highlighted.connect(
            lambda: self.ui.positionSelect.setStyleSheet("")
        )

    ###  _   _       _ _     _       _
    ### | | | |     | (_)   | |     | |
    ### | | | | __ _| |_  __| | __ _| |_ ___  _ __ ___
    ### | | | |/ _` | | |/ _` |/ _` | __/ _ \| '__/ __|
    ### \ \_/ / (_| | | | (_| | (_| | || (_) | |  \__ \
    ###  \___/ \__,_|_|_|\__,_|\__,_|\__\___/|_|  |___/
    ###

    def checkSupplies(self):
        # Check that all supplies have been checked off
        if not self.suppliesList.allPartsChecked():
            self.partsError()
            return False
        # Check that all parts have been mold released
        checked = self.suppliesList.moldReleaseChecked()
        if not checked:
            self.moldReleaseError()
            return False
        # If both pass, return True
        return True

    """
    validateInput(self, widgets = None, indices = None)

        Description: Handles validating the input of widgets for all pros. Can handle two types of widgets,
        QLineEdit and QComboBox. It is assumed that the QLineEdit has a QRegularExpressionValidator on it.
        A valid input is a QLineEdit that has text that matches its validator, or a QComboBox whose index
        is not 0. If a widget has invalid input, it is highlighted. If the widget has valid input, highlighting
        is removed.

        Parameter: widgets - A list of QWidgets to be validated. If none supplied, defaults to the list of
            widgets for the current pro.
        Parameter: indices - A list of ints that give the indices of the widget list to validate. If no list
            is supplied, validates the whole list.

        Returns: Boolean value. True if all checked widgets have valid input, False otherwise.
    """

    def validateInput(self, widgets=None, indices=None):
        if widgets == None and indices == None:  # if nothing given, return
            return

        if widgets == None:  # if no widgets, find some
            widgets = self.widgets[self.pro_index]

        if not indices == None:
            results = [None] * len(indices)
        else:
            results = [None] * len(widgets)
            indices = range(len(widgets))

        passFailDict = {
            "QLineEdit": lambda widget: widget.validator().validate(widget.text(), 0)[0]
            == QValidator.Acceptable,
            "QComboBox": lambda widget: not (widget.currentIndex() == 0),
            "list": lambda l: self.validateInput(widgets=l),
        }

        errorStyleSheet = (
            "QLineEdit { background-color:rgb(149, 186, 255); }"
            "QComboBox { border: 1px solid rgb(149, 186, 255); }"
        )

        for listIndex, index in enumerate(indices):
            widget = widgets[index]
            typename = widget.__class__.__name__

            try:
                results[listIndex] = passFailDict[typename](widget)

                if not results[listIndex]:
                    widget.setStyleSheet(errorStyleSheet)
                else:
                    widget.setStyleSheet("")

            except KeyError:
                pass
        return all(results)

    """
    checkDevice(self)

        Description: Returns an error unless exactly one arduino device is
        plugged in.
    """

    def checkDevice(self):
        error = False
        arduino_ports = [
            p.device
            for p in serial.tools.list_ports.comports()
            if "Arduino" in p.description
        ]
        if len(arduino_ports) == 0:  ## fix for pro2/pro3 General Nanosystems Computers
            arduino_ports = [
                p.device
                for p in serial.tools.list_ports.comports()
                if "USB Serial" in p.description
            ]

        if len(arduino_ports) < 1:
            error = True
            self.generateBox(
                "critical",
                "Device not found",
                "Plug device into any USB port and try again.",
            )

        if len(arduino_ports) > 1:
            error = True
            self.generateBox(
                "critical",
                "More than one Arduino found",
                "Disconnect the ones not in use and try again.",
            )
        return error

    ###  _____                      _______ _                    _______                _______ _
    ### |  _  |                    / /  __ \ |                  / / ___ \              / /  ___| |
    ### | | | |_ __   ___ _ __    / /| /  \/ | ___  ___  ___   / /| |_/ /   _ _ __    / /\ `--.| |_ ___  _ __
    ### | | | | '_ \ / _ \ '_ \  / / | |   | |/ _ \/ __|/ _ \ / / |    / | | | '_ \  / /  `--. \ __/ _ \| '_ \
    ### \ \_/ / |_) |  __/ | | |/ /  | \__/\ | (_) \__ \  __// /  | |\ \ |_| | | | |/ /  /\__/ / || (_) | |_) |
    ###  \___/| .__/ \___|_| |_/_/    \____/_|\___/|___/\___/_/   \_| \_\__,_|_| |_/_/   \____/ \__\___/| .__/
    ###       | |                                                                                       | |
    ###       |_|                                                                                       |_|

    """
    openGUI(self, btn)

        Description: The function connected to the pro select buttons. Sets the current pro, and opens the appropriate GUI pro. This function
                    also calls the suppliesList class to generate the appropriate supplies list, sets the credential checker to the correct pro
                    and starts the secondary thread for credential checking and main timer updating.

        Parameter: btn - The QPushButton corresponding to the pro button clicked
    """

    def openGUI(self, btn):
        # Get pro Information
        self.pro = int(btn.objectName()[3:-6])
        print("pro selected: ", self.pro)
        self.pro_index = self.pro - 1
        self.ui.proSelection.setCurrentIndex(0)
        self.ui.GUIpro.setCurrentIndex(self.pro_index)
        self.panelInput[self.pro_index].setEnabled(True)

        # Data Processor
        self.DP = DataProcessor(
            gui=self,
            save2txt=SAVE_TO_TXT,
            save2SQL=SAVE_TO_SQL,
            lab_version=LAB_VERSION,
            sql_primary=bool(PRIMARY_DP == "SQL"),
        )

        # Supplies List
        self.suppliesList.setpro(self.pro)
        self.suppliesList.setSaveMoldReleaseMethod(self.DP.saveMoldRelease)
        self.suppliesList.setSaveTPSMethod(self.DP.saveTPS)
        self.suppliesList.loadSuppliesList(*self.DP.loadTPS())
        self.suppliesList.loadMoldReleaseList(self.DP.loadMoldRelease())

        # Steps List
        self.stepsList = StepList(
            self.ui.stepsBox,
            self.DP.loadSteps(),
            self.checkProgress,
            self.diagram_popup,
        )
        self.stepsList.setupList()

        # Update tab text
        if not DEBUG:
            pro = f"Panel pro {self.pro}"
            supply = f"pro {self.pro} Supplies List"
            self.ui.tabWidget.setTabText(1, supply + " *Locked*")
            self.ui.tabWidget.setTabEnabled(1, False)
            self.ui.tabWidget.setTabText(2, pro + " *Locked*")
            self.ui.tabWidget.setTabEnabled(2, False)

        # Start credential thread if not already started
        if not any([thread.name == "AutoSave" for thread in enumerateThreads()]):
            Thread(target=self.main, args=(), name="AutoSave", daemon=True).start()

    """
    startRunning(self)

        Description: This function is called when any of the start buttons are clicked. Sets the start time, writes the
                 initial line to the data file, and starts the main timer.
    """

    def startRunning(self):
        # Record start in data processor
        self.saveData()
        self.DP.saveStart()

        # Start main timer
        self.mainTimer.start()

        ## Gui Operations
        # Disable pro return
        self.ui.proReturnButton.setDisabled(True)

        # Enable
        self.setWidgetsEnabled(
            [
                self.ui.saveButtons.buttons()[self.pro_index],  # Save Button
                self.stepsList.getCurrentStep().getCheckbox(),  # First step checkbox
                self.finishButton,  # Finish button
            ]
        )
        # Change finish button text
        self.finishButton.setText("Pause")

    """
    closeGUI(self)

        Description:    Function called when the 'Close GUI' button is pressed on the drop down box.
                        Gives the DP a chance to handle the close, then closes the GUI.
    """

    def closeGUI(self):
        if self.DP is not None:
            self.DP.handleClose()
        self.close()

    """
    stopRunning(self)

        Description:    This function is called when any of the finish buttons are clicked. 
                        Saves all data and disables the finish button. Also
                        handles the case where the pro is being paused.

        Parameter: pause - Boolean value that determines if pro is being paused or ended.
    """

    def stopRunning(self, pause=False):

        # Pause GUI
        if pause:
            self.dialogBox = DialogBox(self.DP.getSessionWorkers())
            self.dialogBox.connectClose(self.closeGUI)
            self.dialogBox.connectResume(self.resume)
            self.dialogBox.connectPause(self.pause)
            self.dialogBox.show()
        # Stop GUI
        else:

            # Timer Information
            self.stopAllTimers()

            # Supplies List
            # self.suppliesList.clearTPS()
            # "TPS" = Tools, Parts, Supplies
            # Resets the Tools, Parts, and Supplies list to the default state.

            # Data Processor
            self.DP.saveFinish()

            # Gui Operations
            self.ui.saveButtons.buttons()[self.pro_index].setDisabled(True)
            self.finishButton.setDisabled(True)
            self.ui.proReturnButton.setDisabled(False)
            self.finishButton.setDisabled(True)

            # Go back to the pro select page
            self.backToproSelect()

    def closeEvent(self, event):
        """
        closeEvent(self, event)

        Description: Handles the clicking of the red 'X' to close the GUI window. If the GUI is running, the GUI
                     cannot be closed this way. Otherwise, gives a prompt to confirm exit.

        Parameter: event - Event that specifies the clicking of the red 'X'.
        """
        if self.running():
            # QMessageBox.critical(self, 'Exit Warning', 'GUI cannot be exited while running.')
            self.generateBox(
                "critical", "Exit Warning", "GUI cannot be exited while running."
            )
            event.ignore()
        else:
            # reply = QMessageBox.warning(self, 'Exit Warning', 'Are you sure you want to exit?', QMessageBox.Yes, QMessageBox.No)
            reply = self.generateBox(
                "warning", "Exit Warning", "Are you sure you want to exit?", True
            )

            if reply == QMessageBox.Yes:
                self.closeGUI()

                event.accept()
                sys.exit(0)
            else:
                event.ignore()

    ###  __  __ _             ___   _                      _           _
    ### |  \/  (_)___  ___   / / | | |_ __  ___  ___  _ __| |_ ___  __| |
    ### | |\/| | / __|/ __| / /| | | | '_ \/ __|/ _ \| '__| __/ _ \/ _` |
    ### | |  | | \__ \ (__ / / | |_| | | | \__ \ (_) | |  | ||  __/ (_| |
    ### |_|  |_|_|___/\___/_/   \___/|_| |_|___/\___/|_|   \__\___|\__,_|

    @classmethod
    def setWidgetsDisabled(cls, widgets):
        cls.setWidgetsEnabled(widgets, enabled=False)

    @staticmethod
    def setWidgetsEnabled(widgets, enabled=True):
        for w in widgets:
            w.setEnabled(enabled)

    # filter out certain events from reaching widgets it's installed on
    def eventFilter(self, obj, event):  # obj = QWidget, event = QEvent
        if isinstance(obj, QComboBox):  # if it's a combo box...
            if event.type() == QEvent.Wheel:  # if the mouse wheel is spinning...
                event.ignore()  # ignore it!
                return True  # return True (to indicate it has been filtered... ?)
        elif isinstance(obj, QLineEdit):  # if it's a line edit...
            if event.type() == QEvent.KeyPress:  # if a key was pressed...
                if event.key() in (
                    Qt.Key_Return,
                    Qt.Key_Enter,
                ):  # if that key was return/enter...
                    event.ignore()  # ignore it!
                    return True  # return True
        return False  # return false (to indicate no filtering has taken place... ?)

    """
    checkProgress(self, pro, x)

        Description: This function is called whenever a checkbox is checked. It disables the clicked checkbox, and enables
                    the next one (as all checkboxes start disabled). This is done in order of steps, to ensure steps are 
                    checked off in order. Also emits signal to save data when checkbox clicked, and enables the finish
                    button when all steps are checked.

        Parameter: pro - The panel pro that is currently being run
        Parameter: x - The index of the checkbox that emitted the signal to call this method
    """

    def checkProgress(self):
        """ Constrain steps to be checked off in order """
        step = self.stepsList.getCurrentStep()  # Latest unchecked step
        checkbox1 = step.getCheckbox()
        checkbox1.setDisabled(True)
        self.stepsList.getNextStep()

        if self.stepsList.getCurrentStep() is not None:
            checkbox2 = self.stepsList.getCurrentStep().getCheckbox()
            checkbox2.setDisabled(False)

        self.saveStep(step.name)  # changed

        if self.stepsList.allStepsChecked():
            # force user to validate straws before finishing

            if self.pro == 1 and not self.data[0][22]:
                return
            self.finishButton.setText("Finish")

    """
    backToproSelect(self)

        Description: The function connected to the pro return button. Resets all data and UI elements, then
                 returns to the pro selection screen.
    """

    def backToproSelect(self):
        # Call reset function for current pro
        [
            self.resetpro1,
            self.resetpro2,
            self.resetpro3,
            self.resetPro4,
            self.resetPro5,
            self.resetpro6,
            self.resetpro7,
        ][self.pro_index]()

        # Reset data and dataTime lists to lists of None
        self._init_data_lists()

        self.ui.previousComments.document().setPlainText("")

        for i in range(len(self.Current_workers)):
            if self.Current_workers[i].text() != "":
                self.Change_worker_ID(self.portals[i])

        # Reset timer information and time display
        self.resetAllTimers()

        # Reset the data processor
        self.DP.handleClose()
        self.DP = None

        # Reset steps list
        self.stepsList.deleteList()

        # Reset supplies list
        self.suppliesList.deleteLists()
        self.suppliesList = SuppliesList(
            self.ui.Tools, self.ui.Parts, self.ui.Supplies, self.ui.MoldRelease
        )
        self.suppliesList.setDiagramPopup(self.diagram_popup)
        self.ui.suppliesList.setCurrentIndex(0)

        # Reset tab indexes
        self.ui.proSelection.setCurrentIndex(1)
        self.ui.tabWidget.setCurrentIndex(0)

    """
    partsError(self)

        Description: The error function for if the start button for the pro has been clicked, but not all of the supplies in the
                 supplies list have been checked off. Generates an error message in a box, then sets the current view to the
                 supplies list.
    """

    def partsError(self):
        self.generateBox(
            "critical",
            "Parts List Not Checked",
            "All tools, parts, and supplies must be checked off before pro can begin.",
        )
        self.ui.tabWidget.setCurrentIndex(1)
        self.ui.suppliesList.setCurrentIndex(0)

    """
    moldReleaseError(self)

        Description: Error function for if mold released supplies for the pro have not been checked off. Generates an error box
                 listing the items to be mold released/checked off, and sets the current view to the mold release list.
    """

    def moldReleaseError(self):
        items = self.suppliesList.getUncheckedMoldReleaseItems()
        str_items = "\n".join(items)

        self.generateBox(
            "critical",
            "Mold Release List Not Checked",
            f"The following items need to be mold released prior to starting this pro:\n{str_items}",
        )
        self.ui.tabWidget.setCurrentIndex(1)
        self.ui.suppliesList.setCurrentIndex(1)

    """
    pause(self)

        Description: Handles pausing the GUI. Writes items to comment file and a step to the data file. Saves the values
                 of all running timers so they can be restored. Stops all timers, including the main timer. This function
                 is connected to the pause button in the popup dialog box for pausing.
    """

    def pause(self):
        ## Data Processor Operations
        # Before doing anything, make sure that the current state of the GUI is saved
        self.saveData()
        # Save pause with data processor
        self.DP.savePause()
        # Include a comment
        self.DP.saveComment(
            f"pro {self.pro} Paused by {self.dialogBox.pauseWorker}\nReason: {self.dialogBox.getComment()}",
            self.getCurrentPanel(),
            self.pro,
        )
        ## Stop all timers
        self.timersRunning = [t for t in self.timers if t.isRunning()]
        self.stopAllTimers()

    """
    resume(self)

        Description: Handles resuming the GUI. This function is connected to the resume button in the popup dialog box for
                 pausing. Writes a new step saying "pro _ Resumed", and restarts and stopped timers. This function is
                 only called if resumed from the dialog box. If the GUI is paused and then closed, the normal load
                 function will handle resuming the pro.
    """

    def resume(self):
        # Save resume with data processor
        self.DP.saveResume()

        # Restart paused timers
        for timer in self.timersRunning:
            timer.start()

        self.dialogBox.hide()

    """
    resizeGUI(self)

        Description: Finds the current screen size, and compares it to the optimal size. If it is smaller, automatically
        rescales the GUI to fit the screen. Also gives a warning about UI elements not displaying properly. Keeps the 
        original aspect ratio.
    """

    def resizeGUI(self):
        # Optimal values taken from the values given in QtCreator for panel.ui
        wOpt = 1550
        hOpt = 687

        aspectRatio = wOpt / hOpt
        resized = True

        w = tkinter.Tk().winfo_screenwidth()
        h = tkinter.Tk().winfo_screenheight()

        if w / wOpt < 1 and w / wOpt < h / hOpt:
            self.setFixedSize(w, w / aspectRatio)
        elif h / hOpt < 1:
            self.setFixedSize(h * aspectRatio, h)
        else:
            resized = False

        if resized:
            self.generateBox(
                "warning",
                "Screen Size Warning",
                f"The current screen size ({w} x {h}) is too small for the optimal GUI size ({wOpt} x {hOpt}). The GUI has been resized, but UI elements may not display correctly.",
            )

    """
    changeColor(self, background_color, text_color)

        Description: Changes the color of the GUI using the input background and text colors. Uses a gradient, so not all elements are the same
                        color. Gradient will fail if specified background color is too close to white or black (in which case most elements will be
                        white or black).

        Parameter: background_color: A tuple of three ints specifying the rgb components of the desired background color.
        Parameter: text_color: A tuple of three ints specifying the rgb components of the desired text color.
    """

    def changeColor(self, background_color, text_color):
        tuple_min = lambda t: tuple(min(x, 255) for x in t)
        tuple_max = lambda t: tuple(max(x, 0) for x in t)
        tuple_add = lambda t, i: tuple((x + i) for x in t)
        invert = lambda t: tuple(255 - x for x in t)

        lighter = tuple_min(tuple_add(background_color, 20))
        darker = tuple_max(tuple_add(background_color, -11))

        text_color_invert = invert(text_color)
        background_color_invert = invert(background_color)

        stylesheet = (
            "QMainWindow, QWidget#centralwidget, QWidget#stepsWidget, QWidget#toolWidget, QWidget#partWidget, QWidget#supplyWidget, QWidget#moldReleaseWidget, QWidget#scrollAreaWidgetContents { background-color: rgb"
            + f"{background_color};"
            + " }\n"
            "QLineEdit { "
            + f"color: rgb{text_color}; background-color: rgb{lighter};"
            + " }\n"
            "QPlainTextEdit, QTextEdit, QLabel { " + f"color: rgb{text_color};" + " }\n"
            "QGroupBox, QTabWidget, QSpinBox { "
            + f"color: rgb{text_color}; background-color: rgb{darker};"
            + " }\n"
            "QPushButton, QScrollArea, QPlainTextEdit, QTextEdit { "
            + f"color: rgb{text_color}; background-color: rgb{darker}"
            + " }\n"
            "QCheckBox { color: "
            + f"rgb{text_color}"
            + "; "
            + f"background-color: rgb{darker}"
            + "; }\n"
            "QLCDNumber { color: white; }\n"
            "QComboBox, QComboBox QAbstractItemView { "
            + f"color: rgb{text_color}; background-color: rgb{background_color}; selection-color: rgb{background_color_invert}; selection-background-color: rgb{text_color_invert};"
            + " }"
            f'QStatusBar {"{"}color: rgb{text_color}{"}"}'
        )

        self.application.setStyleSheet(stylesheet)

    """
    keyPressEvent(self, qKeyEvent)

        Description:    Intercepts all keyboard inputs, and if the key pressed was 'enter' or 'return', a 'tab' is pressed to cycle between
                        QLineEdits (text input boxes).  DOESN'T WORK
        
        Parameter: qKeyEvent - QKeyEvent specifying a keyboard key press event.
    
    def keyPressEvent(self, qKeyEvent):
        if qKeyEvent.key() == Qt.Key_Return or qKeyEvent.key() == Qt.Key_Enter:
            pyautogui.press('tab')
    """

    """
    setFailIndex(self, name)

        Description: Sets the index of the drop down menu to specify failure modes relevant to the failed item picked
                    in the top drop down menu.

        Parameter: name - String specifying the object name of the drop down menu to be displayed.
    """

    def setFailIndex(self, name):
        index = 0
        widget = None
        child = None
        found = True

        if (
            self.ui.failSelect.currentIndex() == 0
            or self.ui.failSelect.currentText() == "Other"
        ):
            self.ui.failSelectTab.setCurrentIndex(0)
        else:
            while found:
                widget = self.ui.failSelectTab.widget(index)

                if widget == None:
                    found = False
                else:
                    child = widget.findChild(QComboBox, name)

                    if child == None:
                        index += 1
                    else:
                        self.ui.failSelectTab.setCurrentIndex(index)
                        found = False

    """
    enableAdditionalFailure(self)

        Description: Shows or hides the position drop down menu, depending on whether that information makes sense for the current
                 failure item and mode.
    """

    def enableAdditionalFailure(self):
        self.ui.failureComments.setDisabled(False)

        if (
            self.ui.failSelect.currentText() != "Select failed item"
            and self.ui.failSelect.currentText() != "Other"
        ):
            self.ui.positionSelectTab.setCurrentIndex(1)
        else:
            self.ui.positionSelectTab.setCurrentIndex(0)

    """
    failure(self)

        Description: Function called when the Submit Failure Button is pressed. Validates that required information is present,
                 then writes all information to the failure file. Lastly, the failure menus are reset to the default state.
    """

    def failure(self):
        ## Reset style sheets
        # Panel
        # self.panelInput[self.pro_index].setStyleSheet('')
        # Entire failure box
        self.ui.failSelect.setStyleSheet("")
        # Fail select tab (anchor, straw, etc...)
        obj = self.ui.failSelectTab.currentWidget().findChild(QComboBox)
        if obj is not None:
            obj.setStyleSheet("")
        # Position select
        obj = self.ui.positionSelectTab.currentWidget().findChild(QComboBox)
        if obj is not None:
            obj.setStyleSheet("")
        # Failure Comments
        self.ui.failureComments.setStyleSheet("")

        ## Check for valid entry
        # If an element has insufficient data (ex: drop down still says "Select"),
        # text will be displayed on self.ui.failStatus
        valid = True

        # Check for....
        # Panel
        if self.getCurrentPanel() == "":
            # self.panelInput[self.pro_index].setStyleSheet('background-color:rgb(149, 186, 255)')
            self.ui.failStatus.setText("Enter Panel ID")
            valid = False

        # Item (Anchor, straw, etc...)
        if self.ui.failSelect.currentIndex() == 0:
            # self.ui.failSelect.setStyleSheet('background-color:rgb(149, 186, 255)')
            self.ui.failStatus.setText("Select failed item")
            valid = False

        # Failure Mode
        obj = self.ui.failSelectTab.currentWidget().findChild(QComboBox)
        if obj is not None and obj.currentIndex() == 0:
            # obj.setStyleSheet('background-color:rgb(149, 186, 255)')
            self.ui.failStatus.setText("Select failure mode")
            valid = False

        # Position
        obj = self.ui.positionSelectTab.currentWidget().findChild(QComboBox)
        if obj is not None and obj.currentIndex() == 0:
            # obj.setStyleSheet('background-color:rgb(149, 186, 255)')
            self.ui.failStatus.setText("Select a position number")
            valid = False

        # If failure is "other", user must supply a comment
        if (
            self.ui.failSelect.currentText() == "Other"
            and self.ui.failureComments.toPlainText() == ""
        ):
            # self.ui.failureComments.setStyleSheet('background-color:rgb(149, 186, 255)')
            self.ui.failStatus.setText("Supply a comment")
            valid = False

        # # If this is not a valid failure, don't record it.
        if not valid:
            #     print('not valid')
            # Reset failure-relted widgets
            #     self.ui.failStatus.setText('Unable to submit failure, try again')
            self.ui.failSelect.setCurrentIndex(0)
            self.ui.positionSelect.setCurrentIndex(0)
            self.ui.anchorFail.setCurrentIndex(0)
            self.ui.strawFail.setCurrentIndex(0)
            self.ui.pinFail.setCurrentIndex(0)
            self.ui.positionSelectTab.setCurrentIndex(0)
            self.ui.failureComments.setPlainText("")
            self.ui.failureComments.setDisabled(True)
            return

        ## Extract data and save

        # Position
        position_label = self.ui.positionSelectTab.currentWidget().findChild(QComboBox)
        position = (
            int(position_label.currentText()) if position_label is not None else None
        )

        # Failure Type
        failure_type = self.ui.failSelect.currentText().strip().lower()

        # Failure Mode
        failure_mode_label = self.ui.failSelectTab.currentWidget().findChild(QComboBox)
        failure_mode = (
            failure_mode_label.currentText() if failure_mode_label is not None else None
        )

        # Comment
        comment = (
            f"Failure: {failure_type}, {f'{position} ,' if position is not None else str()}"
            f"{f'{failure_mode} ,' if failure_mode is not None else str()}"
            f"{self.ui.failureComments.toPlainText().strip()}"
        )

        self.DP.saveFailure(
            failure_type=failure_type,
            failure_mode=failure_mode,
            straw_position=position,
            comment=comment,
        )
        try:
            pass
        except Exception:
            # If saving the failure is unsuccessful, display message and return early.
            self.ui.failStatus.setText("Unable to submit failure")
            return

        # Reset failure-relted widgets
        self.ui.failStatus.setText("Failure submited")
        self.ui.failSelect.setCurrentIndex(0)
        self.ui.positionSelect.setCurrentIndex(0)
        self.ui.anchorFail.setCurrentIndex(0)
        self.ui.strawFail.setCurrentIndex(0)
        self.ui.pinFail.setCurrentIndex(0)
        self.ui.positionSelectTab.setCurrentIndex(0)
        self.ui.failureComments.setPlainText("")
        self.ui.failureComments.setDisabled(True)

        # Show new comments in previous comments box
        self.displayComments()

    """
    Change_worker_ID(self, btn)

        Description: Function that handles the log in and log out features of the GUI.

        Parameter: btn - QPushButton specifying which log in/log out button was pressed.
    """

    def Change_worker_ID(self, btn):
        label = btn.text()
        portalNum = int(btn.objectName().strip("portal")) - 1

        if label == "Log In":
            box = QInputDialog(self, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
            box.setInputMode(QInputDialog.TextInput)

            box.setStyleSheet("color: black; background-color: rgb(255,255,255)")

            box.setWindowTitle("Worker Log In")
            box.setLabelText("Scan your worker ID:")
            ok = box.exec_()
            Current_worker = box.textValue().upper().strip()

            # Recolor secret feature
            # Allows lab personel to change the color of the gui
            # Definitely not essential, but it boosts morale
            # enter goldy to change to UMN colors, Dan likes it too
            if Current_worker == "GOLDY" or Current_worker == "WK-DAMBROSE01":
                self.changeColor(
                    (122, 0, 25), (255, 204, 51)
                )  # 122/0/25 = maroon, 255/204/51 = gold
                self.ui.scrollArea.setStyleSheet("background-color: rgb(122, 0, 25);")
                self.ui.scrollAreaHV.setStyleSheet("background-color: rgb(122, 0, 25);")
            elif (
                Current_worker == "DARK MODE"
                or Current_worker == "WK-AARNETT01"
                or Current_worker == "WK-KBOEDIGH01"
            ):  # enter dark mode to change to dark mode, Adam and Kaitlin like it too
                self.changeColor(
                    (26, 26, 26), (255, 255, 255)
                )  # 26/26/26 = 10% brightness, 255/255/255 = white
                self.ui.scrollArea.setStyleSheet("background-color: rgb(26, 26, 26);")
                self.ui.scrollAreaHV.setStyleSheet("background-color: rgb(26, 26, 26);")
            elif (
                Current_worker == "SURPRISE ME"
            ):  # enter surprise me to get a random color
                seed = int(
                    str(datetime.now())[20:]
                )  # semi random number generator (the current microsecond)
                seedMod = int(
                    str(datetime.now())[17:19]
                )  # another semi random number generator (the current second)
                backR = (seed * seedMod) % 255  # back red
                backG = (seed / seedMod) % 255  # back green
                backB = (seed + seedMod) % 255  # back blue
                textR = (
                    backR + 175
                ) % 255  # text red; keeping all of these at +X makes sure that the text is visible against the back
                textG = (backG + 175) % 255  # text green
                textB = (backB + 175) % 255  # text blue
                self.changeColor((backR, backG, backB), (textR, textG, textB))
                self.ui.scrollArea.setStyleSheet(
                    f"background-color: rgb({backR}, {backG}, {backB});"
                )
                self.ui.scrollAreaHV.setStyleSheet(
                    f"background-color: rgb({backR}, {backG}, {backB});"
                )
            elif (
                Current_worker == "BURN MY CORNEAS"
            ):  # enter burn my corneas to get back to normal colors
                self.changeColor(
                    (255, 255, 255), (0, 0, 0)
                )  # 255/255/255 = white back, 0/0/0 = black text
                self.ui.scrollArea.setStyleSheet(
                    "background-color: rgb(255, 255, 255);"
                )
                self.ui.scrollAreaHV.setStyleSheet(
                    "background-color: rgb(255, 255, 255);"
                )

            if ok and Current_worker != "":
                if not self.DP.validateWorkerID(Current_worker):
                    self.generateBox("critical", "Login Error", "Invalid worker ID.")
                elif self.DP.workerLoggedIn(Current_worker):
                    self.generateBox(
                        "critical",
                        "Login Error",
                        "This worker ID is already logged in.",
                    )
                else:
                    # Record login with data processor
                    self.DP.saveLogin(Current_worker)
                    # Gui Operations
                    self.Current_workers[portalNum].setText(Current_worker)
                    btn.setText("Log Out")
            else:
                Current_worker = ""

        elif label == "Log Out":
            Current_worker = self.Current_workers[portalNum].text().strip().upper()

            if Current_worker != "":
                self.DP.saveLogout(Current_worker)

            self.Current_workers[portalNum].setText("")
            btn.setText("Log In")

        # Recheck credentials
        self.LockGUI.emit(self.DP.checkCredentials())

        self.suppliesList.setWorkers(self.DP.getSessionWorkers())

    """
    lockGUI(self, credentials)

        Description: Locks or unlocks the GUI tabs depending on whether ANY logged in worker has valid credentials
                    for the current pro. Locked tabs cannot be accessed.

        Parameter: credentials - Boolean value specifying if ANY logged in worker has valid credentials.
    """

    def lockGUI(self, credentials):
        pro = f"Panel pro {self.pro}"
        supply = f"pro {self.pro} Supplies List"

        if credentials:
            self.ui.tabWidget.setTabText(1, supply)
            self.ui.tabWidget.setTabEnabled(1, True)
            self.ui.tabWidget.setTabText(2, pro)
            self.ui.tabWidget.setTabEnabled(2, True)
        else:
            self.ui.tabWidget.setTabText(1, supply + " *Locked*")
            self.ui.tabWidget.setTabEnabled(1, False)
            self.ui.tabWidget.setTabText(2, pro + " *Locked*")
            self.ui.tabWidget.setTabEnabled(2, False)

    def main(self):
        elapsedTime = lambda: self.mainTimer.getElapsedTime().total_seconds()
        last_write_time = elapsedTime()
        while True:
            # This loop only aplies if the main timer is running
            if self.running():
                # If the amount of time elapsed by the main timer is more than one write interval, call save data (by emitting the 'SaveData' signal)
                if elapsedTime() - last_write_time > self.writeInterval:
                    self.SaveData.emit()
                    # Set 'last_write_time' to right now
                    last_write_time = elapsedTime()

            time.sleep(0.01)

    ###  ____                    ____        _          __  __      _   _               _
    ### / ___|  __ ___   _____  |  _ \  __ _| |_ __ _  |  \/  | ___| |_| |__   ___   __| |___
    ### \___ \ / _` \ \ / / _ \ | | | |/ _` | __/ _` | | |\/| |/ _ \ __| '_ \ / _ \ / _` / __|
    ###  ___) | (_| |\ V /  __/ | |_| | (_| | || (_| | | |  | |  __/ |_| | | | (_) | (_| \__ \
    ### |____/ \__,_| \_/ \___| |____/ \__,_|\__\__,_| |_|  |_|\___|\__|_| |_|\___/ \__,_|___/

    def saveData(self):
        # Extract data from gui widgets
        self.updateData()

        # Save with DataProcessor
        # print(datetime.now())
        # print(self.data)
        self.DP.saveData()
        try:
            pass
        except Exception:
            self.generateBox(
                "critical", "Save Error", "Error encountered trying to save data."
            )

    """
    saveContinuityMeasurement(self,position,continuity_str,wire_pos_str)

        Description:    Saves a continuity measurement as specified by the input arguments
                        After saving, ensures that the drop downs for this position's continuity
                        measurement on the main GUI screen match the data that is saved. 
                        This method is called both when the drop downs on the main screen have their 
                        index changed, and when continuity data is sent from the wire tension popup.

        Input:
            - position          (int)   The position of the wire that this measurement is for.
            - continuity_str    (str)   One of the following: ['Pass: No Continuity', 'Fail: Right Continuity', 'Fail: Left Continuity', 'Fail: Both Continuity']
            - wire_position     (str)   One of the following : ['Top 1/3', 'Middle 1/3', 'Lower 1/3']
    """

    def saveContinuityMeasurement(self, position, continuity_str, wire_pos_str):
        # First, save the data with the data processor
        self.DP.saveContinuityMeasurement(position, continuity_str, wire_pos_str)

        # TODO: Do we need this stuff?
        # Next, ensure that the display on the main screen matches this measurement
        if (
            self.continuity[position].currentText() != continuity_str
            or self.wire_pos[position].currentText() != wire_pos_str
        ):
            self.displayContinuityMeasurement(position, continuity_str, wire_pos_str)

    def saveHVMeasurement(self, position, current_left, current_right, is_tripped):
        self.DP.saveHVMeasurement(position, current_left, current_right, is_tripped)

        if self.currentLeft[position].text() != current_left:
            self.displayHVMeasurement(position, current_left, current_right)
        if self.currentRight[position].text() != current_right:
            self.displayHVMeasurement(position, current_left, current_right)

    """
    saveStep(self, name)

        Description: The function called to save data when a checkbox is checked. Records that the given step has been executed.

        Parameter: name - Name of step completed
    """

    def saveStep(self, name):
        try:
            self.DP.saveStep(name)
        except Exception:
            self.generateBox(
                "critical", "Save Error", "Error encountered trying to save data"
            )

    """
    saveComments(self, comments = '')

        Description: Handles the saving of comments. Takes any comments from the comment box, and moves them to the
                 previous comments box, giving them a timestamp. Ignores blank comments. Sends comments to the 
                 data processor to be saved. Can give the function the comment to save, or it will get the comment 
                 from the appropriate pro's comment box.
    """

    def saveComments(self, comments=""):

        if comments == "":
            # Get Comment box [<boxes>][<index we want>]
            box = [
                self.ui.commentBox1,
                self.ui.commentBox2,
                self.ui.commentBox3,
                self.ui.commentBox4,
                self.ui.commentBox5,
                self.ui.commentBox6,
                self.ui.commentBox7,
            ][self.pro_index]
            # Extract text
            comments = box.document().toPlainText()
            # Reset comment display
            box.setPlainText("")

        comments = comments.strip()  # remove whitespace around comment

        # if comments are nothing then return
        if comments == "":
            return

        try:
            self.DP.saveComment(
                comments, self.getCurrentPanel(), self.pro
            )  # try to save comment
        except Exception:
            # If it fails, generate a message box and return
            self.generateBox(
                "critical", "Save Error", "Error encountered trying to save comments."
            )
            return

        self.displayComments()  # display updated comments

    @staticmethod
    def timerTuple(timer):
        if timer.wasStarted():
            return (timer.getElapsedTime(), timer.isRunning())
        else:
            return None

    ###  _   _           _       _         ____        _          __  __      _   _               _
    ### | | | |_ __   __| | __ _| |_ ___  |  _ \  __ _| |_ __ _  |  \/  | ___| |_| |__   ___   __| |___
    ### | | | | '_ \ / _` |/ _` | __/ _ \ | | | |/ _` | __/ _` | | |\/| |/ _ \ __| '_ \ / _ \ / _` / __|
    ### | |_| | |_) | (_| | (_| | ||  __/ | |_| | (_| | || (_| | | |  | |  __/ |_| | | | (_) | (_| \__ \
    ###  \___/| .__/ \__,_|\__,_|\__\___| |____/ \__,_|\__\__,_| |_|  |_|\___|\__|_| |_|\___/ \__,_|___/
    ###       |_|

    """
    updateData(self)

        Description:    Calls the appropriate save data function for the pro, then processes the list to turn all data
                        that fails bool(data) to None
    """

    def updateData(self):
        # Call method appropriate for the pro
        [
            self.updateDataProcess1,
            self.updateDataProcess2,
            self.updateDataProcess3,
            self.updateDataProcess4,
            self.updateDataProcess5,
            self.updateDataProcess6,
            self.updateDataProcess7,
        ][self.pro_index]()

        # Process the updated data list by replacing all elements in the list that don't pass bool(el) with None
        self.data[self.pro_index] = [
            (el if bool(el) else None) for el in self.data[self.pro_index]
        ]

    """
    processXUpdateData(self)

        Description: Save function used to save the data for panel pro X. Gets the data currently in all input fields,
                    then writes it to the file.

        Parameter: file - The python file object that is used to write the data to the appropriate file
    """

    def updateDataProcess1(self):
        self.data[self.pro_index][0] = self.ui.panelInput1.text()
        self.data[self.pro_index][1] = self.ui.baseInput1.text()
        self.data[self.pro_index][2] = self.ui.birInput.text()
        self.data[self.pro_index][3] = self.ui.pirInputLA.text()
        self.data[self.pro_index][4] = self.ui.pirInputLB.text()
        self.data[self.pro_index][5] = self.ui.pirInputLC.text()
        self.data[self.pro_index][6] = self.ui.pirInputRA.text()
        self.data[self.pro_index][7] = self.ui.pirInputRB.text()
        self.data[self.pro_index][8] = self.ui.pirInputRC.text()
        self.data[self.pro_index][9] = self.ui.mirInput.text()
        self.data[self.pro_index][10] = self.ui.alfInput.text()
        self.data[self.pro_index][11] = self.ui.alfInput_2.text()
        self.data[self.pro_index][12] = (
            int(self.ui.leftgap.currentText())
            if self.ui.leftgap.currentIndex() != 0
            else None
        )
        self.data[self.pro_index][13] = (
            int(self.ui.rightgap.currentText())
            if self.ui.rightgap.currentIndex() != 0
            else None
        )
        self.data[self.pro_index][14] = (
            int(self.ui.mingap.currentText())
            if self.ui.mingap.currentIndex() != 0
            else None
        )
        self.data[self.pro_index][15] = (
            int(self.ui.maxgap.currentText())
            if self.ui.maxgap.currentIndex() != 0
            else None
        )
        self.data[self.pro_index][16] = self.ui.epoxy_batch1.text()
        self.data[self.pro_index][17] = self.timerTuple(self.timers[1])
        self.data[self.pro_index][18] = self.ui.paasAInput.text()
        self.data[self.pro_index][19] = self.ui.paasCInput.text()
        self.data[self.pro_index][20] = (
            str(self.ui.pallet1code.text()) if self.ui.pallet1code.text() else None
            )
        self.data[self.pro_index][21] = (
            str(self.ui.pallet2code.text()) if self.ui.pallet2code.text() else None
            )

    def updateDataProcess2(self):
        self.data[self.pro_index][0] = self.ui.panelInput2.text()
        self.data[self.pro_index][1] = self.ui.epoxy_batch.text()  # Lower Epoxy
        self.data[self.pro_index][2] = self.timerTuple(
            self.timers[2]
        )  # Lower Epoxy Time
        self.data[self.pro_index][3] = self.ui.epoxy_batch_2.text()  # Upper Epoxy
        self.data[self.pro_index][4] = self.timerTuple(
            self.timers[3]
        )  # Upper Epoxy Time
        self.data[self.pro_index][5] = (
            float(self.ui.temp4.text()) if self.ui.temp4.text() else None
        )  # PAAS-A Max Temp
        self.data[self.pro_index][6] = (
            float(self.ui.temp4_2.text()) if self.ui.temp4_2.text() else None
        )  # PAAS-B Max Temp
        self.data[self.pro_index][7] = self.timerTuple(self.timers[4])  # Heat Time
        self.data[self.pro_index][8] = self.ui.paasBInput.text()  # paas B input

    def updateDataProcess3(self):
        # pro-specific Data
        self.data[self.pro_index][0] = self.ui.panelInput3.text()
        self.data[self.pro_index][1] = self.ui.wireInput.text()
        self.data[self.pro_index][2] = self.timerTuple(self.timers[5])
        # scroll area is saved/updated differently

    def updateDataProcess4(self):
        self.data[self.pro_index][0] = self.ui.panelInput4.text()  # panel input
        self.data[self.pro_index][
            1
        ] = self.ui.epoxy_batch_3.text()  # clear epoxy left - batch
        self.data[self.pro_index][2] = self.timerTuple(
            self.timers[11]
        )  # clear epoxy left - application duration
        self.data[self.pro_index][3] = self.timerTuple(
            self.timers[12]
        )  # clear epoxy left - cure duration
        self.data[self.pro_index][
            4
        ] = self.ui.epoxy_batch_4.text()  # clear epoxy right - batch
        self.data[self.pro_index][5] = self.timerTuple(
            self.timers[13]
        )  # clear epoxy right - application duration
        self.data[self.pro_index][6] = self.timerTuple(
            self.timers[14]
        )  # clear epoxy right - cure duration
        self.data[self.pro_index][
            7
        ] = self.ui.epoxy_batch_5.text()  # silver epoxy left - batch
        self.data[self.pro_index][8] = self.timerTuple(
            self.timers[15]
        )  # silver epoxy left - application duration
        self.data[self.pro_index][9] = self.timerTuple(
            self.timers[17]
        )  # silver epoxy left - cure duration
        self.data[self.pro_index][
            10
        ] = self.ui.epoxy_batch_6.text()  # silver epoxy right - batch
        self.data[self.pro_index][11] = self.timerTuple(
            self.timers[16]
        )  # silver epoxy right - application duration
        self.data[self.pro_index][12] = self.timerTuple(
            self.timers[18]
        )  # silver epoxy right - cure duration

    def updateDataProcess5(self):
        # looking for HV measurements? They bypass this.data and get saved
        # directly to the DP via saveHVMeasurement.
        if len(self.data[self.pro_index]) == 0:
            self.data[self.pro_index].append(self.ui.panelInput5.text())
        self.data[self.pro_index][0] = self.ui.panelInput5.text()

    def updateDataProcess6(self):
        self.data[self.pro_index][0] = self.ui.panelInput6.text()
        self.data[self.pro_index][1] = self.ui.frameInput.text()
        self.data[self.pro_index][2] = self.ui.mrInput1.text()
        self.data[self.pro_index][3] = self.ui.mrInput2.text()
        self.data[self.pro_index][4] = (
            int(self.ui.bpmirgapL.currentText())
            if self.ui.bpmirgapL.currentIndex() != 0
            else None
        )
        self.data[self.pro_index][5] = (
            int(self.ui.bpmirgapR.currentText())
            if self.ui.bpmirgapR.currentIndex() != 0
            else None
        )
        self.data[self.pro_index][6] = self.ui.epoxy_batch41.text()
        self.data[self.pro_index][7] = self.timerTuple(self.timers[6])
        self.data[self.pro_index][8] = self.ui.epoxy_batch42.text()
        self.data[self.pro_index][9] = self.ui.epoxy_batch42_2.text()
        self.data[self.pro_index][10] = self.timerTuple(self.timers[7])
        self.data[self.pro_index][11] = (
            float(self.ui.temp4_4.text()) if self.ui.temp4_4.text() else None
        )
        self.data[self.pro_index][12] = (
            float(self.ui.temp4_5.text()) if self.ui.temp4_5.text() else None
        )
        self.data[self.pro_index][13] = self.timerTuple(self.timers[8])

    def updateDataProcess7(self):
        self.data[self.pro_index][0] = self.ui.panelInput7.text()
        self.data[self.pro_index][1] = self.ui.epoxy_batch5_2.text()
        self.data[self.pro_index][2] = self.timerTuple(self.timers[9])
        self.data[self.pro_index][3] = self.ui.epoxy_batch5_3.text()
        self.data[self.pro_index][4] = self.timerTuple(self.timers[10])

    ###  _                    _   ____        _          __  __      _   _               _
    ### | |    ___   __ _  __| | |  _ \  __ _| |_ __ _  |  \/  | ___| |_| |__   ___   __| |___
    ### | |   / _ \ / _` |/ _` | | | | |/ _` | __/ _` | | |\/| |/ _ \ __| '_ \ / _ \ / _` / __|
    ### | |__| (_) | (_| | (_| | | |_| | (_| | || (_| | | |  | |  __/ |_| | | | (_) | (_| \__ \
    ### |_____\___/ \__,_|\__,_| |____/ \__,_|\__\__,_| |_|  |_|\___|\__|_| |_|\___/ \__,_|___/

    """
    loadpro(self)

        Description:    Called when after a complete panel ID is entered in any of the panel input fields. 
                        Trys to load previous data and steps completed with the data processor, returned in a long list. 
                        If found, also tries calls the appropriate parsing functions to return the GUI to its previous state.
    """

    def loadpro(self):
        ### Load Data

        ## Try to load all previous data
        (
            data,
            elapsed_time,
            steps_completed,
        ) = (
            self.DP.loadData()
        )  # data should be renamed so there isn't self.data and data
        ## If no new data is found, return early
        if not any(
            el is not None for el in data[1:]
        ):  # Everything in data list except for panel
            if not self.pro == 5:
                return

        ### Save data to corresponding data-storing instance variable

        self.data[self.pro_index] = data
        self.mainTimer.setElapsedTime(elapsed_time)

        ### Parse Data to Display

        ## pro Data
        # Get proper parse method for this pro
        parse_pro = [
            self.parsepro1Data,
            self.parsepro2Data,
            self.parsepro3Data,
            self.parsePro4Data,
            self.parsePro5Data,
            self.parsepro6Data,
            self.parsepro7Data,
        ]

        # Call method giving 'data' as input.
        parse_pro[self.pro_index](data)

        ## Process 3 continuity data
        if self.pro == 3:
            measurements = self.loadContinuityMeasurements()
            # Possibilities:
            #   - None: No measurements saved at all
            #   - List of (cont,wire_pos) tuples where index matches wire position
            #       Note, could be (None,None) if no measurement is recorded at that position.

            # If any measurements are found, display them
            if measurements is not None:
                self.parseContinuityMeasurements(measurements)

        ## Process 5 HV data
        if self.pro == 5:
            # [(current_left0, current_right0, is_tripped0), (current_left1, current_right1, is_tripped1), ... ]
            # (None,None,None) if no measurement at that position.
            measurements = self.loadHVMeasurements()

            # if ANY current in ANY measurement is not None then display
            if any(any(current is not None for current in m) for m in measurements):
                self.displayAllHVMeasurements(measurements)

        ## Parse Steps
        self.parseSteps(steps_completed)

        ### Additional GUI operations if data is found

        ## Record resume
        self.DP.saveResume()
        ## Start running again
        self.mainTimer.start()

        ## Enable finish and save
        self.setWidgetsEnabled(
            [self.ui.saveButtons.buttons()[self.pro_index], self.finishButton]
        )

        ## Disable start and "back to pro select" buttons
        self.setWidgetsDisabled(
            [self.startButtons[self.pro_index], self.ui.proReturnButton]
        )

        ## Unless all the steps have been completed, set the finish/pause button text to "Pause"
        if not self.stepsList.allStepsChecked():
            self.finishButton.setText("Pause")

        ## Load and display comments too
        self.displayComments()

    # Load the measurement(s)
    # position = None   : All continuity measurements in a list
    # position = int    : Continuity measurement at specified position
    def loadContinuityMeasurements(self, position=None):
        return self.DP.loadContinuityMeasurements(position)

    # position = None   : All HV measurements in a list
    # position = int    : HV measurement at specified position
    def loadHVMeasurements(self, position=None):
        return self.DP.loadHVMeasurements()

    ###  ____                          _              _   ____  _           _
    ### |  _ \ __ _ _ __ ___  ___     / \   _ __   __| | |  _ \(_)___ _ __ | | __ _ _   _
    ### | |_) / _` | '__/ __|/ _ \   / _ \ | '_ \ / _` | | | | | / __| '_ \| |/ _` | | | |
    ### |  __/ (_| | |  \__ \  __/  / ___ \| | | | (_| | | |_| | \__ \ |_) | | (_| | |_| |
    ### |_|   \__,_|_|  |___/\___| /_/   \_\_| |_|\__,_| |____/|_|___/ .__/|_|\__,_|\__, |
    ###                                                              |_|            |___/

    def displayComments(self):
        # Get string from Data Processor
        s = self.DP.getCommentText()
        # Display modified string
        self.ui.previousComments.setPlainText(s)

    """
    parseSteps(self, steps_completed)

        Description: Parsing function to take the list of steps completed and check the appropriate checkboxes.

        Parameter: steps (int) A count of the number of steps completed
    """

    def parseSteps(self, steps_completed):

        # This method doesn't look at the names of the steps. It checks of
        # as many checkboxes as specified by the input integer.

        # No matter what, start by enabling the first step
        step = self.stepsList.getCurrentStep()
        if step is not None:
            box = step.getCheckbox()
            if box is not None:
                box.setEnabled(True)

        for _ in range(steps_completed):
            if self.stepsList.getCurrentStep():
                checkbox = self.stepsList.getCurrentStep().getCheckbox()
                checkbox.setChecked(True)
                checkbox.setDisabled(True)

                nextCheckbox = self.stepsList.getNextCheckbox()
                self.stepsList.getNextStep()

                if nextCheckbox is not None:
                    nextCheckbox.setDisabled(False)

        # If all steps have been completed, change text of finish button
        if self.stepsList.allStepsChecked():
            self.finishButton.setText("Finish")

    """
    parsepro3WireData(self)

        Description:    This function handles additional data that is saved in pro 3 (continuity, wire position, and wire resistance).
                        It sets the appropriate values in the drop down menus.

        Input: Lists of wire data ordered by panel position
            - cont_data     -   Continuity measurements
            - wire_pos_data -   Wire position
            - res_data      -   Resistance measurements
    """

    def parseContinuityMeasurements(self, data):
        # Display the given data
        for index, measurements in enumerate(data):
            cont_str, wire_pos_str = measurements
            if cont_str is not None and wire_pos_str is not None:
                self.displayContinuityMeasurement(index, cont_str, wire_pos_str)

    def displayContinuityMeasurement(self, index, continuity_str, wire_pos_str):
        # Finds index of string, then sets index to that number
        setText = lambda combo_box, text: combo_box.setCurrentIndex(
            combo_box.findText(text if text != "" else "Select")
        )

        # Call method to update both continuity and wire position displays at this index
        setText(self.continuity[index], continuity_str)
        setText(self.wire_pos[index], wire_pos_str)

    def displayAllHVMeasurements(self, data):
        for index, measurements in enumerate(data):
            current_left, current_right, is_tripped = measurements
            if any(current is not None for current in measurements):
                self.displayHVMeasurement(
                    index, current_left, current_right, is_tripped
                )

    def displayHVMeasurement(self, index, current_left, current_right, is_tripped):
        self.currentLeft[index].setText(str(current_left))
        self.currentRight[index].setText(str(current_right))
        self.isTripped[index].setChecked(is_tripped)
        """
        setLineEdit = lambda line_edit, text : line_edit.setText( # make a lambda fxn that takes a lineEdit and text
            line_edit.findText(
                text if text != '' else ''                                # set the lineEdits content to text if text is not '' otherwise ''
            )
        )
        setLineEdit(self.currentLeft[index],  current_left)               # set text for current left
        setLineEdit(self.currentRight[index], current_right)              # set text for current right

        if is_tripped:                                                    # if the fxn is passed true for is_tripped
            self.isTripped[index].setChecked(True)                        # then check the corresponding index
        """

    """
    parsepro1Data(self, data)

        Description: Given the loaded data, sets the appropriate UI elements with that data. Also handles the enabling/disabling of
                    UI elements to ensure the GUI state is consistent with normal use.

        Parameter: data - A list of the parsed input data
    """

    def parsepro1Data(self, data):
        if data[0] is not None:
            self.ui.panelInput1.setText(data[0])
            self.ui.panelInput1.setDisabled(True)
        if data[1] is not None:
            self.ui.baseInput1.setText(data[1])
            self.ui.baseInput1.setDisabled(True)
        if data[2] is not None:
            self.ui.birInput.setText(data[2])
            self.ui.birInput.setDisabled(True)
        if data[3] is not None:
            self.ui.pirInputLA.setText(data[3])
            self.ui.pirInputLA.setDisabled(True)
        if data[4] is not None:
            self.ui.pirInputLB.setText(data[4])
            self.ui.pirInputLB.setDisabled(True)
        if data[5] is not None:
            self.ui.pirInputLC.setText(data[5])
            self.ui.pirInputLC.setDisabled(True)
        if data[6] is not None:
            self.ui.pirInputRA.setText(data[6])
            self.ui.pirInputRA.setDisabled(True)
        if data[7] is not None:
            self.ui.pirInputRB.setText(data[7])
            self.ui.pirInputRB.setDisabled(True)
        if data[8] is not None:
            self.ui.pirInputRC.setText(data[8])
            self.ui.pirInputRC.setDisabled(True)
        if data[9] is not None:
            self.ui.mirInput.setText(data[9])
            self.ui.mirInput.setDisabled(True)
        if data[10] is not None:
            self.ui.alfInput.setText(data[10])
            self.ui.alfInput.setDisabled(True)
        if data[11] is not None:
            self.ui.alfInput_2.setText(data[11])
            self.ui.alfInput_2.setDisabled(True)
        if data[18] is not None:
            self.ui.paasAInput.setText(data[18])
            self.ui.paasAInput.setDisabled(True)
        if data[19] is not None:
            self.ui.paasCInput.setText(data[19])
            self.ui.paasCInput.setDisabled(True)
            self.ui.leftgap.setEnabled(True)
            self.ui.rightgap.setEnabled(True)
            self.ui.mingap.setEnabled(True)
            self.ui.maxgap.setEnabled(True)
            self.ui.epoxy_batch1.setEnabled(True)
            self.ui.epoxy_mixed1.setEnabled(True)
        if data[12] is not None:
            self.ui.leftgap.setCurrentIndex(int(data[12]))
        if data[13] is not None:
            self.ui.rightgap.setCurrentIndex(int(data[13]))
        if data[14] is not None:
            self.ui.mingap.setCurrentIndex(int(data[14]))
        if data[15] is not None:
            self.ui.maxgap.setCurrentIndex(int(data[15]))
        if data[16] is not None:
            self.ui.epoxy_batch1.setText(data[16])
        if data[17] is not None:
            self.ui.leftgap.setDisabled(True)
            self.ui.rightgap.setDisabled(True)
            self.ui.mingap.setDisabled(True)
            self.ui.maxgap.setDisabled(True)
            self.ui.epoxy_batch1.setDisabled(True)
            self.ui.epoxy_mixed1.setDisabled(True)
            self.ui.epoxy_applied1.setEnabled(True)

            elapsed_time, running = data[17]
            self.timers[1].setElapsedTime(elapsed_time)
            if running:
                self.startTimer(1)
            else:
                self.ui.epoxy_applied1.setDisabled(True)

        # loading from DB doesn't pass the validation bool for
        # the LPAL input, so it's added to the list here
        if len(data) == 22:
            self.data[0].append(False)
            if data[20] is not None and data[21] is not None:
                self.data[0][22] = True
        if data[20] is not None:
            self.ui.pallet1code.setText(data[20])
            self.ui.pallet1code.setDisabled(True)
        if data[21] is not None:
            self.ui.pallet2code.setText(data[21])
            self.ui.pallet2code.setDisabled(True)

    """
    parsepro2Data(self, data)

        Description: Given the loaded data, sets the appropriate UI elements with that data. Also handles the enabling/disabling of
                    UI elements to ensure the GUI state is consistent with normal use.

        Parameter: data - A list of the parsed input data
        0 - panel num (int)
        1 - upper pallet code (int)
        2 - lower pallet code
        3 - lower epoxy batch num (int)
        4 - lower epoxy timer (timer tuple)
        5 - upper epoxy batch num
        6 - upper epoxy timer
        7 - PAAS A max temp (float)
        8 - PAAS B max temp (float)
        9 - heat timer (timer tuple)
    """

    def parsepro2Data(self, data):
        # panel number ---------------------------------------------------------------------------
        if data[0] is not None:  # if panel num data exists
            self.ui.panelInput2.setText(
                data[0]
            )  # set text of panel line edit widget to number
            self.ui.panelInput2.setDisabled(True)  # disable panel line edit

        # lower epoxy ----------------------------------------------------------------------------
        if data[1] is not None:  # if lower epoxy batch num data exists
            self.ui.epoxy_batch.setText(
                data[1]
            )  # set text of lower epoxy line edit widget to num

        if (
            data[2] is not None
        ):  # if lower epoxy timer data exists (if timer has been started)
            self.ui.epoxy_mixed.setDisabled(True)  # disable lower epoxy mixed button
            self.ui.epoxy_batch.setDisabled(
                True
            )  # disable lower epoxy batch line edit widget

            elapsed_time, running = data[
                2
            ]  # extract data from timer tuple [<timedeltaObj>, <isRunningBool>]
            self.timers[2].setElapsedTime(
                elapsed_time
            )  # set time on corresponding timer
            if running:  # if the the loaded data indicates the timer should be running
                self.startTimer(2)  # start the timer
                self.ui.epoxy_inject1.setEnabled(
                    True
                )  # enable lower epoxy inject button (button that stops the timer)
            else:  # the loaded data indicates the timer should NOT be running
                self.ui.epoxy_inject1.setDisabled(
                    True
                )  # disable lower epoxy inject button (timer must have been stopped)

        # upper epoxy ----------------------------------------------------------------------------
        if data[3] is not None:  # if upper epoxy batch num data exists
            self.ui.epoxy_batch_2.setText(
                data[3]
            )  # set text of upper epoxy line edit widget to num

        if (
            data[4] is not None
        ):  # if upper epoxy timer data exists (if timer has been started)
            self.ui.epoxy_mixed_2.setDisabled(True)  # disable upper epoxy mixed button
            self.ui.epoxy_batch_2.setDisabled(
                True
            )  # disable upper epoxy batch line edit widget

            elapsed_time, running = data[
                4
            ]  # extract data from timer tuple [<timedeltaObj>, <isRunningBool>]
            self.timers[3].setElapsedTime(
                elapsed_time
            )  # set time on corresponding timer
            if running:  # if loaded data indicates the timer should be running
                self.startTimer(3)  # start the timer
                self.ui.epoxy_inject2.setEnabled(
                    True
                )  # enable upper epoxy inject button (button that stops the timer)
            else:  # the loaded data indicates the timer should NOT be running
                self.ui.epoxy_inject2.setDisabled(
                    True
                )  # disable upper epoxy inject button (timer must have been stopped)
                self.ui.heat_start.setEnabled(
                    True
                )  # enable heat start button (epoxy stuff has been finished)

        # heat stuff -----------------------------------------------------------------------------
        if data[4] is not None:  # if paas A max temp num data exists
            self.ui.temp4.setText(
                str(data[4])
            )  # set text of paas A max temp line edit widget to num
        if data[6] is not None:  # if paas B max temp num data exists
            self.ui.temp4_2.setText(
                str(data[6])
            )  # set text of paas B max temp line edit widget to num

        if data[7] is not None:  # if heat timer data exists (if timer has been started)
            self.ui.heat_start.setDisabled(True)  # disable heat start button

            elapsed_time, running = data[
                7
            ]  # extract timer tuple data [<timedeltaObj>, <isRunningBool>]
            self.timers[4].setElapsedTime(
                elapsed_time
            )  # set time on corresponding timer
            if running:  # if loaded data indicates the timer should be running
                self.startTimer(4)  # start the timer
                self.ui.heat_finished.setEnabled(
                    True
                )  # enable heat finish button (button that stops the timer)
                self.ui.temp4.setEnabled(
                    True
                )  # enable paas A max temp line edit widget
                self.ui.temp4_2.setEnabled(
                    True
                )  # enable paas B max temp line edit widget
            else:  # loaded data indicates the timer should NOT be running
                self.ui.heat_finished.setDisabled(
                    True
                )  # disable heat finished button (timer must've been stopped)
                self.ui.temp4.setDisabled(
                    True
                )  # disable paas A max temp line edit widget
                self.ui.temp4_2.setDisabled(
                    True
                )  # disable paas B max temp line edit widget

        # PAAS B Entry ---------------------------------------------------------------------------
        if data[8] is not None:
            self.ui.paasBInput.setText(data[8])
            self.ui.paasBInput.setDisabled(True)

    """
    parsepro3Data(self, data)

        Description: Given the loaded data, sets the appropriate UI elements with that data. Also handles the enabling/disabling of
                    UI elements to ensure the GUI state is consistent with normal use.

        Parameter: data - A list of the parsed input data
    """

    def parsepro3Data(self, data):
        if data[0] is not None:
            self.ui.panelInput3.setText(data[0])
            self.ui.panelInput3.setDisabled(True)
        if data[1] is not None:
            self.ui.wireInput.setText(data[1])
            self.ui.wireInput.setDisabled(True)
            self.ui.launch_wire_tensioner.setDisabled(False)
            self.ui.launch_tension_box.setDisabled(False)
            # Enable all continuity widgets
            self.setWidgetsEnabled(self.continuity + self.wire_pos)
        if data[2] is not None:
            # Process timer
            # print(data)
            elapsed_time, running = data[2]
            self.timers[5].setElapsedTime(elapsed_time)
            if running:
                self.startTimer(5)
        else:
            self.startTimer(5)

    def parsePro4Data(self, data):
        # PANEL INPUT
        if data[0] is not None:  # if panel input data exists
            self.ui.panelInput4.setText(data[0])  # set it's text to data[0]
            self.ui.panelInput4.setDisabled(True)  # and disable the panel input widget

        # LEFT PIN
        if data[2] is not None:  # if timer data for left pin application time exists
            self.ui.epoxyMixedLP.setDisabled(
                True
            )  # the timer has been started so disable mixed button
            self.ui.epoxy_batch_3.setDisabled(
                True
            )  # and epoxy batch data has been entered so disable batch input widget
            self.ui.epoxy_batch_3.setText(
                data[1]
            )  # the batch ID data must've been entered so set the batch input widget to data[1]

            elapsed_time, running = data[
                2
            ]  # data[2] is a timer tuple, (timedelta>, <bool>)
            self.timers[11].setElapsedTime(
                elapsed_time
            )  # timer 11 corresponds to the left pin application duration
            if running:  # if the timer is running
                self.startTimer(11)  # resume running timer 11
                self.ui.epoxyInjectedLP.setEnabled(
                    True
                )  # and enable the button that stops it
            else:  # if it's not running, it must be finished since there is recorded time for it
                self.ui.epoxyInjectedLP.setDisabled(
                    True
                )  # disable the button that stops it since it has already finished

            # if timer data for application timer exists, then data for cure time also exists, since they're started by the same button
            elapsed_time, running = data[
                3
            ]  # data [3] is a timer tuple, (<timedelta>, <bool>)
            self.timers[12].setElapsedTime(
                elapsed_time
            )  # timer 12 corresponds to the left pin cure duration
            if running:  # if the timer is running
                self.startTimer(12)  # resume running timer 12
                self.ui.epoxyFinishedLP.setEnabled(
                    True
                )  # and enable the button that stops it
            else:  # if it's not running, it must be finished since there is recorded time for it
                self.ui.epoxyFinishedLP.setDisabled(
                    True
                )  # disable the button that stops it since it has already finished
        elif (
            data[1] is not None
        ):  # ELSE if batch ID data for left pin exists (batch entered, not started)
            self.ui.epoxy_batch_3.setText(
                data[1]
            )  # set the batch input widget to data[1]
            self.ui.epoxyMixedLP.setEnabled(True)
        else:
            self.ui.epoxy_batch_3.setEnabled(True)
            self.ui.epoxyMixedLP.setEnabled(True)

        # RIGHT PIN
        if data[5] is not None:  # if timer data for right pin application time exists
            self.ui.epoxyMixedRP.setDisabled(
                True
            )  # the timer has been started so disable mixed button
            self.ui.epoxy_batch_4.setDisabled(
                True
            )  # and epoxy batch data has been entered so disable batch input widget
            self.ui.epoxy_batch_4.setText(
                data[4]
            )  # the batch ID data must've been entered so set the batch input widget to data[4]

            elapsed_time, running = data[
                5
            ]  # data[5] is a timer tuple, (timedelta>, <bool>)
            self.timers[13].setElapsedTime(
                elapsed_time
            )  # timer 13 corresponds to the right pin application duration
            if running:  # if the timer is running
                self.startTimer(13)  # resume running timer 13
                self.ui.epoxyInjectedRP.setEnabled(
                    True
                )  # and enable the button that stops it
            else:  # if it's not running, it must be finished since there is recorded time for it
                self.ui.epoxyInjectedRP.setDisabled(
                    True
                )  # disable the button that stops it since it has already finished

            # if timer data for application timer exists, then data for cure time also exists, since they're started by the same button
            elapsed_time, running = data[
                6
            ]  # data [6] is a timer tuple, (<timedelta>, <bool>)
            self.timers[14].setElapsedTime(
                elapsed_time
            )  # timer 14 corresponds to the right pin cure duration
            if running:  # if the timer is running
                self.startTimer(14)  # resume running timer 14
                self.ui.epoxyFinishedRP.setEnabled(
                    True
                )  # and enable the button that stops it
            else:  # if it's not running, it must be finished since there is recorded time for it
                self.ui.epoxyFinishedRP.setDisabled(
                    True
                )  # disable the button that stops it since it has already finished
        elif (
            data[4] is not None
        ):  # ELSE if batch ID data for left pin exists (batch entered, not started)
            self.ui.epoxy_batch_4.setText(
                data[4]
            )  # set the batch input widget to data[4]
            self.ui.epoxyMixedRP.setEnabled(True)
        else:
            self.ui.epoxy_batch_4.setEnabled(True)
            self.ui.epoxyMixedRP.setEnabled(True)

        # LEFT OMEGA
        if data[8] is not None:  # if timer data for left omega application time exists
            self.ui.epoxyMixedLOP.setDisabled(
                True
            )  # the timer has been started so disable mixed button
            self.ui.epoxy_batch_5.setDisabled(
                True
            )  # and epoxy batch data has been entered so disable batch input widget
            self.ui.epoxy_batch_5.setText(
                data[7]
            )  # the batch ID data must've been entered so set the batch input widget to data[7]

            elapsed_time, running = data[
                8
            ]  # data[8] is a timer tuple, (timedelta>, <bool>)
            self.timers[15].setElapsedTime(
                elapsed_time
            )  # timer 15 corresponds to the left omega application duration
            if running:  # if the timer is running
                self.startTimer(15)  # resume running timer 15
                self.ui.epoxyAppliedLOP.setEnabled(
                    True
                )  # and enable the button that stops it
            else:  # if it's not running, it must be finished since there is recorded time for it
                self.ui.epoxyAppliedLOP.setDisabled(
                    True
                )  # disable the button that stops it since it has already finished

            # if timer data for application timer exists, then data for cure time also exists, since they're started by the same button
            elapsed_time, running = data[
                9
            ]  # data [9] is a timer tuple, (<timedelta>, <bool>)
            self.timers[16].setElapsedTime(
                elapsed_time
            )  # timer 16 corresponds to the left omega cure duration
            if running:  # if the timer is running
                self.startTimer(16)  # resume running timer 16
                self.ui.epoxyCuredLOP.setEnabled(
                    True
                )  # and enable the button that stops it
            else:  # if it's not running, it must be finished since there is recorded time for it
                self.ui.epoxyCuredLOP.setDisabled(
                    True
                )  # disable the button that stops it since it has already finished
        elif (
            data[7] is not None
        ):  # ELSE if batch ID data for left pin exists (batch entered, not started)
            self.ui.epoxy_batch_5.setText(
                data[1]
            )  # set the batch input widget to data[7]
            self.ui.epoxyMixedLOP.setEnabled(True)
        else:
            self.ui.epoxy_batch_5.setEnabled(True)
            self.ui.epoxyMixedLOP.setEnabled(True)

        # RIGHT OMEGA
        if (
            data[11] is not None
        ):  # if timer data for right omega application time exists
            self.ui.epoxyMixedROP.setDisabled(
                True
            )  # the timer has been started so disable mixed button
            self.ui.epoxy_batch_6.setDisabled(
                True
            )  # and epoxy batch data has been entered so disable batch input widget
            self.ui.epoxy_batch_6.setText(
                data[10]
            )  # the batch ID data must've been entered so set the batch input widget to data[10]

            elapsed_time, running = data[
                11
            ]  # data[11] is a timer tuple, (timedelta>, <bool>)
            self.timers[17].setElapsedTime(
                elapsed_time
            )  # timer 17 corresponds to the right omega application duration
            if running:  # if the timer is running
                self.startTimer(17)  # resume running timer 15
                self.ui.epoxyAppliedROP.setEnabled(
                    True
                )  # and enable the button that stops it
            else:  # if it's not running, it must be finished since there is recorded time for it
                self.ui.epoxyAppliedROP.setDisabled(
                    True
                )  # disable the button that stops it since it has already finished

            # if timer data for application timer exists, then data for cure time also exists, since they're started by the same button
            elapsed_time, running = data[
                12
            ]  # data [12] is a timer tuple, (<timedelta>, <bool>)
            self.timers[18].setElapsedTime(
                elapsed_time
            )  # timer 18 corresponds to the right omega cure duration
            if running:  # if the timer is running
                self.startTimer(18)  # resume running timer 18
                self.ui.epoxyCuredROP.setEnabled(
                    True
                )  # and enable the button that stops it
            else:  # if it's not running, it must be finished since there is recorded time for it
                self.ui.epoxyCuredROP.setDisabled(
                    True
                )  # disable the button that stops it since it has already finished
        elif (
            data[10] is not None
        ):  # ELSE if batch ID data for left pin exists (batch entered, not started)
            self.ui.epoxy_batch_6.setText(
                data[10]
            )  # set the batch input widget to data[10]
            self.ui.epoxyMixedROP.setEnabled(True)
        else:
            self.ui.epoxy_batch_6.setEnabled(True)
            self.ui.epoxyMixedROP.setEnabled(True)

    def parsePro5Data(self, data):
        # The start button is the first thing to (indirectly?) trigger this, and panel input
        # needs to have a valid panel before that can be pushed, so really there's nothing to parse!
        # So really all this does is validates the panel input and prints stuff if it's invalid
        if not self.validateInput(indices=[0]):
            print("\n\npro 5 PANEL INPUT VALIDATION FAILED\n\n")

    """
    parsepro4Data(self, data)

        Description: Given the loaded data, sets the appropriate UI elements with that data. Also handles the enabling/disabling of
                    UI elements to ensure the GUI state is consistent with normal use.

        Parameter: data - A list of the parsed input data
    """

    def parsepro6Data(self, data):
        if data[0] is not None:
            self.ui.panelInput6.setText(data[0])
            self.ui.panelInput6.setDisabled(True)
            self.ui.epoxy_mixed41.setDisabled(False)
            self.ui.epoxy_batch41.setDisabled(False)
            self.ui.bpmirgapL.setDisabled(False)
            self.ui.bpmirgapR.setDisabled(False)
        if data[1] is not None:
            self.ui.frameInput.setText(data[1])
            self.ui.frameInput.setDisabled(True)
        if data[2] is not None:
            self.ui.mrInput1.setText(data[2])
            self.ui.mrInput1.setDisabled(True)
        if data[3] is not None:
            self.ui.mrInput2.setText(data[3])
            self.ui.mrInput2.setDisabled(True)
        if data[4] is not None:
            self.ui.bpmirgapL.setCurrentIndex(int(data[4]))
        if data[5] is not None:
            self.ui.bpmirgapR.setCurrentIndex(int(data[5]))
        if data[6] is not None:
            self.ui.epoxy_batch41.setText(data[6])
        if data[7] is not None:
            self.ui.bpmirgapL.setDisabled(True)
            self.ui.bpmirgapR.setDisabled(True)
            self.ui.epoxy_mixed41.setDisabled(True)
            self.ui.epoxy_applied41.setDisabled(False)

            # Process timer
            try:
                elapsed_time, running = data[7]
            except:
                data[7] = (self.timers[6].getElapsedTime(), self.timers[6].isRunning())
                elapsed_time, running = data[7]
                self.generateBox(
                    "critical",
                    "Data Processor Error",
                    "SQL Processor inactive, BP/IR epoxy timer may not function.",
                )
            self.timers[6].setElapsedTime(elapsed_time)
            if running:
                self.startTimer(6)
            else:
                self.ui.epoxy_applied41.setDisabled(True)
                self.ui.epoxy_mixed42.setDisabled(False)
                self.ui.epoxy_batch42.setDisabled(False)
        if data[8] is not None:
            self.ui.epoxy_batch42.setText(data[8])
        if data[9] is not None:
            self.ui.epoxy_batch42_2.setText(data[9])
        if data[10] is not None:
            self.ui.epoxy_batch42.setDisabled(True)
            self.ui.epoxy_batch42_2.setDisabled(True)
            self.ui.epoxy_mixed42.setDisabled(True)

            # Process timer
            try:
                elapsed_time, running = data[10]
            except:
                data[10] = (self.timers[7].getElapsedTime(), self.timers[7].isRunning())
                elapsed_time, running = data[10]
                self.generateBox(
                    "critical",
                    "Data Processor Error",
                    "SQL Processor inactive, Frame epoxy timer may not function.",
                )
            self.timers[7].setElapsedTime(elapsed_time)
            if running:
                self.startTimer(7)
                self.ui.epoxy_applied42.setDisabled(False)
            else:
                self.ui.epoxy_applied42.setDisabled(True)
                self.ui.heat_start4.setDisabled(False)
        if data[11] is not None:
            self.ui.temp4_4.setText(str(data[11]))
        if data[12] is not None:
            self.ui.temp4_5.setText(str(data[12]))
        if data[13] is not None:
            self.ui.heat_start4.setDisabled(True)
            self.ui.heat_finished4.setDisabled(False)
            self.ui.temp4_4.setDisabled(False)
            self.ui.temp4_5.setDisabled(False)

            # Process timer
            try:
                elapsed_time, running = data[13]
            except:
                data[13] = (self.timers[8].getElapsedTime(), self.timers[8].isRunning())
                elapsed_time, running = data[13]
                self.generateBox(
                    "critical",
                    "Data Processor Error",
                    "SQL Processor inactive, heating timer may not function.",
                )
            self.timers[8].setElapsedTime(elapsed_time)
            if running:
                self.startTimer(8)
            else:
                self.ui.heat_finished4.setDisabled(True)
                self.ui.temp4_4.setDisabled(True)
                self.ui.temp4_5.setDisabled(True)

    """
    parsepro7Data(self, data)

        Description: Given the loaded data, sets the appropriate UI elements with that data. Also handles the enabling/disabling of
                    UI elements to ensure the GUI state is consistent with normal use.

        Parameter: data - A list of the parsed input data
    """

    def parsepro7Data(self, data):
        # print("data passed to parsepro7Data is", data)
        # if data[0] is not None:
        #     self.ui.panelInput7.setText(str(data[0]))

        ## Note from Billy
        ## The pro7loadData function return a list of size 4
        ## The original design for parsepro7Data requires a list of size 5
        ## Change my code if you need
        if data[0] is not None:
            self.ui.panelInput7.setText(str(data[0]))
            self.ui.panelInput7.setDisabled(True)
            self.ui.epoxy_batch5_2.setDisabled(False)
            self.ui.epoxy_batch5_3.setDisabled(False)
            self.ui.epoxy_mixed5_2.setDisabled(False)
            self.ui.epoxy_mixed5_3.setDisabled(False)
        # if data[1] is not None:
        #     self.ui.epoxy_batch5_2.setText(str(data[1]))

        # if data[2] is not None:
        #     self.ui.epoxy_batch5_2.setDisabled(True)

        #     # Process timer
        #     elapsed_time, running = data[2]
        #     self.timers[9].setElapsedTime(elapsed_time)
        #     if running:
        #         self.startTimer(9)
        #         self.ui.epoxy_applied5_2.setDisabled(False)
        #     else:
        #         self.ui.epoxy_applied5_2.setDisabled(True)

        if data[1] is not None:
            self.ui.epoxy_batch5_2.setText(str(data[1]))

        if data[2] is not None:
            self.ui.epoxy_batch5_2.setDisabled(True)

            # Process timer
            elapsed_time, running = data[2]
            self.timers[9].setElapsedTime(elapsed_time)
            if running:
                self.startTimer(9)
                self.ui.epoxy_applied5_2.setDisabled(False)
            else:
                self.ui.epoxy_applied5_2.setDisabled(True)

        if data[3] is not None:
            self.ui.epoxy_batch5_3.setText(str(data[3]))

        if data[4] is not None:
            self.ui.epoxy_batch5_3.setDisabled(True)
            # print("data[4] is not None")

            # Process timer
            elapsed_time, running = data[4]
            self.timers[10].setElapsedTime(elapsed_time)
            if running:
                self.startTimer(10)
                self.ui.epoxy_applied5_3.setDisabled(False)
            else:
                self.ui.epoxy_applied5_3.setDisabled(True)

    ###  ____                 ___
    ### |  _ \  __ _ _   _   / _ \ _ __   ___
    ### | | | |/ _` | | | | | | | | '_ \ / _ \
    ### | |_| | (_| | |_| | | |_| | | | |  __/
    ### |____/ \__,_|\__, |  \___/|_| |_|\___|
    ###              |___/

    """
    pro1Part1(self)

        Description: The function called when the pro 1 start button is clicked. Validates barcode input, and checks if supplies list is checked
                 off. The main timer is also started if everything is correct.

        Disables: Barcode Inputs
                  Start Button

        Enables: First Step Checkbox
                 Gap Measurement Drop Down Menus
                
    """

    def pro1part1(self):
        # print("pro 1 PART 1")

        # Ensure that all parts have been checked off
        if not (self.checkSupplies() or DEBUG):
            return

        # Ensure that all input data is valid
        if not self.validateInput(indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 17, 18]):
            return

        # (Dis/En)able widgets
        self.setWidgetsDisabled(
            [
                # Start Button, Panel Input
                self.ui.startbutton1,
                self.ui.panelInput1,
                # All parts input
                self.ui.baseInput1,
                self.ui.birInput,
                self.ui.pirInputLA,
                self.ui.pirInputLB,
                self.ui.pirInputLC,
                self.ui.pirInputRA,
                self.ui.pirInputRB,
                self.ui.pirInputRC,
                self.ui.mirInput,
                self.ui.alfInput,
                self.ui.alfInput_2,
                self.ui.paasAInput,
                self.ui.paasCInput,
            ]
        )
        self.setWidgetsEnabled(
            [
                # Gaps Measurements
                self.ui.leftgap,
                self.ui.rightgap,
                self.ui.mingap,
                self.ui.maxgap,
                # Epoxy entry and button
                self.ui.epoxy_batch1,
                self.ui.epoxy_mixed1,
                self.ui.pallet1code,
                self.ui.pallet2code
            ]
        )
        
        # LPAL not yet validated
        self.data[0][22] = False

        # Start Running
        self.startRunning()

    """
    pro1part2(self)

        Description: The function called when the 'Epoxy Mixed' button is pressed. This function checks that an epoxy batch, and all gap measurements
                 have been input, as well as that the correct steps have been checked off. Starts the timer thread for the pro 1 epoxy timer.

        Disables: Epoxy Batch
                  Epoxy Mixed Button

        Enables: Epoxy Applied Button
    """

    def pro1part2(self):
        if not self.validateInput(indices=range(16)):
            return

        # (En/Dis)able Stuff
        self.setWidgetsDisabled([self.ui.epoxy_batch1, self.ui.epoxy_mixed1])
        self.ui.epoxy_applied1.setEnabled(True)

        # Start Timers
        self.startTimer(1)

        # Save data
        self.saveData()

    """
    pro1CheckEpoxySteps(self)

        Description: Function called when 'Masking Removed' button is pressed. This function checks to make sure the appropriate steps
                 have been checked off. If they have, the epoxy timer is ended.

        Disables: Epoxy Applied Button
    """

    def pro1CheckEpoxySteps(self):
        # Stop timer
        self.timers[1].stop()
        self.ui.epoxy_applied1.setDisabled(True)

        # Save with data processor
        self.saveData()

    # Validate LPALs
    def checkLPALs(self):
        if not self.validateInput(indices=[19,20]):
            return
        self.ui.lpalLabel.setText("Straws Validated.")
        print(self.data)
        print(len(self.data[0]))
        self.data[0][22] = True

        if self.stepsList.allStepsChecked():
            self.finishButton.setText("Finish")
        
        self.saveData()



    """
    resetpro1(self)

        Description: The function to reset all pro 1 data and UI elements to the state before pro 1 is started.

        Disables: Finish Button
                  Checkboxes
                  
        Enables: Start Button
                 Barcode Inputs
    """

    def resetpro1(self):
        self.data[0] = [None for x in self.data[0]]

        # Reset input widgets (panel input, parts input, epoxy_input)
        input_widgets = [
            self.ui.panelInput1,
            self.ui.baseInput1,
            self.ui.birInput,
            self.ui.pirInputLA,
            self.ui.pirInputLB,
            self.ui.pirInputLC,
            self.ui.pirInputRA,
            self.ui.pirInputRB,
            self.ui.pirInputRC,
            self.ui.mirInput,
            self.ui.alfInput,
            self.ui.epoxy_batch1,
            self.ui.paasAInput,
            self.ui.paasCInput,
            self.ui.pallet1code,
            self.ui.pallet2code
        ]
        self.setWidgetsEnabled(input_widgets)
        for w in input_widgets:
            w.setText("")

        # Enable start button
        self.ui.startbutton1.setEnabled(True)

        # Reset gap measurements
        self.ui.leftgap.setCurrentIndex(0)
        self.ui.rightgap.setCurrentIndex(0)
        self.ui.mingap.setCurrentIndex(0)
        self.ui.maxgap.setCurrentIndex(0)

        # Reset comment box text
        self.ui.commentBox1.document().setPlainText("")
        self.ui.previousComments.document().setPlainText("")

        # Reset time display
        self.timers[1].reset()

    ###  ____                _____
    ### |  _ \  __ _ _   _  |_   _|_      _____
    ### | | | |/ _` | | | |   | | \ \ /\ / / _ \
    ### | |_| | (_| | |_| |   | |  \ V  V / (_) |
    ### |____/ \__,_|\__, |   |_|   \_/\_/ \___/
    ###              |___/

    """
    pro2part1(self)

        Description: The function called when the pro 2 start button is pressed. Validates that a panel number has been supplied, as well as
                 loading pallet numbers, and that the supplies list has been checked off. Starts the main timer.

        Disables: Panel Number Input
                  Loading Pallet Inputs

        Enables: First Step Checkbox
                 Epoxy Batches
                 Epoxy Mixed Buttons
    """

    def pro2part1(self):
        # print("pro 2 PART 1")

        # Ensure supplies checked off
        if not (self.checkSupplies() or DEBUG):
            return

        # Ensure valid input
        if not self.validateInput(indices=range(1)):
            return

        # Set focus on epoxy input
        self.ui.epoxy_batch.setFocus()

        # Disable panel and LPAl inputs and start button
        self.setWidgetsDisabled(
            [
                self.ui.startbutton2,
                self.ui.panelInput2
            ]
        )

        # Enable widgets
        self.setWidgetsEnabled(
            [
                self.ui.epoxy_batch,  # Epoxy input
                self.ui.epoxy_mixed,  # Epoxy button
                self.ui.epoxy_batch_2,  # Epoxy input (top)
                self.ui.epoxy_mixed_2,  # Epoxy mixed button (top)
                self.ui.launch_straw_tensioner,  # Straw tensioner button
                self.ui.paasBInput,  # PAAS B line edit
            ]
        )

        # Start running
        self.startRunning()

    """
    pro2part2(self)

        Description: The function called by clicking the first 'Epoxy Mixed' button. If there is an epoxy batch,
                    the timer for epoxying is started, otherwise the batch is highlighted.

        Disables: Epoxy Mixed Button 1

        Enables: Epoxy Injected Button 1
    """

    def pro2part2(self):
        # Ensure valid input
        if not self.validateInput(indices=[3]):
            return

        # (Dis/En)able widgets
        self.ui.epoxy_mixed.setDisabled(True)
        self.ui.epoxy_inject1.setEnabled(True)

        # Reset stylesheet
        self.ui.epoxy_batch.setStyleSheet("")

        # Start timer
        self.startTimer(2)
        if self.timers[2].getElapsedTime == 1800:
            self.generateBox(
                "critical", "Epoxy Timer at 30 minutes", "Rotate straws into alignment."
            )
        if self.timers[2].getElapsedTime == 3600:
            self.generateBox(
                "critical", "Epoxy Timer at 1 hour", "Rotate straws into alignment."
            )
        if self.timers[2].getElapsedTime == 5400:
            self.generateBox(
                "critical",
                "Epoxy Timer at 1 hour 30 minutes",
                "Rotate straws into alignment.",
            )

        # Save data
        self.saveData()

    """
    pro2part2_2(self)

        Description: The function called by the second 'Epoxy Mixed' button. Validates the second epoxy batch number, and
                 starts the second epoxy timer thread.

        Disables: Epoxy Batch Input 2
                  Epoxy Mixed Button 2

        Enables: Epoxy Injected Button 2
    """

    def pro2part2_2(self):
        # Ensure valid input
        if not self.validateInput(indices=[5]):
            return False

        # Reset style sheet
        self.ui.epoxy_batch_2.setStyleSheet("")

        # (Dis/En)able epoxy inputs and buttons
        self.ui.epoxy_mixed_2.setDisabled(True)
        self.ui.epoxy_batch_2.setDisabled(True)
        self.ui.epoxy_inject2.setEnabled(True)

        # Start timers
        self.startTimer(3)

        # Save data
        self.saveData()

    """
    pro2part2_3(self)

        Description: Function called by clicking the second 'Epoxy Injected' button.

        Disables: Epoxy Injected Button 2

        Enables: Heat Start Button
    """

    def pro2part2_3(self):

        # Stop the timer
        self.stopTimer(3)

        # (Dis/En)able widgets
        self.ui.epoxy_inject2.setDisabled(True)
        self.ui.heat_start.setEnabled(True)

        # Save data
        self.saveData()

    """
    pro2part2_4(self)

        Description: Function called by the 'Heat Finished' button. Records the maximum temperatures and heating time.

        Disables: PAAS-A Max Temp Input
                  PAAS-B Max Temp Input
                  Heat Finished Button
    """

    def pro2part2_4(self):

        # Reset stylesheets of temperature inputs
        self.ui.temp4.setStyleSheet("")
        self.ui.temp4_2.setStyleSheet("")

        # Disable heat widgets
        self.setWidgetsDisabled([self.ui.heat_finished, self.ui.temp4, self.ui.temp4_2])

        # Focus on comment box
        self.ui.commentBox2.setFocus()

        # Save data
        self.saveData()

    """
    pro2EpoxyInjected(self)

        Description: Function called by clicking first 'Epoxy Injected' button.

        Disables: Epoxy Injected Button 1

        Enables: Epoxy Batch Input 2
                 Epoxy Mixed Button 2
    """

    def pro2EpoxyInjected(self):
        # stop the corresponding timer
        self.stopTimer(2)
        # Disable first epoxy button
        self.ui.epoxy_inject1.setDisabled(True)
        # Enable next input and button and set focus
        self.ui.epoxy_mixed_2.setEnabled(True)
        self.ui.epoxy_batch_2.setEnabled(True)
        self.ui.epoxy_batch_2.setFocus()
        self.saveData()

    """
    pro2Heating(self)

        Description: Function called by clicking 'Heat Start' button. Starts the pro 2 heating timer thread.

        Disables: Heat Start Button

        Enables: Heat Finished Button
                 PAAS-A Max Temp Input
                 PAAS-B Max Temp Input
    """

    def pro2Heating(self):
        # Disable start heat button
        self.ui.heat_start.setDisabled(True)

        # Enable temperature inputs and stop heating button
        self.setWidgetsEnabled([self.ui.heat_finished, self.ui.temp4, self.ui.temp4_2])
        self.ui.temp4.setFocus()

        # Start Timer
        self.startTimer(4)

    def pro2CheckTemp(self):
        if self.validateInput(indices=[7, 8]):
            self.stopTimer(4)
            self.pro2part2_4()

    """
    resetpro2(self)

        Description: The function to reset the pro 2 data and UI elements to the state before pro 2 was started.

        Disables: Finish Button
                  Checkboxes

        Enables: Panel Number Input
                 Loading Pallet Inputs
    """

    def resetpro2(self):
        self.data[1] = [None for x in self.data[1]]
        self.ui.startbutton2.setEnabled(True)
        self.ui.panelInput2.setEnabled(True)
        self.ui.panelInput2.setText("")
        self.ui.pallet1code.setText("")
        self.ui.pallet2code.setText("")
        self.ui.paasBInput.setText("")
        self.ui.epoxy_batch.setText("")
        self.ui.epoxy_batch_2.setText("")
        self.ui.temp4.setText("")
        self.ui.temp4_2.setText("")
        self.ui.commentBox2.document().setPlainText("")
        for timer in self.timers[2:5]:
            timer.reset()

    ###  ____                _____ _
    ### |  _ \  __ _ _   _  |_   _| |__  _ __ ___  ___
    ### | | | |/ _` | | | |   | | | '_ \| '__/ _ \/ _ \
    ### | |_| | (_| | |_| |   | | | | | | | |  __/  __/
    ### |____/ \__,_|\__, |   |_| |_| |_|_|  \___|\___|
    ###              |___/

    """
    pro3part1(self)

        Description: Function called by Start Button. Validates the Panel Number Input and Wire Input, while also checking that the supplies
                 list is checked off. Starts both the main timer, and the wire insertion timer.

        Disables: Panel Number Input
                  Wire Input
                  Start Button

        Enables: First Step Checkbox
                 Continuity Comboboxes
                 Wire Position Comboboxes
                 Wire Resistance Comboboxes
    """

    def pro3part1(self):
        # print("pro 3 PART 1")

        # Ensure that all parts have been checked off
        if not (self.checkSupplies() or DEBUG):
            return

        # Ensure that panel number is valid
        if not self.validateInput(indices=[0]):
            return

        # old verification for wire input, didn't just delete, since we may want to move it.
        # in addition to this you need to put 1 into the indicies for validate input above here.
        """
        # Verify that wire has been QCd with DataProcessor
        wire = self.ui.wireInput.text()
        if not self.DP.wireQCd(wire):
            self.generateBox('critical', 'Wire Input Invalid', 'Sense wire spool not yet QCd')
            return
        """

        # If all tests pass, continue

        # Disable start button, panel input, and wire input, and don't let user input calibration factor
        self.ui.panelInput3_2.setText("")
        self.ui.panelInput3_2.setDisabled(True)
        # panelInput3_2 is the calibration factor display line.  Should be renamed later.
        self.setWidgetsDisabled(
            [self.ui.startbutton3, self.ui.panelInput3, self.ui.wireInput]
        )

        # Enable wire tensioner button
        self.setWidgetsEnabled([self.ui.launch_wire_tensioner])

        # Enable all widgets in the continuity table
        self.setWidgetsEnabled(self.continuity + self.wire_pos)

        # Start timers
        self.startRunning()
        self.startTimer(5)

        # Save data
        self.saveData()

    """
    resetpro3(self)

        Description: Function that resets the pro 3 data list and UI elements to the state before the pro began.

        Disables: Continuity Comboboxes
                  Wire Position Comboboxes
                  Wire Resistance Comboboxes
    """

    def resetpro3(self):
        self.data[2] = [None for x in self.data[2]]
        self.ui.panelInput3.setEnabled(True)
        self.ui.wireInput.setEnabled(True)
        self.ui.startbutton3.setEnabled(True)
        self.ui.commentBox3.document().setPlainText("")
        self.ui.panelInput3.setText("")
        self.ui.wireInput.setText("")
        self.timers[5].reset()
        for i in range(len(self.continuity)):
            self.continuity[i].setCurrentIndex(0)
            self.wire_pos[i].setCurrentIndex(0)

        list(map(lambda obj: obj.setDisabled(True), self.continuity))
        list(map(lambda obj: obj.setDisabled(True), self.wire_pos))

    ###   ____              _____
    ###  |  _ \ _ __ ___   |  ___|__  _   _ _ __
    ###  | |_) | '__/ _ \  | |_ / _ \| | | | '__|
    ###  |  __/| | | (_) | |  _| (_) | |_| | |
    ###  |_|   |_|  \___/  |_|  \___/ \__,_|_|
    ###

    def pro4part0(self):
        # Ensure that all inputs are valid
        # indicies is the location of the data you want checked in the list of user input stuff
        if not self.validateInput(indices=[0]):
            return

        self.setWidgetsEnabled(
            [
                self.ui.panelInput4,
                self.ui.epoxy_batch_3,
                self.ui.epoxy_batch_4,
                self.ui.epoxy_batch_5,
                self.ui.epoxy_batch_6,
                self.ui.epoxyMixedLP,
                self.ui.epoxyMixedRP,
            ]
        )

        self.setWidgetsDisabled(
            [
                self.ui.epoxyInjectedLP,
                self.ui.epoxyInjectedRP,
                self.ui.epoxyFinishedLP,
                self.ui.epoxyFinishedRP,
                self.ui.epoxyAppliedLOP,
                self.ui.epoxyAppliedROP,
                self.ui.startButton4,
                self.ui.epoxyCuredLOP,
                self.ui.epoxyCuredROP,
            ]
        )

        self.ui.epoxyMixedLOP.setEnabled(True)
        self.ui.epoxyMixedROP.setEnabled(True)
        self.ui.commentBox2.setFocus()

        self.startRunning()
        self.saveData()

    # connected to epoxy mixed for LP, starts timer 11
    def mixEpoxyLPP(self):
        if not self.validateInput(indices=[1]):
            print("Validation Failed")
            return

        self.startTimer(11)
        self.startTimer(12)
        self.ui.epoxyMixedLP.setDisabled(True)
        self.ui.epoxy_batch_3.setDisabled(True)
        self.ui.epoxyInjectedLP.setEnabled(True)
        self.saveData()
        self.ui.commentBox2.setFocus()

    # connected to epoxy mixed for RP, starts timer 13
    # INDEX 4 POINTS TO ROP BATCH
    def mixEpoxyRPP(self):
        if not (self.validateInput(indices=[2])):
            print("Validation Failed")
            return
        self.startTimer(13)
        self.startTimer(14)
        self.ui.epoxyMixedRP.setDisabled(True)
        self.ui.epoxy_batch_4.setDisabled(True)
        self.ui.epoxyInjectedRP.setEnabled(True)
        self.saveData()
        self.ui.commentBox2.setFocus()

    def applyEpoxyLPP(self):
        self.stopTimer(11)
        self.ui.epoxyInjectedLP.setDisabled(True)
        self.ui.epoxyFinishedLP.setEnabled(True)
        self.saveData()
        self.ui.commentBox2.setFocus()

    def applyEpoxyRPP(self):
        self.stopTimer(13)
        self.ui.epoxyInjectedRP.setDisabled(True)
        self.ui.epoxyFinishedRP.setEnabled(True)
        self.saveData()
        self.ui.commentBox2.setFocus()

    def cureEpoxyLPP(self):
        self.stopTimer(12)
        self.ui.epoxyFinishedLP.setDisabled(True)
        self.saveData()
        self.ui.commentBox2.setFocus()

    def cureEpoxyRPP(self):
        self.stopTimer(14)
        self.ui.epoxyFinishedRP.setDisabled(True)
        self.saveData()
        self.ui.commentBox2.setFocus()

    def mixEpoxyLOP(self):
        if not (self.validateInput(indices=[3])):
            print("Validation Failed")
            return
        self.startTimer(15)
        self.startTimer(17)
        self.ui.epoxyMixedLOP.setDisabled(True)
        self.ui.epoxy_batch_5.setDisabled(True)
        self.ui.epoxyAppliedLOP.setEnabled(True)
        self.saveData()
        self.ui.commentBox2.setFocus()

    def mixEpoxyROP(self):
        if not (self.validateInput(indices=[4])):
            print("Validation Failed")
            return
        self.startTimer(16)
        self.startTimer(18)
        self.ui.epoxyMixedROP.setDisabled(True)
        self.ui.epoxy_batch_6.setDisabled(True)
        self.ui.epoxyAppliedROP.setEnabled(True)
        self.saveData()
        self.ui.commentBox2.setFocus()

    def applyEpoxyLOP(self):
        self.stopTimer(15)
        self.ui.epoxyAppliedLOP.setDisabled(True)
        self.ui.epoxyCuredLOP.setEnabled(True)
        self.saveData()
        self.ui.commentBox2.setFocus()

    def applyEpoxyROP(self):
        self.stopTimer(16)
        self.ui.epoxyAppliedROP.setDisabled(True)
        self.ui.epoxyCuredROP.setEnabled(True)
        self.saveData()
        self.ui.commentBox2.setFocus()

    def cureEpoxyLOP(self):
        self.stopTimer(17)
        self.ui.epoxyCuredLOP.setDisabled(True)
        self.saveData()

    def cureEpoxyROP(self):
        self.stopTimer(18)
        self.ui.epoxyCuredROP.setDisabled(True)
        self.saveData()
        self.ui.commentBox2.setFocus()

    def resetPro4(self):
        self.ui.panelInput4.setText("")
        self.ui.epoxy_batch_3.setText("")
        self.ui.epoxy_batch_4.setText("")
        self.ui.epoxy_batch_5.setText("")
        self.ui.epoxy_batch_6.setText("")
        self.timers[11].reset()
        self.timers[12].reset()
        self.timers[13].reset()
        self.timers[14].reset()
        self.timers[15].reset()
        self.timers[16].reset()
        self.timers[17].reset()
        self.timers[18].reset()

    ###   ____              _____ _
    ###  |  _ \ _ __ ___   |  ___(_)_   _____
    ###  | |_) | '__/ _ \  | |_  | \ \ / / _ \
    ###  |  __/| | | (_) | |  _| | |\ V /  __/
    ###  |_|   |_|  \___/  |_|   |_| \_/ \___|
    ###
    # Very little to do here.
    def pro5part0(self):
        if not self.validateInput(indices=[0]):
            print("Validation Failed")
            return
        self.startRunning()
        self.saveData()

    def resetPro5(self):
        self.ui.panelInput5.setText("")

    ###   ____                ____  _
    ###  |  _ \  __ _ _   _  / ___|(_)_  __
    ###  | | | |/ _` | | | | \___ \| \ \/ /
    ###  | |_| | (_| | |_| |  ___) | |>  <
    ###  |____/ \__,_|\__, | |____/|_/_/\_\
    ###               |___/
    """
    pro6part1(self)

        Description: Function called by Start Button. Validates the Panel Number Input, and checks that the supplies list has been checked off.
                 Starts the main timer.

        Disables: Panel Number Input
                  Start Button

        Enables: Epoxy Batch 1
                 Epoxy Mixed Button 1
                 Gap Measurement Drop Down Menus
    """

    def pro6part1(self):

        # Ensure that all parts have been checked off
        if not (self.checkSupplies() or DEBUG):
            return

        # Ensure that all input data is valid
        if not self.validateInput(indices=range(4)):
            return

        # Disable start button, panel input, and part inputs
        self.setWidgetsEnabled(
            [
                self.ui.startButton6,
                self.ui.panelInput4,
                self.ui.frameInput,
                self.ui.mrInput1,
                self.ui.mrInput2,
            ]
        )

        # Enable Epoxy and gap measurements
        self.setWidgetsEnabled(
            [
                self.ui.epoxy_batch41,
                self.ui.epoxy_mixed41,
                self.ui.bpmirgapL,
                self.ui.bpmirgapR,
            ]
        )

        # Start main timer
        self.startRunning()
        self.saveData()

    """
    pro6part2(self)

        Description: Function called when 'Epoxy Mixed' button 1 is clicked. Validates Epoxy Input 1, and starts epoxy timer 1.

        Disables: Gap Measurment Drop Down Menus
                  Epoxy Batch Input 1
                  Epoxy Mixed Button 1

        Enables: Epoxy Applied Button 1
    """

    def pro6part2(self):
        # Check valid input
        if not self.validateInput(indices=range(4, 7)):
            return

        # Disable previous widgets
        self.setWidgetsDisabled(
            [
                self.ui.bpmirgapL,
                self.ui.bpmirgapR,
                self.ui.epoxy_batch41,
                self.ui.epoxy_mixed41,
            ]
        )

        # Enable stop epoxy button
        self.ui.epoxy_applied41.setEnabled(True)

        # Start timer
        self.startTimer(6)

        # Save data
        self.saveData()

    """
    pro6part2_2(self)

        Description: Function called when Epoxy Applied Button 1 is clicked. Records the elapsed time of the the first epoxy session.

        Disables: Epoxy Applied Button 1

        Enables: Epoxy Mixed Button 2
                 Epoxy Batch Inputs 2 and 3
    """

    def pro6part2_2(self):

        self.stopTimer(6)

        # Disable
        self.ui.epoxy_applied41.setDisabled(True)

        # Enable
        self.setWidgetsEnabled(
            [self.ui.epoxy_mixed42, self.ui.epoxy_batch42, self.ui.epoxy_batch42_2]
        )

        # Save data
        self.saveData()

    """
    pro6part3(self)

        Description: Function called when Epoxy Mixed Button 2 is clicked. Validates Epoxy Batch Inputs 2 and 3, and starts the second pro 4
                 epoxy timer.

        Disables: Epoxy Batch Inputs 2 and 3
                  Epoxy Mixed Button 2
        
        Enables: Epoxy Applied Button 2
    """

    def pro6part3(self):
        # Verify input
        if not self.validateInput(indices=[8, 9]):
            return

        # Enable
        self.ui.epoxy_applied42.setEnabled(True)

        # Disable
        self.setWidgetsDisabled(
            [self.ui.epoxy_batch42, self.ui.epoxy_batch42_2, self.ui.epoxy_mixed42]
        )

        # Start Timer
        self.startTimer(7)

        # Save data
        self.saveData()

    """
    pro6part3_2(self)

        Description: Function called when Epoxy Applied Button 2 is clicked. Records the elapsed time for pro 4 epoxy session 2.

        Disables: Epoxy Applied Button 2

        Enables: Heat Start Button
    """

    def pro6part3_2(self):
        # Stop the timer
        self.stopTimer(7)
        # Enable/Disable
        self.ui.epoxy_applied42.setDisabled(True)
        self.ui.heat_start4.setEnabled(True)

        # Save data
        self.saveData()

    """
    pro6part4(self)

        Description: Function called when Heat Start Button is clicked. Starts the heating timer thread.

        Disables: Heat Start Button

        Enables: Heat Finished Button
                 PAAS-A Max Temp Input
                 PAAS-C Max Temp Input
    """

    def pro6part4(self):

        self.ui.heat_start4.setDisabled(True)

        # Enable heat widgets
        self.setWidgetsEnabled(
            [self.ui.heat_finished4, self.ui.temp4_4, self.ui.temp4_5]
        )

        # Start timer
        self.startTimer(8)

    """
    pro6part4_2(self)

        Description: Function that ends the heating timer and records the max temperatures.

        Disables: Heat Finished Button
                  PAAS-A Max Temp Input
                  PAAS-C Max Temp Input
    """

    def pro6part4_2(self):

        # Disable widgets
        self.setWidgetsDisabled(
            [self.ui.temp4_4, self.ui.temp4_5, self.ui.heat_finished4]
        )

        # Save data
        self.saveData()

    """
    pro6CheckTemp(self)

        Description: Function called when Heat Finished Button is clicked. Checkes that something has been entered into the temperature input boxes (line edits).
                 If not, highlights the boxes with no text input.
    """

    def pro6CheckTemp(self):
        if self.validateInput(indices=[11, 12]):
            self.stopTimer(8)
            self.pro6part4_2()

    """
    resetpro6(self)

        Description: Resets the data and UI elements for pro 4 to how they were before the pro began.

        Disables: Finish Button
                  Steps Checkboxes

        Enables: Gap Measurement Drop Down Menus
                 Start Button
                 Panel Number Input
                 Frame Number Input
                 Middle Rib Number Inputs
    """

    def resetpro6(self):
        self.data[3] = [None for x in self.data[3]]
        self.ui.panelInput6.setText("")
        self.ui.bpmirgapL.setCurrentIndex(0)
        self.ui.bpmirgapR.setCurrentIndex(0)
        self.ui.epoxy_batch41.setText("")
        self.ui.epoxy_batch42.setText("")
        self.ui.epoxy_batch42_2.setText("")
        self.ui.temp4_4.setText("")
        self.ui.temp4_5.setText("")
        self.ui.frameInput.setText("")
        self.ui.mrInput1.setText("")
        self.ui.mrInput2.setText("")
        for timer in self.timers[6:9]:
            timer.reset()
        self.ui.commentBox4.document().setPlainText("")
        self.ui.bpmirgapL.setEnabled(True)
        self.ui.bpmirgapR.setEnabled(True)
        self.ui.startButton6.setEnabled(True)
        self.ui.panelInput4.setEnabled(True)
        self.ui.frameInput.setDisabled(False)
        self.ui.mrInput1.setDisabled(False)
        self.ui.mrInput2.setDisabled(False)

    ###   ____                ____
    ###  |  _ \  __ _ _   _  / ___|  _____   _____ _ __
    ###  | | | |/ _` | | | | \___ \ / _ \ \ / / _ \ '_ \
    ###  | |_| | (_| | |_| |  ___) |  __/\ V /  __/ | | |
    ###  |____/ \__,_|\__, | |____/ \___| \_/ \___|_| |_|
    ###               |___/

    """
    pro7part1(self)

        Description: Function called when Start Button is clicked. Validates that all supplies have been checked off, and that a valid panel 
                 number has been input. If so, the pro begins. Otherwise, highlights prerequisite steps before pro begins.
        
        Disables: Start Button
                  Panel Number Input

        Enables: Epoxy Mixed Buttons
                 Epoxy Batch Inputs
                 Step 1 Checkbox
    """

    def pro7part1(self):

        # Ensure that all parts have been checked off
        if not (self.checkSupplies() or DEBUG):
            return

        # Ensure that all input data is valid
        if not self.validateInput(indices=[0]):
            return

        # Enable
        self.setWidgetsEnabled(
            [
                self.ui.epoxy_mixed5_2,
                self.ui.epoxy_batch5_2,
                self.ui.epoxy_mixed5_3,
                self.ui.epoxy_batch5_3,
            ]
        )

        # Disable
        self.setWidgetsDisabled([self.ui.startButton7, self.ui.panelInput7])

        # Start timer
        self.startRunning()

    """
    pro7part2(self)

        Description: Function called when Epoxy Mixed Button (Left) clicked. Validates the epoxy batch, and then starts the 
                 epoxy timer thread for left side flooding.

        Disables: Epoxy Batch Input (Left)
                  Epoxy Mixed Button (Left)

        Enables: Epoxy Applied Button (Left)
    """

    def pro7part2(self):

        # Verify input
        if not self.validateInput(indices=[1]):
            return

        # Disable
        self.setWidgetsEnabled([self.ui.epoxy_batch5_2, self.ui.epoxy_mixed5_2])

        # Enable
        self.ui.epoxy_applied5_2.setEnabled(True)

        # Start timer
        self.startTimer(9)

        # Save data
        self.saveData()

    """
    pro7part2_2(self)

        Description: Function called when Epoxy Applied Button (Left) is pressed. Ends epoxy fill timer for left side.
        
        Disables: Epoxy Applied Button (Left)
    """

    def pro7part2_2(self):
        self.stopTimer(9)
        # Disable widget
        self.ui.epoxy_applied5_2.setDisabled(True)
        self.ui.epoxy_batch5_3.setEnabled(True)
        self.saveData()

    """
    pro7part3(self)

        Description: Function called when Epoxy Mixed Button (Right) is pressed. Validates epoxy batch input, then
                 starts the epoxy fill timer for the right side.
        
        Disables: Epoxy Batch Input (Right)
                  Epoxy Mixed Button (Right)

        Enables: Epoxy Applied Button (Right)
    """

    def pro7part3(self):

        # Validate input
        if not self.validateInput(indices=[3]):
            return

        # (Dis/En)able widgets
        self.ui.epoxy_batch5_3.setDisabled(True)
        self.ui.epoxy_mixed5_3.setDisabled(True)
        self.ui.epoxy_applied5_3.setEnabled(True)

        # Start timer
        self.startTimer(10)

        # Save data
        self.saveData()

    """
    pro7part3_2(self)

        Description: Function called when Epoxy Applied Button (Right) is pressed. Stops the epoxy fill timer for the right side, and
                 records the data.
        
        Disables: Epoxy Applied Button (Right)
    """

    def pro7part3_2(self):
        self.stopTimer(10)
        # Disable widgets
        self.ui.epoxy_applied5_3.setDisabled(True)

        # Save data
        self.saveData()

    """
    resetpro7(self)

        Description: Resets the UI elements and data list for panel pro 5 to the state before the pro was started.

        Disables: Finish Button
                  Step Checkboxes

        Enables: Start Button
                 Panel Number Input
    """

    def resetpro7(self):
        self.data[4] = [None for x in self.data[4]]
        self.ui.panelInput7.setText("")
        self.ui.epoxy_batch5_2.setText("")
        self.ui.epoxy_batch5_3.setText("")
        self.timers[9].reset()
        self.timers[10].reset()
        self.ui.commentBox5.document().setPlainText("")
        self.ui.startButton7.setEnabled(True)
        self.ui.panelInput7.setEnabled(True)

    ###   _                           _        ___  _   _                  ____ _   _ ___
    ###  | |    __ _ _   _ _ __   ___| |__    / _ \| |_| |__   ___ _ __   / ___| | | |_ _|___
    ###  | |   / _` | | | | '_ \ / __| '_ \  | | | | __| '_ \ / _ \ '__| | |  _| | | || |/ __|
    ###  | |__| (_| | |_| | | | | (__| | | | | |_| | |_| | | |  __/ |    | |_| | |_| || |\__ \
    ###  |_____\__,_|\__,_|_| |_|\___|_| |_|  \___/ \__|_| |_|\___|_|     \____|\___/|___|___/
    ###

    """
    generateBox(self, type, title, text, question = False)

        Description: A function to handle generating error message boxes. A separate function was needed, as the default color scheme
                    makes them nearly unreadable. This generates boxes with a white background and black text.

        Parameter: type - A string giving the type of the box to set the appropriate icon (question, warning, or critical)
        Parameter: title - A string giving the desired error box title text
        Parameter: text - A string giving the desired error box text
        Parameter: question - A boolean value that determines if this box asks a question. If it does, the box is given yes and no buttons

        Return: A QMessageBox with the desired input qualities
    """

    def generateBox(self, type, title, text, question=False):
        iconDict = {
            "question": QMessageBox.Question,
            "warning": QMessageBox.Warning,
            "critical": QMessageBox.Critical,
        }
        box = QMessageBox()
        box.setWindowTitle(title)
        box.setText(text)
        box.setIcon(iconDict[type])
        box.setStyleSheet("color: black; background-color: white")

        if question:
            box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        return box.exec_()

    """
    diagram_popup(self, diagram)

        Description: Function that is called when any step button is clicked. Displays the corresponding step picture as a popup window
                    in the main GUI.

        Parameter: diagram - String specifying the filename of the image to be displayed.
    """

    def diagram_popup(self, diagram):
        buffer = 50
        wOpt = tkinter.Tk().winfo_screenwidth() - buffer
        hOpt = tkinter.Tk().winfo_screenheight() - buffer

        self._diagram = QLabel()

        pixmap = QPixmap()
        pixmap.load(str(self.imagePath / diagram))

        w = pixmap.width()
        h = pixmap.height()

        if not w == 0 and not h == 0:
            if w > wOpt or h > hOpt:
                self._diagram.setPixmap(
                    pixmap.scaled(wOpt - 20, hOpt - 20, Qt.KeepAspectRatio)
                )
                self._diagram.resize(wOpt, hOpt)
            else:
                self._diagram.setPixmap(pixmap.scaled(w, h, Qt.KeepAspectRatio))
                self._diagram.resize(w + 20, h + 20)

            self._diagram.setAlignment(Qt.AlignCenter)
            # self._diagram.setMovie(movie)
            # movie.start()
            self._diagram.show()

    # creates straw tensioner gui window
    # uses StrawTension from GUIs/current/tension_devices/straw_tensioner/run_straw_tensioner.pyw
    def strawTensionPopup(self):
        # this function probably doesn't need to exist but it makes the lambda a teeny bit more readable
        def saveStrawTensionMeasurement(position, tension, uncertainty):
            self.DP.saveStrawTensionMeasurement(position, tension, uncertainty)

        if self.checkDevice() == True:  # if no device,
            return  # return from this function
        if (
            self.strawTensionWindow is None
        ):  # if there's no strawTension window present...
            self.strawTensionWindow = StrawTension(  # make one! (creating it doesn't show it though)
                saveMethod=lambda position, tension, uncertainty: saveStrawTensionMeasurement(  # pass it a save method, so it can...
                    position, tension, uncertainty
                ),  # ...save data to the DB
                inGUI=(
                    self.ui.panelInput2.text()[2:]
                ),  # let the tensioner gui know what panel it's being used for
            )
        self.strawTensionWindow.show()  # show the window
        self.strawTensionWindow.resize(
            1600, 1200
        )  # resize for readability (default is 400x200?)

    # creates wire tensioner gui window
    # uses wireTensionWindow from GUIs/current/tension_devices/wire_tensioner/wire_tensioner.py
    def wireTensionPopup(self):
        # Method to save the wire tension measurements
        def saveWireTensionMeasurement(pos, tension, timer, calibration):
            self.ui.panelInput3_2.setText(str(calibration))
            self.DP.saveWireTensionMeasurement(pos, tension, timer, calibration)

        if self.checkDevice() == False:
            if self.wireTensionWindow is None:
                # Construct Wire Tension Window whose save method is to call the two methods defined above
                self.wireTensionWindow = WireTensionWindow(
                    saveMethod=lambda tension_tpl, cont_tpl: (
                        saveWireTensionMeasurement(*tension_tpl),
                        self.saveContinuityMeasurement(*cont_tpl),
                    ),
                    loadContinuityMethod=self.loadContinuityMeasurements,
                )

            # Show the window
            self.wireTensionWindow.show()

    # creates tension box gui window
    # uses TensionBox from GUIs/current/tension_devices/tension_box/tensionbox_window.py
    def tensionboxPopup(self):
        if self.checkDevice() == False:
            if self.tensionBoxWindow is None:
                self.tensionBoxWindow = TensionBox(
                    saveMethod=(
                        lambda panel, is_straw, position, length, frequency, pulse_width, tension: self.DP.saveTensionboxMeasurement(
                            self.getCurrentPanel(),
                            is_straw,
                            position,
                            length,
                            frequency,
                            pulse_width,
                            tension,
                        )
                    ),
                    panel=self.getCurrentPanel(),
                )
            self.tensionBoxWindow.show()

    # creates panel heater gui window
    # uses HeatControl from GUIs/current/tension_devices/panel_heater/PanelHeater.py
    def panelHeaterPopup(self):
        if self.checkDevice() == True:  # if no device connected,
            return  # return from this function

        if self.panelHeaterWindow == None:  # if no window yet,
            # get the current panel ID (one of the inputs will have text, the others will have none)
            panelID = f"{self.ui.panelInput6.text()}{self.ui.panelInput2.text()}{self.ui.panelInput1.text()}"
            self.panelHeaterWindow = HeatControl(
                port="GUI",
                panel=panelID,
                saveMethod=(
                    lambda temp_paas_a, temp_paas_bc: (
                        self.DP.savePanelTempMeasurement(temp_paas_a, temp_paas_bc)
                    )
                ),
            )
            self.panelHeaterWindow.show()


def except_hook(exctype, exception, tb):
    """
    except_hook(exctype, exception, traceback)

    Description: Enables exception handling that is more intuitive. By default, uncaught exceptions
                 cause PyQt GUIs to hang and then display the "Python has encountered and error and
                 needs to close" box. By defining this function (and setting sys.excepthook = except_hook
                 in the main function), uncaught exceptions immediately close the GUI, and display the
                 error message on screen (like a normal python script).

    Parameter: exctype - The class of the uncaught exception
    Parameter: exception - Exception object that went uncaught.
    Parameter: tb - The traceback of the exception that specifies where and why it happened.
    """
    sys.__excepthook__(exctype, exception, tb)
    sys.exit()


def checkPackages():
    # list of packages to check, each tuple has the name of the package and a
    # boolean to determine if the version is correct
    packageList = [
        ("cycler", cycler.__version__ == "0.10.0"),
        ("kiwisolver", kiwisolver.__version__ == "1.1.0"),
        ("matplotlib", matplotlib.__version__ == "3.1.0"),
        ("numpy", np.__version__ == "1.16.4"),
        ("pyautogui", pyautogui.__version__ == "0.9.44"),
        ("pyparsing", pyparsing.__version__ == "2.4.0"),
        (
            "PyQt5",
            PYQT_VERSION_STR == "5.12.2",
        ),  # PyQt5 doesn't have a __version__ member, but PyQt5.Qt has PYQT_VERSION_STR
        ("pyrect", pyrect.__version__ == "0.1.4"),
        ("pyscreeze", pyscreeze.__version__ == "0.1.21"),
        ("pytweening", pytweening.__version__ == "1.0.3"),
        ("scipy", scipy.__version__ == "1.5.1"),
        ("setuptools", setuptools.__version__ == "40.8.0"),
        ("six", six.__version__ == "1.12.0"),
        ("sqlalchemy", sqlalchemy.__version__ == "1.3.5"),
    ]
    # loop through list of package tuples
    for package in packageList:
        if not package[
            1
        ]:  # if the boolean statement is false (if the version is incorrect)
            # display a tkinter error with the following string as it's message (I apologize for putting 200+ characters on one line)
            # package[0] gets the name of the package, and platform.node() gets the name of the computer
            message = f"An incompatible version of {package[0]} is installed on this computer.  The GUI may not function normally, and DATA MAY NOT BE SAVED.  Contact a member of the software team for help, and mention that {package[0]} needs updating on {platform.node()}"
            packageErrorRoot = tkinter.Tk()  # create a tkinter root
            packageErrorRoot.withdraw()  # hide the root (hide the tiny blank window that tkinter wants)
            tkinter.messagebox.showerror(  # show error message
                title="Version Error",  # name it 'Version Error'
                message=message,  # put the huge string from before into it
            )
            break  # break out of for loop to prevent a million error messages (one is enough)

    if sys.version[:3] != "3.7":  # if python version is wrong
        # just like above, display a tkinter error (except with different text)
        message = f"The wrong version of python is installed on this computer.  The GUI will not function normally, and DATA MAY NOT BE SAVED.  Contact a member of the software team immediately, and mention that the wrong version of python is installed on {platform.node()}"
        pythonErrorRoot = tkinter.Tk()
        pythonErrorRoot.withdraw()
        tkinter.messagebox.showerror(title="Version Error", message=message)


if __name__ == "__main__":
    sys.excepthook = (
        except_hook  # catch annoying "python has stopped working" error on crash
    )
    checkPackages()  # check package versions
    app = QApplication(sys.argv)  # create new app to run
    app.setStyle(QStyleFactory.create("Fusion"))  # aestetics
    app.setAttribute(Qt.AA_EnableHighDpiScaling)  # aestetics

    # Load various location paths from the txt file paths-lab.txt
    # Assume that PANGUI lives in GUIS/panel/current
    current_dir = os.path.dirname(__file__)
    top_dir = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
    paths_file_location = os.path.abspath(
        os.path.join(current_dir, "paths-lab.txt")
    )  # absolute location of the txt file
    paths = dict(
        np.loadtxt(paths_file_location, delimiter=",", dtype=str)
    )  # load the paths
    paths.update(
        (k, top_dir + "/" + v) for k, v in paths.items()
    )  # make paths absolute

    ctr = panelGUI(paths)  # create gui window
    ctr.show()  # show gui window
    app.exec_()  # go!
