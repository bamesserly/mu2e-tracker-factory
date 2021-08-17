# This script is used to run the continuity and resistance test.
# It talks to the tester box Arduino and writes a log file.

import datetime
import serial
import serial.tools.list_ports
import uncertainties  # module for propagating uncertainties.
import colorama  # used to colour the terminal output
import numpy
import os
from guis.common.getresources import GetProjectPaths
from sys import exit


def GetSerialPort():
    baudrate = 115200
    timeout = None

    # Linux ports look like this: "/dev/ttyACM0" or "/dev/cu.usbmodemFD1231"
    # Windows ports look like this: "COM6"
    # from command line, try: python -m serial.tools.list_ports
    serialport = None
    avail_ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(avail_ports):
        # print("{}: {} [{}]".format(port, desc, hwid))
        if "USB" in desc or "USB" in hwid:

            # The QC computer uses a different arduino than the others and/or
            # the resistance arduino box is named differently on this computer
            # and/or confusion is caused with the temp/humid device
            if "15" in os.getenv("USERDOMAIN") and not (
                "Arduino" in desc or "Arduino" in hwid
            ):
                continue

            try:
                serialport = serial.Serial(
                    port=port, baudrate=baudrate, timeout=timeout
                )
                print("Using port", port)
                return serialport
            except:
                continue
    print("Can't find working port. Is arduino plugged in?")
    print("Ports found:")
    for port, desc, hwid in sorted(avail_ports):
        print("{}: {} [{}]".format(port, desc, hwid))
    exit()


# Initialize colorama.  autoreset = True makes it return to
# normal output after each print statement.
colorama.init(autoreset=True)

# This was measured with a Fluke multimeter.
calibration_resistor = uncertainties.ufloat(149.8, 0.3)

timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

# Lists to keep track of OK vs bad measurements.
wires_ok = [False] * 96
straws_ok = [False] * 96
oks = [wires_ok, straws_ok]

# ser_wrapper is a simple wrapper around the serial port that writes
# all written/read lines to a logfile.
class ser_wrapper:
    def __init__(self, ser, logfile):
        self.logfile = open(logfile, "w", buffering=1)
        self.ser = ser

    def readline(self):
        line = self.ser.readline().decode("utf-8").strip() + "\n"
        self.logfile.write(line)
        return line

    def write(self, cmd):
        self.ser.write(str(cmd).encode("utf8"))

    def __del__(self):
        self.logfile.close()


def main():
    ############################################################################
    # Get workers from input()
    ############################################################################
    print("Welcome to the Resistance and Continuity Test")
    print(
        "Type or scan your worker IDs, pressing enter after each one.  Enter a blank line when done"
    )
    workers = []
    while True:
        worker = input("worker name> ")
        if worker == "":
            break
        workers.append(worker)
    wstr = ", ".join(workers)

    ############################################################################
    # Get panel number from input()
    ############################################################################
    print(
        'Type or scan the panel ID number. Just the 3-digit number "109",'
        'skip the "MN" part.'
    )
    panelid = input("panel ID> ")
    panelid = str(panelid)

    ############################################################################
    # Specify which measurement is being done
    ############################################################################
    when = -1
    while True:
        try:
            print("Which resistance measurement is this?")
            when = int(
                input(
                    "[1] brass-brass (i-i) \n[2] aluminum-aluminum (o-o)\n[3] Final QC\n>"
                )
            )
            assert when in [1, 2, 3]
            break
        except AssertionError:
            print("Invalid measurement. Must be 1, 2, or 3.")
        except ValueError:
            print("Invalid measurement. Must be integer 1, 2, or 3.")

    ############################################################################
    # wrap the serial port.  From here on, use "ser" for any serial port communication.
    # Additional lines can be "manually" added to the logfile, but these should all start with
    # "#" to avoid confusing the parse_log script that runs later.
    ############################################################################
    stage_tag = {1: "i-i", 2: "o-o", 3: "finalQC"}
    logfilename = (
        "resistancetest_MN" + panelid + "_" + timestamp + "_" + stage_tag[when] + ".log"
    )
    dir_path = GetProjectPaths()["panelresistancedata"] / "RawData" / f"MN{panelid}"
    dir_path.mkdir(exist_ok=True, parents=True)

    logfile = dir_path / logfilename

    print("raw data going to", str(logfile))

    serialport = GetSerialPort()

    ser = ser_wrapper(serialport, logfile)

    ser.logfile.write("# datetime: " + timestamp + "\n")
    ser.logfile.write("# workerids: " + wstr + "\n")
    ser.logfile.write("# panelid:" + panelid + "\n")
    ser.logfile.write("# measurement stage:" + stage_tag[when] + "\n")
    # ser.readline()

    # Tell the arduino to enter straws-only mode if when = i-i or o-o
    if when == 1 or when == 2:
        ser.write("s")  # yes, straw mode
    else:
        ser.write("\n")  # no, not straw mode

    # Here begins the main loop to measure every straw and wire.
    print("Begin testing!  Press Ctrl+C when the panel is finished.")
    print("Idx,\twire/straw,\tArduino R,\tHigh/Pass/Low,\tTruncated Mean R,\tN valid")
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
                print("not line")
            if line.startswith("#"):
                # Ignore "commented" lines from the Arduino.
                # These get logged in the log file regardless.
                print(line)
                continue
            # Split the line along commas.
            # 104 tokens are expected: index, straw/wire, 100 ADC values,
            # Arduino mean resistance, and HIGH/LOW/PASS.
            linelist = line.split(",")
            if len(linelist) != 104:
                print("# Possibly garbled line, please check and re-measure!")
                print(line)
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
                    print(
                        100 - n_items,
                        "measurements had to be discarded, please re-measure!",
                    )
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
            print(
                idx,
                "\t",
                at_wire_str,
                "\t\t",
                arduino_R,
                "\t\t",
                arduino_result,
                "\t\t",
                resistance_str,
                "\t\t",
                n_items,
            )

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
                        print("Missing values for", sw_str)
                    print(idx)
            if first == False:
                print("")

        print("Finished measuring panel %s." % panelid)
        print("Log file is at", dir_path + logfilename)

        # Close the serial port.
        del ser

    # Once data collection is finished, we can parse the log file and make a graph
    # This is done in separate scripts with the log file, in case the data acquisition crashes
    # we can rerun parse_log or make_graph.
    import parse_log

    datafilename = parse_log.parse_log(logfile)
    print("Data file and plots are at", datafilename)
    import make_graph

    make_graph.make_graph(datafilename, panelid, logfilename, stage_tag[when])


if __name__ == "__main__":
    main()
