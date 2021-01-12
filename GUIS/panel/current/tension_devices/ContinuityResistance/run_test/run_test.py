# This script is used to run the continuity and resistance test.
# It talks to the tester box Arduino and writes a log file.
# Note: this script (and other QC scripts) use python 2.7.

import datetime
import serial
import uncertainties  # module for propagating uncertainties.
import colorama  # used to colour the terminal output
import numpy

# Initialize colorama.  autoreset = True makes it return to
# normal output after each print statement.
colorama.init(autoreset=True)

# Serial port parameters.  You may need to change "port" if you change computers.
port = "/dev/ttyACM0"
# testing switched from /ttyAMC1
# port = "/dev/cu.usbmodemFA131"
# port = "/dev/cu.usbmodemFA1331"
# port = "/dev/cu.usbmodemFD1231"
baudrate = 115200
timeout = None

serialport = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)

# This was measured with a Fluke multimeter.
calibration_resistor = uncertainties.ufloat(149.8, 0.3)

timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

logfilename = "log/resistancetest_" + timestamp + ".log"

# Lists to keep track of OK vs bad measurements.
wires_ok = [False] * 96
straws_ok = [False] * 96
oks = [wires_ok, straws_ok]

# ser_wrapper is a simple wrapper around the serial port that writes
# all written/read lines to a logfile.
class ser_wrapper:
    def __init__(self, ser):
        self.logfile = open(logfilename, "w", buffering=1)
        self.ser = ser

    def readline(self):
        line = self.ser.readline()
        self.logfile.write(line)
        return line

    def __del__(self):
        self.logfile.close()


# wrap the serial port.  From here on, use "ser" for any serial port communication.
# Additional lines can be "manually" added to the logfile, but these should all start with
# "#" to avoid confusing the parse_log script that runs later.
ser = ser_wrapper(serialport)
ser.logfile.write("# datetime: " + timestamp + "\n")

# This section gathers the worker and panel IDs.
# The workers can use the bar-code scanner or the keyboard for this.
print "Welcome to the Resistance and Continuity Test"
print "Type or scan your worker IDs, pressing enter after each one.  Enter a blank line when done"
workers = []
while True:
    worker = raw_input("worker name> ")
    if worker == "":
        break
    workers.append(worker)
wstr = ", ".join(workers)
ser.logfile.write("# workerids: " + wstr + "\n")

print "Type or scan the panel ID number"
panelid = raw_input("panel ID> ")
ser.logfile.write("# panelid:" + panelid + "\n")
ser.readline()

# Here begins the main loop to measure every straw and wire.
print "Begin testing!  Press Ctrl+C when the panel is finished."
print "Idx,\twire/straw,\tArduino R,\tHigh/Pass/Low,\tTruncated Mean R,\tN valid"
lastline, line = None, None  # lastline is a buffer for the previously-read line.
try:
    while True:
        # If we have a line in the serial port, buffer the previous line and read the new one.
        if ser.ser.inWaiting():
            lastline = line
            line = ser.readline()
        else:
            continue

        if not line:
            continue
        if line.startswith("#"):
            # Ignore "commented" lines from the Arduino.
            # These get logged in the log file regardless.
            print line
            continue
        # Split the line along commas.
        # 104 tokens are expected: index, straw/wire, 100 ADC values,
        # Arduino mean resistance, and HIGH/LOW/PASS.
        linelist = line.split(",")
        if len(linelist) != 104:
            print "# Possibly garbled line, please check and re-measure!"
            print line
            continue
        # Unpack the data
        idx, at_wire = int(linelist[0]), int(linelist[1])
        data = sorted(map(int, linelist[2:-2]))  # raw ADC values
        arduino_R = float(linelist[-2])
        arduino_result = linelist[-1].strip()  # HIGH/LOW/PASS
        at_wire_str = "wire" if at_wire else "straw"

        # If the measurement passes, record this in the lists.
        if arduino_result == "PASS":
            oks[int(at_wire)][idx] = True

        # Colour the terminal output appropriately.
        if arduino_result in ("HIGH", "LOW", "UNSTABLE"):
            arduino_result = colorama.Fore.RED + arduino_result
        else:
            arduino_result = colorama.Fore.GREEN + arduino_result

        # Here we recalculate the mean of the ADC values but filter out zeroes.
        if sum(data) > 0:
            filtered_data = [d for d in data if d != 0]
            n_items = len(filtered_data)

            filtered_mean = sum(filtered_data) / float(n_items)
            filtered_sigma = numpy.std(filtered_data)
            filtered = uncertainties.ufloat(filtered_mean, filtered_sigma)
            if n_items < 90:
                # Lots of filtered-out zeroes can indicate a problem, so we suggest
                # that the workers re-measure.
                print 100 - n_items, "measurements had to be discarded, please re-measure!"
        else:
            filtered = uncertainties.ufloat(0, 0)
            n_items = float("nan")

        # With the mean ADC value, we calculate the resistance, but it might be infinity.
        try:
            resistance = calibration_resistor * (1023 / filtered - 1)
        except ZeroDivisionError:
            resistance = uncertainties.ufloat(float("inf"), float("inf"))

        # I prefer str() to convert the value to a string, but some values give an error,
        # so repr() is used in those cases and it always works.
        try:
            resistance_str = str(resistance)
        except (ValueError, OverflowError):
            resistance_str = repr(resistance)

        # print the values for the user.  \t are tab characters.
        print idx, "\t", at_wire_str, "\t\t", arduino_R, "\t\t", arduino_result, "\t\t", resistance_str, "\t\t", n_items

except KeyboardInterrupt:
    # This happens when the user ends the test with Ctrl+C.
    # First we go through the "oks" list, which contains two lists of True/False values
    # for the wires and straws.
    for i, x_ok in enumerate(oks):
        first = True
        for idx, ok in enumerate(x_ok):
            if ok == False:
                if first:
                    first = False
                    sw_str = "wire" if i else "straw"
                    print "Missing values for", sw_str,
                print idx,
        if first == False:
            print ""

    print "Finished measuring panel %s." % panelid
    print "Log file is at", logfilename

    # Close the serial port.
    del ser

# Once data collection is finished, we can parse the log file and make a graph
# This is done in separate scripts with the log file, in case the data acquisition crashes
# we can rerun parse_log or make_graph.
import parse_log

datafilename = parse_log.parse_log(logfilename)
print "Data file and plots are at", datafilename
import make_graph

make_graph.make_graph(datafilename)
