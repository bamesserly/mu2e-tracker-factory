# GUI for tensioning straws with Vernier force sensor.
# Plots sensor output in realtime.
# Acceptable straw tension is saved to a CSV file in
# ..\..\..\..\..\Data\Panel Data\external_gui_data\straw_tension_data\
#
# This GUI is launched by PANGUI.py within process 2. Additionally, it can be
# run in standalone mode, by running this .py script directly.
#
# Whether run from within PANGUI.py or standalone, it will save csv data to the
# external_gui_data folder above.
#
# When called from within PANGUI.py, the saveMethod function is defined, and
# the data is simultaneously saved to the database via a dataProcessor function
# saveStrawTensionMeasurement. At the moment, only the database version of
# saveStrawTensionMeasurement is defined, which means that the text data is not
# saving its own copy of the csv data. The only csv data is being saved to
# external_gui_data by this script itself.

import sys, queue, time, csv
import qwt  ## requires pythonqwt, sip
import threading, serial, os
import serial.tools.list_ports  ## automatically get COM port
import numpy as np
from datetime import datetime
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets

DEBUG = False
# from straw_tensioner_window import Ui_MainWindow   ## edit via straw_tensioner_window.ui in Qt Designer
# moving Ui_MainWindow into this file makes the previous line redundant


class StrawTension(QMainWindow):
    """ GUI to display data from Arduino Uno and Vernier force sensor DFS-BTA """

    def __init__(
        self,
        port_loc=None,
        saveMethod=None,
        calibration=None,
        maxdatas=8824,
        wait=50.0,
        parent=None,
        networked=False,
        inGUI=-1,
    ):
        super(StrawTension, self).__init__(parent)
        self.thdl = None  ## data thread
        self.temp, self.uncertainty = [], []
        self.interval = QTimer()  ## wait interval between data points
        self.port_loc = port_loc  ## maps sensor locations to COM ports
        self.calibration = calibration
        self.maxdatas, self.wait = maxdatas, wait
        self.directory = os.path.dirname(os.path.realpath(__file__)) + "\\"
        self.networked = networked
        self.saveMethod = saveMethod  # method from PANGUI to save data to DB
        self.port_loc = self.getPortLoc()  # get arduino port
        self.inGUI = inGUI  # if -1, this gui is operating independent of PANGUI, otherwise it's a panel number

        self.ui = Ui_MainWindow()  ## set up GUI and plot axes
        self.ui.setupUi(self)
        if inGUI != -1:  # if not running independently
            self.ui.panel_id.setText(f"MN{inGUI}")  # set panel id line edit widget text
            self.ui.panel_id.setDisabled(True)  # disable panel id line edit widget

        with open(self.directory + "straw_tensionvalues.csv", "r") as f:
            self.straw_tensionvalues = np.array(
                [row for row in csv.reader(f, delimiter=",")][1:]
            )
        self.straw_number = self.ui.strawnumbox.value()
        if self.ui.hmd_label.text():
            self.hmd = self.ui.hmd_label.text()  ## relative humidity (%)
        else:
            self.hmd = 26  # default text displayed in GUI
        self.min_tension = self.straw_tensionvalues[:, 2].astype(
            float
        )  ## minimum tension

        self.tmpplot, self.tmpcurve = self.dynamic_plot(
            "Tension (grams)", self.straw_tensionvalues, "lime"
        )

        self.ui.tplot_layout.addWidget(self.tmpplot)
        self.ui.realtime_display.clicked.connect(self.start_data)  ## set up buttons
        # self.ui.pause_display.clicked.connect(self.pause_data)
        self.interval.timeout.connect(self.next)
        # self.ui.pause_display.setEnabled(False)

        ## to add reset, send "1" to Arduino

        self.offset_zero = 0.0
        self.calmode = False
        self.ui.setzero.clicked.connect(self.zero)
        # self.ui.pause_display.setEnabled(False)

        ## adding force sensor zero as required startup step
        self.ui.realtime_display.setDisabled(True)
        # self.ui.statusbar.showMessage("Arduino connected: Press Tension Straw to begin")
        self.ui.statusbar.showMessage(
            "Arduino connected. Set switch on force sensor to 10N. Click Set Force Sensor Zero to begin."
        )
        print("initialized")

    def start_data(self):
        """ Start data collection """
        self.ui.statusbar.showMessage("")
        if self.ui.autoincrement.isChecked():  ## auto-increment straw number by two
            x = self.ui.strawnumbox.value()
            self.ui.strawnumbox.setValue(x + 2)

        if self.ui.hmd_label.text():
            self.hmd = self.ui.hmd_label.text()  ## relative humidity (%)
        else:
            self.hmd = 26  # default text displayed in GUI

        self.straw_number = self.ui.strawnumbox.value()
        self.nom_tension = float(
            self.straw_tensionvalues[self.straw_number, 3]
        ) - float(self.hmd)
        self.ui.nominal_label.setText("%5.2f" % float(self.nom_tension))

        self.temp, self.uncertainty = [], []  ## clear plot of previous straw's tension
        self.panel = self.ui.panel_id.text()
        com = self.port_loc["Vernier Force Sensor"][0]

        qs = queue.Queue()
        ## baud rate 9600 for Vernier sensor
        if self.calmode == True:  ## use raw data (no offset) to find offset
            self.thdl = GetDataThread(
                self.straw_number,
                qs,
                0.0,
                self.panel,
                com,
                9600,
                networked=self.networked,
            )
        if self.calmode == False:  ## includes offset subtraction
            self.thdl = GetDataThread(
                self.straw_number,
                qs,
                self.offset_zero,
                self.panel,
                com,
                9600,
                networked=self.networked,
            )
        self.thdl.start()
        self.ui.realtime_display.setEnabled(False)
        self.ui.setzero.setEnabled(False)
        self.interval.start(self.wait)

    def getPortLoc(self):
        arduino_ports = [
            p.device
            for p in serial.tools.list_ports.comports()
            if "Arduino" in p.description
        ]
        if len(arduino_ports) == 0:  ## fix for Day2/Day3 General Nanosystems Computers
            arduino_ports = [
                p.device
                for p in serial.tools.list_ports.comports()
                if "USB Serial" in p.description
            ]
        if len(arduino_ports) < 1:
            print("Arduino not found \nPlug straw tensioner into any USB port")
            time.sleep(2)
            print("Exiting script")
            sys.exit()
        print("Arduino at {}".format(arduino_ports[0]))
        ## Locations of sensors
        return {"Vernier Force Sensor": [arduino_ports[0], 0]}

    def dynamic_plot(self, data_type, st, color, xaxis=True):
        plot = qwt.QwtPlot(self)
        plot.setCanvasBackground(Qt.black)
        if xaxis:
            plot.setAxisTitle(qwt.QwtPlot.xBottom, "Time (s)")
        plot.setAxisScale(qwt.QwtPlot.xBottom, 0, 10, 1)
        plot.setAxisTitle(qwt.QwtPlot.yLeft, data_type)
        plot.setAxisScale(qwt.QwtPlot.yLeft, 18, 28, 2)
        plot.replot()
        curve = qwt.QwtPlotCurve("")
        curve.setRenderHint(qwt.QwtPlotItem.RenderAntialiased)
        pen = QPen(QColor(color), 2)
        curve.setPen(pen)
        curve.attach(plot)
        ## add max straw tension, 850g for all straws
        curvemax = qwt.QwtPlotCurve("max_tension")
        curvemax.attach(plot)
        penlim = QPen(QColor("yellow"), 2)
        curvemax.setPen(penlim)
        curvemax.setData(np.arange(100), 850 * np.ones(100))
        ## add min straw tension, depends on straw length
        self.curvemin = qwt.QwtPlotCurve("min_tension")
        self.curvemin.attach(plot)
        self.curvemin.setPen(penlim)
        self.curvemin.setData(
            np.arange(100),
            (float(self.min_tension[int(self.straw_number)]) - float(self.hmd))
            * np.ones(100),
        )
        plot.replot()
        return plot, curve

    def next(self):
        """ Add next data to the plots """
        data_list = list(self.thdl.transfer(self.thdl.qs))
        if len(data_list) > 0 and data_list[-1][0][1] != "nan":  ## skip blank data
            data = dict(
                tension=data_list[-1][0][0],
                uncertainty=data_list[-1][0][1],
                timestamp=data_list[-1][1],
            )
            if self.calmode == True:  ## use raw data in calibration mode
                caltmp = float(data["tension"])
            if self.calmode == False:  ## data with offset subtracted
                caltmp = float(
                    data["tension"]
                )  ## includes subtraction of offset at zero
            calhmd = float(data["uncertainty"])
            state = data_list[-1][2]

            self.ui.tension_label.setText("%5.2f" % caltmp)  ## tension in label box
            self.ui.unc_label.setText(str(calhmd))  ## uncertainty in label
            if caltmp <= 850.0 and caltmp >= float(
                self.min_tension[int(self.straw_number)]
            ) - float(self.hmd):
                self.ui.rangepanel.setStyleSheet("background-color: green")
                message = "Straw tension acceptable: move to next straw"
            else:
                self.ui.rangepanel.setStyleSheet("background-color: red")
                message = "Straw tension outside acceptable range: repull straw"

            self.temp.append((data["timestamp"], caltmp))
            self.uncertainty.append((data["timestamp"], calhmd))
            if len(self.temp) > self.maxdatas:
                self.temp.pop(0), self.uncertainty.pop(0)
            t = [x[0] for x in self.temp]  ## time (s)
            tmp = [float(t[1]) for t in self.temp]  ## tension (grams force)
            hmd = [float(h[1]) for h in self.uncertainty]  ## uncertainty (grams force)
            ave = [sum(y) / float(len(y)) for y in [tmp]]
            self.curvemin.setData(
                np.arange(100),
                (float(self.min_tension[(self.straw_number)]) - float(self.hmd))
                * np.ones(100),
            )
            for a in [[self.tmpplot, tmp, self.tmpcurve]]:
                a[0].setAxisScale(qwt.QwtPlot.xBottom, t[0], max(8, t[-1]))
                ymin, ymax = min(a[1]) - 3.0, max(max(a[1]) + 4.0, a[1][-1])
                a[0].setAxisScale(qwt.QwtPlot.yLeft, 0, 1000, 100)
                a[2].setData(t, a[1])  ## add new data to the plots
                a[0].replot()
            self.ui.ave_temp.setText("%5.2f" % tmp[-1])
            self.ui.ave_temp.setStyleSheet("color: lime")

            if DEBUG:
                state = b"end"
            if state == b"end":
                if self.saveMethod:
                    self.saveMethod(self.ui.strawnumbox.value(), tmp[-1], hmd[-1])
                self.pause_data()
                self.ui.statusbar.showMessage(message)

            if self.calmode == True:
                if len(self.temp) > 50:
                    print("gathered 50 values")
                    caldata = np.array(self.temp)
                    if np.nanstd(caldata[:, 1]) > 5:
                        print("Uncertainty > 5g. Recalibrating")
                        self.temp = []
                    else:
                        self.pause_data()
                        self.offset_zero = np.nanmean(caldata[:, 1])
                        print(
                            "Calibration data collected: {:.2f}g offset at zero".format(
                                self.offset_zero
                            )
                        )
                        self.calmode = False
                        self.ui.setzero.setEnabled(True)
                        self.ui.realtime_display.setEnabled(True)
                        self.ui.statusbar.showMessage(
                            "Force sensor zero set. Ready to tension straw."
                        )

    def pause_data(self):
        """ Pause data collection """
        if self.thdl:  ## must stop thread if it's running
            self.thdl.join(0.1)  ## make thread timeout
            self.thdl = None
        self.interval.stop()
        QTimer.singleShot(180, lambda: self.ui.realtime_display.setEnabled(True))
        # self.ui.pause_display.setEnabled(False)
        QTimer.singleShot(180, lambda: self.ui.setzero.setEnabled(True))

    def zero(self):
        """ Set zero by subtracting sensor offset at zero tension. """
        self.ui.setzero.setEnabled(False)
        self.calmode = True
        self.start_data()


class GetDataThread(threading.Thread):
    """ Read data from Arduino Uno and Vernier force sensor DFS-BTA"""

    def __init__(self, stn, qs, cal, loc, COM, baudrate, timeout=0.08, networked=False):
        threading.Thread.__init__(self)
        self.running = threading.Event()
        self.running.set()
        self.qs = qs
        self.stn = stn  ## straw position in panel
        self.cal = cal  ## offset at zero tension
        self.nano_params = {"port": COM, "baudrate": baudrate, "timeout": timeout}
        if networked:  ## saving data to networked drive MU2E-CART1
            # print('networked')
            self.mu2ecart = "\\\MU2E-CART1\\Users\\Public\\Database Backup\\Panel data\\straw_tensioner_data\\"
            self.datafile = (
                self.mu2ecart + loc + "_" + datetime.now().strftime("%Y-%m-%d")
            )
        else:
            self.directory = os.path.dirname(os.path.realpath(__file__)) + "\\"
            self.datafile = (
                self.directory
                + "..\\..\\..\\..\\..\\Data\\Panel Data\\external_gui_data\\straw_tension_data\\"
                + loc
                + "_"
                + datetime.now().strftime("%Y-%m-%d")
            )
        if not os.path.isfile(self.datafile + ".csv"):
            with open(self.datafile + ".csv", mode="a+") as f:
                f.write("Date,StrawPosition,Tension(grams),Uncertainty(grams),Epoc\n")

    def run(self):
        print("thread running")
        t0 = time.time()
        self.nano = serial.Serial(**self.nano_params)
        while self.running.isSet():
            line = self.nano.readline().strip()
            if line != b"":
                line = line.split(b" ")
                if (
                    len(line) == 3 and line[2] != b"nan"
                ):  ## skip partial lines and 'nan' uncertainty
                    THdata = [
                        "%5.2f" % (float(line[1]) - float(self.cal)),
                        "%5.2f" % float(line[2]),
                    ]
                    # print(THdata)
                    print(line)
                    timestamp = time.time() - t0
                    state = line[0]  ## b'reading' or b'end'
                    self.qs.put((THdata, timestamp, state))
                    # join thread on "end" signal: slope=-9, see Arduino code to edit
                    if state == b"end":
                        with open(
                            self.datafile + ".csv", mode="a+"
                        ) as f:  ## save to csv
                            f.write(datetime.now().strftime("%Y-%m-%d_%H%M%S") + ",")
                            f.write(str(self.stn) + ",")  ## straw position in panel
                            f.write(str(THdata[0]) + ",")  ## tension (grams force)
                            f.write(str(THdata[1]) + ",")  ## uncertainty (grams force)
                            f.write(str(time.time()) + "\n")
                        break
        self.nano.close()

    def transfer(self, qs):
        try:
            yield qs.get(True, 0.01)
        except queue.Empty:
            return

    def join(self, timeout=None):
        self.running.clear()
        threading.Thread.join(self, timeout)
        print("thread joined")


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(745, 583)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.centralwidget.sizePolicy().hasHeightForWidth()
        )
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setMinimumSize(QtCore.QSize(511, 518))
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.gridLayout_3.addWidget(self.label_5, 0, 0, 1, 2)
        self.top_layout = QtWidgets.QWidget(self.centralwidget)
        self.top_layout.setObjectName("top_layout")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.top_layout)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_3 = QtWidgets.QLabel(self.top_layout)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 0, 0, 1, 1)
        self.panel_id = QtWidgets.QLineEdit(self.top_layout)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.panel_id.setFont(font)
        self.panel_id.setText("")
        self.panel_id.setObjectName("panel_id")
        self.gridLayout_2.addWidget(self.panel_id, 0, 1, 1, 2)
        self.setzero = QtWidgets.QPushButton(self.top_layout)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.setzero.setFont(font)
        self.setzero.setObjectName("setzero")
        self.gridLayout_2.addWidget(self.setzero, 1, 0, 1, 3)
        self.label = QtWidgets.QLabel(self.top_layout)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 2, 0, 1, 2)
        self.strawnumbox = QtWidgets.QSpinBox(self.top_layout)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.strawnumbox.sizePolicy().hasHeightForWidth())
        self.strawnumbox.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(18)
        self.strawnumbox.setFont(font)
        self.strawnumbox.setMaximum(95)
        self.strawnumbox.setObjectName("strawnumbox")
        self.gridLayout_2.addWidget(self.strawnumbox, 2, 2, 1, 1)
        self.realtime_display = QtWidgets.QPushButton(self.top_layout)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.realtime_display.setFont(font)
        self.realtime_display.setObjectName("realtime_display")
        self.gridLayout_2.addWidget(self.realtime_display, 3, 0, 1, 3)
        self.autoincrement = QtWidgets.QCheckBox(self.top_layout)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.autoincrement.setFont(font)
        self.autoincrement.setIconSize(QtCore.QSize(32, 32))
        self.autoincrement.setObjectName("autoincrement")
        self.gridLayout_2.addWidget(self.autoincrement, 4, 0, 1, 3)
        self.rangepanel = QtWidgets.QGraphicsView(self.top_layout)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.rangepanel.sizePolicy().hasHeightForWidth())
        self.rangepanel.setSizePolicy(sizePolicy)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 127, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 63, 63))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(127, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(170, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 127, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.NoBrush)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 127, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 63, 63))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(127, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(170, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 127, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.NoBrush)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(127, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 127, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 63, 63))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(127, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(170, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(127, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(127, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.NoBrush)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
        self.rangepanel.setPalette(palette)
        self.rangepanel.setAutoFillBackground(False)
        self.rangepanel.setObjectName("rangepanel")
        self.gridLayout_2.addWidget(self.rangepanel, 5, 0, 1, 3)
        self.gridLayout_3.addWidget(self.top_layout, 1, 0, 1, 1)
        self.plot_groupbox = QtWidgets.QGroupBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.plot_groupbox.sizePolicy().hasHeightForWidth()
        )
        self.plot_groupbox.setSizePolicy(sizePolicy)
        self.plot_groupbox.setMinimumSize(QtCore.QSize(521, 361))
        self.plot_groupbox.setTitle("")
        self.plot_groupbox.setObjectName("plot_groupbox")
        self.gridLayout = QtWidgets.QGridLayout(self.plot_groupbox)
        self.gridLayout.setObjectName("gridLayout")
        self.tplot_layout = QtWidgets.QVBoxLayout()
        self.tplot_layout.setObjectName("tplot_layout")
        self.gridLayout.addLayout(self.tplot_layout, 0, 0, 1, 1)
        self.gridLayout_3.addWidget(self.plot_groupbox, 1, 1, 1, 1)
        self.bottomLayout = QtWidgets.QGridLayout()
        self.bottomLayout.setObjectName("bottomLayout")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.label_2.setPalette(palette)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_2.setFont(font)
        self.label_2.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label_2.setObjectName("label_2")
        self.bottomLayout.addWidget(self.label_2, 0, 0, 2, 1)
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.label_6.setPalette(palette)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_6.setFont(font)
        self.label_6.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label_6.setObjectName("label_6")
        self.bottomLayout.addWidget(self.label_6, 0, 1, 2, 2)
        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        self.label_7.setWordWrap(True)
        self.label_7.setObjectName("label_7")
        self.bottomLayout.addWidget(self.label_7, 1, 2, 2, 1)
        self.tension_label = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.tension_label.sizePolicy().hasHeightForWidth()
        )
        self.tension_label.setSizePolicy(sizePolicy)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Shadow, brush)
        self.tension_label.setPalette(palette)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.tension_label.setFont(font)
        self.tension_label.setFrameShape(QtWidgets.QFrame.Box)
        self.tension_label.setObjectName("tension_label")
        self.bottomLayout.addWidget(self.tension_label, 2, 0, 1, 1)
        self.nominal_label = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.nominal_label.sizePolicy().hasHeightForWidth()
        )
        self.nominal_label.setSizePolicy(sizePolicy)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Shadow, brush)
        self.nominal_label.setPalette(palette)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.nominal_label.setFont(font)
        self.nominal_label.setFrameShape(QtWidgets.QFrame.Box)
        self.nominal_label.setText("")
        self.nominal_label.setObjectName("nominal_label")
        self.bottomLayout.addWidget(self.nominal_label, 2, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.label_4.setPalette(palette)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_4.setFont(font)
        self.label_4.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label_4.setObjectName("label_4")
        self.bottomLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.label_8.setPalette(palette)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_8.setFont(font)
        self.label_8.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label_8.setObjectName("label_8")
        self.bottomLayout.addWidget(self.label_8, 3, 1, 2, 1)
        self.unc_label = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.unc_label.sizePolicy().hasHeightForWidth())
        self.unc_label.setSizePolicy(sizePolicy)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Shadow, brush)
        self.unc_label.setPalette(palette)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.unc_label.setFont(font)
        self.unc_label.setFrameShape(QtWidgets.QFrame.Box)
        self.unc_label.setText("")
        self.unc_label.setObjectName("unc_label")
        self.bottomLayout.addWidget(self.unc_label, 4, 0, 2, 1)
        self.hmd_label = QtWidgets.QLineEdit(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.hmd_label.setFont(font)
        self.hmd_label.setObjectName("hmd_label")
        self.bottomLayout.addWidget(self.hmd_label, 5, 1, 1, 1)
        self.gridLayout_3.addLayout(self.bottomLayout, 2, 1, 1, 1)
        self.ave_temp = QtWidgets.QLabel(self.centralwidget)
        self.ave_temp.setGeometry(QtCore.QRect(600, 50, 101, 21))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.ave_temp.setFont(font)
        self.ave_temp.setAutoFillBackground(False)
        self.ave_temp.setText("")
        self.ave_temp.setObjectName("ave_temp")
        self.top_layout.raise_()
        self.plot_groupbox.raise_()
        self.label_5.raise_()
        self.ave_temp.raise_()
        self.unc_label.raise_()
        self.tension_label.raise_()
        self.label_2.raise_()
        self.label_4.raise_()
        self.label_6.raise_()
        self.nominal_label.raise_()
        self.label_7.raise_()
        self.label_8.raise_()
        self.hmd_label.raise_()
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 745, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "StrawTensioner"))
        self.label_5.setText(
            _translate("MainWindow", "Straw Tensioner - Vernier Force Sensor")
        )
        self.label_3.setText(_translate("MainWindow", "Panel ID"))
        self.panel_id.setPlaceholderText(_translate("MainWindow", "MN000"))
        self.setzero.setText(_translate("MainWindow", "Set Force Sensor Zero"))
        self.label.setText(_translate("MainWindow", "Straw \n", "Number"))
        self.realtime_display.setText(_translate("MainWindow", "Tension Straw"))
        self.autoincrement.setText(
            _translate("MainWindow", "Auto-Increment \n", "Straw Number")
        )
        self.label_2.setText(_translate("MainWindow", "Tension (grams)"))
        self.label_6.setText(_translate("MainWindow", "Nominal Tension "))
        self.label_7.setText(
            _translate(
                "MainWindow",
                "Note: Nominal tension corrected by -1g for each +1% humidity",
            )
        )
        self.tension_label.setText(_translate("MainWindow", "0"))
        self.label_4.setText(_translate("MainWindow", "Uncertainty"))
        self.label_8.setText(_translate("MainWindow", "Humidity (%)"))
        self.hmd_label.setPlaceholderText(_translate("MainWindow", "26"))


def run():
    """
    arduino_ports = [p.device for p in serial.tools.list_ports.comports()
                     if 'Arduino' in p.description]
    if len(arduino_ports)==0:  ## fix for Day2/Day3 General Nanosystems Computers
         arduino_ports = [p.device for p in serial.tools.list_ports.comports()
                     if 'USB Serial' in p.description]
    if len(arduino_ports)<1:
         print('Arduino not found \nPlug straw tensioner into any USB port')
         time.sleep(2)
         print("Exiting script")
         sys.exit()
    print("Arduino at {}".format(arduino_ports[0]))
    ## Locations of sensors
    port_loc = {"Vernier Force Sensor":[arduino_ports[0],0]}
    """
    calibration = {"Vernier Force Sensor": None}

    app = QApplication(sys.argv)
    ctr = StrawTension(maxdatas=8824, wait=50.0, networked=False)
    ctr.show()
    ctr.resize(1600, 1200)  # set to a comfy size
    app.exec_()


if __name__ == "__main__":
    run()
#### Test conditions: Python 3.7 32bit on Windows 64bit
