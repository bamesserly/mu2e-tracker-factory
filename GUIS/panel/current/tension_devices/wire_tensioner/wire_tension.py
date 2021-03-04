#### Wire Tensioner GUI 0326
#### Run with motor_loadcell_0326.ino on Arduino Micro

import sys, os, threading, serial, time, queue
import threading
import serial.tools.list_ports  ## automatically get COM port
from datetime import datetime
from PyQt5.QtCore import QRect, Qt, QTimer, QMetaObject, QCoreApplication
from PyQt5.QtGui import QFont, QPalette, QColor, QBrush
from PyQt5.QtWidgets import (
    QLabel,
    QFrame,
    QStackedWidget,
    QWidget,
    QPushButton,
    QSizePolicy,
    QCheckBox,
    QVBoxLayout,
    QLayout,
    QSpinBox,
    QLineEdit,
    QMainWindow,
    QApplication,
    QComboBox,
    QMessageBox,
)
from pathlib import Path

sys.path.insert(0, str(Path(Path(__file__).parent).resolve()))
from wire_tensioner_window import Ui_Dialog  ## edit via QTDesigner


class WireTensionWindow(QMainWindow):
    """ GUI to interface with load cell / stepper motor wire tensioner  """

    def __init__(self, saveMethod, loadContinuityMethod, wait=10.0, parent=None):
        super(WireTensionWindow, self).__init__(parent)
        self.saveMethod = saveMethod
        self.loadContinuityMethod = loadContinuityMethod
        self.wait = wait
        self.port = self.getPortLocation()

        ## Setup UI
        self.ui = Ui_Dialog()  ## set up GUI window
        self.ui.setupUi(self)
        self.mode = "tension"  ## switch set to tension
        self.wait = wait

        ## Widgets
        self.interval = QTimer()  ## wait interval between data points
        self.interval.timeout.connect(self.next)
        self.ui.tension_harden.clicked.connect(
            lambda: self.tension_wire(pretension=True)
        )
        self.ui.tension_only.clicked.connect(
            lambda: self.tension_wire(pretension=False)
        )
        self.ui.resetmotor.clicked.connect(self.reset)
        self.ui.next_straw.clicked.connect(self.increment_straw)
        self.ui.recordtension.clicked.connect(self.record)
        self.ui.tarebutton.clicked.connect(lambda: self.tareloadcell(tare=50))
        self.ui.tarebutton2.clicked.connect(lambda: self.tareloadcell(tare=0))
        self.ui.setcalbutton.clicked.connect(self.setcalibration)
        self.ui.strawnumbox.valueChanged.connect(self.clearlabel)
        # replaced wire with higher installation tension to compensate for friction on solder
        self.ui.tension_replaced.clicked.connect(
            lambda: self.tension_wire(pretension=True, replaced=True)
        )

        ## Load calibration factor
        self.micro = serial.Serial(port=self.port, baudrate=9600, timeout=0.08)
        self.micro.write(b"c")
        self.micro.write(b"\n")
        x = self.micro.readline()
        print(x)
        self.initcal = float(x.split()[1])
        print(self.initcal)
        self.micro.close()
        self.ui.calibfactor.setText(str(self.initcal))
        print("testing")
        self.ui.statuslabel.setText(
            "Initialized. Ready to work harden and tension wire."
        )

        ## Try to load and display the continuity measurement for the default position
        # self.loadContinuity()

        # Start data
        self.start_data()

    def clearlabel(self):
        self.ui.recordlabel.setText("")

    def start_data(self):
        """ Monitor data continuously through GUI """
        self.wire_number = self.ui.strawnumbox.value()
        print("wire", self.wire_number)
        qs = queue.Queue()
        if self.mode == "tension":
            self.thdl = GetDataThread(qs, self.port)
        self.thdl.start()
        self.interval.start(self.wait)
        self.wirestarttime = int(time.time())

    def tareloadcell(self, tare=50):
        """ Tare load cell. Default tare for calibration is with 50g reference mass. """
        print("tare load cell")
        self.thdl.join()
        self.micro = serial.Serial(port=self.port, baudrate=9600, timeout=0.08)
        print(self.micro.readline())
        self.micro.write(b"\n")
        if tare == 0:  ## tare at 0g
            self.micro.write(b"z2")
        else:  ## tare at 50g for calibration
            self.micro.write(b"z")
        self.micro.write(b"\n")
        print(self.micro.readline())
        self.micro.write(b"\n")
        print(self.micro.readline())
        self.micro.write(b"\n")
        self.micro.close()
        self.ui.calibmode.setText("Tared")
        if tare == 50:
            self.ui.statuslabel.setText("Hang 100g mass and click set")
        self.start_data()

    def setcalibration(self):
        print("setting calbration factor")
        self.thdl.join()
        self.micro = serial.Serial(port=self.port, baudrate=9600, timeout=0.08)
        self.micro.write(b"s")
        self.micro.write(b"\n")
        time.sleep(2)
        cal = self.initcal
        for i in range(30):
            x = self.micro.readline()
            print(x)
            if x != b"":
                x = x.split()
                if x[0] == b"calibration_factor":
                    print(x)
                    cal = x[1]
                    self.ui.calibfactor.setText(str(float(cal)))
                    break
        print(cal, self.initcal)
        if float(cal) == float(self.initcal):
            self.ui.statuslabel.setText("Error updating calibration")
        print("setting calibration", cal)
        # self.ui.calibfactor.setText(str(float(x)))
        self.micro.close()
        self.start_data()
        self.ui.calibmode.setText("Set")
        self.ui.statuslabel.setText("Calibration factor set.")

    ## METHOD THAT WRITES DATA TO TEXT FILE ###################################
    def record(self):
        print("inside record")
        got_data = False

        position = int(self.ui.strawnumbox.value())
        tension = float(self.ui.tensionlabel.text().strip("-"))
        timer = float(self.ui.strawtimelabel.text())
        calib = float(self.ui.calibfactor.text())
        cont = "N/A"
        # wire_pos = self.ui.selectWirePosition.currentText()
        print(position, tension, timer, calib, cont)

        try:
            # Extract data from widgets
            position = int(self.ui.strawnumbox.value())
            tension = float(self.ui.tensionlabel.text().strip("-"))
            timer = float(self.ui.strawtimelabel.text())
            calib = float(self.ui.calibfactor.text())
            cont = "N/A"
            print(position, tension, timer, calib, cont)
            got_data = True
        except ValueError:
            pass
        except AttributeError:
            pass

        if got_data:
            # Call save method with data
            self.saveMethod(
                # Tension measurement
                position,
                tension,
                timer,
                calib,
                ## Continuity measurement
                # (position, cont, wire_pos),
            )

    def tension_wire(self, pretension=True, replaced=False):
        self.thdl.join()
        self.wirestarttime = int(time.time())
        self.ui.statuslabel.setText("Tensioning wire")
        self.ui.tensionlabel.setText("")
        self.micro = serial.Serial(port=self.port, baudrate=9600, timeout=0.08)
        if pretension:
            self.micro.write(b"p")
            self.micro.write(b"\n")
        if replaced:
            self.micro.write(b"t85")
        else:
            self.micro.write(b"t")
        self.micro.write(b"\n")
        self.micro.close()
        self.start_data()
        self.ui.statuslabel.setText("Wire tensioned")

    def next(self):
        """ Update GUI with new data """
        data_list = list(self.thdl.transfer(self.thdl.qs))
        if len(data_list) > 0:
            tension = "%.2f" % data_list[0][1]
            self.ui.tensionlabel.setText(tension)
        wiretimer = int(time.time()) - self.wirestarttime
        self.ui.strawtimelabel.setText(str(wiretimer))

    def increment_straw(self):
        """ increment straw number by 2 if straw layer selected """
        self.thdl.join()
        if self.ui.topcheck.isChecked() or self.ui.bottomcheck.isChecked():
            self.ui.strawnumbox.setValue(self.ui.strawnumbox.value() + 2)
        else:
            self.ui.strawnumbox.setValue(self.ui.strawnumbox.value() + 1)
        self.reset()  # rest motor and start data
        self.ui.recordlabel.setText("")

    def reset(self):
        """ reset stepper motor to fully extended postion """
        self.thdl.join()  # end current thread
        self.wirestarttime = int(time.time())
        self.ui.statuslabel.setText("Resetting motor")
        self.ui.tensionlabel.setText("")
        self.micro = serial.Serial(port=self.port, baudrate=9600, timeout=0.08)
        self.micro.write(b"r")
        self.micro.write(b"\n")
        self.micro.close()
        self.start_data()
        self.ui.statuslabel.setText("Motor reset")

    def closeEvent(self, *args, **kwargs):
        """ End continuous data monitoring and free Arduino when GUI is closed """
        super(QMainWindow, self).closeEvent(*args, **kwargs)
        self.reset()
        self.thdl.join()

    def loadContinuity(self, position=None):
        # If no position is given, use current position
        if position is None:
            position = self.ui.strawnumbox.value()
        # Load data using method given in initialization
        cont, wire_pos = self.loadContinuityMethod(position)
        # If nothing is loaded, use default measurement
        if not all(meas is not None for meas in [cont, wire_pos]):
            cont = "Pass: No Continuity"
            wire_pos = "Middle 1/3"
        # Finds index of string, then sets index to that number
        setText = lambda combo_box, text: combo_box.setCurrentIndex(
            combo_box.findText(text)
        )
        # Call method on both continuity drop-downs with loaded data
        setText(self.ui.selectContinuity, cont)
        setText(self.ui.selectWirePosition, wire_pos)

    @staticmethod
    def getPortLocation():
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
            print("Arduino not found \nPlug wire tensioner into any USB port")
            time.sleep(2)
            print("Exiting script")
            sys.exit()
        print("Arduino at {}".format(arduino_ports[0]))
        return arduino_ports[0]


class GetDataThread(threading.Thread):
    """ Read data from Arduino Micro and stepper motor / load cell  """

    def __init__(self, qs, COM, baudrate=9600, timeout=0.08):
        threading.Thread.__init__(self)
        self.running = threading.Event()
        self.running.set()
        self.qs = qs
        self.micro_params = {"port": COM, "baudrate": baudrate, "timeout": timeout}
        print("starting thread")

    def run(self):
        self.micro = serial.Serial(**self.micro_params)
        print("thread running")
        while self.running.isSet():
            self.micro.write(b"\n")  ## requests motor postion and load cell reading
            line = self.micro.readline().strip()
            if line != b"":
                line = line.split(b"\t")
                if len(line) == 2:
                    THdata = [float(line[0]), float(line[1])]
                    # print(THdata)
                    self.qs.put((THdata))
                elif len(line) == 3:
                    print("work hardening tension:", float(line[1]))
        self.micro.close()
        print("closed")

    def transfer(self, qs):
        try:
            yield qs.get(True, 0.01)
        except queue.Empty:
            return

    def join(self, timeout=None):
        self.running.clear()
        threading.Thread.join(self, timeout)
        print("thread joined")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ctr = WireTensionWindow(
        lambda position, tension, timer, calib: print(
            f"\nPosition:\t{position}\nTension:\t{tension}\nTimer:\t{timer}\nCalibration:\t{calib}",
        ),
        None,
    )
    ctr.show()
    app.exec_()
