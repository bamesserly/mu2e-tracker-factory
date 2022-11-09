################################################################################
# Simple GUI to track anchor construction
################################################################################

from datetime import datetime
from guis.common.gui_utils import except_hook
from guis.common.panguilogger import SetupPANGUILogger
import sys
from time import sleep


# Utility functions
def getInput(prompt, checkcondition):
    while True:
        # try:
        s = input(f"{prompt}> ").strip().upper()
        if checkcondition(s):
            return s
        # except KeyboardInterrupt: # doesn't work. it's a python feature.
        #    raise
        # except TypeError:
        #    print("ERROR: you did your check condition lambda wrong")
        #    raise
        # If interpreter gets here, input was invalid
        print("INVALID INPUT")


def enterLPALInfo():
    lpal_id = getInput(
        prompt="Enter LPALID (LPALID##)",
        checkcondition=lambda s: len(s) == 8
        and s.startswith("LPALID")
        and s[-2:].isnumeric()
        and (s[-2:] == "01" or s[-2:] == "02"),
    )

    lpal_number = getInput(
        prompt="Enter LPAL number (LPAL####)",
        checkcondition=lambda s: len(s) == 8
        and s.startswith("LPAL")
        and s[-4:].isnumeric(),
    )

    return lpal_id, lpal_number


def scanLPALPosition():
    # Scan LPAL position
    # format POS.0 - POS.99
    position = getInput(
        prompt="Scan position barcode for straw",
        checkcondition=lambda s: len(s) in [5, 6]
        and s.upper().startswith("POS.")
        and s[4:].isnumeric()
        and int(s[4:]) % 2 == 0,
    )
    return position.upper()


def scanPanelSide():
    which_side = getInput(
        prompt="Left [L/l] or right [R/r] side",
        checkcondition=lambda s: len(s) == 1 and s.upper() in ["R", "L"],
    )
    return which_side


def run():
    print(
        """
    \n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\
         ___      .__   __.   ______  __    __    ______   .______           _______  __    __   __
        /   \     |  \ |  |  /      ||  |  |  |  /  __  \  |   _  \         /  _____||  |  |  | |  |
       /  ^  \    |   \|  | |  ,----'|  |__|  | |  |  |  | |  |_)  |       |  |  __  |  |  |  | |  |
      /  /_\  \   |  . `  | |  |     |   __   | |  |  |  | |      /        |  | |_ | |  |  |  | |  |
     /  _____  \  |  |\   | |  `----.|  |  |  | |  `--'  | |  |\  \----.   |  |__| | |  `--'  | |  |
    /__/     \__\ |__| \__|  \______||__|  |__|  \______/  | _| `._____|    \______|  \______/  |__|
    """
    )
    sleep(0.3)
    worker = getInput(
        prompt="Scan worker ID",
        checkcondition=lambda x: True,
    )

    lpal_id, lpal_num = enterLPALInfo()

    logger = SetupPANGUILogger(
        "root", tag="Anchors", be_verbose=False, straw_location=lpal_num
    )

    sys.excepthook = except_hook  # crash, don't hang, when an exception is raised
    # gotta call this after logger initiated

    print("=" * 71)
    logger.info(f"worker:{worker}, lpalid:{lpal_id}, lpal:{lpal_num}")

    start_time = datetime.now()

    print("=" * 71)
    print(
        '\nScan or type position ("POS.XX") and side ("L/R") when you complete an anchor.'
    )
    print("\nContinue scanning until you're done.")
    print("\nPress ctrl-c to log out.\n")
    print("=" * 71)
    n_anchors_attached = 0
    while True:
        position = scanLPALPosition()
        which_side = scanPanelSide()
        which_side_string = {"L": "left", "R": "right"}
        logger.info(
            f"Anchor attached {lpal_num}, {position}, {which_side_string[which_side]}"
        )
        print("=" * 70)
        n_anchors_attached += 1
        logger.debug(f"{n_anchors_attached} anchors attached.")
        logger.debug(f"elapsed_time:{datetime.now()-start_time}")


if __name__ == "__main__":
    run()
