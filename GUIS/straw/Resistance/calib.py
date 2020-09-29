#                                                                             *
#   Author:             Cole Kampa
#   Email:         <kampa041@umn.edu>
#   Institution: University of Minnesota
#   Project:              Mu2e
#   Date:	    	    8/31/17
#
#   Description:
#   A Python 3 script using PySerial to control and read from an Arduino
#   Uno and PCB connected to two calibration pallets. One pallet has
#   150 Ohm resistors, while the other is a wire (essentially zero
#   resistance). This script updates calib.csv, which is used with the
#   main script, measurement.py.
#
#   Columns in file (for database): straw_barcode, create_time,
#   worker_barcode, workstation_barcode, resistance, temperature,
#   humidity, test_type
#
#   Packages: PySerial
#
#   general order: arbrcrdrerfrgrhrirjrkrlrmrnrorpr
#
#   adjusted order: 1)erfrgrhr 2)arbrcrdr 3)mrnrorpr 4)irjrkrlr

import serial
from datetime import datetime
import time
import sys
import os

# pip install colorama should work fine
import colorama
from colorama import Back  # , Fore, Style

# set a larger window size
os.system("mode con: cols=130 lines=50")


##-Global Variables-##
straw_nums = [
    "01",
    "02",
    "03",
    "04",
    "05",
    "06",
    "07",
    "08",
    "09",
    "10",
    "11",
    "12",
    "13",
    "14",
    "15",
    "16",
    "17",
    "18",
    "19",
    "20",
    "21",
    "22",
    "23",
    "24",
]

"""
test_res_1 = {'01':150.6, '02':150.0, '03':149.8, '04':149.6, '05':149.9,
              '06':150.3, '07':150.3, '08':149.6, '09':149.9, '10':150.1,
              '11':150.0, '12':149.9, '13':150.5, '14':149.5, '15':151.1,
              '16':150.3, '17':150.2, '18':150.0, '19':150.1, '20':150.1,
              '21':150.5, '22':150.0, '23':150.2, '24':150.3}
"""

test_res_1 = {
    "01": 150.3,
    "02": 150.2,
    "03": 150.0,
    "04": 150.5,
    "05": 150.1,
    "06": 150.1,
    "07": 150.0,
    "08": 150.2,
    "09": 150.3,
    "10": 151.1,
    "11": 149.5,
    "12": 150.5,
    "13": 149.9,
    "14": 150.0,
    "15": 150.1,
    "16": 149.9,
    "17": 149.6,
    "18": 150.3,
    "19": 150.3,
    "20": 149.9,
    "21": 149.6,
    "22": 149.8,
    "23": 150.0,
    "24": 150.6,
}

test_res_2 = {
    "01": 0.1,
    "02": 0.1,
    "03": 0.1,
    "04": 0.1,
    "05": 0.1,
    # test_res_2 = {'01':75, '02':0, '03':0, '04':0, '05':0,
    "06": 0.1,
    "07": 0.1,
    "08": 0.1,
    "09": 0.1,
    "10": 0.1,
    "11": 0.1,
    "12": 0.1,
    "13": 0.1,
    "14": 0.1,
    "15": 0.1,
    "16": 0.1,
    "17": 0.1,
    "18": 0.1,
    "19": 0.1,
    "20": 0.1,
    "21": 0.1,
    "22": 0.1,
    "23": 0.1,
    "24": 0.1,
}

first_straw = {
    "a": "01ii",
    "b": "01io",
    "c": "01oi",
    "d": "01oo",
    "e": "02ii",
    "f": "02io",
    "g": "02oi",
    "h": "02oo",
    "i": "03ii",
    "j": "03io",
    "k": "03oi",
    "l": "03oo",
    "m": "04ii",
    "n": "04io",
    "o": "04oi",
    "p": "04oo",
}
#             Vin,V5, R0, R1, R2, R3, R4, R5
board_meas = [8.05, 5.0, 509.8, 509.8, 510.0, 510.0, 509.8, 510.0]

# first_straw = {'a':'02ii','b':'02io','c':'02oi','d':'02oo', 'e':'01ii','f':'01io','g':'01oi','h':'01oo',
#               'i':'04ii','j':'04io','k':'04oi','l':'04oo', 'm':'03ii','n':'03io','o':'03oi','p':'03oo'}

com_port = "COM3"

calib_file = "calib_check_" + datetime.now().strftime("%Y-%m-%d_%H%M%S") + ".csv"

meas_cycles = "abcdefghijklmnop"
avg_method = "average"
#   'average' for a strict averaging of resistance values, 'minimum'
#   for minimum measured resistance (max measured voltage)

##STARTING ARDUINO CONNECTION##
ser = serial.Serial(com_port, 9600)
print(ser.readline().decode("utf-8").rstrip())

# Gather voltage info
def voltage_calib():
    print("Remove cover of resistance meter box to measure...\n\n" + "Voltage:")
    vin = float(input("VIN vs. GND (black headers): "))
    v5 = float(input("5V vs. GND (black headers): "))
    return vin, v5


# Gather resistor 2 (on circuit board) info
def resistor_calib():
    r = [0, 0, 0, 0, 0, 0]
    print("\n" + "Resistance (Ohms):")
    print("(Small black rectangles, labeled on board)")
    r[0] = float(input("R0: "))
    r[1] = float(input("R1: "))
    r[2] = float(input("R2: "))
    r[3] = float(input("R3: "))
    r[4] = float(input("R4: "))
    r[5] = float(input("R5: "))
    return r


# Measure two resistance values with calibration pallet (150Ohm and 0 Ohm)
def measurement(vin, v5, r2, avg_type, straw_nums, first_straw):
    meas_dict = {}
    # setting averaging method
    if avg_type == "average":
        ser.write(b"y")
    elif avg_type == "minimum":
        ser.write(b"z")
    # creating meas_dict with keys that follow '01ii' scheme, in order
    for value in straw_nums:
        meas_dict[value + "ii"] = [0, 0]  # [res1, res2]
        meas_dict[value + "io"] = [0, 0]  # [res1, res2]
        meas_dict[value + "oi"] = [0, 0]  # [res1, res2]
        meas_dict[value + "oo"] = [0, 0]  # [res1, res2]
    # Measure voltage with arduino
    print("\nConnect left & right connectors to calibration pallet #1.")
    input("Press enter to calibrate...")
    voltage_1 = arduino_voltage(v5, first_straw)
    print("\nConnect left & right connectors to calibration pallet #2.")
    input("Press enter to calibrate...")
    print()
    voltage_2 = arduino_voltage(v5, first_straw)
    # Calculate measured resistance
    for key, value in sorted(meas_dict.items()):
        if voltage_1[key] != 0:
            value[0] = (
                float(r2[(int(key[:2]) - 1) // 4 - 1])
                * (v5 - voltage_1[key])
                / voltage_1[key]
            )
        else:
            # print(key + ': Voltage from first pallet = 0; R=inf\n')
            value[
                0
            ] = 0  # we just want to set this to inf...may screw with calibration a bit
        if voltage_2[key] != 0:
            value[1] = (
                float(r2[(int(key[:2]) - 1) // 4 - 1])
                * (v5 - voltage_2[key])
                / voltage_2[key]
            )
        else:
            # print(key + ': Voltage from second pallet = 0; R=inf\n')
            value[0] = 0
    # TESTING
    # input('Press enter to see calculations...')
    # print measured resistances, for reference
    return meas_dict


def arduino_voltage(v5, first_straw):
    volt_dict = {}
    # print("first_straw.items() :" + str(first_straw.items()))
    for key, value in sorted(first_straw.items()):
        straw1 = int(value[:2])
        measuring = value[2:]
        straws = [
            str("%02d" % (straw1)) + measuring,
            str("%02d" % (straw1 + 4)) + measuring,
            str("%02d" % (straw1 + 8)) + measuring,
            str("%02d" % (straw1 + 12)) + measuring,
            str("%02d" % (straw1 + 16)) + measuring,
            str("%02d" % (straw1 + 20)) + measuring,
        ]

        # Get raw arduino measurements for this switch configuratin. Go through each raw arduino measurement. If there are any 0's (failed conection), measure again.
        repeat_counter = 0
        measure_again = True

        nonZero_arduino_measurements = [0, 0, 0, 0, 0, 0]

        while measure_again and repeat_counter <= 20:  # Will loop a maximum of 20 times
            print("\n current key: " + str(key))
            ser.write(
                bytes(key + "r", "ascii")
            )  # send signal to switch to new cycle, then read
            bits_list = (
                ser.readline().decode("utf-8").rstrip().split(",")
            )  # bits_list is raw output from arduino

            # bits_list[0] is just the key (a, b, c, etc...) for the given cycle
            if bits_list[0] != key:
                print("Error! The wrong measurement was collected from the arduino!")
                input("Enter to exit...")
                sys.exit(0)
            del bits_list[0]

            # FOR DEBUGGING#
            # print('\n\n Before filtering \n')
            # print("nonZero_arduino_measurements: " + str(nonZero_arduino_measurements))
            # print("bits_list: " + str(bits_list))

            # Check arduino measurements for zeros

            index = 0
            measure_again = False  # if this remains false, numbers are non-zero
            while index < len(bits_list):
                # Get data
                current_number = nonZero_arduino_measurements[index]
                if current_number == 0:
                    new_number = float(bits_list[index])
                    if new_number != 0:  # if new_number is non-zero...
                        nonZero_arduino_measurements[
                            index
                        ] = new_number  # record new_number
                    if (
                        new_number == 0 and current_number == 0
                    ):  # if new_number is also zero...
                        measure_again = True
                        # new_number is not recorded, you need to measure again
                # Next index
                index += 1

            # print('\n After filtering \n')
            # print("nonZero_arduino_measurements: " + str(nonZero_arduino_measurements))
            # print("bits_list: " + str(bits_list))

            repeat_counter += 1

            print("\n Repeat counter: " + str(repeat_counter))
            print("Measure again: " + str(measure_again))

        print("nonZero_arduino_measurements: " + str(nonZero_arduino_measurements))
        # After obtaining good non-zero arduino measurements, calculate voltage and save
        # for key in straws:
        i = 0
        for key in sorted(straws):
            # calculate voltage and save
            volt_dict[key] = float(nonZero_arduino_measurements[i]) * v5 / 1023.0
            i += 1

    return volt_dict


def calculate_calib(
    meas_dict, tr1, tr2, straw_nums
):  # tr = test resistance (resistance of test pallets measured by-hand w/ multimeter (see top)
    calib_dict = {}
    for value in straw_nums:
        calib_dict[value + "ii"] = [0, 0, ""]  # [% error, device resistance, pass/fail]
        calib_dict[value + "io"] = [0, 0, ""]  # [% error, device resistance, pass/fail]
        calib_dict[value + "oi"] = [0, 0, ""]  # [% error, device resistance, pass/fail]
        calib_dict[value + "oo"] = [0, 0, ""]  # [% error, device resistance, pass/fail]
    for key, value in sorted(meas_dict.items()):
        print("key: " + str(key))
        print("value[0]: " + str(value[0]))
        print("value[1]: " + str(value[1]))
        perc_e = 1 - (value[0] - value[1]) / (tr1[key[:2]] - tr2[key[:2]])
        print("%e: " + str(perc_e))
        ##########
        # testing while not changing to r2 (shorted)
        if perc_e != 1:
            dev_res = value[0] / (1 - perc_e) - tr1[key[:2]]
        else:
            dev_res = 0
        #########
        # dev_res = value[0]/(1-perc_e) - tr1[key[:2]]
        calib_dict[key][0] = perc_e
        calib_dict[key][1] = dev_res
        # only certain values pass calibration (based on our expectations)
        if (0.10 <= perc_e <= 0.40) and (100.0 <= dev_res <= 500):
            calib_dict[key][2] = "pass"
        else:
            calib_dict[key][2] = "fail"

    return calib_dict


def display_calib(vin, v5, r2_list, save_dict):
    print("\n" + "Vin = " + str(vin) + ", 5V = " + str(v5))
    print(
        "R0 = "
        + str(r2_list[0])
        + ", "
        + "R1 = "
        + str(r2_list[1])
        + ", "
        + "R2 = "
        + str(r2_list[2])
        + "\n"
        + "R3 = "
        + str(r2_list[3])
        + ", "
        + "R4 = "
        + str(r2_list[4])
        + ", "
        + "R5 = "
        + str(r2_list[5])
        + "\n\n"
    )

    i = 1
    print("#/Type %Err     Dev_Res")
    print("-----------------------")
    for key, value in sorted(save_dict.items()):
        print(
            "(" + key + ": " + "%5.3f" % value[0] + ", " + "%8.2f" % value[1] + ", ",
            end="",
        )
        if value[2] == "pass":
            print(Back.GREEN, end="")
        else:
            print(Back.RED, end="")
        print(value[2] + Back.RESET + ")", end="")
        # every four measurements, print a new line
        if i % 4 == 0:
            print()
        else:
            print(", ", end="")

        i += 1


def check_repeat():
    check = input("\nDoes this calibration look good (y/n)? ")
    if check == "y":
        return False
    else:
        print("Repeating calibration...\n")
        return True


def save_calib(c_file, vin, v5, r2, calib_dict):
    print("\nNow saving...\n")
    # write voltage calibration
    c_file.write("*Vin, 5V*" + "\n" + str(vin) + ", " + str(v5) + "\n")
    # write resistance calibration
    c_file.write("*R0, R1, R2, R3, R4, R5*\n")
    c_file.write(
        str(r2[0])
        + ", "
        + str(r2[1])
        + ", "
        + str(r2[2])
        + ", "
        + str(r2[3])
        + ", "
        + str(r2[4])
        + ", "
        + str(r2[5])
        + "\n"
    )
    # write measurement calibration (one line for each of the 96 measurements)
    # key = '01ii', value[0] = 0 <= %err <= 1.0, value[1] = Device_Resistance
    c_file.write("*Measurement, % Error, Device_Resistance*" + "\n")
    for key, value in sorted(calib_dict.items()):
        c_file.write(key + ", " + str(value[0]) + ", " + str(value[1]) + "\n")


def main():
    colorama.init()  # turn colorama ANSII conversion on
    # open the file as 'w'=write (will overwrite current calibration file)
    with open(calib_file, "w") as f:
        use_store = input("Use stored values for board measurements (y/n)? ")
        if use_store == "y":
            r2_vals = [0, 0, 0, 0, 0, 0]
            (
                vin,
                v5,
                r2_vals[0],
                r2_vals[1],
                r2_vals[2],
                r2_vals[3],
                r2_vals[4],
                r2_vals[5],
            ) = board_meas
        else:
            vin, v5 = voltage_calib()
            r2_vals = resistor_calib()

        save_dict = {}
        for value in straw_nums:
            save_dict[value + "ii"] = [
                0,
                0,
                "fail",
            ]  # [% error, device resistance, pass/fail]
            save_dict[value + "io"] = [
                0,
                0,
                "fail",
            ]  # [% error, device resistance, pass/fail]
            save_dict[value + "oi"] = [
                0,
                0,
                "fail",
            ]  # [% error, device resistance, pass/fail]
            save_dict[value + "oo"] = [
                0,
                0,
                "fail",
            ]  # [% error, device resistance, pass/fail]

        repeat = True
        counter = 0
        while repeat == True:
            meas_res = measurement(
                vin, v5, r2_vals, avg_method, straw_nums, first_straw
            )
            calib_dict = calculate_calib(meas_res, test_res_1, test_res_2, straw_nums)
            all_pass = True
            for key, value in sorted(save_dict.items()):
                # original code:
                # if value[2] != 'pass' and calib_dict[key][2] == 'pass': #Replaces former 'fail's with new 'pass's

                # altered filtering process [9-13-18]
                if value[2] != "pass":  # If what's currently there fails, try the new
                    value[0] = calib_dict[key][0]
                    value[1] = calib_dict[key][1]
                    value[2] = calib_dict[key][2]
                if value[2] != "pass":  #
                    all_pass = False
            display_calib(vin, v5, r2_vals, save_dict)
            counter += 1
            if all_pass == True or counter >= 5:
                repeat = check_repeat()
        save_calib(f, vin, v5, r2_vals, save_dict)
        colorama.deinit()  # turn colorama ANSII conversion off


main()
