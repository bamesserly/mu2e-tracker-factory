#### Simply read heater box output, assuming it's currently running

import serial  ## from pyserial
import serial.tools.list_ports
import time, csv, sys, os
from datetime import datetime as dt
import numpy as np
import traceback
import threading

import logging

logger = logging.getLogger("root")

from guis.common.getresources import GetProjectPaths


class HeatControl:
    """Python interface to collect and visualize data from PAAS heater control system"""

    def __init__(
        self, port, panel, wait=120000, ndatapts=450, parent=None, saveMethod=None
    ):
        if port == "GUI":  # PANGUI doesn't have a get port function
            port = getport("VID:PID=2341:8037")  # opened in PANGUI w/ port = "GUI"
        self.port = port
        self.panel = panel
        self.wait = wait  # wait interval between data points (ms)
        self.ndatapts = ndatapts  # number data points to collect
        self.hct = None  # heater control data thread
        # self.interval = QTimer()  # timer for interval between data points
        self.saveMethod = saveMethod  # pass data to PANGUI

        ## records for realtime plot
        self.timerec = []  # measurement collection times
        self.tempArec = []  # PAAS-A temperature [C]
        self.temp2rec = []  # 2nd PAAS temperature [C]

        logger.debug("initialized")

    def saveMethod_placeholder(self):
        ## self.tempArec = PAAS-A temperatures
        ## self.temp2rec = PAAS-B or PAAS-C temperatures
        logger.info(
            f"last temperature measurements: {self.tempArec[-1]} {self.temp2rec[-1]}"
        )

    def update_setpoint(self):
        """Get initial user choice temperature setpoint, or change setpoint
        partway through heat cycle, e.g. after funnels removed"""
        self.setpt = int(55)
        # if thread already running, send it the new setpoint
        if self.hct:
            logger.info("sending sp %s" % self.setpt)
            self.hct.setpt = self.setpt

    def start_data(self):
        logger.debug("HeatControl::start_data")
        """ Start serial interface and data collection thread """
        # paas2dict = {"PAAS-B": "b", "PAAS-C": "c", "None": "0"}
        self.paas2input = "PAAS-B"
        logger.info("2nd PAAS type: %s" % self.paas2input)
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
        # self.interval.timeout.connect(self.next) # every timeout calls the next function
        self.hct = DataThread(self.micro, self.panel, self.paastype, self.setpt)
        self.hct.start()
        time.sleep(60)  # don't join (?) for 60 seconds
        # self.interval.start(self.wait)  # timeout every wait seconds

    # In this function: pass temperatures out to PANGUI
    def next(self):
        """Add next data to the GUI display"""
        ## get the most recent measurement held in thread
        data_list = list(self.hct.transfer())
        if len(data_list) > 0:  # should only have one set of measurements
            ## display values in GUI, include values in record (for realtime plot)
            # self.ui.tempPA.setText(str(data_list[0][0]))
            self.tempArec.append(float(data_list[0][0]))
            if self.paas2input != "None":
                self.temp2rec.append(float(data_list[0][1]))
                # self.ui.tempP2.setText(str(data_list[0][1]))
            else:  # PAAS-A only
                self.temp2rec.append(0.0)  # (avoid -242 or 988)
            self.timerec.append((time.time() - self.t0) / 60.0)
            if len(self.timerec) > self.ndatapts:
                self.endtest()
            else:
                self.hct.savedata()
                ## update plot display

            # Pass the data to the parent PANGUI
            # self.tempArec = PAAS-A temperatures
            # self.temp2rec = NULL or PAAS-B or PAAS-C temperature
            self.saveMethod(self.tempArec[-1], self.temp2rec[-1])

    def closeEvent(self, event):
        """Prevent timer and thread from outliving main window, close serial"""
        self.endtest()

    def endtest(self):
        """Join data collection thread to end or reset test"""
        # self.interval.stop()
        if self.hct:  ## must stop thread if it's running
            # self.hct.join(0.1)  ## make thread timeout
            self.hct.join(10)  ## make thread timeout
            self.hct = None


class DataThread(threading.Thread):
    """Read data from Arduino in temperature control box"""

    def __init__(self, micro, panel, paastype, setpoint):
        threading.Thread.__init__(self)
        self.running = threading.Event()
        self.running.set()
        self.micro = micro
        self.paastype = paastype
        self.setpt = setpoint
        outfilename = panel + "_" + dt.now().strftime("%Y-%m-%d") + ".csv"
        self.datafile = GetProjectPaths()["heatdata"] / outfilename
        ## create file if needed and write header
        if not self.datafile.is_file():
            with open(self.datafile, "a+", newline="") as file:
                file.write(
                    ",".join(["Date", "PAASA_Temp[C]", "2ndPAAS_Temp[C]", "Epoc\n"])
                )

    def run(self):
        logger.debug("thread running")
        n, nmax = 0, 40
        # flag = self.running.wait(10)
        # print(flag)
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
                if len(test.strip().split()) < 2:  # skip split line error
                    logger.info("skipping fragment of split line")
                    continue
                if "val" in test:  # duty cycle 0-255 for voltage control
                    logger.info(test.strip())
                elif "Time" in test:  # time since start in milliseconds
                    duration = float(test.strip().split()[-1])
                    duration = round(duration / 3600000, 3)
                    logger.info(f"Time since start {duration} hours")
                elif "Temperature" in test:  # temperature reading
                    test = test.strip().split()
                    try:
                        float(test[-1])
                    except ValueError:
                        logger.info("skipping fragment of split line")
                        continue
                    if test[1] == "1:":
                        temp1 = test[-1]  # PAAS-A temperature [C]
                    elif test[1] == "2:":
                        temp2 = test[-1]  # 2nd PAAS temperature [C]
                elif "recovery" in test:
                    line = test.strip().split()
                    variable = line[1]
                    value = float(line[2])
                    if "timestamp" in test:
                        value = int(value) / 3600000  # convert ms to hours
                        logger.info(f"{variable} {value} hrs")
                    else:
                        logger.info(f"{variable} {value} C")
                else:
                    logger.info(test.strip())
                n += 1
                time.sleep(1)
            if n == nmax:  # probable error with serial connection
                logger.error("Error with serial connection ->")
                # clear temps to not send old value if requested by GUI
                self.temp1 = 0  # 'error'
                self.temp2 = 0  # 'error'
                n = 0
                return
            else:
                logger.info("PAAS-A temp: %s" % temp1)
                logger.info("2nd PAAS temp: %s" % temp2)
                self.temp1 = temp1
                self.temp2 = temp2
                n = 0
        logger.debug("thread running check")
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
            logger.warning("failed saving measurement: temperature data not collected")

    def transfer(self):
        try:
            yield [self.temp1, self.temp2]
        except:
            return

    def join(self, timeout=None):
        self.running.clear()
        threading.Thread.join(self, timeout)
        logger.info("thread joined")


######################################################################################


def getport(hardwareID):
    """Get COM port number. Distinguish Arduino types when multiple devices are connected
    (also works on General Nanosystems where Arduinos recognized as "USB Serial")."""
    ports = [
        p.device for p in serial.tools.list_ports.comports() if hardwareID in p.hwid
    ]
    if len(ports) < 1:
        logger.error("Arduino not found \nPlug device into any USB port")
        time.sleep(2)
        sys.exit()
    return ports[0]


def run():
    from guis.common.panguilogger import SetupPANGUILogger

    logger = SetupPANGUILogger("root", "HeaterMonitor")
    # heater control uses Arduino Micro: hardware ID 'VID:PID=2341:8037'
    port = getport("VID:PID=2341:8037")
    logger.info("Arduino Micro at {}".format(port))

    # view traceback if error causes GUI to crash
    sys.excepthook = traceback.print_exception

    # GUI
    h = HeatControl(port, panel="MN000")
    h.start_data()


if __name__ == "__main__":
    run()
