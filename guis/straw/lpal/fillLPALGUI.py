################################################################################
#
# Load Straws onto LPAL
#
# Next step: straws are done, onto panel production
#
#
################################################################################
from guis.common.panguilogger import SetupPANGUILogger

logger = SetupPANGUILogger("root", "FillLPAL")

from pathlib import Path
from csv import DictReader, DictWriter
from time import time
import sys

from guis.common.dataProcessor import (
    SQLDataProcessor as SQLDP,
)  # importing this calls an automerge
from guis.common.timer import QLCDTimer
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication, QLCDNumber
from guis.common.db_classes.straw import Straw
from guis.common.getresources import GetProjectPaths
from guis.common.gui_utils import except_hook
from data.workers.credentials.credentials import Credentials


# GUI object -- needed by sql data processor
class FillLPALGUI(QObject):
    # Dummy object right now. Eventually, may want to turn this program into a
    # full-fledged gui.
    timer_signal = pyqtSignal()

    def __init__(self):
        super(FillLPALGUI, self).__init__(None)
        app = QApplication(sys.argv)

        # timer stuff
        self.timer = QLCDTimer(
            QLCDNumber(),  # no timer display for this ui
            QLCDNumber(),  # no timer display for this ui
            QLCDNumber(),  # no timer display for this ui
            lambda: self.timer_signal.emit(),
            max_time=28800,
        )  # 0 - Main Timer: Turns red after 8 hours
        self.timer_signal.connect(self.timer.display)
        self.startTimer = lambda: self.timer.start()
        self.stopTimer = lambda: self.timer.stop()
        self.resetTimer = lambda: self.timer.reset()
        self.mainTimer = self.timer  # data processor wants it
        self.running = lambda: self.timer.isRunning()

        # process info
        self.pro = 11
        self.pro_index = self.pro - 1
        self.data = []

    def setPalletID(self, pallet_id):
        self.pallet_id = pallet_id

    def setPalletNumber(self, pallet_number):
        self.pallet_number = pallet_number

    def getPalletID(self):
        return self.pallet_id

    def getPalletNumber(self):
        return self.pallet_number


# Utility functions
def getInput(prompt, checkcondition):
    while True:
        s = input(f"{prompt}: ").strip().upper()
        try:
            if checkcondition(s):
                return s
        except Exception:
            pass
        # If interpreter gets here, input was invalid
        print("INVALID INPUT")
        if not getYN("Try again?"):
            return None


def getYN(instructions):
    s = input(f"{instructions} (y/n)")
    return "N" not in s.upper()


def enterLPALInfo():
    lpalid = getInput(
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

    return lpalid, lpal_number


def compareDBwithTxtFile(lpal, outfile):
    # Sanity check: DB and txt file should agree on content of LPAL
    # They can differ if someone manually changes the txt files.
    #
    # side effect: print results of check
    # return: lists of unfilled positions for db and txt file
    unfilled_txt = getUnfilledPositions(outfile)  # from text file
    unfilled_db = lpal.getUnfilledPositions()  # from the DB

    # Txt file and DB agree.
    # When totally filled, unfilled_txt = [], unfilled_db = None, which is why we
    # need both checks.
    if (not unfilled_txt and not unfilled_db) or unfilled_txt == unfilled_db:
        logger.debug("db and text file agree on which positions are filled.")
        logger.debug(f"{unfilled_txt} {unfilled_db}")
        logger.debug(f"filled (DB) {lpal.getFilledPositions()}")
    # Txt file and DB do not agree
    else:
        logger.warning(
            f"Text file and database disagree on which LPAL positions are unfilled."
        )
        logger.info(f"unfilled (txt file {outfile})\n{getUnfilledPositions(outfile)}")
        logger.info(f"filled (DB)\n{lpal.getFilledPositions()}")
        logger.info(f"unfilled (DB)\n{lpal.getUnfilledPositions()}")
        logger.info(
            "You can proceed to scan any and all straws to set the "
            "record straight in the DB AND text file."
        )

    return unfilled_txt, unfilled_db


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
    return int(position[4:])


# LPAL txt file functions
def getLPALFile(lpalid, lpal, worker):
    outfile = (
        GetProjectPaths()["lpals"]
        / f"LPAL{str(lpal).zfill(4)}_LPALID{str(lpalid).zfill(2)}.csv"
    )

    # If it doesn't exist yet, write a header (with cpals) and all the positions
    if not outfile.exists():
        logger.info("It looks like you're loading a new LPAL.")

        with outfile.open("w") as f:
            f.write("Position,Straw,Timestamp,Cpal," + str(worker) + "\n")

            for i in range(0, 96, 2):
                f.write(f"{i},,\n")

    # Return outfile
    return outfile


def readRows(file):
    with file.open("r") as f:
        reader = DictReader(line for line in f if line.split(",")[0])
        rows = [row for row in reader]
    return rows, reader.fieldnames


def saveStrawToLPALFile(file, position, straw, cpal):
    # Read-in current file
    rows, fieldnames = readRows(file)

    # Assemble new row
    new_row = {
        "Position": position,
        "Straw": straw,
        "Timestamp": int(time()),
        "Cpal": cpal,
    }
    # Replace row in previous data with the new row
    rows[int(position / 2)] = new_row

    # Re-write file replacing overwriting the row containing the new straw
    with file.open("w") as f:
        writer = DictWriter(f, fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def getUnfilledPositions(file):
    # Read-in a file and return a list of the unfilled positions
    rows, _ = readRows(file)

    # Return the position of all rows that don't have a straw recorded
    return [int(row["Position"]) for row in rows if not row["Straw"]]


# DB functions
def doDatabaseSetup(lpalid, lpal_number):
    # Start database procedure
    # Internally, use the lpal number (lpalgui.getPalletNumber) and id
    # (lpalgui.getPalletID) to create the straw_location object
    lpalgui = FillLPALGUI()
    lpalgui.setPalletID(lpalid)
    lpalgui.setPalletNumber(lpal_number)
    lpalgui.startTimer()
    DP = SQLDP(gui=lpalgui, stage="straws")
    try:
        DP.saveStart()
    except AssertionError as e:
        logger.error(
            f"According to the DB, there are still straws on {lpalgui.getPalletID()}."
        )
        logger.error(f"Please mergedown!")
        logger.error("If this message is still appearing after MD, contact Ben.")
        sys.exit()
    DP.saveResume()

    return lpalgui, DP


def getOrCreateStraw(straw_id):
    straw = Straw.exists(straw_id=straw_id)
    if not straw:
        logger.debug(f"Straw {straw_id} not found in the DB. Creating it.")
        straw = Straw.Straw(id=straw_id)
    return straw


def removeStrawFromCurrentLocation(straw, straw_position):
    straw_location = straw_position.getStrawLocation()
    position_on_straw_location = straw_position.position_number
    straw_location.removeStraw(straw, position_on_straw_location)
    logger.info(
        f"Straw ST{straw.id} removed from {repr(straw_location)}, position {position_on_straw_location}."
    )
    return straw_location


def removeStrawFromCurrentLocations(straw, cpals):
    # list of StrawPositions where the DB thinks this straw is currently
    # located.
    # Hopefully, it's just present in one place: the cpal from which we're
    # transferring it.
    straw_positions = straw.locate()

    # (1) straw not found anywhere. possible that we just created this straw
    if len(straw_positions) == 0:
        logger.debug(f"Straw ST{straw.id} not found present on any CPAL.")
    # (2) straw found on exactly 1 CPAL -- GOOD
    elif (
        len(straw_positions) == 1
        and straw_positions[0].getStrawLocationType() == "CPAL"
    ):
        cpal = removeStrawFromCurrentLocation(straw, straw_positions[0])
        cpals.add(cpal)  # record this cpal
    # (3) straw found in more than one location
    else:
        logger.debug(
            f"Straw ST{straw.id} found present somewhere other than a single CPAL."
        )
        logger.debug("\n".join([repr(i) for i in straw_positions]))
        logger.debug("Removing straw from all locations.")
        for p in straw_positions:
            straw_location = removeStrawFromCurrentLocation(straw, p)
            cpals.add(straw_location)  # record this straw location

    return True


def saveStrawToDB(position, straw_id, lpal, cpals):
    # 1. Get Straw object
    straw = getOrCreateStraw(int(straw_id[2:]))
    if not straw:
        return

    # 2. Remove straw from current CPAL (and any other pallets)
    if not removeStrawFromCurrentLocations(straw, cpals):
        return

    # 3. Remove straw currently in this position
    lpal.removeStraw(straw=None, position=position, commit=True)

    # 3. Add straw to LPAL in the DB
    lpal.addStraw(straw, position)
    logger.info(f"Straw {straw_id} added to LPAL{lpal.number} at position {position}.")


# Collect basic info, set up db
def initialize():
    # return worker, lpal, outfile, data processor

    # Get User
    credential_checker = Credentials("prep")

    worker = getInput(
        prompt="Enter worker ID ",
        checkcondition=lambda s: credential_checker.checkCredentials(s),
    )

    # Get LPAL Info
    lpalid, lpal_number = enterLPALInfo()
    print(lpalid)

    # Setup DB
    lpalgui, DP = doDatabaseSetup(lpalid, lpal_number)

    # Get LoadingPallet(StrawLocation) object just created in DB
    lpal = DP.procedure.getStrawLocation()

    # Get outfile (create it and write a header if first time)
    outfile = getLPALFile(lpal.pallet_id, lpal.number, worker)

    return worker, lpal, outfile, lpalgui, DP


# Heavy-lifting function -- call in a loop until you're done
def addStrawToLPAL(lpal, outfile, cpals, latest_cpal):
    # Sanity check: do db and txt file agree?
    unfilled_lpal_positions_txt_file, unfilled_lpal_positions_db = compareDBwithTxtFile(
        lpal, outfile
    )
    logger.debug(f"Unfilled Positions:\n{unfilled_lpal_positions_txt_file}")

    # All positions filled - continue scanning?
    if len(unfilled_lpal_positions_txt_file) == 0:
        logger.info(f"Records indicate this LPAL has been filled.")
        if not getYN("Continue scanning straws?"):
            return "finish"

    # Specify first CPAL
    if latest_cpal == None:
        latest_cpal = getInput(
            prompt="Enter the first CPAL number",
            checkcondition=lambda s: len(s) == 8
            and s.startswith("CPAL")
            and s[-4:].isnumeric(),
        )
        print("\n")

    # Enter LPAL position
    position = scanLPALPosition()
    if not position in unfilled_lpal_positions_txt_file:
        if not getYN("There is already a straw at this position. Replace it?"):
            return "scanning", latest_cpal

    print(f"\nCurrent CPAL: {latest_cpal}\n")

    # Enter straw or a new cpal
    straw_id = None
    while straw_id is None:
        straw_or_cpal = getInput(
            prompt=f"Scan straw or different CPAL",
            checkcondition=lambda s: len(s) == 7
            or len(s) == 8
            and (s.upper().startswith("ST") or s.upper().startswith("CPAL"))
            and s[4:].isnumeric(),
        )
        # check validity of input
        if not straw_or_cpal:
            return "scanning", latest_cpal

        if straw_or_cpal.upper().startswith("CPAL"):
            latest_cpal = straw_or_cpal
            logger.info(f"Switched to {latest_cpal}.")
            continue

        straw_id = straw_or_cpal

    # Save straw to LPAL txt file
    saveStrawToLPALFile(outfile, position, straw_id, latest_cpal)

    # Save to DB
    saveStrawToDB(position, straw_id, lpal, cpals)

    return "scanning", latest_cpal


# main
def run():
    sys.excepthook = except_hook  # crash, don't hang when an exception is raised
    print(
        """
    \n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n
    | |   |  _ \ / \  | |     | |    ___   __ _  __| | ___ _ __ 
    | |   | |_) / _ \ | |     | |   / _ \ / _` |/ _` |/ _ \ '__|
    | |___|  __/ ___ \| |___  | |__| (_) | (_| | (_| |  __/ |   
    |_____|_| /_/   \_\_____| |_____\___/ \__,_|\__,_|\___|_|                                                   
    """
    )

    # collect basic info, setup DB
    worker, lpal, outfile, lpalgui, DP = initialize()

    # enter straws
    cpals = set()
    latest_cpal = None
    status = "scanning"
    while status == "scanning":
        print("\n")
        # side effect: can update latest_cpal
        status, latest_cpal = addStrawToLPAL(lpal, outfile, cpals, latest_cpal)

    lpalgui.stopTimer()

    if status == "finish":
        logger.info(f"LPAL{lpal.number} loading marked as finished. Goodbye")
        print(
            "\nTIP: You can always re-run this script to fix single straws up until the straws are loaded onto the panel."
        )
        DP.saveFinish()
    else:
        logger.info(f"LPAL{lpal.number} loading paused. Goodbye.")
        DP.savePause()  # TODO this isn't saving the elapsed time for some reason


if __name__ == "__main__":
    run()

# DB checks
# print(lpal.location_type, lpal.number, lpal.pallet_id)
# print("is empty?", lpal._palletIsEmpty(lpal.pallet_id))
# positions = lpal.getStrawPositions()
# print(positions)
# print(lpal._queryStrawPresents().all())
# print(lpal._queryStrawPositions().all())
# print(f"Unfilled Positions:\n{lpal.getUnfilledPositions()}")
# print(f"Filled Positions:\n{lpal.getFilledPositions()}")

# elif any(p.getStrawLocation().id == lpal.id for p in straw_positions]:
# [position.getStrawLocation().removeStraw(straw, position.position_number, True) for position in straw_positions if position.getStrawLocation().location_type == "CPAL"]
