#### run_heat_control.py
#### python interface to collect and visualize data from [PAAS_heater_1009.ino]
#### variable temperature setpoint input

import serial  ## from pyserial
import serial.tools.list_ports
import time, csv, sys, os
from datetime import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import traceback
import threading

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from tension_devices.panel_heater.heat_control_window import (
    Ui_MainWindow,
)  ## edit via heat_control_window.ui in Qt Designer

import matplotlib

matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class HeatControl(QMainWindow):
    """ Python interface to collect and visualize data from PAAS heater control system """

    def __init__(
        self, port, panel, wait=120000, ndatapts=300, parent=None, saveMethod=None
    ):
        super(HeatControl, self).__init__(parent)
        if port == "GUI":  # PANGUI doesn't have a get port function
            port = getport("VID:PID=2341:8037")  # opened in PANGUI w/ port = "GUI"
        self.port = port
        self.panel = panel
        self.wait = wait  # wait interval between data points
        self.ndatapts = ndatapts  # number data points to collect
        self.hct = None  # heater control data thread
        self.interval = QTimer()  # timer for interval between data points
        self.saveMethod = saveMethod  # pass data to PANGUI

        ## records for realtime plot
        self.timerec = []  # measurement collection times
        self.tempArec = []  # PAAS-A temperature [C]
        self.temp2rec = []  # 2nd PAAS temperature [C]

        ## set up GUI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.start_button.clicked.connect(self.start_data)
        self.testplot3()

        ## 2nd PAAS type selection required before start of data collection
        self.ui.paas2_box.currentIndexChanged.connect(self.selectpaas)
        self.ui.setpt_box.currentIndexChanged.connect(self.selectpass)
        self.ui.start_button.setDisabled(True)
        self.ui.end_data.clicked.connect(self.endtest)

        ## user choice temperature setpoint
        self.ui.setpt_box.currentIndexChanged.connect(self.update_setpoint)
        print("initialized")

    def saveMethod_placeholder(self):
        ## self.tempArec = PAAS-A temperatures
        ## self.temp2rec = PAAS-B or PAAS-C temperatures
        print("last temperature measurements:", self.tempArec[-1], self.temp2rec[-1])

    def selectpaas(self):
        """ Enable start data collection if both 2nd PAAS and setpoint selected """
        if (
            self.ui.paas2_box.currentText() != "Select..."
            and self.ui.setpt_box.currentText() != "Select..."
            and self.ui.paas2_box.isEnabled()
        ):
            self.ui.start_button.setEnabled(True)
        else:
            self.ui.start_button.setDisabled(True)

    def update_setpoint(self):
        """Get initial user choice temperature setpoint, or change setpoint
        partway through heat cycle, e.g. after funnels removed"""
        if self.ui.setpt_box.currentText() != "Select...":
            self.setpt = int(self.ui.setpt_box.currentText())
            self.ui.labelsp.setText(f"Current setpoint: {self.setpt}C")
            # if thread already running, send it the new setpoint
            if self.hct:
                print("sending sp", self.setpt)
                self.hct.setpt = self.setpt
        else:  # for case with 'Select...' option (start will be disabled)
            self.setpt = 0
            self.ui.labelsp.setText(f"Current setpoint: {self.setpt}C")

    def start_data(self):
        """ Start serial interface and data collection thread """
        self.ui.start_button.setDisabled(True)
        self.ui.paas2_box.setDisabled(True)
        self.ui.setpt_box.removeItem(0)  # cannot revert to 'Select...'
        self.paas2input = self.ui.paas2_box.currentText().split()[0]
        print("2nd PAAS type:", self.paas2input)
        self.update_setpoint()  # initial temperature setpoint
        ## map combobox entries to character to send via serial
        paas2dict = {"PAAS-B": "b", "PAAS-C": "c", "None": "0"}
        micro_params = {"port": self.port, "baudrate": 2000000, "timeout": 0.08}
        self.micro = serial.Serial(**micro_params)
        ## trigger paas2 input request
        time.sleep(0.2)
        self.micro.write(b"\n")
        test = self.micro.readline()
        while test == b"" or test == b"\r\n":  # skip blank lines if any
            self.micro.write(b"\n")
            test = self.micro.readline()
        ## send character that determines second PAAS plate
        self.paastype = paas2dict[self.paas2input].encode("utf8")
        ## plot will have time since start of test
        self.t0 = time.time()

        ## run data collection from separate thread to avoid freezing GUI
        self.interval.timeout.connect(self.next)
        self.hct = DataThread(self.micro, self.panel, self.paastype, self.setpt)
        self.hct.start()
        self.interval.start(self.wait)  # get data at every timeout

    # In this function: pass temperatures out to PANGUI
    def next(self):
        """ Add next data to the GUI display """
        ## get the most recent measurement held in thread
        data_list = list(self.hct.transfer())
        if len(data_list) > 0:  # should only have one set of measurements
            ## display values in GUI, include values in record (for realtime plot)
            self.ui.tempPA.setText(str(data_list[0][0]))
            self.tempArec.append(float(data_list[0][0]))
            if self.paas2input != "None":
                self.temp2rec.append(float(data_list[0][1]))
                self.ui.tempP2.setText(str(data_list[0][1]))
            else:  # PAAS-A only
                self.temp2rec.append(0.0)  # (avoid -242 or 988)
            self.timerec.append((time.time() - self.t0) / 60.0)
            if len(self.timerec) > self.ndatapts:
                self.endtest()
            else:
                self.hct.savedata()
                ## update plot display
                self.testplot2()

            # Pass the data to the parent PANGUI
            # self.tempArec = PAAS-A temperatures
            # self.temp2rec = NULL or PAAS-B or PAAS-C temperature
            self.saveMethod(self.tempArec[-1], self.temp2rec[-1])

    def testplot3(self):
        """ Set up canvas for plotting temperature vs. time """
        self.ui.data_widget = QWidget(self.ui.graphicsView)
        layout = QHBoxLayout(self.ui.graphicsView)
        self.z = np.array([[-10, -10]])
        self.canvas = DataCanvas(
            self.ui.data_widget,
            data=self.z,
            width=5,
            height=4,
            dpi=100,
            xlabel="Time since start [minutes]",
            ylabel="Temperature [C]",
        )
        layout.addWidget(self.canvas)
        self.ui.data_widget.repaint()

    def testplot2(self):
        """ Update plot: new [time,temperature] array """
        self.z = np.array([self.timerec, self.tempArec, self.temp2rec]).T
        self.canvas.read_data(self.z, self.paas2input)
        self.ui.data_widget.repaint()

    def closeEvent(self, event):
        """ Prevent timer and thread from outliving main window, close serial """
        self.endtest()

    def endtest(self):
        """ Join data collection thread to end or reset test """
        self.interval.stop()
        if self.hct:  ## must stop thread if it's running
            self.hct.join(0.1)  ## make thread timeout
            self.hct = None


class DataThread(threading.Thread):
    """ Read data from Arduino in temperature control box """

    def __init__(self, micro, panel, paastype, setpoint):
        threading.Thread.__init__(self)
        self.running = threading.Event()
        self.running.set()
        self.micro = micro
        self.paastype = paastype
        self.setpt = setpoint
        self.directory = os.path.dirname(os.path.realpath(__file__)) + "\\"
        self.datafile = (
            self.directory
            + "..\\..\\..\\..\\..\\Data\\Panel Data\\external_gui_data\\heat_control_data\\"
            + panel
            + "_"
            + dt.now().strftime("%Y-%m-%d")
            + ".csv"
        )
        ## create file if needed and write header
        if not os.path.isfile(self.datafile):
            with open(self.datafile, "a+", newline="") as file:
                file.write(
                    ",".join(["Date", "PAASA_Temp[C]", "2ndPAAS_Temp[C]", "Epoc\n"])
                )
        print("saving data to", self.datafile)

    def run(self):
        print("thread running")
        n, nmax = 0, 40
        while self.running.isSet():
            self.micro.write(self.paastype)
            self.micro.write(str(self.setpt).encode("utf8"))
            self.micro.write(b"\n")
            ## extract measurements
            temp1, temp2 = "", ""
            while not (temp1 and temp2) and n < nmax:
                test = self.micro.readline().decode("utf8")
                if test == "":
                    n += 1
                    self.micro.write(self.paastype)
                    self.micro.write(str(self.setpt).encode("utf8"))
                    self.micro.write(b"\n")
                    continue
                # print(repr(test))
                if len(test.strip().split()) < 2:  # skip split line error
                    print("skipping fragment of split line")
                    continue
                if "val" in test:  # duty cycle 0-255 for voltage control
                    print(test.strip())
                elif "Temp" in test:  # temperature reading
                    test = test.strip().split()
                    try:
                        float(test[-1])
                    except ValueError:
                        print("skipping fragment of split line")
                        continue
                    if test[1] == "1:":
                        temp1 = test[-1]  # PAAS-A temperature [C]
                    elif test[1] == "2:":
                        temp2 = test[-1]  # 2nd PAAS temperature [C]
                n += 1
                time.sleep(1)
            if n == nmax:  # probable error with serial connection
                print("Error with serial connection ->")
                # clear temps to not send old value if requested by GUI
                self.temp1 = 0  # 'error'
                self.temp2 = 0  # 'error'
                n = 0
                return
            else:
                print("PAAS-A temp:", temp1)
                print("2nd PAAS temp:", temp2)
                self.temp1 = temp1
                self.temp2 = temp2
                n = 0
        print("thread running check")
        ## close serial if thread joined
        if self.micro:
            self.micro.close()

    def savedata(self):
        # print('setpoint in thread',self.setpt)
        if self.temp1 and self.temp2:
            with open(self.datafile, "a+", newline="") as file:
                cw = csv.writer(file)
                cw.writerow(
                    [
                        dt.now().strftime("%Y-%m-%d_%H%M%S"),
                        str(self.temp1),
                        str(self.temp2),
                        str(time.time()),
                    ]
                )
        else:
            print("failed saving measurement: temperature data not collected")

    def transfer(self):
        try:
            yield [self.temp1, self.temp2]
        except:
            return

    def join(self, timeout=None):
        self.running.clear()
        threading.Thread.join(self, timeout)
        print("thread joined")


class DataCanvas(FigureCanvas):
    """Each canvas class will use this to embed a matplotlib in the PyQt5 GUI"""

    def __init__(
        self,
        parent=None,
        data=None,
        width=2,
        height=2,
        dpi=100,
        xlabel="xlabel",
        ylabel="ylabel",
    ):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.axes.clear()
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.axes.grid(True)
        self.axes.set_ylabel(ylabel)
        self.axes.set_xlabel(xlabel)
        box = self.axes.get_position()
        self.axes.set_position(
            [
                box.x0 + box.width * 0.05,
                box.y0 + box.height * 0.05,
                box.width * 1.0,
                box.height * 1.0,
            ]
        )
        self.prev = None
        self.prev2 = None

    def read_data(self, data, p2):
        if p2 == "None":  # only PAAS-A
            if self.prev:
                self.prev.remove()
            (self.prev,) = self.axes.plot(data[:, 0], data[:, 1], "g.")
        else:  # plot temperature for 2 PAAS plates
            if self.prev:
                self.prev.remove()
                self.prev2.remove()
            (self.prev,) = self.axes.plot(data[:, 0], data[:, 1], "g.", label="PAAS-A")
            (self.prev2,) = self.axes.plot(data[:, 0], data[:, 2], "b.", label=p2)
            self.axes.legend()
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()


######################################################################################


def getport(hardwareID):
    """Get COM port number. Distinguish Arduino types when multiple devices are connected
    (also works on General Nanosystems where Arduinos recognized as "USB Serial")."""
    ports = [
        p.device for p in serial.tools.list_ports.comports() if hardwareID in p.hwid
    ]
    if len(ports) < 1:
        print("Arduino not found \nPlug device into any USB port")
        time.sleep(2)
        print("Exiting script")
        sys.exit()
    return ports[0]


if __name__ == "__main__":
    # heater control uses Arduino Micro: hardware ID 'VID:PID=2341:8037'
    port = getport("VID:PID=2341:8037")
    print("Arduino Micro at {}".format(port))

    # view traceback if error causes GUI to crash
    sys.excepthook = traceback.print_exception

    # GUI
    app = QApplication(sys.argv)
    ctr = HeatControl(port, panel="MN000")
    ctr.show()
    app.exec_()
