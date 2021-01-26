###
# make_CPAL_labels.py
#
# Used to make barcodes for initial straw prep
# Does not require any user input as it will automatically keep track of
# all necessary information
#
# Uses BarcodePrinter class: \\MU2E-CART1\Database Backup\BarcodePrinter\BarcodePrinter.py
#
# Created by: Joe Dill, January 2019, dillx031@umn.edu
# Revision of straw_label_script.py by Mathew Hiel
#
###

import time
from datetime import datetime
import sys
import os

# #import BarcodePrinter
sys.path.insert(0, os.path.dirname(__file__) + "/../")
# Billy: The line below actually import a .py file which contains the BarcodePrinter class in BarcodePrinter.py
# Therefore, when we call BarcodePrinter, we are calling a module object whose type is not allowed to be called
# See more at the second answer of https://stackoverflow.com/questions/4534438/typeerror-module-object-is-not-callable
from BarcodePrinter import BarcodePrinter


# automatically keep track of the number of straw batches done in a day
def update_daily_num():
    # Get old number
    f = open(
        os.path.dirname(__file__)
        + "/../../../Modules/BarcodePrinter/CpalLabels/dailytotal.txt",
        "r",
    )
    old_number = int(f.read())
    f.close()
    # Calculate new number
    new_number = (old_number + 1) % 100  # If data > 100, reset to 0
    # Write new number
    f = open(
        os.path.dirname(__file__)
        + "/../../../Modules/BarcodePrinter/CpalLabels/dailytotal.txt",
        "w",
    )
    f.write(str(new_number))
    f.close()
    # Return
    return new_number


def reset_daily_num():
    f = open(
        os.path.dirname(__file__)
        + "/../../../Modules/BarcodePrinter/CpalLabels/dailytotal.txt",
        "w",
    )
    f.write("00")
    f.close()


def update_cpal_num():
    # Get old number
    f = open(
        os.path.dirname(__file__)
        + "/../../../Modules/BarcodePrinter/CpalLabels/cpalnum.txt",
        "r",
    )
    old_number = int(f.read())
    f.close()
    # Calculate new number
    new_number = (old_number + 1) % 10000
    # Write new number
    f = open(
        os.path.dirname(__file__)
        + "/../../../Modules/BarcodePrinter/CpalLabels/cpalnum.txt",
        "w",
    )
    f.write(str(new_number))
    f.close()
    # Return
    return new_number


def undo():
    # Get current number
    f = open(
        os.path.dirname(__file__)
        + "/../../../Modules/BarcodePrinter/CpalLabels/palnum.txt",
        "r",
    )
    current_number = int(f.read())
    f.close()
    # Get previous number
    if current_number == 0:
        previous_number = 10000
    else:
        previous_number = current_number - 1
    # Write previous_number
    f = open(
        os.path.dirname(__file__)
        + "/../../../Modules/BarcodePrinter/CpalLabels/cpalnum.txt",
        "w",
    )
    f.write(str(previous_number))
    f.close()
    # Return
    return new_number


def check_new_day():
    # Get last date
    f = open(
        os.path.dirname(__file__)
        + "/../../../Modules/BarcodePrinter/CpalLabels/date.txt",
        "r",
    )
    last_date = f.read()
    f.close()
    # Update file if new day
    if datetime.today().strftime("%m%d%y") != last_date:
        reset_daily_num()
        f = open(
            os.path.dirname(__file__)
            + "/../../../Modules/BarcodePrinter/CpalLabels/date.txt",
            "w",
        )
        f.write(datetime.today().strftime("%m%d%y"))
        f.close()


# Function used in makeStrawGui.py
def print_barcodes():
    # Get numbers
    print("print_barcodes")
    check_new_day()
    cpal_num = update_cpal_num()
    count = update_daily_num()
    # Make barcode strings
    cpal_barcode = "CPAL" + ("%04d" % cpal_num)
    co2_barcode = "CO2." + datetime.today().strftime("%m%d%y") + "." + ("%02d" % count)
    se_barcode = "SE." + datetime.today().strftime("%m%d%y") + "." + ("%02d" % count)
    # Print Barcodes
    bp = BarcodePrinter.BarcodePrinter()
    bp.print_barcode(cpal_barcode, bar_width=3, number=2, close_when_finished=False)
    bp.print_barcode(co2_barcode, bar_width=2, number=1, close_when_finished=False)
    bp.print_barcode(se_barcode, bar_width=2, number=1, close_when_finished=True)


def main():
    print_barcodes()


if __name__ == "__main__":
    main()
