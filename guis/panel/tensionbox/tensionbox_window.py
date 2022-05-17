# run.py
#
# Python code used to run the GUI and control the Arduino Micro for straw tension measurements.
#
# Created 14 December 2014
# By Vadim Rusu (vrusu@fnal.gov)
# Updated 22 February 2016
# By Lauren Yates (yatesla@fnal.gov)

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QHBoxLayout, QFileDialog, QGridLayout, QLabel
import sys
import os

import serial.tools.list_ports  ## automatically get COM port
import guis.panel.tensionbox.tensionbox_ui as tensionbox_ui  ## edit in Qt Designer, convert with pyuic5

import numpy as np
from numpy.fft import rfft, irfft
from numpy import argmax, sqrt, mean, diff, log
import matplotlib
import matplotlib.pyplot as plt
import serial  ## from pyserial
import math, time, os
import csv

from scipy.signal import blackmanharris, fftconvolve
from guis.panel.tensionbox.parabolic import parabolic

from guis.common.db_classes.measurements_panel import TensionboxMeasurement

from datetime import datetime as dt
from guis.panel.tensionbox.X0117d import DataCanvas  ## control window for plots

from guis.common.getresources import GetProjectPaths

nplot = 200
nmax = 400
SampleRate = 1.0 / 8900.0  # In kHz

nlines = 2000  # Should match DataLength in the Arduino code

# Read in the list of straw lengths from a text file
# Text file must have one straw length per line (in units of centimeters), must be ordered from 0 to 95, and must be
#     named straw_lengths.txt
this_folder = os.path.dirname(os.path.realpath(__file__))


class TensionBox(QMainWindow, tensionbox_ui.Ui_MainWindow):
    """
    Class definition for the UI and associated functions.

    Vadim: hwl is inherited from both QtGui.QDialog and myui.Ui_Dialog
    """

    def __init__(self, saveMethod=None, panel=str(), pro=str(), parent=None):
        """Vadim: Initialization of the class. Call the __init__ for the super classes"""
        super(TensionBox, self).__init__(parent)
        self.setupUi(self)
        self.connectActions()
        self.process = pro
        self.panel = panel

        # Save input variables
        if panel:
            self.panelID.setText(panel)
            self.panelID.setDisabled(True)
        self.saveMethod = saveMethod

        self.portloc = self.getPortLocation()  ## Arduino COM port
        self.openSerial()
        self.setupCanvas()
    

    def openSerial(self):
        """Open the serial connection with the Arduino"""
        self.ser = serial.Serial(port=self.portloc, baudrate=115200)
        time.sleep(1)

    def main(self):
        """Make the dialog window visible for the user to interact with"""
        self.show()

    def connectActions(self):
        """Connect the user interface controls to the logic"""
        self.runButton.clicked.connect(self.run)
        self.runnext.clicked.connect(lambda: self.run(nextstraw=True))
    
    def acquire_tbdata(self):
        if self.process == 6:
            self.wire_tensions = [None]*96
            self.straw_tensions = [None]*96
        else:
            self.wire_tensions = []
            self.straw_tensions = []
            
            # acquire and process straw tb data
            straw_prelim = TensionboxMeasurement.get_tb_measurements(self.panel, "straw")
            min_straws = []
            for i in range(96):
                # iterate through the list of
                min_entry = None
                for j in range(len(straw_prelim)):
                    if straw_prelim[j][4] == i:
                        if min_entry == None or straw_prelim[j][9] > min_entry[9]:
                            min_entry = straw_prelim[j]
                if min_entry is not None:
                    self.straw_tensions.append(min_entry[8])
                else:
                    self.straw_tensions.append(None)
    
            # acquire and process wire tb data
            wire_prelim = TensionboxMeasurement.get_tb_measurements(self.panel, "wire")
            min_wires = []
            for i in range(96):
                # iterate through the list of
                min_entry = None
                for j in range(len(wire_prelim)):
                    if wire_prelim[j][4] == i:
                        if min_entry == None or wire_prelim[j][9] > min_entry[9]:
                            min_entry = wire_prelim[j]
                if min_entry is not None:
                    self.wire_tensions.append(min_entry[8])
                else:
                    self.wire_tensions.append(None)
                
    def process_data(self):
        wire_data=[]
        straw_data=[]
        for i in range(96):
            if self.wire_tensions[i] is not None:
                wire_data.append(self.wire_tensions[i])
            else:
                wire_data.append(1000)
            if self.straw_tensions[i] is not None:
                straw_data.append(self.straw_tensions[i])
            else:
                straw_data.append(1000)
            
        return [wire_data, straw_data]
        
    def plot_tensions(self, initial):
        if initial:
            wire_data, straw_data = self.process_data()
            indices=[*range(0,96,1)]
            self.wire_plotted = self.canvas.axes.plot(indices,wire_data,"g.",color="k")[0]
            self.straw_plotted = self.canvas.rhs_axes.plot(indices,straw_data,"g.",color="r")[0]
        else:
            wire_data, straw_data = self.process_data()
            self.wire_plotted.set_ydata(wire_data)
            self.straw_plotted.set_ydata(straw_data)
            self.canvas.draw()
            self.canvas.flush_events()
        
    def display_scroll(self, initial):
        wire_display=[]
        straw_display=[]
        
        for i in range(96):
            if self.wire_tensions[i] != None:
                wire_display.append(round(self.wire_tensions[i],2))
            else:
                wire_display.append(None)
            if self.straw_tensions[i] != None:
                straw_display.append(round(self.straw_tensions[i],2))
            else:
                straw_display.append(None)
        
        if initial is True:
            self.tbGrid = QGridLayout()
        else:
            for i in range(self.tbGrid.count()):
                self.tbGrid.itemAt(i).widget().close()
                
        for i in range(96):
            tbLabel = QLabel(f"{i}")  # start with straw position labels
            tbLabel.setStyleSheet("color: black")
            tbLabel.setObjectName(
                f"tbLabel_{i}"
            )  # they can't (shouldn't) all have the same name
                
            tb_wire_label = QLabel(
                f"{wire_display[i]}"
            )  # create qlabels for the wires
            tb_wire_label.setStyleSheet("color: black")
            tb_wire_label.setObjectName(
                f"tbLabel_{wire_display[i]}"
            )  # they can't (shouldn't) all have the same name
            
            # set proper data
            self.tbGrid.addWidget(tbLabel, i, 0)  # add them to grid, 0th column
            self.tbGrid.addWidget(
                tb_wire_label, i, 1, Qt.AlignHCenter
            )  # add them to grid, 1st column
            
            tb_straw_label = QLabel(
                f"{straw_display[i]}"
            )  # create qlabels for the straws
            tb_straw_label.setStyleSheet("color: black")
            tb_straw_label.setObjectName(
                f"tbLabel_{straw_display[i]}"
            )  # they can't (shouldn't) all have the same name

            self.tbGrid.addWidget(
                tb_straw_label, i, 2, Qt.AlignHCenter
            )  # add them to grid, 2n column
            
            # add the newly created grid layout to the GUI
            self.scrollContents.setLayout(self.tbGrid)
            # scrollontents is made in the .ui file, and hvGrid is made in this file by the stuff above in this function
                
                
                
                
                
                
    def setupCanvas(self):
        """Set up canvas for plotting wire number vs. tension"""
        self.data_widget = QWidget(self.graphicsView)
        layout = QHBoxLayout(self.graphicsView)
        self.acquire_tbdata()
        self.canvas = DataCanvas(
            self.data_widget,
            data=None,
            width=5,
            height=4,
            dpi=100,
            xlabel="Wire Number",
            ylabel="Wire Tension [g]",
            ylabel2="Straw Tension [g]",
        )
        layout.addWidget(self.canvas)
        self.data_widget.repaint()
        
        self.plot_tensions(True)
        self.display_scroll(True)

    def run(self, nextstraw=False):
        """
        Function that is called when the "runButton" is clicked

            Reads in relevant information from the UI. Calls the function that triggers the Arduino to take data, and
            thus obtains the frequency of the straw's vibrations. Computes the tension.

            ***
            After each run, writes a line with the time, straw number, straw length, temperature, relative humidity,
            frequency, pulse width used, and tension to the output file.
            ***
        """
        ## increment straw number if "measure next" button clicked
        if nextstraw:
            self.spinBox.setValue(self.spinBox.value() + 1)

        # Read in the straw number
        strawNumber = self.spinBox.value()
        # Read in the measurement type, and set straw flag appropriately
        if str(self.comboBox.currentText()) == "Wire":
            is_straw = 0
            print("\nwire number", strawNumber)
        elif str(self.comboBox.currentText()) == "Straw":
            is_straw = 1
            print("\nstraw number", strawNumber)
        else:
            is_straw = -1

        # Set the straw or wire length
        if strawNumber == -1:
            # Set the straw length based on what is in the straw length box
            length = float(self.lengthEdit.text())  # units are now in meters.
        else:
            if is_straw == 0:
                # Read in the wire lengths
                lengths = np.loadtxt(os.path.join(this_folder, "wire_lengths.txt"))
            elif is_straw == 1:
                # Read in the straw lengths
                lengths = np.loadtxt(os.path.join(this_folder, "straw_lengths.txt"))
            else:
                lengths = np.zeros(96)
            lengths = lengths / 100.0  # Convert to meters
            # Look up the length, based on the straw number
            length = lengths[strawNumber]
            # Set the length in the UI (meters)
            length_display = "%.3f" % length

            self.lengthEdit.setText(length_display)
        # Set straw and wire parameters [see parameters.txt]
        mu = 0.00010505  # effective mass density in [g/cm]
        K = 156.5
        C = 3.067

        # Set the nominal tension to compute the initial pulse width to use
        try:
            tension = float(self.tensionEdit.text())
        except ValueError:
            tension = 80.0  # nominal tension in grams
        # Wires: calculate nominal frequency from nominal tension
        if is_straw == 0:
            freq = (1 / (2 * length)) * np.sqrt(tension / mu)
        # Straws: calculate nominal frequency from nominal tension
        elif is_straw == 1:
            # For a straw
            tension = tension * 10.0  # nominal tension in grams
            freq = np.sqrt(tension / 1000) * (K / (2 * length)) + C / (length) ** 2
            # tension = [1000*((f-C/(L/100)**2)*2*(L/100)/K)**2 for L,f in zip(length,freq)]
        # Calculate the desired pulse width in microseconds
        pulse_width = (1.0 / (2 * freq)) * 10 ** 6

        for i in range(0, self.SpinNiter.value()):
            # Call the function that triggers the Arduino to take data
            freq = self.ping10(i, pulse_width)

            # Given the frequency, calculate the tension in the straw or wire
            if is_straw == 0:
                # For a wire
                # tension = mu*(length**2)*(freq**2)/245.16625
                grav_accel = 9.80665  # acceleration due to gravity [m/s^2]
                tension = (
                    4 * (length ** 2) * mu * (freq ** 2) * (100 / grav_accel)
                )  # tension in grams
            elif is_straw == 1:
                # For a straw
                tension = (
                    1000 * ((freq - C / length ** 2) ** 2) * (2 * length / K) ** 2
                )  # tension in grams
            else:
                tension = 0

            # Set the tension in the UI
            tension_display = "%.3f" % tension
            self.tensionEdit.setText(tension_display)

            # print(strawNumber, is_straw, length,freq,pulse_width,tension)

            """
            # Write a summary of the results to the output file
            fdef.write(str(dt.now()))
            panel=self.panelID.text()
            if panel=='': ## default MN000 for testing
                panel = 'MN000'
            value = ' {0} {1} {2} {3} {4} {5} {6}\n'.format(panel,strawNumber, is_straw, length, freq, pulse_width, tension)
            fdef.write(str(value))
            """
            self.save(
                is_straw=bool(is_straw),
                position=strawNumber,
                length=length,
                frequency=freq,
                pulse_width=pulse_width,
                tension=tension,
            )
            if is_straw == 1:
                self.straw_tensions[self.spinBox.value()] = tension
            else:
                self.wire_tensions[self.spinBox.value()] = tension
            
            self.plot_tensions(False)
            self.display_scroll(False)

            # Given the frequency, calculate the desired pulse width in microseconds for the next run
            pulse_width = (1.0 / (2 * freq)) * 10 ** 6

    def ping10(self, i, pulse_width):
        """
        Function that prompts the Arduino to take data for one iteration

        Reads in the resulting data. Writes it to an output file. Returns
        relative humidity, temperature, and measured vibration frequency.

        These output files are just used to hold values in order to iteratively
        calculate means. I don't think they should be tracked or saved."
        """

        data1 = [0] * nlines
        for ik in range(0, self.SpinNpulses.value()):

            filename = "cache/cache" + str(ik) + ".txt"
            file = os.path.join(this_folder, filename)
            f = open(file, "w")

            # Trigger the Arduino to take data
            self.ser.write(b"5\n")

            # Write out the desired pulse width
            # Arduino code must be updated to know to accept this

            try:
                self.ser.write(bytes(str(int(pulse_width)) + "\n", "UTF-8"))
            except ValueError:
                print(
                    "NaN Pulse Width! In the past, this has been caused by "
                    "a power issue -- not enough power, broken barrel jack."
                )
            self.ser.readline()  # Read in the line where Arduino echos trigger

            # Read in the line where Arduino prints the pulse width, and print it out once per iteration
            if ik == 0:
                # print (str(self.ser.readline()))  # Read in and print line where Arduino prints pulse width
                print(self.ser.readline().decode("utf-8").strip())
            else:
                self.ser.readline()  # Read in and print line where Arduino prints pulse width
            # Read in the straw displacement data, and write it out to a file
            for ic in range(0, nlines):
                line = int(self.ser.readline())
                if line >= 8192:
                    val = (line - 16383) * 1.22
                else:
                    val = (line + 1) * 1.22

                f.write(" %s" % val)
                if ic < nlines - 1:
                    f.write(",")
            # ser.close()
            f.close()

            # Read back in the data from that file and add it to previous data
            data = np.genfromtxt(file, delimiter=",")
            data = data - data.mean()
            data1 = np.add(data1, data)

            # Set the value in the progress bar (based on both iterations and pulses)
            self.progressBar.setValue(
                100
                * (i + 1)
                * (ik + 1)
                / (self.SpinNiter.value() * self.SpinNpulses.value())
            )

        # Compute the frequency
        freq = freq_from_fft(data1, 1.0 / SampleRate)

        # Write these results back out to the UI
        freq_display = "%.3f" % freq
        # self.freqEdit.setText(str(freq))
        self.freqEdit.setText(freq_display)

        # Use this to plot the data only on the last iteration
        if i == self.SpinNiter.value() - 1:
            # other options: plt.close(1); plt.close()
            plt.close("all")
            plotadc(data1)
        return freq

    def cleanUp(self):
        # Clean up everything
        for i in self.__dict__:
            item = self.__dict__[i]
            clean(item)

    """
    save(self,is_straw,position,length,frequency,pulse_width,tension)

        Description:    Saves a tension measurement

        Input:
            is_straw    (bool)  -   Indicates whether this measurement is for a straw or a wire. True => Straw, False => Wire
            position    (int)   -   Position of wire/straw on panel
            length      (float) -   Length of item being measured
            frequency   (float) -   Measured frequency
            pulse_width (float) -   Measured pulse_width
            tension     (float) -   Measured tension
    """

    def save(self, is_straw, position, length, frequency, pulse_width, tension):
        # Get the panel ID
        panel = self.panelID.text()
        if panel == "":  ## default MN000 for testing
            panel = None

        # Get process
        process = str(self.process)

        # If this window has a pointer to a save method, call that method as well.
        if self.saveMethod is not None:
            self.saveMethod(
                panel, is_straw, position, length, frequency, pulse_width, tension
            )

        # Add entry to csv file
        outfile = panel + "_proc" + process + ".csv"
        outfile = GetProjectPaths()["straw_tensioner_data"] / outfile
        outfile.parent.mkdir(exist_ok=True, parents=True)

        if outfile.is_file():
            with open(outfile, "a", newline="") as f:
                csvwriter = csv.writer(f)
                entry = [
                    dt.now().isoformat(),
                    is_straw,
                    position,
                    length,
                    frequency,
                    pulse_width,
                    tension,
                ]
                csvwriter.writerow(entry)
        else:
            with open(outfile, "w", newline="") as f:
                f.write("Tension Box data for " + panel + "\n")
                csvwriter = csv.writer(f)
                header = [
                    "timestamp",
                    "is_straw",
                    "position",
                    "length",
                    "frequency",
                    "pulse_width",
                    "tension",
                ]
                csvwriter.writerow(header)
                entry = [
                    dt.now().isoformat(),
                    is_straw,
                    position,
                    length,
                    frequency,
                    pulse_width,
                    tension,
                ]
                csvwriter.writerow(entry)

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
            print("Arduino not found \nPlug tension box into any USB port")
            time.sleep(2)
            print("Exiting script")
            sys.exit()
        print("Arduino at {}".format(arduino_ports[0]))
        return arduino_ports[0]


def freq_from_fft(signal, fs):
    """Estimate frequency from peak of FFT"""

    # Compute Fourier transform of windowed signal
    windowed = signal * blackmanharris(len(signal))
    f = rfft(windowed)

    # Find the peak and interpolate to get a more accurate peak
    i = argmax(abs(f[:nmax]))  # Just use this for less-accurate, naive version
    true_i = parabolic(log(abs(f)), i)[0]

    # Convert to equivalent frequency
    return fs * true_i / len(windowed)


def plotadc(y0):
    """Plots the data (ADC counts) from the Arduino and the FFT of that data"""

    ft0 = np.fft.fft(y0 * np.hanning(len(y0))) / (len(y0) / 4)
    logft0 = 20 * np.log10(abs(ft0) / 4096)
    fftnumber0 = 1.0 / (len(y0) * SampleRate)

    plt.clf()
    # plt.ion()
    fig = plt.figure(1)

    ax1 = fig.add_subplot(211)

    ax1.set_title("Data")
    ax1.set_xlabel("ms")
    ax1.set_ylabel("ADC counts")
    xx = range(0, len(y0))
    x = np.asarray(xx)
    x = x * SampleRate * 1000  # Make it ms
    ax1.plot(x[0:1800], y0[0:1800])
    ax1.get_yaxis().get_major_formatter().set_useOffset(False)
    # leg = ax1.legend()

    ax2 = fig.add_subplot(212)

    # ax2.set_title("Plot title...")
    ax2.set_xlabel("Hz")
    ax2.set_ylabel("dBFS")
    xft0 = [fftnumber0 * float(i) for i in xx]

    ax2.plot(xft0[0:nplot], logft0[0:nplot], label="the data")
    # ax2.plot(xft0, logft0, label='the data')
    ax2.get_yaxis().get_major_formatter().set_useOffset(False)

    plt.show()


def clean(item):
    """Clean up the memory by closing and deleting the item if possible."""
    if isinstance(item, list) or isinstance(item, dict):
        for _ in range(len(item)):
            clean(item.pop())
    else:
        try:
            item.close()
        except (RuntimeError, AttributeError):  # deleted or no close method
            pass
        try:
            item.deleteLater()
        except (RuntimeError, AttributeError):  # deleted or no deleteLater method
            pass


# end cleanUp


def run():
    app = QApplication(sys.argv)
    hwl1 = TensionBox(
        saveMethod=lambda *args: print(f"\nMeasurement: {args}"),
        panel="MN999",
    )
    hwl1.main()
    app.aboutToQuit.connect(hwl1.cleanUp)
    sys.exit(app.exec_())


if __name__ == "__main__":
    run()
