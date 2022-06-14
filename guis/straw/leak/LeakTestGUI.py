################################################################################
#
# Straw Leak Test GUI
#
# Happens after prep, resistance, and CO2 endpiece steps.
#
# This process is not currently uploaded to the DB, all data is saved to txt
# files and pdfs only.
#
# Next step: consolidation/cutting
#
################################################################################
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
    QListWidgetItem,
)
import serial  ## Takes this from pyserial, not serial
import datetime
from guis.straw.leak.least_square_linear import *  ## Contributes fit functions
from guis.straw.leak.leakUI import Ui_MainWindow  ## Main GUI window
from guis.straw.leak.N0207a import Ui_Dialog  ## Pop-up GUI window for straw selection
from guis.straw.leak.WORKER import Ui_Dialogw
import inspect
from guis.straw.leak.WriteToFile import *  ## Functions to save to pallet file
import csv
from pathlib import Path

from data.workers.credentials.credentials import Credentials
from guis.straw.leak.remove import Ui_DialogBox
from guis.common.getresources import GetProjectPaths, GetStrawLeakInoPorts
from guis.common.save_straw_workers import saveWorkers
from guis.straw.leak.straw_leak_utilities import *
from guis.common.gui_utils import except_hook

# Import logger from Modules (only do this once)
from guis.common.panguilogger import SetupPANGUILogger

logger = SetupPANGUILogger("root", tag="Leak_Test")

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

    def __init__(self, paths, COM, baudrate, app, arduino_input=False):
        super(LeakTestStatus, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()
        ## Add a timeout (0.08 sec) to avoid freezing GUI while waiting for serial data from arduinos
        self.COM = GetStrawLeakInoPorts()
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

        self.leakDirectory = paths["strawleakdata"]
        self.palletDirectoryLTSclass = paths["palletsLTG"]
        self.leakDirectoryRaw = self.leakDirectory / "raw_data"
        self.leakDirectoryCom = self.leakDirectory / "comments"
        self.workerDirectory = paths["leakworkers"]

        self.starttime = 50 * [0]

        self.Choosenames = [
            ["empty0", "empty1", "empty2", "empty3", "empty4"],
            ["empty5", "empty6", "empty7", "empty8", "empty9"],
            ["empty10", "empty11", "empty12", "empty13", "empty14"],
            ["empty15", "empty16", "empty17", "empty18", "empty19"],
            ["empty20", "empty21", "empty22", "empty23", "empty24"],
            ["empty25", "empty26", "empty27", "empty28", "empty29"],
            ["empty30", "empty31", "empty32", "empty33", "empty34"],
            ["empty35", "empty36", "empty37", "empty38", "empty39"],
            ["empty40", "empty41", "empty45", "empty46", "empty47"],
            ["empty45", "empty46", "empty47", "empty48", "empty49"],
        ]

        self.chambers_status = [
            ["empty0", "empty1", "empty2", "empty3", "empty4"],
            ["empty5", "empty6", "empty7", "empty8", "empty9"],
            ["empty10", "empty11", "empty12", "empty13", "empty14"],
            ["empty15", "empty16", "empty17", "empty18", "empty19"],
            ["empty20", "empty21", "empty22", "empty23", "empty24"],
            ["empty25", "empty26", "empty27", "empty28", "empty29"],
            ["empty30", "empty31", "empty32", "empty33", "empty34"],
            ["empty35", "empty36", "empty37", "empty38", "empty39"],
            ["empty40", "empty41", "empty42", "empty43", "empty44"],
            ["empty45", "empty46", "empty47", "empty48", "empty49"],
        ]

        # dict of <chamber> : "<straw name>_rawdata.txt"
        self.files = {}
        # Passed straws with saved data
        self.straw_list = []
        self.result = GetProjectPaths()["leaktestresultsLTG"]

        # what are these next two lines for??
        result = open(self.result, "a+", 1)
        result.close()

        self.leak_rate = [0] * 50
        self.leak_rate_err = [0] * 50
        self.passed = ["U"] * 50

        # chamber volume occupied = chamber volume empty - straw volume
        for n in range(len(CHAMBER_VOLUME)):
            for m in range(len(CHAMBER_VOLUME[n])):
                CHAMBER_VOLUME[n][m] = CHAMBER_VOLUME[n][m] - STRAW_VOLUME

        self.max_time = (
            7200  # When time exceeds 2 hours stops fitting data (still saving it)
        )
        self.max_co2_level = (
            1800  # when ppm exceeds 1800 stops fitting and warns user of failure
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
        self.ui.PdfButtons.buttonClicked.connect(self.DisplayPlot)
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
        saveWorkers(self.workerDirectory, self.Current_workers, self.justLogOut)
        self.lockGUI(False)

        self.ui.commentSubmitPB.clicked.connect(self.makeComment)
        self.ui.lookupSubmitPB.clicked.connect(self.readComments)

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
        thread2 = threading.Thread(target=self.dataCollection, args=(app,))
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
            for COL in range(5):
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

    def read_arduino_line(self, row):
        # Check arduino connection, update GUI status, return if no connection
        if self.COM_con[row] == None:
            self.ArduinoStart.emit(row, None)
            return None

        self.ArduinoStart.emit(row, True)

        # Read the arduino line
        arduino_line = self.arduino[row].readline().strip()

        if arduino_line == b"":
            return None

        return arduino_line

    def parse_arduino_line(self, line, row):
        line = ["%5.2f" % float(member) for member in line.split()]
        ppm = float(line[1])
        col = int(float(line[0]))
        chamber = chamber_from_row_col(row, col)
        return chamber, ppm

    def write_raw_ppm_to_file(self, chamber, ppm):
        human_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        unix_time = time.time()

        with open(self.files[chamber], "a+", 1) as f:
            f.write(
                str(format(unix_time, ".0f"))
                + "\t"
                + str(chamber)
                + "\t"
                + ("%.0f" % ppm)
                + "\t"
                + str(human_datetime)
                + "\n"
            )
            f.flush()  ## Needed to send data in buffer to file

        return unix_time

    # (1) Read arduino data, (2) fit leak rate, (3) plot
    def handleStart(self):
        """Start data collection for all chambers connected to the Arduino"""
        # self.StrtData[0].setDisabled(True)
        # self._running[0] = True
        # for x in self.ui.ActionButtons.buttons():
        #    x.setEnabled(True)
        t_latest_measurement = 10 * [
            0
        ]  # time that the nth measurement was made for a row
        t_previous_measurement = 10 * [
            time.time()
        ]  # time that the n-1th measurement was made for a row
        n_consecutive_empty_readings = 10 * [
            0
        ]  # number of consecutive empty lines read for a row
        while any(self._running):
            i = 0
            ####################################################################
            # LOOP ROWS
            ####################################################################
            for tf in self._running:
                # cycles through rows
                row = i
                i = i + 1

                if self.testThreads("Buffer" + str(row)):
                    continue

                if tf != True:
                    continue

                # READ a single arduino line corresponding to one ppm
                # measured in one chamber.
                arduino_line = self.read_arduino_line(row)

                if not arduino_line:
                    n_consecutive_empty_readings[row] += 1

                    # if we've gotten many empty readings for this row in sequence,
                    # reconnect and reset the count of empty readings
                    if n_consecutive_empty_readings[row] > 60:
                        self.arduino[row].close()
                        self.Connect_Arduino(self.COM[row])
                        if self.COM_con[row] != None:
                            n_consecutive_empty_readings[row] = 0

                    continue

                n_consecutive_empty_readings[row] = 0

                # WRITE the ppm to a chamber-, date-specific file
                chamber, ppm = self.parse_arduino_line(arduino_line, row)

                t_latest_measurement[row] = self.write_raw_ppm_to_file(chamber, ppm)

                # FIT AND PLOT -- Loop chambers in this row. Read data from the
                # raw data files, measure leak rates, plot data + fits to pdf
                # files.

                # update the plots in this row no more than once every 15 sec
                if t_latest_measurement[row] < (t_previous_measurement[row] + 15.0):
                    continue

                t_previous_measurement[row] = t_latest_measurement[row]

                for col in range(5):
                    # cycles through columns
                    chamber = chamber_from_row_col(row, col)
                    ppm = []
                    ppm_err = []
                    timestamps = []
                    slope = 0
                    slope_err = 0
                    intercept = 0
                    intercept_err = 0
                    outfile = self.files[chamber]

                    # open the raw data readings for this chamber and save them
                    # in the ppm, ppm_err, and timestamps variables
                    timestamps, ppm, ppm_err = get_data_from_file(outfile)

                    try:
                        running_duration = timestamps[-1]
                    except IndexError:
                        running_duration = 0

                    # Chamber is empty -- go no further
                    # self.Choosenames[row][col] = "ST00854_chamber0_2021_06_15"
                    if str(self.Choosenames[row][col])[0:5] == "empty":
                        # print("No straw in chamber %.0f" % (chamber))
                        continue

                    # All chambers start with "processing" code U -> yellow
                    if self.passed[chamber] == "U":
                        self.StrawProcessing.emit(chamber)

                    # Not enough data for this chamber, skip it
                    if len(ppm) < MIN_N_DATAPOINTS_FOR_FIT:
                        # print("Straw %s in chamber %.0f is in preparation stage. Please wait for more data" %(self.Choosenames[row][col][:7],chamber))
                        # self.Chambers[chamber].setStyleSheet("background-color: rgb(225, 225, 0);")
                        # self.ChamberLabels[f].setText('Processing')
                        continue

                    # unlock the button that shows the leak plot for this chamber
                    self.EnablePlot.emit(chamber)

                    # If max ppm is larger than threshold and we haven't already passed,
                    # Then mark this chamber as a large leak (red) and skip it
                    if max(ppm) > self.max_co2_level and self.passed[chamber] != "P":
                        self.LargeLeak.emit(chamber)
                        self.leak_rate[chamber] = 100
                        continue

                    # if max(timestamps) > self.max_time :
                    #    print("Straw %s has been in Chamber %.0f for over 2 hours.  Data is saving but no longer fitting." %(self.Choosenames[row][col][:7],chamber))
                    #    continue

                    ############################################################
                    ############################################################
                    # Calculate leak rate and related parameters

                    slope, slope_err, intercept, intercept_err = get_fit(
                        timestamps,
                        ppm,
                        ppm_err,
                    )

                    self.leak_rate[chamber] = calculate_leak_rate(
                        slope, CHAMBER_VOLUME[row][col]
                    )

                    self.leak_rate_err[chamber] = calculate_leak_rate_err(
                        self.leak_rate[chamber],
                        slope,
                        slope_err,
                        CHAMBER_VOLUME[row][col],
                        CHAMBER_VOLUME_ERR[row][col],
                    )

                    # print("Leak rate for straw %s in chamber %.0f is %.2f +- %.2f CC per minute * 10^-5"
                    #% (self.Choosenames[row][col][:7],chamber,self.leak_rate[chamber] *(10**5),self.leak_rate_err[chamber]*(10**5)))
                    # self.ChamberLabels[chamber].setText(str('%.2f ± %.2f' % ((self.leak_rate[chamber]*(10**5)),self.leak_rate_err[chamber]*(10**5))))

                    # Write the leak rate to the GUI
                    self.UpdateStrawText.emit(chamber)

                    # pass, fail, or unknown
                    leak_status = evaluate_leak_rate(
                        len(ppm),
                        self.leak_rate[chamber],
                        self.leak_rate_err[chamber],
                        running_duration,
                    )

                    # Update the GUI given the pass-fail status
                    if leak_status == PassFailStatus.PASS:
                        self.StrawStatus.emit(chamber, True)
                    elif leak_status == PassFailStatus.FAIL:
                        self.StrawStatus.emit(chamber, False)
                    else:
                        pass

                    self.passed[chamber] = leak_status.value

                    title = self.Choosenames[row][col] + "_fit"
                    outfile = self.leakDirectoryRaw / title
                    outfile = outfile.with_suffix(".pdf")

                    plot(
                        title,
                        timestamps,
                        ppm,
                        slope,
                        slope_err,
                        intercept,
                        self.leak_rate[chamber],
                        self.leak_rate_err[chamber],
                        leak_status,
                        outfile,
                    )

                    ## Graph and save graph of fit
                # END loop over chambers
            # END while any(self._running)

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
        logger.debug(f"Load/Unload called for chamber {chamber}.")

        # if chamber is empty...(loading)
        # return after
        if self.chambers_status[ROW][COL][:5] == "empty":
            # ensure a credentialed worker is logged in
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
            # otherwise prompt log in
            else:
                self.openLogInDialog()
            return

        # else (chamber is not empty...)
        save_to_master = True  # save to the master leak rate spreadsheet?

        # Unload an unfinished straw - ask to save to master spreadsheet
        if self.passed[chamber] == "U":
            msg = "Has this straw conclusively failed leak test?"
            reply = QMessageBox.question(
                self,
                "Conclusive Failure",
                msg,
                QMessageBox.Yes,
                QMessageBox.No,
            )

            # Not a conclusive failure -- don't save to master spreadsheet
            if reply == QMessageBox.No:
                save_to_master = False

        thread = threading.Thread(
            target=self.unloadAction, args=(ROW, COL, chamber, btn, save_to_master)
        )
        thread.daemon = True  # Daemonize thread
        thread.start()

    def deleteFiles(self, ROW, COL):
        path1 = self.leakDirectoryRaw / str(self.Choosenames[ROW][COL] + "_rawdata.txt")
        path2 = self.leakDirectoryRaw / str(self.Choosenames[ROW][COL] + "_fit.pdf")
        path3 = self.leakDirectoryRaw / str(
            self.Choosenames[ROW][COL] + "_fit_temp.pdf"
        )

        if path1.is_file():
            os.remove(path1)

        if path2.is_file():
            os.remove(path2)

        if path3.is_file():
            os.remove(path3)

    def unloadAction(self, ROW, COL, chamber, btn, save_to_master=True):
        if save_to_master:
            self.SaveCSV(chamber)
        self.Save(chamber)
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
            wasrunning = False
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
            wasrunning = False

        ctr = StrawSelect(
            self.leakDirectory
        )  ## Generate pop-up window for straw selection
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

    def update_name(self, row, col):
        """Change file name based on chamber contents"""
        chamber = chamber_from_row_col(row, col)
        self.files[chamber] = self.leakDirectoryRaw / str(
            self.Choosenames[row][col] + "_rawdata.txt"
        )
        x = open(self.files[chamber], "a+", 1)
        x.close()
        logger.debug(f"Saving data to file {self.Choosenames[row][col]}")

    def DisplayPlot(self, btn):
        """Make and display a copy of the fitted data"""
        chamber = int(btn.objectName().strip("PdfButton"))
        ROW = int(chamber / 5)
        COL = chamber % 5
        # print('Plotting data for chamber', chamber)
        filepath = self.leakDirectoryRaw / str(
            self.Choosenames[ROW][COL] + "_fit.pdf"
        )  ## Data is still being saved here. Don't open
        filepath_temp = self.leakDirectoryRaw / str(
            self.Choosenames[ROW][COL] + "_fit_temp.pdf"
        )  ## Static snapshot. Safe to open
        if filepath_temp.is_file():
            try:
                os.system(
                    "TASKKILL /F /IM AcroRd32.exe"
                )  ## ?Possibly find a better way to close file
            except:
                openplots = None
        if filepath.is_file():
            shutil.copyfile(str(filepath), str(filepath_temp))
            os.startfile(filepath_temp, "open")
        else:
            logger.info(f"No fit yet for chamber {chamber} data. Wait for more data.")

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

            # update combo box with worker names (on comment tab)
            self.ui.workerSelectCB.clear()
            self.ui.workerSelectCB.addItems(self.sessionWorkers)

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
        saveWorkers(self.workerDirectory, self.Current_workers, self.justLogOut)
        self.justLogOut = ""

    def lockGUI(self, credentials):
        if credentials:
            self.ui.tabWidget.setTabText(1, "Leak Test")
            self.ui.tabWidget.setTabEnabled(1, True)
            self.ui.tabWidget.setTabText(2, "Comments")
            self.ui.tabWidget.setTabEnabled(2, True)
        else:
            self.ui.tabWidget.setTabText(1, "Leak Test *Locked*")
            self.ui.tabWidget.setTabEnabled(1, False)
            self.ui.tabWidget.setTabText(2, "Comments *Locked*")
            self.ui.tabWidget.setTabEnabled(2, False)

    def SaveCSV(self, chamber):
        """Save data to CSV file after straw passes or fails"""
        ROW = int(chamber / 5)
        COL = chamber % 5

        path = GetProjectPaths()["leaktestresultsLTG"]

        Current_worker = self.getWorker()

        if self.Choosenames[ROW][COL][:7] in self.straw_list:
            logger.info(
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
                logger.info("Saving chamber %s data to CSV file" % chamber)
                result.write(self.Choosenames[ROW][COL][:7] + ",")
                # result.write(self.StrawLabels[chamber].text() + ",")
                result.write(currenttime + ",")
                result.write("CO2" + ",")
                result.write(Current_worker + ",")
                result.write("chamber" + str(chamber) + ",")
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

        cpals_file = self.leakDirectory / "CPALS.txt"
        with open(cpals_file, "r") as f:
            line = f.readline()

            line = line.translate({ord(c): None for c in "\n"})

            while line != "":
                if line not in self.cpals:
                    self.cpals.append(line)

                line = f.readline()
                line = line.translate({ord(c): None for c in "\n"})

        for chamber in range(0, 50):
            ROW = int(chamber / 5)
            COL = chamber % 5

            if self.Choosenames[ROW][COL][:5] != "empty":
                strawname = self.Choosenames[ROW][COL][:7]

                try:
                    cpal = FindCPALContainingStraw(strawname)[1]
                    if cpal not in self.cpals:
                        self.cpals.append(cpal)
                except StrawNotFoundError:
                    continue

        return

    def editPallet(self):
        if self.checkCredentials():
            self.getCPALS()
            rem = removeStraw(self.cpals, self.palletDirectoryLTSclass)
            rem.exec_()
        else:
            self.openLogInDialog()

    def strawsTesting(self):
        for chamber in range(0, 50):
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

    def dataCollection(self, app):
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

    # testing in progress: color the chamber yellow
    def setStrawProcessing(self, chamber):
        self.Chambers[chamber].setStyleSheet("background-color: rgb(225, 225, 0);")

    def setEnablePlot(self, chamber):
        for x in self.ui.PdfButtons.buttons():
            if int(x.objectName().strip("PdfButton")) == chamber:
                x.setEnabled(True)

    # large leak: color the chamber red
    def setLargeLeak(self, chamber):
        self.ChamberLabels[chamber].setText("Large Leak!")
        self.Chambers[chamber].setStyleSheet("background-color: rgb(225, 40, 40);")

    def setStrawStatus(self, chamber, passed):
        if passed:
            if self.leak_rate[chamber] < NOTIFY_LOW_LEAK_RATE:
                self.Chambers[chamber].setStyleSheet(
                    "background-color: rgb(204, 153, 255);"  # purple
                )
            elif self.leak_rate[chamber] < UPPER_GOOD_LEAK_RATE:
                self.Chambers[chamber].setStyleSheet(
                    "background-color: rgb(0, 128, 255);"
                )  # blue
            else:
                self.Chambers[chamber].setStyleSheet(
                    "background-color: rgb(40, 225, 40);"
                )  # green
        else:
            self.Chambers[chamber].setStyleSheet("background-color: rgb(225, 40, 40);")

    def setToggleRemoved(self, status):
        self.ui.RemoveButton.setEnabled(status)

    def setUpdateStrawText(self, chamber):
        self.ChamberLabels[chamber].setText(
            str(
                "%.2f ± %.2f"
                % (
                    (self.leak_rate[chamber] * (10**5)),
                    self.leak_rate_err[chamber] * (10**5),
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

    # this function has it's own thread (called "thread")
    # deals with locking/unlocking the gui and responding to the removal of CPALs
    def signalChecking(self):
        changed = False
        signal = False
        while True:
            self.getCPALS()
            pallets_testing = self.cpals != []

            # XOR(pallets_testing, signal)
            if pallets_testing and not signal or (not pallets_testing and signal):
                self.ToggleRemoved.emit(pallets_testing)
                signal = not signal

            credentials = self.checkCredentials()

            # keeps gui locked when started up and until someone logs in or an arduino is running
            if (
                (credentials and not changed) or (not credentials and changed)
            ) and not any(self._running):
                self.LockGUI.emit(credentials)
                changed = not changed

    # connected to the comment submit button
    def makeComment(self):
        # figure out which chamber the straw is in
        row = -1
        col = -1
        for lst in self.Choosenames:
            if self.ui.strawIDLE.text() in lst:
                row = self.Choosenames.index(lst)
                col = lst.index(self.ui.strawIDLE.text())

        # if unable to find a valid index, show a warning
        if row == -1 or col == -1:
            msg = "The entered straw ID does not correspond to a currently loaded straw.\nContinue?"
            reply = QMessageBox.question(
                self, "Message", msg, QMessageBox.Yes, QMessageBox.No
            )
            # option to abort comment submission
            if reply == QMessageBox.No:
                return

        # gotta select a worker, no anonymous comments
        if self.ui.workerSelectCB.currentText() == "":
            QMessageBox.warning(
                self, "Message", "No worker is selected, unable to submit comment."
            )
            return

        # confirm inflation test failure (if applicable)
        if self.ui.inflationCheckBox.isChecked():
            msg = f"Are you sure you want to mark {self.ui.strawIDLE.text()} as having failed the inflation test?"
            reply = QMessageBox.question(
                self, "Message", msg, QMessageBox.Yes, QMessageBox.No
            )
            # option to abort comment submission
            if reply == QMessageBox.No:
                # uncheck and return
                self.ui.inflationCheckBox.setChecked(False)
                return

        # get comment text
        message = self.ui.commentPTE.document().toPlainText()
        # remove commas, since it'll be saved in a csv
        message = message.replace(",", "")
        message = message.replace("\n", "\\n")

        # make sure there's a comment to save
        if len(message) < 1:
            QMessageBox.warning(
                self, "Message", "No text input, unable to submit comment"
            )

        # make row with f-string
        comment = f'{self.ui.strawIDLE.text()},chamber{(5*col+row) if (5*col+row!=-6) else "NotFound"},{self.ui.workerSelectCB.currentText()},{message},{int(datetime.datetime.now().timestamp())},{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        if self.ui.inflationCheckBox.isChecked():
            comment += ",FAILED_INFLATION_TEST"
        else:
            comment += ",_"

        # Check if file exists, if not make it and add a header
        if not os.path.exists(
            (
                f"{self.leakDirectory}/comments/{(self.ui.strawIDLE.text()).upper()}_comments.csv"
            )
        ):
            with open(
                f"{self.leakDirectory}/comments/{(self.ui.strawIDLE.text()).upper()}_comments.csv",
                "a",
            ) as file:
                file.write(
                    "strawID,chamber,worker,comment,epochTime,humanTime,inflationTestStatus"
                )

        # open file and append the comment row thingy
        with open(
            f"{self.leakDirectory}/comments/{(self.ui.strawIDLE.text()).upper()}_comments.csv",
            "a",
        ) as file:
            file.write("\n" + comment)

        # clear out text edit
        self.ui.commentPTE.clear()

        # update comment display
        self.ui.lookupIDLE.setText(self.ui.strawIDLE.text())
        self.readComments()

    # looks up comments for a straw and displays them on the right side of the comments page
    def readComments(self):
        self.ui.commentLW.clear()
        failBrush = QtGui.QBrush(QtCore.Qt.red)
        goodFont = QtGui.QFont()
        goodFont.setPointSize(8)
        goodFont.setBold(False)

        # check if a file exists
        if not os.path.exists(
            (
                f"{self.leakDirectory}/comments/{(self.ui.lookupIDLE.text()).upper()}_comments.csv"
            )
        ):
            QMessageBox.warning(
                self,
                "Message",
                f"No comments file found for {self.ui.lookupIDLE.text()}.",
            )
            return

        # a file exists, so open it
        with open(
            f"{self.leakDirectory}/comments/{(self.ui.lookupIDLE.text()).upper()}_comments.csv",
            "r",
        ) as file:
            for row in file:
                if row != [""]:
                    # com is a list: [strawID,chamber,worker,comment,epochTime,humanTime,inflationTestStatus]
                    # com = file.readline()
                    com = row.split(sep=",")
                    logger.info(com)
                    if com != [
                        "strawID",
                        "chamber",
                        "worker",
                        "comment",
                        "epochTime",
                        "humanTime",
                        "inflationTestStatus\n",
                    ] and com != [""]:
                        com3 = com[3].replace("\\n", "\n")
                        newItem = QListWidgetItem(
                            f"{com[2]}, {com[5]}"
                            + "\n"
                            + f"{com3}"
                            + (
                                "\nFAILED INFLATION TEST"
                                if com[6] == "FAILED_INFLATION_TEST"
                                else ""
                            )
                        )
                        newItem.setFont(goodFont)
                        if len(com[6]) > 2:
                            newItem.setBackground(failBrush)
                        self.ui.commentLW.addItem(newItem)

        return


class StrawSelect(QDialog):
    """Pop-up window for entering straw barcode"""

    def __init__(self, leakDirectory):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.show()
        # *****change Max length back to 7 for production*****
        self.ui.lineEdit.setMaxLength(7)
        self.straw_load = "empty"
        self.ui.okayButton.clicked.connect(self.StrawInput)
        self.ui.cancelButton.clicked.connect(self.Cancel)
        self.leakDirectory = leakDirectory

    def StrawInput(self):
        self.straw_load = self.ui.lineEdit.text().upper()
        if (
            self.straw_load[:2] == "st"
            or self.straw_load[:2] == "ST"
            and all(ch.isdigit() for ch in self.straw_load[2:])
        ):
            try:
                checkStraw(self.straw_load, "C-O2", "leak")

                logger.info(f"Straw {self.straw_load} loaded")
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
            except StrawConsolidateError:
                QMessageBox.critical(
                    self,
                    "Pallet File Error",
                    "Straw not found in final line of any CPAL file.\nWas consolidate or CO2 gui run? Do you need to mergedown?",
                )

        else:
            logger.warning("Not a valid straw barcode. Try formatting like st00023.")
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
            logger.info(f"Welcome {self.Worker_ID}!")
            self.deleteLater()
        else:
            logger.info("Not a valid worker ID.")
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
                for pallet in os.listdir(self.palletDirectory / palletid):
                    if CPAL + ".csv" == pallet:
                        pfile = self.palletDirectory / palletid / pallet
                        with open(pfile, "r") as file:
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
            "Are you sure you want \nto permanently remove "
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
            for pallet in os.listdir(self.palletDirectory / palletid):
                if CPAL + ".csv" == pallet:
                    pfile = self.palletDirectory / palletid / pallet
                    with open(pfile, "a") as file:
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
        pfile = ""

        for palletid in os.listdir(self.palletDirectory):
            for pallet in os.listdir(self.palletDirectory / palletid):
                if CPAL + ".csv" == pallet:
                    found = True
                    pfile = self.palletDirectory / palletid / pallet
                    with open(pfile, "r") as file:
                        old_line = ""
                        line = file.readline()

                        while line != "\n" and line != "":
                            old_line = line
                            line = file.readline()

                        if straw in old_line:
                            valid = True
                    break

        return found, valid, pfile

    def updateMenu(self):
        for i in self.CPALS:
            self.ui.Menu.addItem(i)

    def selectionChange(self):
        CPAL, lastTask, straws, passfail = self.getPallet(self.ui.Menu.currentText())
        self.displayPallet(CPAL, lastTask, straws, passfail)


def run():
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    paths = GetProjectPaths()
    lts = LeakTestStatus(paths, "COM11", 115200, app, arduino_input=True)
    lts.show()
    app.exec_()


if __name__ == "__main__":
    run()
