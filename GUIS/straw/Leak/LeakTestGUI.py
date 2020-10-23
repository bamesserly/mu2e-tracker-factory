### X0306b.py Updated - Ben Hiltbrand <hiltb004@umn.edu>

### Attempts to upload to database when unloading straw, with an error message if it fails
### Rudimentary checking of straws before loading, with error messages
### Interface with the pressurization GUI for handling of removing straws
### Improved performance by using multithreading
### Implemented signals to retain thread-safety
### 10/24/18 - Implemented new credentials system
### 12/04/18 - Bug fixes

from PyQt5 import QtCore, QtGui
import time, sys, logging, random, os, os.path, shutil, functools
from PyQt5.QtWidgets import (
    qApp,
    QApplication,
    QLabel,
    QWidget,
    QGridLayout,
    QPushButton,
    QVBoxLayout,
    QMainWindow,
    QDialog,
    QPushButton,
    QLineEdit,
    QMessageBox,
    QInputDialog,
)
from PyQt5 import QtGui
import serial  ## Takes this from pyserial, not serial
import datetime
import numpy as np
import matplotlib.pyplot as plt
from least_square_linear import *  ## Contributes fit functions
from N0202a import Ui_MainWindow  ## Main GUI window
from N0207a import Ui_Dialog  ## Pop-up GUI window for straw selection
from WORKER import Ui_Dialogw
import inspect
from WriteToFile import *  ## Functions to save to pallet file
import csv
from pathlib import Path

dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)

sys.path.insert(0, "..\\Upload")

sys.path.insert(
    0, str(Path(Path(__file__).resolve().parent.parent.parent.parent / "Data"))
)
from workers.credentials.credentials import Credentials

from remove import Ui_DialogBox

# move up one directory
sys.path.insert(0, os.path.dirname(__file__) + "..\\")
from masterUpload import *


import threading


class LeakTestStatus(QMainWindow):

    # Signals for updating GUI from non-main thread
    ArduinoStart = QtCore.pyqtSignal(int, bool)
    StrawProcessing = QtCore.pyqtSignal(int)
    EnablePlot = QtCore.pyqtSignal(int)
    LargeLeak = QtCore.pyqtSignal(int)
    StrawStatus = QtCore.pyqtSignal(int, bool)
    ToggleRemoved = QtCore.pyqtSignal(bool)
    UpdateStrawText = QtCore.pyqtSignal(int)
    FailedUpload = QtCore.pyqtSignal(str, str)
    # UnloadUpdate = QtCore.pyqtSignal(int, 'QPushButton')
    UnloadUpdate = QtCore.pyqtSignal(int)
    LockGUI = QtCore.pyqtSignal(bool)

    def __init__(self, COM, baudrate, arduino_input=False):
        super(LeakTestStatus, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()
        ## Add a timeout (0.08 sec) to avoid freezing GUI while waiting for serial data from arduinos
        self.COM = [
            "COM8",
            "COM9",
            "COM10",
            "COM11",
            "COM12",
            "COM3",
            "COM4",
            "COM5",
            "COM6",
            "COM7",
        ]
        self.COM_con = [None, None, None, None, None, None, None, None, None, None]
        self.arduino = [
            serial.Serial(port=self.COM_con[0], baudrate=115200, timeout=0.08),
            serial.Serial(port=self.COM_con[1], baudrate=115200, timeout=0.08),
            serial.Serial(port=self.COM_con[2], baudrate=115200, timeout=0.08),
            serial.Serial(port=self.COM_con[3], baudrate=115200, timeout=0.08),
            serial.Serial(port=self.COM_con[4], baudrate=115200, timeout=0.08),
            serial.Serial(port=self.COM_con[5], baudrate=115200, timeout=0.08),
            serial.Serial(port=self.COM_con[6], baudrate=115200, timeout=0.08),
            serial.Serial(port=self.COM_con[7], baudrate=115200, timeout=0.08),
            serial.Serial(port=self.COM_con[8], baudrate=115200, timeout=0.08),
            serial.Serial(port=self.COM_con[9], baudrate=115200, timeout=0.08),
        ]

        self.baudrate = [
            115200,
            115200,
            115200,
            115200,
            115200,
            115200,
            115200,
            115200,
            115200,
            115200,
        ]
        self.cutOffTime = 27000  # Makes a decision on pass/fail after this time, even if the uncertainty is not low enough
        self.number_of_chambers = 5
        self.max_chambers = 50

        self.cpalDirectory = (
            os.path.dirname(__file__)
            + "..\\..\\..\\Data\\Leak test data\\CPALS in Testing\\CPALS.txt"
        )
        self.networkDirectory = (
            os.path.dirname(__file__)
            + "..\\..\\..\\Data\\Leak test data\\Leak Test Results\\"
        )
        self.workerDirectory = (
            os.path.dirname(__file__)
            + "..\\..\\..\\Data\\workers\\straw workers\\leak testing\\"
        )

        self.starttime = [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        ]

        self.chamber_id = {
            "ch0": 0,
            "ch1": 1,
            "ch2": 2,
            "ch3": 3,
            "ch4": 4,
            "ch5": 5,
            "ch6": 6,
            "ch7": 7,
            "ch8": 8,
            "ch9": 9,
            "ch10": 10,
            "ch11": 11,
            "ch12": 12,
            "ch13": 13,
            "ch14": 14,
            "ch15": 15,
            "ch16": 16,
            "ch17": 17,
            "ch18": 18,
            "ch19": 19,
            "ch20": 20,
            "ch21": 21,
            "ch22": 22,
            "ch23": 23,
            "ch24": 24,
            "ch25": 25,
            "ch26": 26,
            "ch27": 27,
            "ch28": 28,
            "ch29": 29,
            "ch30": 30,
            "ch31": 31,
            "ch32": 32,
            "ch33": 33,
            "ch34": 34,
            "ch35": 35,
            "ch36": 36,
            "ch37": 37,
            "ch38": 38,
            "ch39": 39,
            "ch40": 40,
            "ch41": 41,
            "ch42": 42,
            "ch43": 43,
            "ch44": 44,
            "ch45": 45,
            "ch46": 46,
            "ch47": 47,
            "ch48": 48,
            "ch49": 49,
        }

        self.Choosenames1 = ["empty0", "empty1", "empty2", "empty3", "empty4"]
        self.Choosenames2 = ["empty5", "empty6", "empty7", "empty8", "empty9"]
        self.Choosenames3 = ["empty10", "empty11", "empty12", "empty13", "empty14"]
        self.Choosenames4 = ["empty15", "empty16", "empty17", "empty18", "empty19"]
        self.Choosenames5 = ["empty20", "empty21", "empty22", "empty23", "empty24"]
        self.Choosenames6 = ["empty25", "empty26", "empty27", "empty28", "empty29"]
        self.Choosenames7 = ["empty30", "empty31", "empty32", "empty33", "empty34"]
        self.Choosenames8 = ["empty35", "empty36", "empty37", "empty38", "empty39"]
        self.Choosenames9 = ["empty40", "empty41", "empty45", "empty46", "empty47"]
        self.Choosenames10 = ["empty45", "empty46", "empty47", "empty48", "empty49"]
        self.Choosenames = [
            self.Choosenames1,
            self.Choosenames2,
            self.Choosenames3,
            self.Choosenames4,
            self.Choosenames5,
            self.Choosenames6,
            self.Choosenames7,
            self.Choosenames8,
            self.Choosenames9,
            self.Choosenames10,
        ]

        self.chambers_status1 = ["empty0", "empty1", "empty2", "empty3", "empty4"]
        self.chambers_status2 = ["empty5", "empty6", "empty7", "empty8", "empty9"]
        self.chambers_status3 = ["empty10", "empty11", "empty12", "empty13", "empty14"]
        self.chambers_status4 = ["empty15", "empty16", "empty17", "empty18", "empty19"]
        self.chambers_status5 = ["empty20", "empty21", "empty22", "empty23", "empty24"]
        self.chambers_status6 = ["empty25", "empty26", "empty27", "empty28", "empty29"]
        self.chambers_status7 = ["empty30", "empty31", "empty32", "empty33", "empty34"]
        self.chambers_status8 = ["empty35", "empty36", "empty37", "empty38", "empty39"]
        self.chambers_status9 = ["empty40", "empty41", "empty42", "empty43", "empty44"]
        self.chambers_status10 = ["empty45", "empty46", "empty47", "empty48", "empty49"]
        self.chambers_status = [
            self.chambers_status1,
            self.chambers_status2,
            self.chambers_status3,
            self.chambers_status4,
            self.chambers_status5,
            self.chambers_status6,
            self.chambers_status7,
            self.chambers_status8,
            self.chambers_status9,
            self.chambers_status10,
        ]

        self.files = {}
        self.straw_list = []  ## Passed straws with saved data
        self.result = self.networkDirectory + "Leak Test Results.csv"
        result = open(self.result, "a+", 1)
        result.close()
        #        self.result = self.directory + datetime.now().strftime("%Y-%m-%d_%H%M%S") + '_%s.csv' % self.COM

        self.chamber_volume1 = [594, 607, 595, 605, 595]  ## For row 1 chambers
        self.chamber_volume2 = [606, 609, 612, 606, 595]
        self.chamber_volume3 = [592, 603, 612, 606, 567]
        self.chamber_volume4 = [585, 575, 610, 615, 587]
        self.chamber_volume5 = [611, 600, 542, 594, 591]
        self.chamber_volume6 = [598, 451, 627, 588, 649]
        self.chamber_volume7 = [544, 600, 534, 594, 612]
        self.chamber_volume8 = [606, 594, 515, 583, 601]
        self.chamber_volume9 = [557, 510, 550, 559, 527]
        self.chamber_volume10 = [567, 544, 572, 561, 578]
        self.chamber_volume = [
            self.chamber_volume1,
            self.chamber_volume2,
            self.chamber_volume3,
            self.chamber_volume4,
            self.chamber_volume5,
            self.chamber_volume6,
            self.chamber_volume7,
            self.chamber_volume8,
            self.chamber_volume9,
            self.chamber_volume10,
        ]

        self.chamber_volume_err1 = [13, 31, 15, 10, 21]
        self.chamber_volume_err2 = [37, 7, 12, 17, 15]
        self.chamber_volume_err3 = [15, 12, 7, 4, 2]
        self.chamber_volume_err4 = [8, 15, 6, 10, 11]
        self.chamber_volume_err5 = [4, 3, 8, 6, 9]
        self.chamber_volume_err6 = [31, 11, 25, 20, 16]
        self.chamber_volume_err7 = [8, 8, 11, 8, 6]
        self.chamber_volume_err8 = [6, 10, 8, 10, 8]
        self.chamber_volume_err9 = [6, 8, 6, 9, 6]
        self.chamber_volume_err10 = [7, 6, 8, 7, 6]
        self.chamber_volume_err = [
            self.chamber_volume_err1,
            self.chamber_volume_err2,
            self.chamber_volume_err3,
            self.chamber_volume_err4,
            self.chamber_volume_err5,
            self.chamber_volume_err6,
            self.chamber_volume_err6,
            self.chamber_volume_err8,
            self.chamber_volume_err9,
            self.chamber_volume_err10,
        ]

        # self.leak_rate = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        # self.leak_rate_err = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

        self.leak_rate = [0] * self.max_chambers
        self.leak_rate_err = [0] * self.max_chambers

        # self.passed = ['U','U','U','U','U','U','U','U','U','U','U','U','U','U','U','U','U','U','U','U','U','U','U','U','U',
        #'U','U','U','U','U','U','U','U','U','U','U','U','U','U','U','U','U','U','U','U','U','U','U','U','U']

        self.passed = ["U"] * self.max_chambers

        self.straw_volume = 26.0
        for n in range(len(self.chamber_volume)):
            for m in range(len(self.chamber_volume[n])):
                self.chamber_volume[n][m] = (
                    self.chamber_volume[n][m] - self.straw_volume
                )
        # (conversion_rate*real_leak_rate=the_leak_rate_when_using_20/80_argon/co2 in chamber)
        # Conversion rate proportional to amount of CO2 (1/5)
        # Partial pressure of CO2 as 2 absolution ATM presure inside and 0 outside, chamber will be 1 to 0(1/2)
        # Multiplied by 1.4 for the argon gas leaking as well conservative estimate (should we reduce?
        self.conversion_rate = 0.14
        # max leak rate for straws
        straws_in_detector = 20736
        total_leak_detector = 6  # cc/min
        max_leakrate = float(total_leak_detector) / float(straws_in_detector)  # CC/min
        self.max_leakrate = max_leakrate / 3

        self.excluded_time = 120  # wait 2 minutes before using data for fit
        self.max_time = (
            7200  # When time exceeds 2 hours stops fitting data (still saving it)
        )
        self.min_number_datapoints = (
            10  # requires 10 datapoints before attempting to fit
        )
        self.max_co2_level = (
            1800  # when PPM exceeds 1800 stops fitting and warns user of failure
        )

        ## set of Arduino status boxes
        self.Arduinos = [
            self.ui.arduino1,
            self.ui.arduino2,
            self.ui.arduino3,
            self.ui.arduino4,
            self.ui.arduino5,
            self.ui.arduino6,
            self.ui.arduino7,
            self.ui.arduino8,
            self.ui.arduino9,
            self.ui.arduino10,
        ]

        ## buttons for plotting belong to a QButtonGroup called PdfButtons
        self.ui.PdfButtons.buttonClicked.connect(self.Plot)
        for x in self.ui.PdfButtons.buttons():
            x.setText("Plot")
            x.setDisabled(True)

        ## buttons for loading/unloading straws to a QButtonGroup called ActionButtons
        self.ui.ActionButtons.buttonClicked.connect(self.Action)

        for x in self.ui.ActionButtons.buttons():
            x.setText("Load")
            x.setDisabled(True)

        ## sets for chamber status boxes and status labels
        self.Chambers = [
            self.ui.ch0,
            self.ui.ch1,
            self.ui.ch2,
            self.ui.ch3,
            self.ui.ch4,
            self.ui.ch5,
            self.ui.ch6,
            self.ui.ch7,
            self.ui.ch8,
            self.ui.ch9,
            self.ui.ch10,
            self.ui.ch11,
            self.ui.ch12,
            self.ui.ch13,
            self.ui.ch14,
            self.ui.ch15,
            self.ui.ch16,
            self.ui.ch17,
            self.ui.ch18,
            self.ui.ch19,
            self.ui.ch20,
            self.ui.ch21,
            self.ui.ch22,
            self.ui.ch23,
            self.ui.ch24,
            self.ui.ch25,
            self.ui.ch26,
            self.ui.ch27,
            self.ui.ch28,
            self.ui.ch29,
            self.ui.ch30,
            self.ui.ch31,
            self.ui.ch32,
            self.ui.ch33,
            self.ui.ch34,
            self.ui.ch35,
            self.ui.ch36,
            self.ui.ch37,
            self.ui.ch38,
            self.ui.ch39,
            self.ui.ch40,
            self.ui.ch41,
            self.ui.ch42,
            self.ui.ch43,
            self.ui.ch44,
            self.ui.ch45,
            self.ui.ch46,
            self.ui.ch47,
            self.ui.ch48,
            self.ui.ch49,
        ]

        self.ChamberLabels = [
            self.ui.label_ch0,
            self.ui.label_ch1,
            self.ui.label_ch2,
            self.ui.label_ch3,
            self.ui.label_ch4,
            self.ui.label_ch5,
            self.ui.label_ch6,
            self.ui.label_ch7,
            self.ui.label_ch8,
            self.ui.label_ch9,
            self.ui.label_ch10,
            self.ui.label_ch11,
            self.ui.label_ch12,
            self.ui.label_ch13,
            self.ui.label_ch14,
            self.ui.label_ch15,
            self.ui.label_ch16,
            self.ui.label_ch17,
            self.ui.label_ch18,
            self.ui.label_ch19,
            self.ui.label_ch20,
            self.ui.label_ch21,
            self.ui.label_ch22,
            self.ui.label_ch23,
            self.ui.label_ch24,
            self.ui.label_ch25,
            self.ui.label_ch26,
            self.ui.label_ch27,
            self.ui.label_ch28,
            self.ui.label_ch29,
            self.ui.label_ch30,
            self.ui.label_ch31,
            self.ui.label_ch32,
            self.ui.label_ch33,
            self.ui.label_ch34,
            self.ui.label_ch35,
            self.ui.label_ch36,
            self.ui.label_ch37,
            self.ui.label_ch38,
            self.ui.label_ch39,
            self.ui.label_ch40,
            self.ui.label_ch41,
            self.ui.label_ch42,
            self.ui.label_ch43,
            self.ui.label_ch44,
            self.ui.label_ch45,
            self.ui.label_ch46,
            self.ui.label_ch47,
            self.ui.label_ch48,
            self.ui.label_ch49,
        ]

        self.StrawLabels = [
            self.ui.label_st0,
            self.ui.label_st1,
            self.ui.label_st2,
            self.ui.label_st3,
            self.ui.label_st4,
            self.ui.label_st5,
            self.ui.label_st6,
            self.ui.label_st7,
            self.ui.label_st8,
            self.ui.label_st9,
            self.ui.label_st10,
            self.ui.label_st11,
            self.ui.label_st12,
            self.ui.label_st13,
            self.ui.label_st14,
            self.ui.label_st15,
            self.ui.label_st16,
            self.ui.label_st17,
            self.ui.label_st18,
            self.ui.label_st19,
            self.ui.label_st20,
            self.ui.label_st21,
            self.ui.label_st22,
            self.ui.label_st23,
            self.ui.label_st24,
            self.ui.label_st25,
            self.ui.label_st26,
            self.ui.label_st27,
            self.ui.label_st28,
            self.ui.label_st29,
            self.ui.label_st30,
            self.ui.label_st31,
            self.ui.label_st32,
            self.ui.label_st33,
            self.ui.label_st34,
            self.ui.label_st35,
            self.ui.label_st36,
            self.ui.label_st37,
            self.ui.label_st38,
            self.ui.label_st39,
            self.ui.label_st40,
            self.ui.label_st41,
            self.ui.label_st42,
            self.ui.label_st43,
            self.ui.label_st44,
            self.ui.label_st45,
            self.ui.label_st46,
            self.ui.label_st47,
            self.ui.label_st48,
            self.ui.label_st49,
        ]

        self.StrtData = [
            self.ui.StartData_1,
            self.ui.StartData_2,
            self.ui.StartData_3,
            self.ui.StartData_4,
            self.ui.StartData_5,
            self.ui.StartData_6,
            self.ui.StartData_7,
            self.ui.StartData_8,
            self.ui.StartData_9,
            self.ui.StartData_10,
        ]
        self.StpData = [
            self.ui.StopData_1,
            self.ui.StopData_2,
            self.ui.StopData_3,
            self.ui.StopData_4,
            self.ui.StopData_5,
            self.ui.StopData_6,
            self.ui.StopData_7,
            self.ui.StopData_8,
            self.ui.StopData_9,
            self.ui.StopData_10,
        ]

        self.ui.StartButtons.buttonClicked.connect(self.startArduino)
        self.ui.StopButtons.buttonClicked.connect(self.handleStop)

        for x in self.StpData:
            x.setDisabled(True)
        ##        self.Current_worker = 'Unknown worker'
        ##        self.Previous_worker = 'Unknown worker'
        ##        self.ui.Log_out.setDisabled(True)
        self.ui.PortalButtons.buttonClicked.connect(self.Change_worker_ID)
        self.Current_workers = [
            self.ui.Current_worker1,
            self.ui.Current_worker2,
            self.ui.Current_worker3,
            self.ui.Current_worker4,
        ]
        self.sessionWorkers = []
        self.previousSessionWorkers = []

        self.ui.RemoveButton.clicked.connect(self.editPallet)
        self.ui.RemoveButton.setDisabled(True)

        self._running = [
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
        ]

        self.cpals = []

        self.stationID = "leak"
        self.credentialChecker = Credentials(self.stationID)

        self.justLogOut = ""
        self.saveWorkers()
        self.lockGUI(False)

        # Connect Signals
        self.ArduinoStart.connect(self.setArduinoStart)
        self.StrawProcessing.connect(self.setStrawProcessing)
        self.EnablePlot.connect(self.setEnablePlot)
        self.LargeLeak.connect(self.setLargeLeak)
        self.StrawStatus.connect(self.setStrawStatus)
        self.ToggleRemoved.connect(self.setToggleRemoved)
        self.UpdateStrawText.connect(self.setUpdateStrawText)
        self.FailedUpload.connect(self.setFailedUpload)
        self.UnloadUpdate.connect(self.setUnloadUpdate)
        self.LockGUI.connect(self.lockGUI)

        # Start self.main in a background thread, so that the GUI keeps updating
        thread = threading.Thread(target=self.signalChecking, args=())
        thread.daemon = True  # Daemonize thread
        thread.start()

        # Start data collection in background, to reduce GUI lagging
        thread2 = threading.Thread(target=self.dataCollection, args=())
        thread2.daemon = True  # Daemonize thread
        thread2.start()

        # ROW starts at 0

    def Connect_Arduino(self, a_port):
        index = self.COM.index(a_port)
        try:
            serial.Serial(port=a_port, baudrate=115200, timeout=0.08)
            # print("Arduino at port %s, baudrate %s" % (self.COM[self.COM.index(a_port)],'115200'))
            self.COM_con[index] = a_port
        except serial.SerialException:
            # print("Arduino at port %s is not connected" % self.COM[self.COM.index(a_port)])
            self.COM_con[index] = None
        self.arduino[index] = serial.Serial(
            port=self.COM_con[index], baudrate=115200, timeout=0.08
        )

    def startArduino(self, btn):
        if self.checkCredentials():
            ROW = int(btn.objectName().strip("StartData_")) - 1
            self.arduino[ROW].close()
            self.Connect_Arduino(self.COM[ROW])
            if self.COM_con[ROW] == None:
                self.Arduinos[ROW].setStyleSheet("background-color: rgb(170, 0, 0);")
                return

            self.StrtData[ROW].setDisabled(True)
            self.StpData[ROW].setEnabled(True)
            self.Arduinos[ROW].setStyleSheet("background-color: rgb(0, 170, 0);")
            for x in self.ui.ActionButtons.buttons():
                if (
                    (5 * ROW - 1)
                    < int(x.objectName().strip("ActionButton"))
                    < (5 * (ROW + 1))
                ):
                    x.setEnabled(True)
            for COL in range(self.number_of_chambers):
                self.update_name(ROW, COL)
            thread = threading.Thread(
                target=self.ReadinBuffer, args=(ROW,), name=("Buffer" + str(ROW))
            )
            thread.daemon = True  # Daemonize thread
            thread.start()

            self._running[ROW] = True
        else:
            self.openLogInDialog()

    def handleStop(self, btn):
        ROW = int(btn.objectName().strip("StopData_")) - 1
        self._running[ROW] = False
        self.StrtData[ROW].setEnabled(True)
        self.StpData[ROW].setDisabled(True)
        for x in self.ui.ActionButtons.buttons():
            if (
                (5 * ROW - 1)
                < int(x.objectName().strip("ActionButton"))
                < (5 * (ROW + 1))
            ):
                x.setDisabled(True)
        for x in self.ui.PdfButtons.buttons():
            if (5 * ROW - 1) < int(x.objectName().strip("PdfButton")) < (5 * (ROW + 1)):
                x.setDisabled(True)
        self.Arduinos[ROW].setStyleSheet("background-color: rgb(149, 186, 255);")

    def ReadinBuffer(self, ROW):
        starting_up_time = 1
        starting_up = True
        beginning_time = time.time()
        while starting_up:
            buffer = self.arduino[ROW].readline().strip()
            if (time.time() - beginning_time) > starting_up_time:
                starting_up = False

    def handleStart(self):
        """Start data collection for all chambers connected to the Arduino"""
        # self.StrtData[0].setDisabled(True)
        # self._running[0] = True
        # for x in self.ui.ActionButtons.buttons():
        #    x.setEnabled(True)
        empty_lines = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        pasttime = [
            time.time(),
            time.time(),
            time.time(),
            time.time(),
            time.time(),
            time.time(),
            time.time(),
            time.time(),
            time.time(),
            time.time(),
        ]
        while any(self._running):
            i = 0
            for tf in self._running:
                # cycles through rows
                ROW = i
                i = i + 1

                if self.testThreads("Buffer" + str(ROW)):
                    continue

                if tf == True:
                    ## Read Arduino and split into multiple files
                    # ppms = self.arduino[ROW].readline().strip().split()
                    if empty_lines[ROW] > 60:
                        self.arduino[ROW].close()
                        self.Connect_Arduino(self.COM[ROW])
                        if self.COM_con[ROW] != None:
                            empty_lines[ROW] = 0

                    if self.COM_con[ROW] == None:
                        # self.Arduinos[ROW].setStyleSheet("background-color: rgb(170, 0, 0);")
                        self.ArduinoStart.emit(ROW, False)
                        continue
                    else:
                        # self.Arduinos[ROW].setStyleSheet("background-color: rgb(0, 170, 0);")
                        self.ArduinoStart.emit(ROW, True)

                    arduino_line = self.arduino[ROW].readline().strip()
                    if arduino_line == b"":
                        empty_lines[ROW] = empty_lines[ROW] + 1
                    if arduino_line != b"":
                        empty_lines[ROW] = 0
                        ppms = arduino_line.split()
                        formattedList = ["%5.2f" % float(member) for member in ppms]
                        currenttime = datetime.datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                        epoctime = [
                            time.time(),
                            time.time(),
                            time.time(),
                            time.time(),
                            time.time(),
                            time.time(),
                            time.time(),
                            time.time(),
                            time.time(),
                            time.time(),
                        ]
                        file = int(float(formattedList[0]))
                        file = file + ROW * 5
                        with open(self.files[file], "a+", 1) as f:
                            f.write(
                                str(format(epoctime[ROW], ".0f"))
                                + "\t"
                                + str(file)
                                + "\t"
                                + ("%.0f" % float(formattedList[1]))
                                + "\t"
                                + str(currenttime)
                                + "\n"
                            )
                            f.flush()  ## Needed to send data in buffer to file
                        # print(epoctime,'\t',file,'\t',formattedList[1],'\t',currenttime)
                        if epoctime[ROW] >= (pasttime[ROW] + 15.0):  ## Previously 15.0
                            # print("")
                            # print(self.COM[ROW])
                            pasttime[ROW] = epoctime[ROW]
                            PPM = {}
                            PPM_err = {}
                            timestamp = {}
                            #                        starttime = {}
                            slope = {}
                            slope_err = {}
                            intercept = {}
                            intercept_err = {}
                            for COL in range(self.number_of_chambers):
                                # cycles through columns
                                chamber = ROW * 5 + COL
                                PPM[chamber] = []
                                PPM_err[chamber] = []
                                timestamp[chamber] = []
                                #                            starttime[chamber] = 0
                                slope[chamber] = 0
                                slope_err[chamber] = 0
                                intercept[chamber] = 0
                                intercept_err[chamber] = 0
                                with open(
                                    self.networkDirectory
                                    + self.Choosenames[ROW][COL]
                                    + "_rawdata.txt",
                                    "r+",
                                    1,
                                ) as readfile:
                                    for line in readfile:
                                        numbers_float = line.split()[:3]
                                        if numbers_float[2] == "0.00":
                                            continue
                                        if self.starttime[chamber] == 0:
                                            self.starttime[chamber] = float(
                                                numbers_float[0]
                                            )
                                        eventtime = (
                                            float(numbers_float[0])
                                            - self.starttime[chamber]
                                        )
                                        if eventtime > self.excluded_time:
                                            PPM[chamber].append(float(numbers_float[2]))
                                            PPM_err[chamber].append(
                                                (
                                                    (float(numbers_float[2]) * 0.02)
                                                    ** 2
                                                    + 20 ** 2
                                                )
                                                ** 0.5
                                            )
                                            timestamp[chamber].append(eventtime)
                                    if str(self.Choosenames[ROW][COL])[0:5] == "empty":
                                        # print("No straw in chamber %.0f" % (chamber))
                                        continue

                                    if self.passed[chamber] == "U":
                                        self.StrawProcessing.emit(chamber)

                                    if len(PPM[chamber]) < self.min_number_datapoints:
                                        # print("Straw %s in chamber %.0f is in preparation stage. Please wait for more data" %(self.Choosenames[ROW][COL][:7],chamber))
                                        # self.Chambers[chamber].setStyleSheet("background-color: rgb(225, 225, 0);")
                                        # self.ChamberLabels[f].setText('Processing')
                                        continue
                                    ##                                    for x in self.ui.PdfButtons.buttons():
                                    ##                                        if int(x.objectName().strip('PdfButton')) == chamber:
                                    ##                                              x.setEnabled(True)

                                    self.EnablePlot.emit(chamber)

                                    if (
                                        max(PPM[chamber]) > self.max_co2_level
                                        and self.passed[chamber] != "P"
                                    ):
                                        # print("CO2 in chamber %.0f exceed 1800. Significant leak?!? Please flush and remove straw" %chamber)
                                        ##                                        self.ChamberLabels[chamber].setText('Large Leak!')
                                        ##                                        self.Chambers[chamber].setStyleSheet("background-color: rgb(225, 40, 40);")
                                        self.LargeLeak.emit(chamber)
                                        self.leak_rate[chamber] = 100
                                        continue
                                    # if max(timestamp[chamber]) > self.max_time :
                                    #    print("Straw %s has been in Chamber %.0f for over 2 hours.  Data is saving but no longer fitting." %(self.Choosenames[ROW][COL][:7],chamber))
                                    #    continue
                                    slope[chamber] = get_slope(
                                        timestamp[chamber],
                                        PPM[chamber],
                                        PPM_err[chamber],
                                    )

                                    if slope[chamber] == 0:
                                        slope[chamber] = 1e-100

                                    slope_err[chamber] = get_slope_err(
                                        timestamp[chamber],
                                        PPM[chamber],
                                        PPM_err[chamber],
                                    )
                                    intercept[chamber] = get_intercept(
                                        timestamp[chamber],
                                        PPM[chamber],
                                        PPM_err[chamber],
                                    )
                                    intercept_err[chamber] = get_intercept_err(
                                        timestamp[chamber],
                                        PPM[chamber],
                                        PPM_err[chamber],
                                    )
                                    # leak rate in cc/min = slope(PPM/sec) * chamber_volume(cc) * 10^-6(1/PPM) * 60 (sec/min) * conversion_rate
                                    self.leak_rate[chamber] = (
                                        slope[chamber]
                                        * self.chamber_volume[ROW][COL]
                                        * (10 ** -6)
                                        * 60
                                        * self.conversion_rate
                                    )
                                    # error = sqrt((lr/slope)^2 * slope_err^2 + (lr/ch_vol)^2 * ch_vol_err^2)
                                    self.leak_rate_err[chamber] = (
                                        (self.leak_rate[chamber] / slope[chamber]) ** 2
                                        * slope_err[chamber] ** 2
                                        + (
                                            self.leak_rate[chamber]
                                            / self.chamber_volume[ROW][COL]
                                        )
                                        ** 2
                                        * self.chamber_volume_err[ROW][COL] ** 2
                                    ) ** 0.5
                                    straw_status = "unknown status"
                                    # print("Leak rate for straw %s in chamber %.0f is %.2f +- %.2f CC per minute * 10^-5"
                                    #% (self.Choosenames[ROW][COL][:7],chamber,self.leak_rate[chamber] *(10**5),self.leak_rate_err[chamber]*(10**5)))
                                    # self.ChamberLabels[chamber].setText(str('%.2f ± %.2f' % ((self.leak_rate[chamber]*(10**5)),self.leak_rate_err[chamber]*(10**5))))

                                    self.UpdateStrawText.emit(chamber)

                                    ## Passed straw
                                    if (
                                        len(PPM[chamber]) > 20
                                        and self.leak_rate[chamber] < self.max_leakrate
                                        and self.leak_rate_err[chamber]
                                        < self.max_leakrate / 10
                                    ):
                                        # print("Straw in chamber %.0f has Passed, Please remove" % chamber)
                                        straw_status = "Passed leak requirement"
                                        # self.Chambers[chamber].setStyleSheet("background-color: rgb(40, 225, 40);")
                                        self.StrawStatus.emit(chamber, True)
                                        self.passed[chamber] = "P"
                                    elif (
                                        len(PPM[chamber]) > 20
                                        and self.leak_rate[chamber] < self.max_leakrate
                                        and eventtime > self.cutOffTime
                                    ):
                                        # print("Straw in chamber %.0f has Passed, Please remove" % chamber)
                                        straw_status = "Passed leak requirement"
                                        # self.Chambers[chamber].setStyleSheet("background-color: rgb(40, 225, 40);")
                                        self.StrawStatus.emit(chamber, True)
                                        self.passed[chamber] = "P"
                                    ## Failed straw
                                    elif (
                                        len(PPM[chamber]) > 20
                                        and self.leak_rate[chamber] > self.max_leakrate
                                        and self.leak_rate_err[chamber]
                                        < self.max_leakrate / 10
                                    ):
                                        # print("FAILURE SHAME DISHONOR: Straw in chamber %.0f has failed, Please remove and reglue ends" % chamber)
                                        straw_status = "Failed leak requirement"
                                        # self.Chambers[chamber].setStyleSheet("background-color: rgb(225, 40, 40);")
                                        self.StrawStatus.emit(chamber, False)
                                        self.passed[chamber] = "F"
                                    elif (
                                        len(PPM[chamber]) > 20
                                        and self.leak_rate[chamber] > self.max_leakrate
                                        and eventtime > self.cutOffTime
                                    ):
                                        # print("FAILURE SHAME DISHONOR: Straw in chamber %.0f has failed, Please remove and reglue ends" % chamber)
                                        straw_status = "Failed leak requirement"
                                        # self.Chambers[chamber].setStyleSheet("background-color: rgb(225, 40, 40);")
                                        self.StrawStatus.emit(chamber, False)
                                        self.passed[chamber] = "F"
                                    elif (
                                        len(PPM[chamber]) > 20
                                        and (
                                            self.leak_rate[chamber]
                                            - 10 * self.leak_rate_err[chamber]
                                        )
                                        > self.max_leakrate
                                    ):
                                        # print("FAILURE SHAME DISHONOR: Straw in chamber %.0f has failed, Please remove and reglue ends" % chamber)
                                        straw_status = "Failed leak requirement"
                                        # self.Chambers[chamber].setStyleSheet("background-color: rgb(225, 40, 40);")
                                        self.StrawStatus.emit(chamber, False)
                                        self.passed[chamber] = "F"

                                    ## Graph and save graph of fit
                                    x = np.linspace(0, max(timestamp[chamber]))
                                    y = slope[chamber] * x + intercept[chamber]
                                    plt.plot(timestamp[chamber], PPM[chamber], "bo")
                                    # plt.errorbar(timestamp[f],PPM[f], yerr=PPM_err[f], fmt='o')
                                    plt.plot(x, y, "r")
                                    plt.xlabel("time (s)")
                                    plt.ylabel("CO2 level (PPM)")
                                    plt.title(self.Choosenames[ROW][COL] + "_fit")
                                    plt.figtext(
                                        0.49,
                                        0.80,
                                        "Slope = %.2f +- %.2f x $10^{-3}$ PPM/sec \n"
                                        % (
                                            slope[chamber] * 10 ** 4,
                                            slope_err[chamber] * 10 ** 4,
                                        )
                                        + "Leak Rate = %.2f +- %.2f x $10^{-5}$ cc/min \n"
                                        % (
                                            self.leak_rate[chamber] * (10 ** 5),
                                            self.leak_rate_err[chamber] * (10 ** 5),
                                        )
                                        + straw_status
                                        + "\t"
                                        + currenttime,
                                        fontsize=12,
                                        color="r",
                                    )
                                    plt.savefig(
                                        self.networkDirectory
                                        + self.Choosenames[ROW][COL]
                                        + "_fit.pdf"
                                    )
                                    plt.clf()

            # sys.stdout.flush()
            # qApp.processEvents()
            # app.processEvents()
            time.sleep(0.1)

    def lineno(self):
        """Call in debugging to get current line number"""
        return inspect.currentframe().f_back.f_lineno

    def Action(self, btn):
        """Load or unload straw depending on chamber contents"""
        chamber = int(btn.objectName().strip("ActionButton"))
        ROW = int(chamber / 5)
        COL = chamber % 5

        if self.chambers_status[ROW][COL][:5] == "empty":
            if self.checkCredentials():
                self.chambers_status[ROW][COL] = "Processing"
                self.ChamberLabels[chamber].setText(self.chambers_status[ROW][COL])
                self.ChangeStraw(chamber)
                if self.Choosenames[ROW][COL][:5] != "empty":
                    btn.setText("Unload")
                    # self.ui.RemoveButton.setDisabled(False)
                else:
                    self.chambers_status[ROW][COL] = "empty"
                    self.ChamberLabels[chamber].setText("Empty")
                    self.StrawLabels[chamber].setText("No straw")
                    btn.setText("Load")
                    self.Chambers[chamber].setStyleSheet(
                        "background-color: rgb(149, 186, 255)"
                    )
                    self.NoStraw(ROW, COL)
            else:
                self.openLogInDialog()
        elif self.chambers_status[ROW][COL][:5] != "empty":
            if self.passed[chamber] == "U":
                msg = f"This straw has not finished leak testing. Unloading now will NOT record leak data for this straw.\n\nAre you sure you want to unload {self.Choosenames[ROW][COL][:7]}?"
                reply = QMessageBox.warning(
                    self,
                    "Straw Not Finished Leak Testing",
                    msg,
                    QMessageBox.Yes,
                    QMessageBox.No,
                )

                if reply == QMessageBox.Yes:
                    thread = threading.Thread(
                        target=self.unloadActionNoSaving, args=(ROW, COL, chamber, btn)
                    )
                    thread.daemon = True  # Daemonize thread
                    thread.start()
                    return
                else:
                    return

            thread = threading.Thread(
                target=self.unloadAction, args=(ROW, COL, chamber, btn)
            )
            thread.daemon = True  # Daemonize thread
            thread.start()

    def deleteFiles(self, ROW, COL):
        path1 = os.path.join(
            self.networkDirectory, f"{self.Choosenames[ROW][COL]}_rawdata.txt"
        )
        path2 = os.path.join(
            self.networkDirectory, f"{self.Choosenames[ROW][COL]}_fit.pdf"
        )
        path3 = os.path.join(
            self.networkDirectory, f"{self.Choosenames[ROW][COL]}_fit_temp.pdf"
        )

        if os.path.exists(path1):
            os.remove(path1)

        if os.path.exists(path2):
            os.remove(path2)

        if os.path.exists(path3):
            os.remove(path3)

    def unloadAction(self, ROW, COL, chamber, btn):
        self.SaveCSV(chamber)
        self.Save(chamber)
        self.strawUpload(chamber)
        self.chambers_status[ROW][COL] = "empty"
        self.leak_rate[chamber] = 0
        self.leak_rate_err[chamber] = 0
        self.leak_rate[chamber] = 0
        self.leak_rate_err[chamber] = 0
        self.passed[chamber] = "U"
        self.NoStraw(ROW, COL)
        # self.UnloadUpdate.emit(chamber, btn)
        self.UnloadUpdate.emit(chamber)

    def unloadActionNoSaving(self, ROW, COL, chamber, btn):
        self.deleteFiles(ROW, COL)
        self.chambers_status[ROW][COL] = "empty"
        self.leak_rate[chamber] = 0
        self.leak_rate_err[chamber] = 0
        self.leak_rate[chamber] = 0
        self.leak_rate_err[chamber] = 0
        self.passed[chamber] = "U"
        self.NoStraw(ROW, COL)
        # self.UnloadUpdate.emit(chamber, btn)
        self.UnloadUpdate.emit(chamber)

    def NoStraw(self, ROW, COL):
        """Initialize chambers with no straws loaded"""
        wasrunning = bool()
        if self._running[ROW] == True:
            wasrunning = True
            self._running[ROW] = False
        else:
            wasrunning == False
        straw = "empty%s" % ((ROW) * 5 + COL)
        self.Choosenames[ROW][COL] = straw
        self.update_name(ROW, COL)
        self._running[ROW] = wasrunning

    def ChangeStraw(self, chamber):
        """Update chamber contents with barcode scan or keyboard"""
        ROW = int(chamber / 5)
        COL = chamber % 5

        if self._running[ROW] == True:
            wasrunning = True
            self._running[ROW] = False
        else:
            wasrunning == False

        ctr = StrawSelect()  ## Generate pop-up window for straw selection
        ctr.exec_()  ## windowModality = ApplicationModal. Main GUI blocked when pop-up is open
        straw = str(ctr.straw_load)
        self.StrawLabels[chamber].setText(straw)
        if straw == "empty":  # Empty chamber
            straw = "empty%s" % chamber
            self.Choosenames[ROW][COL] = straw
        else:
            self.Choosenames[ROW][COL] = (
                straw
                + "_chamber%.0f_" % chamber
                + datetime.datetime.now().strftime("%Y_%m_%d")
            )
            self.starttime[chamber] = 0
        self.update_name(ROW, COL)
        self._running[ROW] = wasrunning

    def update_name(self, ROW, COL):
        """Change file name based on chamber contents"""
        chamber = ROW * 5 + COL
        filename = self.networkDirectory + self.Choosenames[ROW][COL]
        self.files[chamber] = filename + "_rawdata.txt"
        x = open(self.files[chamber], "a+", 1)
        print("Saving data to file %s" % self.Choosenames[ROW][COL])

    def Plot(self, btn):
        """Make and display a copy of the fitted data"""
        chamber = int(btn.objectName().strip("PdfButton"))
        ROW = int(chamber / 5)
        COL = chamber % 5
        # print('Plotting data for chamber', chamber)
        filepath = (
            self.networkDirectory + self.Choosenames[ROW][COL] + "_fit.pdf"
        )  ## Data is still being saved here. Don't open
        filepath_temp = (
            self.networkDirectory + self.Choosenames[ROW][COL] + "_fit_temp.pdf"
        )  ## Static snapshot. Safe to open
        if os.path.exists(filepath_temp):
            try:
                os.system(
                    "TASKKILL /F /IM AcroRd32.exe"
                )  ## ?Possibly find a better way to close file
            except:
                openplots = None
        if os.path.exists(filepath):
            shutil.copyfile(str(filepath), str(filepath_temp))
            os.startfile(filepath_temp, "open")
        else:
            print("No fit yet for chamber", chamber, "data. Wait for more data.")

    def Change_worker_ID(self, btn):
        label = btn.text()
        portalNum = 0
        if label == "Log In":
            portalNum = int(btn.objectName().strip("portal")) - 1
            Current_worker, ok = QInputDialog.getText(
                self, "Worker Log In", "Scan your worker ID:"
            )
            if not ok:
                return

            if len(self.sessionWorkers) == 0:
                self.previousSessionWorkers = []
                self.previousSessionWorkers.append(Current_worker)

            self.sessionWorkers.append(Current_worker)

            self.Current_workers[portalNum].setText(Current_worker)
            btn.setText("Log Out")
            # self.ui.tabWidget.setCurrentIndex(1)
        elif label == "Log Out":
            portalNum = int(btn.objectName().strip("portal")) - 1
            Current_worker = self.Current_workers[portalNum].text()
            self.justLogOut = self.Current_workers[portalNum].text()
            self.sessionWorkers.remove(Current_worker)

            if len(self.sessionWorkers) > 0:
                self.previousSessionWorkers.remove(Current_worker)

            Current_worker = ""
            self.Current_workers[portalNum].setText(Current_worker)
            btn.setText("Log In")
        self.saveWorkers()
        self.justLogOut = ""

    def lockGUI(self, credentials):
        if credentials:
            self.ui.tabWidget.setTabText(1, "Leak Test")
            self.ui.tabWidget.setTabEnabled(1, True)
        else:
            self.ui.tabWidget.setTabText(1, "Leak Test *Locked*")
            self.ui.tabWidget.setTabEnabled(1, False)

    def SaveCSV(self, chamber):
        """Save data to CSV file after straw passes or fails"""
        ROW = int(chamber / 5)
        COL = chamber % 5

        path = self.networkDirectory + "Leak Test Results.csv"

        Current_worker = self.getWorker()

        if self.Choosenames[ROW][COL][:7] in self.straw_list:
            print(
                "Data for straw %s in chamber %s already saved"
                % (self.Choosenames[ROW][COL][:7], chamber)
            )
        else:
            self.straw_list.append(self.Choosenames[ROW][COL][:7])
            currenttime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.result, "r+", 1) as result:
                begining = result.read(1)
                first = False
                if begining == "":
                    first = True
                result.close()
            with open(self.result, "a+", 1) as result:
                if not first:
                    result.write("\n")
                print("Saving chamber %s data to CSV file" % chamber)
                result.write(self.Choosenames[ROW][COL][:7] + ",")
                # result.write(self.StrawLabels[chamber].text() + ",")
                result.write(currenttime + ",")
                result.write("CO2" + ",")
                result.write(Current_worker + ",")
                result.write("chamber" + str(chamber) + ",")
                # print(self.leak_rate)
                result.write(str(self.leak_rate[chamber]) + ",")
                result.write(str(self.leak_rate_err[chamber]))
                # result.close()

            # Write to network
            with open(path, "r+", 1) as result:
                begining = result.read(1)
                first = False
                if begining == "":
                    first = True
                result.close()
            with open(path, "a+", 1) as result:
                if not first:
                    result.write("\n")
                print("Saving chamber %s data to CSV file" % chamber)
                result.write(self.Choosenames[ROW][COL][:7] + ",")
                # result.write(self.StrawLabels[chamber].text() + ",")
                result.write(currenttime + ",")
                result.write("CO2" + ",")
                result.write(Current_worker + ",")
                result.write("chamber" + str(chamber) + ",")
                # print(self.leak_rate)
                result.write(str(self.leak_rate[chamber]) + ",")
                result.write(str(self.leak_rate_err[chamber]))

    def closeEvent(self, event):
        # print("Terminate leak tests and data collection?")
        quit_msg = "Are you sure you want to exit the program?"
        reply = QMessageBox.question(
            self, "Message", quit_msg, QMessageBox.Yes, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            event.accept()
            sys.exit(0)
        else:
            event.ignore()

    def Save(self, chamber):
        # Save data to .csv file under Pallets
        ROW = int(chamber / 5)
        COL = chamber % 5

        strawname = self.Choosenames[ROW][COL][:7]

        if len(self.sessionWorkers) > 0:
            workers = self.sessionWorkers
        else:
            workers = self.previousSessionWorkers

        result = self.passed[chamber]

        UpdateStrawInfo("leak", workers, strawname, result)

    def checkCredentials(self):
        return self.credentialChecker.checkCredentials(self.sessionWorkers)

    def saveWorkers(self):
        previousWorkers = []
        activeWorkers = []
        exists = os.path.exists(
            self.workerDirectory + datetime.datetime.now().strftime("%Y-%m-%d") + ".csv"
        )
        if exists:
            with open(
                self.workerDirectory
                + datetime.datetime.now().strftime("%Y-%m-%d")
                + ".csv",
                "r",
            ) as previous:
                today = csv.reader(previous)
                for row in today:
                    previousWorkers = []
                    for worker in row:
                        previousWorkers.append(worker)
        for i in range(len(self.Current_workers)):
            if self.Current_workers[i].text() != "":
                activeWorkers.append(self.Current_workers[i].text())
        for prev in previousWorkers:
            already = False
            for act in activeWorkers:
                if prev == act:
                    already = True
            if not already:
                if prev != self.justLogOut:
                    activeWorkers.append(prev)
        with open(
            self.workerDirectory
            + datetime.datetime.now().strftime("%Y-%m-%d")
            + ".csv",
            "a+",
        ) as workers:
            if exists:
                workers.write("\n")
            if len(activeWorkers) == 0:
                workers.write(",")
            for i in range(len(activeWorkers)):
                workers.write(activeWorkers[i])
                if i != len(activeWorkers) - 1:
                    workers.write(",")

    def openLogInDialog(self):
        QMessageBox.warning(self, "Login Required", "Please login to complete action")
        self.ui.tabWidget.setCurrentIndex(0)

    def getWorker(self):
        if len(self.sessionWorkers) > 0:
            return self.sessionWorkers[0]
        else:
            return self.previousSessionWorkers[0]

    def getCPALS(self):
        self.cpals = []

        with open(self.cpalDirectory, "r") as f:
            line = f.readline()

            line = line.translate({ord(c): None for c in "\n"})

            while line != "":
                if line not in self.cpals:
                    self.cpals.append(line)

                line = f.readline()
                line = line.translate({ord(c): None for c in "\n"})

        for chamber in range(0, self.max_chambers):
            ROW = int(chamber / 5)
            COL = chamber % 5

            if self.Choosenames[ROW][COL][:5] != "empty":
                strawname = self.Choosenames[ROW][COL][:7]

                try:
                    cpal = FindCPAL(strawname)[1]
                    if cpal not in self.cpals:
                        self.cpals.append(cpal)
                except StrawNotFoundError:
                    continue

        return

    def strawUpload(self, chamber):
        ROW = int(chamber / 5)
        COL = chamber % 5

        strawname = self.Choosenames[ROW][COL][:7]
        # strawname = strawname.upper()

        uploadWorker = self.getWorker()

        leakrate = self.leak_rate[chamber]
        uncertainty = self.leak_rate_err[chamber]
        currenttime = datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")
        (_, cpal) = FindCPAL(strawname)

        uploader = getUploader(self.stationID)("prod")

        try:
            uploader.beginUpload(
                strawname,
                uploadWorker,
                leakrate,
                uncertainty,
                currenttime,
                chamber,
                cpal,
            )
        except UploadFailedError as error:
            self.FailedUpload.emit(strawname, error.message)

    def editPallet(self):
        if self.checkCredentials():
            self.getCPALS()
            rem = removeStraw(
                self.cpals, os.path.dirname(__file__) + "..\\..\\..\\Data\\Pallets\\"
            )
            rem.exec_()
        else:
            self.openLogInDialog()

    def strawsTesting(self):
        for chamber in range(0, self.max_chambers):
            ROW = int(chamber / 5)
            COL = chamber % 5

            if self.Choosenames[ROW][COL][:5] != "empty":
                return True
        return False

    def testThreads(self, name):
        for threads in threading.enumerate():
            if threads.name == name:
                return True

        return False

    def dataCollection(self):
        while True:
            if any(self._running):
                self.handleStart()

            time.sleep(0.01)
            app.processEvents()

    def setArduinoStart(self, ROW, state):
        if state:
            self.Arduinos[ROW].setStyleSheet("background-color: rgb(0, 170, 0);")

        else:
            self.Arduinos[ROW].setStyleSheet("background-color: rgb(170, 0, 0);")

    def setStrawProcessing(self, chamber):
        self.Chambers[chamber].setStyleSheet("background-color: rgb(225, 225, 0);")

    def setEnablePlot(self, chamber):
        for x in self.ui.PdfButtons.buttons():
            if int(x.objectName().strip("PdfButton")) == chamber:
                x.setEnabled(True)

    def setLargeLeak(self, chamber):
        self.ChamberLabels[chamber].setText("Large Leak!")
        self.Chambers[chamber].setStyleSheet("background-color: rgb(225, 40, 40);")

    def setStrawStatus(self, chamber, passed):
        if passed:
            self.Chambers[chamber].setStyleSheet("background-color: rgb(40, 225, 40);")
        else:
            self.Chambers[chamber].setStyleSheet("background-color: rgb(225, 40, 40);")

    def setToggleRemoved(self, status):
        self.ui.RemoveButton.setEnabled(status)

    def setUpdateStrawText(self, chamber):
        self.ChamberLabels[chamber].setText(
            str(
                "%.2f ± %.2f"
                % (
                    (self.leak_rate[chamber] * (10 ** 5)),
                    self.leak_rate_err[chamber] * (10 ** 5),
                )
            )
        )

    def setFailedUpload(self, strawname, message):
        QMessageBox.warning(
            self, "Upload Error", strawname + " failed upload\n" + message
        )

    def setUnloadUpdate(self, chamber):
        self.ChamberLabels[chamber].setText("Empty")
        self.StrawLabels[chamber].setText("No straw")

        for b in self.ui.ActionButtons.buttons():
            if int(b.objectName().strip("ActionButton")) == chamber:
                btn = b

        btn.setText("Load")
        self.Chambers[chamber].setStyleSheet("background-color: rgb(149, 186, 255)")

        for x in self.ui.PdfButtons.buttons():
            if int(x.objectName().strip("PdfButton")) == chamber:
                x.setDisabled(True)

    def signalChecking(self):
        changed = False
        signal = False
        while True:
            self.getCPALS()
            pallets_testing = self.cpals != []

            if pallets_testing and not signal or (not pallets_testing and signal):
                self.ToggleRemoved.emit(pallets_testing)
                signal = not signal

            credentials = self.checkCredentials()

            if (
                (credentials and not changed) or (not credentials and changed)
            ) and not any(self._running):
                self.LockGUI.emit(credentials)
                changed = not changed


class StrawSelect(QDialog):
    """Pop-up window for entering straw barcode"""

    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.show()
        # *****change Max length back to 7 for production*****
        self.ui.lineEdit.setMaxLength(7)
        self.straw_load = "empty"
        self.ui.okayButton.clicked.connect(self.StrawInput)
        self.ui.cancelButton.clicked.connect(self.Cancel)

    def StrawInput(self):
        self.straw_load = self.ui.lineEdit.text().upper()
        if (
            self.straw_load[:2] == "st"
            or self.straw_load[:2] == "ST"
            and all(ch.isdigit() for ch in self.straw_load[2:])
        ):
            try:
                checkStraw(self.straw_load, "C-O2", "leak")
                print("Straw", self.straw_load, "loaded")
                self.deleteLater()
            except StrawRemovedError:
                QMessageBox.critical(
                    self, "Testing Error", "Unable to test straw:\nStraw was removed"
                )
            except StrawNotFoundError:
                QMessageBox.critical(
                    self,
                    "Testing Error",
                    "Unable to test straw:\nStraw was not found in pallet files",
                )
            except StrawNotTestedError:
                QMessageBox.critical(
                    self,
                    "Testing Error",
                    "Unable to test straw:\nPrevious step was not performed or documented",
                )
            except StrawFailedError as error:
                QMessageBox.critical(
                    self, "Testing Error", "Unable to test straw:\n" + error.message
                )
        else:
            print("Not a valid straw barcode. Try formatting like st00023.")
            self.straw_load = "empty"

    def Cancel(self):
        self.straw_load = "empty"


class WorkerID(QDialog):
    """Pop-up window for entering worker ID"""

    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialogw()
        self.ui.setupUi(self)
        self.show()
        self.Worker_ID = "Unknown worker"
        self.ui.lineEdit.setMaxLength(13)
        self.ui.okayButton.clicked.connect(self.WorkerIDInput)

    def WorkerIDInput(self):
        self.Worker_ID = self.ui.lineEdit.text()
        if True:
            print("Welcome", self.Worker_ID + "!")
            self.deleteLater()
        else:
            print("Not a valid worker ID.")
            self.Worker_ID = "Unknown worker"


class removeStraw(QDialog):
    def __init__(self, CPALS, palletDirectory, webapp=None, parent=None):
        super(removeStraw, self).__init__(parent)
        self.ui = Ui_DialogBox()
        self.ui.setupUi(self)
        self.palletDirectory = palletDirectory
        self.sessionWorkers = []
        self.CPALS = CPALS

        self.strawLabels = [
            self.ui.straw_1,
            self.ui.straw_2,
            self.ui.straw_3,
            self.ui.straw_4,
            self.ui.straw_5,
            self.ui.straw_6,
            self.ui.straw_7,
            self.ui.straw_8,
            self.ui.straw_9,
            self.ui.straw_10,
            self.ui.straw_11,
            self.ui.straw_12,
            self.ui.straw_13,
            self.ui.straw_14,
            self.ui.straw_15,
            self.ui.straw_16,
            self.ui.straw_17,
            self.ui.straw_18,
            self.ui.straw_19,
            self.ui.straw_20,
            self.ui.straw_21,
            self.ui.straw_22,
            self.ui.straw_23,
            self.ui.straw_24,
        ]
        self.pfLabels = [
            self.ui.pf_1,
            self.ui.pf_2,
            self.ui.pf_3,
            self.ui.pf_4,
            self.ui.pf_5,
            self.ui.pf_6,
            self.ui.pf_7,
            self.ui.pf_8,
            self.ui.pf_9,
            self.ui.pf_10,
            self.ui.pf_11,
            self.ui.pf_12,
            self.ui.pf_13,
            self.ui.pf_14,
            self.ui.pf_15,
            self.ui.pf_16,
            self.ui.pf_17,
            self.ui.pf_18,
            self.ui.pf_19,
            self.ui.pf_20,
            self.ui.pf_21,
            self.ui.pf_22,
            self.ui.pf_23,
            self.ui.pf_24,
        ]

        self.ui.removeButtons.buttonClicked.connect(self.delete)
        self.ui.moveButtons.buttonClicked.connect(self.moveStraw)
        self.ui.addButtons.buttonClicked.connect(self.addStraw)
        self.ui.Menu.currentIndexChanged.connect(self.selectionChange)
        self.updateMenu()

    def getPallet(self, CPAL, path=""):
        lastTask = ""
        straws = []
        passfail = []

        if path == "":
            for palletid in os.listdir(self.palletDirectory):
                for pallet in os.listdir(self.palletDirectory + palletid + "\\"):
                    if CPAL + ".csv" == pallet:
                        with open(
                            self.palletDirectory + palletid + "\\" + pallet, "r"
                        ) as file:
                            dummy = csv.reader(file)
                            history = []
                            for line in dummy:
                                if line != []:
                                    history.append(line)
                            lastTask = history[len(history) - 1][1]
                            for entry in range(len(history[len(history) - 1])):
                                if entry > 1 and entry < 50:
                                    if entry % 2 == 0:
                                        if (
                                            history[len(history) - 1][entry]
                                            == "_______"
                                        ):
                                            straws.append("Empty")
                                        else:
                                            straws.append(
                                                history[len(history) - 1][entry]
                                            )
                                    else:
                                        if history[len(history) - 1][entry] == "P":
                                            passfail.append("Pass")
                                        elif history[len(history) - 1][entry] == "_":
                                            passfail.append("Incomplete")
                                        else:
                                            passfail.append("Fail")
                        break
        else:
            with open(path, "r") as file:
                dummy = csv.reader(file)
                history = []
                for line in dummy:
                    if line != []:
                        history.append(line)
                lastTask = history[len(history) - 1][1]
                for entry in range(len(history[len(history) - 1])):
                    if entry > 1 and entry < 50:
                        if entry % 2 == 0:
                            if history[len(history) - 1][entry] == "_______":
                                straws.append("Empty")
                            else:
                                straws.append(history[len(history) - 1][entry])
                        else:
                            if history[len(history) - 1][entry] == "P":
                                passfail.append("Pass")
                            elif history[len(history) - 1][entry] == "_":
                                passfail.append("Incomplete")
                            else:
                                passfail.append("Fail")

        return CPAL, lastTask, straws, passfail

    def displayPallet(self, CPAL, lastTask, straws, passfail):
        # self.ui.palletLabel.setText('Pallet: ' + CPAL)
        steps1 = ["prep", "ohms", "C-O2", "infl", "leak", "lasr", "leng", "silv"]
        steps2 = [
            "Straw Prep",
            "Resistance",
            "CO2 End Pieces",
            "Inflation",
            "Leak Rate",
            "Laser Cut",
            "Length",
            "Silver Epoxy",
        ]
        self.ui.lastLabel.setText("Last Step: " + steps2[steps1.index(lastTask)])
        for pos in range(len(self.strawLabels)):
            self.strawLabels[pos].setText(straws[pos])
        for pos in range(len(self.pfLabels)):
            self.pfLabels[pos].setText(passfail[pos])

    def delete(self, btn):
        pos = int(btn.objectName().strip("remove_")) - 1
        CPAL, lastTask, straws, passfail = self.getPallet(self.ui.Menu.currentText())
        if straws[pos] == "Empty":
            return
        buttonReply = QMessageBox.question(
            self,
            "Straw Removal Confirmation",
            "Are you sure you want \
to permanently remove "
            + straws[pos]
            + " from "
            + CPAL
            + " ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if buttonReply != QMessageBox.Yes:
            return
        for palletid in os.listdir(self.palletDirectory):
            for pallet in os.listdir(self.palletDirectory + palletid + "\\"):
                if CPAL + ".csv" == pallet:
                    with open(
                        self.palletDirectory + palletid + "\\" + pallet, "a"
                    ) as file:
                        file.write("\n")
                        file.write(
                            datetime.datetime.now().strftime("%Y-%m-%d_%H:%M") + ","
                        )
                        file.write(lastTask + ",")
                        for place in range(len(straws)):
                            if place == pos:
                                file.write("_______,_,")
                                continue
                            if straws[place] == "Empty":
                                file.write("_______,_,")
                                continue
                            file.write(straws[place] + ",")
                            if passfail[place] == "Pass":
                                file.write("P,")
                            elif passfail[place] == "Incomplete":
                                file.write("_,")
                            else:
                                file.write("F,")
                        i = 0
                        for worker in self.sessionWorkers:
                            file.write(worker)
                            if i != len(self.sessionWorkers) - 1:
                                file.write(",")
                            i = i + 1
        CPAL, lastTask, straws, passfail = self.getPallet(CPAL)
        self.displayPallet(CPAL, lastTask, straws, passfail)

    def moveStraw(self, btn):
        pos = int(btn.objectName().strip("move_")) - 1
        CPAL, lastTask, straws, passfail = self.getPallet(
            self.ui.palletLabel.text()[8:]
        )
        if straws[pos] == "Empty":
            return
        items = ("This Pallet", "Another Pallet")
        item, okPressed = QInputDialog.getItem(
            self,
            "Move Straw",
            "Where would you like to move this straw to?",
            items,
            0,
            False,
        )
        if not okPressed:
            return
        if item == "This Pallet":
            newpos, okPressed = QInputDialog.getInt(
                self, "Move Straw", "New Straw Position:", pos, 0, 23, 1
            )
            if not okPressed:
                return
            if straws[newpos] != "Empty":
                buttonReply = QMessageBox.critical(
                    self,
                    "Move Error",
                    "Position "
                    + str(newpos)
                    + " is already \
                filled by straw "
                    + straws[newpos]
                    + " .",
                    QMessageBox.Ok | QMessageBox.Cancel,
                    QMessageBox.Cancel,
                )
                return
            buttonReply = QMessageBox.question(
                self,
                "Straw Move Confirmation",
                "Are you sure you want to move "
                + straws[pos]
                + " from position "
                + str(pos)
                + " to position "
                + str(newpos)
                + " ?",
                QMessageBox.Ok | QMessageBox.Cancel,
                QMessageBox.Cancel,
            )
            if buttonReply != QMessageBox.Ok:
                return

            found, valid, path = self.validCPAL(CPAL)

            with open(path, "a") as file:
                file.write("\n")
                file.write(datetime.now().strftime("%Y-%m-%d_%H:%M") + ",")
                file.write(lastTask + ",")
                for place in range(len(straws)):
                    if place == pos:
                        file.write("_______,_,")
                        continue
                    if place == newpos:
                        file.write(straws[pos] + ",")
                        if passfail[pos] == "Pass":
                            file.write("P,")
                        elif passfail[pos] == "Incomplete":
                            file.write("_,")
                        else:
                            file.write("F,")
                        continue
                    if straws[place] == "Empty":
                        file.write("_______,_,")
                        continue
                    file.write(straws[place] + ",")
                    if passfail[place] == "Pass":
                        file.write("P,")
                    elif passfail[place] == "Incomplete":
                        file.write("_,")
                    else:
                        file.write("F,")
                file.write(",".join(self.sessionWorkers))

        if item == "Another Pallet":
            found, valid, path = self.validCPAL(CPAL)
            newpal, okPressed = QInputDialog.getText(
                self,
                "Move Straw",
                "Scan the pallet number of the pallet the straw will be moved to:",
                QLineEdit.Normal,
                "",
            )

            valid = self.validateCPALNumber(newpal)
            again = True

            while not valid and again:
                newpal, again = QInputDialog.getText(
                    self,
                    "Add Straw",
                    "INVALID CPAL NUMBER\nCPAL numbers have the form CPAL####.\n\nScan the pallet number of the pallet the straw will be moved to:",
                    QLineEdit().Normal,
                    "",
                )
                valid = self.validateStrawNumber(newstraw)

            if not valid and not again:
                return

            found, valid, newpath = self.validCPAL(newpal)
            again = True

            while not found and again:
                newpal, again = QInputDialog.getText(
                    self,
                    "Add Straw",
                    "INVALID CPAL NUMBER\nUnable to locate the pallet file for the CPAL specified.\n\nScan the pallet number of the pallet the straw will be moved to:",
                    QLineEdit().Normal,
                    "",
                )
                found, valid, path = self.validCPAL(newpal)

            if not found and not again:
                return

            if not okPressed:
                return

            newpal, newlastTask, newstraws, newpassfail = self.getPallet(
                newpal, newpath
            )

            if newlastTask != lastTask:
                buttonReply = QMessageBox.critical(
                    self,
                    "Move Error",
                    "Pallet "
                    + CPAL
                    + " and pallet "
                    + newpal
                    + " are at different stages of production.",
                    QMessageBox.Ok | QMessageBox.Cancel,
                    QMessageBox.Cancel,
                )
                return

            newpos, okPressed = QInputDialog.getInt(
                self,
                "Move Straw",
                "New Straw Position on " + newpal + ":",
                pos,
                0,
                23,
                1,
            )

            if not okPressed:
                return

            if newstraws[newpos] != "Empty":
                buttonReply = QMessageBox.critical(
                    self,
                    "Move Error",
                    "Position "
                    + str(newpos)
                    + " is already filled by straw "
                    + newstraws[newpos]
                    + " .",
                    QMessageBox.Ok | QMessageBox.Cancel,
                    QMessageBox.Cancel,
                )
                return

            with open(newpath, "a") as file:
                file.write("\n")
                file.write(datetime.now().strftime("%Y-%m-%d_%H:%M") + ",")
                file.write("adds,")
                for place in range(len(newstraws)):
                    if place == newpos:
                        file.write(straws[pos] + "," + CPAL + ",")
                    else:
                        file.write("_______,_,")
                ",".join(self.sessionWorkers)

                file.write("\n")
                file.write(datetime.now().strftime("%Y-%m-%d_%H:%M") + ",")
                file.write(newlastTask + ",")
                for place in range(len(newstraws)):
                    if place == newpos:
                        file.write(straws[pos] + ",")
                        if passfail[pos] == "Pass":
                            file.write("P,")
                        elif passfail[pos] == "Incomplete":
                            file.write("_,")
                        else:
                            file.write("F,")
                        continue
                    if newstraws[place] == "Empty":
                        file.write("_______,_,")
                        continue
                    file.write(newstraws[place] + ",")
                    if newpassfail[place] == "Pass":
                        file.write("P,")
                    elif newpassfail[place] == "Incomplete":
                        file.write("_,")
                    else:
                        file.write("F,")
                file.write(",".join(self.sessionWorkers))

                with open(path, "a") as file:
                    file.write("\n")
                    file.write(datetime.now().strftime("%Y-%m-%d_%H:%M") + ",")
                    file.write(lastTask + ",")
                    for place in range(len(straws)):
                        if place == pos:
                            file.write("_______,_,")
                            continue
                        if straws[place] == "Empty":
                            file.write("_______,_,")
                            continue
                        file.write(straws[place] + ",")
                        if passfail[place] == "Pass":
                            file.write("P,")
                        elif passfail[place] == "Incomplete":
                            file.write("_,")
                        else:
                            file.write("F,")
                    file.write(",".join(self.sessionWorkers))

        CPAL, lastTask, straws, passfail = self.getPallet(CPAL, path)
        self.displayPallet(CPAL, lastTask, straws, passfail)

    def addStraw(self, btn):
        add = False
        pos = int(btn.objectName().strip("add_")) - 1
        CPAL = self.ui.palletLabel.text()[8:]
        found, valid, path = self.validCPAL(CPAL)
        CPAL, lastTask, straws, passfail = self.getPallet(CPAL, path)
        passFailDict = dict(zip(straws, passfail))

        if straws[pos] == "Empty":
            add = True

        items = ("Parent Straw", "Another Pallet")
        item, okPressed = QInputDialog.getItem(
            self, "Add Straw", "Where are you adding the straw from?", items, 0, False
        )

        if okPressed:
            newstraw, okPressed = QInputDialog.getText(
                self,
                "Add Straw",
                "Scan the straw number of the new straw:",
                QLineEdit().Normal,
                "",
            )

            if okPressed:
                valid = self.validateStrawNumber(newstraw)
                again = True

                while not valid and again:
                    newstraw, again = QInputDialog.getText(
                        self,
                        "Add Straw",
                        "INVALID STRAW NUMBER\nStraw numbers have the form ST#####.\n\nScan the straw number of the new straw:",
                        QLineEdit().Normal,
                        "",
                    )
                    valid = self.validateStrawNumber(newstraw)

                if not valid and not again:
                    return

                if item == items[0]:
                    parent, okPressed = QInputDialog.getText(
                        self,
                        "Add Straw",
                        "Scan the straw number of the parent straw:",
                        QLineEdit.Normal,
                        "",
                    )

                    if okPressed:
                        valid = self.validateStrawNumber(parent)
                        again = True

                        while not valid and again:
                            parent, again = QInputDialog.getText(
                                self,
                                "Add Straw",
                                "INVALID STRAW NUMBER\nStraw numbers have the form ST#####.\n\nScan the straw number of the parent straw:",
                                QLineEdit().Normal,
                                "",
                            )
                            valid = self.validateStrawNumber(parent)

                        if not valid and not again:
                            return

                        valid = parent in straws
                        again = True

                        while not valid and again:
                            parent, again = QInputDialog.getText(
                                self,
                                "Add Straw",
                                f"INVALID STRAW NUMBER\nStraw {parent} was not found on {CPAL}.\n\nScan the straw number of the parent straw:",
                                QLineEdit().Normal,
                                "",
                            )
                            valid = parent in straws

                        if not valid and not again:
                            return

                        if not add:
                            reply = QMessageBox.warning(
                                self,
                                "Replacing Straw",
                                f"There is already a straw in position {pos + 1}.\n\nDo you wish to replace {straws[pos]} with {newstraw}?",
                                QMessageBox.Yes,
                                QMessageBox.No,
                            )

                            if reply == QMessageBox.Yes:
                                with open(path, "a") as file:
                                    file.write("\n")
                                    file.write(
                                        datetime.now().strftime("%Y-%m-%d_%H:%M") + ","
                                    )
                                    file.write(lastTask + ",")
                                    for place in range(len(straws)):
                                        if place == pos:
                                            file.write("_______,_,")
                                            continue
                                        if straws[place] == "Empty":
                                            file.write("_______,_,")
                                            continue
                                        file.write(straws[place] + ",")
                                        if passfail[place] == "Pass":
                                            file.write("P,")
                                        elif passfail[place] == "Incomplete":
                                            file.write("_,")
                                        else:
                                            file.write("F,")
                                    file.write(",".join(self.sessionWorkers))

                                    file.write("\n")
                                    file.write(
                                        datetime.now().strftime("%Y-%m-%d_%H:%M") + ","
                                    )
                                    for place in range(len(newstraws)):
                                        if place == pos:
                                            file.write(f"adds,{newstraw},{parent},")
                                        else:
                                            file.write("_______,_,")
                                    file.write(",".join(self.sessionWorkers))

                                    file.write("\n")
                                    file.write(
                                        datetime.now().strftime("%Y-%m-%d_%H:%M") + ","
                                    )
                                    file.write(lastTask + ",")
                                    for place in range(len(straws)):
                                        if place == pos:
                                            file.write(f"{newstraw},")
                                            if passFailDict[parent] == "Incomplete":
                                                file.write("_,")
                                            else:
                                                file.write(
                                                    f"{passFailDict[parent][0]},"
                                                )
                                            continue
                                        if straws[place] == "Empty":
                                            file.write("_______,_,")
                                            continue
                                        file.write(straws[place] + ",")
                                        if passfail[place] == "Pass":
                                            file.write("P,")
                                        elif passfail[place] == "Incomplete":
                                            file.write("_,")
                                        else:
                                            file.write("F,")
                                    file.write(",".join(self.sessionWorkers))
                        else:
                            with open(path, "a") as file:
                                file.write("\n")
                                file.write(
                                    datetime.now().strftime("%Y-%m-%d_%H:%M") + ","
                                )
                                for place in range(len(straws)):
                                    if place == pos:
                                        file.write(f"adds,{newstraw},{parent},")
                                    else:
                                        file.write("_______,_,")
                                file.write(",".join(self.sessionWorkers))

                                file.write("\n")
                                file.write(
                                    datetime.now().strftime("%Y-%m-%d_%H:%M") + ","
                                )
                                file.write(lastTask + ",")
                                for place in range(len(straws)):
                                    if place == pos:
                                        file.write(f"{newstraw},")
                                        if passFailDict[parent] == "Incomplete":
                                            file.write("_,")
                                        else:
                                            file.write(f"{passFailDict[parent][0]},")
                                        continue
                                    if straws[place] == "Empty":
                                        file.write("_______,_,")
                                        continue
                                    file.write(straws[place] + ",")
                                    if passfail[place] == "Pass":
                                        file.write("P,")
                                    elif passfail[place] == "Incomplete":
                                        file.write("_,")
                                    else:
                                        file.write("F,")
                                file.write(",".join(self.sessionWorkers))

                else:
                    newpal, okPressed = QInputDialog.getText(
                        self,
                        "Add Straw",
                        "Scan the pallet number of the pallet the straw came from:",
                        QLineEdit.Normal,
                        "",
                    )

                    valid = self.validateCPALNumber(newpal)
                    again = True

                    while not valid and again:
                        newpal, again = QInputDialog.getText(
                            self,
                            "Add Straw",
                            "INVALID CPAL NUMBER\nCPAL numbers have the form CPAL####.\n\nScan the pallet number of the pallet the straw came from:",
                            QLineEdit().Normal,
                            "",
                        )
                        valid = self.validateStrawNumber(newstraw)

                    if not valid and not again:
                        return

                    found, valid, newpath = self.validCPAL(newpal)
                    again = True

                    while not found and again:
                        newpal, again = QInputDialog.getText(
                            self,
                            "Add Straw",
                            "INVALID CPAL NUMBER\nUnable to locate the pallet file for the CPAL specified.\n\nScan the pallet number of the pallet the straw will be moved to:",
                            QLineEdit().Normal,
                            "",
                        )
                        found, valid, path = self.validCPAL(newpal)

                    if not found and not again:
                        return

                    found, valid, newpath = self.validCPAL(newpal, newstraw)
                    again = True

                    while not valid and again:
                        newpal, again = QInputDialog.getText(
                            self,
                            "Add Straw",
                            f"INVALID CPAL NUMBER\nStraw {newstraw} not found in pallet file for {newpal}.\n\nScan the pallet number of the pallet the straw will be moved to:",
                            QLineEdit().Normal,
                            "",
                        )
                        found, valid, path = self.validCPAL(newpal)

                    if not valid and not again:
                        return

                    if okPressed:
                        newpal, newlastTask, newstraws, newpassfail = self.getPallet(
                            newpal, newpath
                        )
                        newPassFailDict = dict(zip(newstraws, newpassfail))

                        if newlastTask != lastTask:
                            buttonReply = QMessageBox.critical(
                                self,
                                "Move Error",
                                f"Pallet {CPAL} and pallet {newpal} are at different stages of production.",
                                QMessageBox.Ok,
                            )
                        else:
                            if not add:
                                reply = QMessageBox.warning(
                                    self,
                                    "Replacing Straw",
                                    f"There is already a straw in position {pos + 1}.\n\nDo you wish to replace {straws[pos]} with {newstraw}?",
                                    QMessageBox.Yes,
                                    QMessageBox.No,
                                )

                                with open(path, "a") as file:
                                    file.write("\n")
                                    file.write(
                                        datetime.now().strftime("%Y-%m-%d_%H:%M") + ","
                                    )
                                    file.write(lastTask + ",")
                                    for place in range(len(straws)):
                                        if place == pos:
                                            file.write("_______,_,")
                                            continue
                                        if straws[place] == "Empty":
                                            file.write("_______,_,")
                                            continue
                                        file.write(straws[place] + ",")
                                        if passfail[place] == "Pass":
                                            file.write("P,")
                                        elif passfail[place] == "Incomplete":
                                            file.write("_,")
                                        else:
                                            file.write("F,")
                                    file.write(",".join(self.sessionWorkers))

                                    file.write("\n")
                                    file.write(
                                        datetime.now().strftime("%Y-%m-%d_%H:%M") + ","
                                    )
                                    for place in range(len(newstraws)):
                                        if place == pos:
                                            file.write(f"adds,{newstraw},{newpal},")
                                        else:
                                            file.write("_______,_,")
                                    file.write(",".join(self.sessionWorkers))

                                    file.write("\n")
                                    file.write(
                                        datetime.now().strftime("%Y-%m-%d_%H:%M") + ","
                                    )
                                    file.write(lastTask + ",")
                                    for place in range(len(straws)):
                                        if place == pos:
                                            file.write(f"{newstraw},")
                                            if (
                                                newPassFailDict[newstraw]
                                                == "Incomplete"
                                            ):
                                                file.write("_,")
                                            else:
                                                file.write(
                                                    f"{newPassFailDict[newstraw][0]},"
                                                )
                                            continue
                                        if straws[place] == "Empty":
                                            file.write("_______,_,")
                                            continue
                                        file.write(straws[place] + ",")
                                        if passfail[place] == "Pass":
                                            file.write("P,")
                                        elif passfail[place] == "Incomplete":
                                            file.write("_,")
                                        else:
                                            file.write("F,")
                                    file.write(",".join(self.sessionWorkers))

                                with open(newpath, "a") as file:
                                    file.write("\n")
                                    file.write(
                                        datetime.now().strftime("%Y-%m-%d_%H:%M") + ","
                                    )
                                    file.write(newlastTask + ",")
                                    for place in range(len(newstraws)):
                                        if place == pos:
                                            file.write("_______,_,")
                                            continue
                                        if newstraws[place] == "Empty":
                                            file.write("_______,_,")
                                            continue
                                        file.write(newstraws[place] + ",")
                                        if newpassfail[place] == "Pass":
                                            file.write("P,")
                                        elif newpassfail[place] == "Incomplete":
                                            file.write("_,")
                                        else:
                                            file.write("F,")
                                    file.write(",".join(self.sessionWorkers))

                            else:
                                with open(path, "a") as file:
                                    file.write("\n")
                                    file.write(
                                        datetime.now().strftime("%Y-%m-%d_%H:%M") + ","
                                    )
                                    for place in range(len(newstraws)):
                                        if place == pos:
                                            file.write(f"adds,{newstraw},{newpal},")
                                        else:
                                            file.write("_______,_,")
                                    file.write(",".join(self.sessionWorkers))

                                    file.write("\n")
                                    file.write(
                                        datetime.now().strftime("%Y-%m-%d_%H:%M") + ","
                                    )
                                    file.write(lastTask + ",")
                                    for place in range(len(straws)):
                                        if place == pos:
                                            file.write(f"{newstraw},")
                                            if (
                                                newPassFailDict[newstraw]
                                                == "Incomplete"
                                            ):
                                                file.write("_,")
                                            else:
                                                file.write(
                                                    f"{newPassFailDict[newstraw][0]},"
                                                )
                                            continue
                                        if straws[place] == "Empty":
                                            file.write("_______,_,")
                                            continue
                                        file.write(straws[place] + ",")
                                        if passfail[place] == "Pass":
                                            file.write("P,")
                                        elif passfail[place] == "Incomplete":
                                            file.write("_,")
                                        else:
                                            file.write("F,")
                                    file.write(",".join(self.sessionWorkers))

                            with open(newpath, "a") as file:
                                file.write("\n")
                                file.write(
                                    datetime.now().strftime("%Y-%m-%d_%H:%M") + ","
                                )
                                file.write(newlastTask + ",")
                                for place in range(len(newstraws)):
                                    if place == pos:
                                        file.write("_______,_,")
                                        continue
                                    if newstraws[place] == "Empty":
                                        file.write("_______,_,")
                                        continue
                                    file.write(newstraws[place] + ",")
                                    if newpassfail[place] == "Pass":
                                        file.write("P,")
                                    elif newpassfail[place] == "Incomplete":
                                        file.write("_,")
                                    else:
                                        file.write("F,")
                                file.write(",".join(self.sessionWorkers))

            CPAL, lastTask, straws, passfail = self.getPallet(CPAL)

            if straws[pos] != "Empty":
                self.ui.moveButtons.buttons()[pos].setDisabled(False)
                self.ui.removeButtons.buttons()[pos].setDisabled(False)

            self.displayPallet(CPAL, lastTask, straws, passfail)

    def validateStrawNumber(self, straw):
        firstLetter = ["s", "S"]
        secondLetter = ["t", "T"]
        valid = True

        if len(straw) != 7:
            valid = False

        if valid and ((straw[0] not in firstLetter) and (straw[1] not in secondLetter)):
            valid = False

        if valid and not straw[2:].isdigit():
            valid = False

        return valid

    def validateCPALNumber(self, CPAL):
        start = "CPAL"
        valid = True

        if len(CPAL) != 8:
            valid = False

        if valid and CPAL[:4].upper() != start:
            valid = False

        if valid and not CPAL[4:].isdigit():
            valid = False

        return valid

    def validCPAL(self, CPAL, straw="ST"):
        found = False
        valid = False
        path = ""

        for palletid in os.listdir(self.palletDirectory):
            for pallet in os.listdir(self.palletDirectory + palletid + "\\"):
                if CPAL + ".csv" == pallet:
                    found = True

                    with open(
                        self.palletDirectory + palletid + "\\" + pallet, "r"
                    ) as file:
                        path = self.palletDirectory + palletid + "\\" + pallet
                        old_line = ""
                        line = file.readline()

                        while line != "\n" and line != "":
                            old_line = line
                            line = file.readline()

                        if straw in old_line:
                            valid = True
                    break

        return found, valid, path

    def updateMenu(self):
        for i in self.CPALS:
            self.ui.Menu.addItem(i)

    def selectionChange(self):
        CPAL, lastTask, straws, passfail = self.getPallet(self.ui.Menu.currentText())
        self.displayPallet(CPAL, lastTask, straws, passfail)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)
    sys.exit()


if __name__ == "__main__":
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    lts = LeakTestStatus("COM11", 115200, arduino_input=True)
    lts.show()
    app.exec_()
