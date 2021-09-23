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

# from guis.common.db_classes.straw_location import LoadingPallet
from guis.common.dataProcessor import SQLDataProcessor as SQLDP
from guis.common.timer import QLCDTimer
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication, QLCDNumber
from guis.common.db_classes.straw import Straw
from guis.common.getresources import GetProjectPaths


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


def getLPALFile(lpalid, lpal):
    outfile = (
        GetProjectPaths()["lpals"] / f"LPAL{lpal}_LPALID{str(lpalid).zfill(2)}.csv"
    )

    # If it doesn't exist yet, writes a header and all the positions
    if not outfile.exists():
        with outfile.open("w") as f:
            f.write("Position,Straw,Timestamp\n")
            for i in range(0, 96, 2):
                f.write(f"{i},,\n")

    # Return outfile
    return outfile


def readRows(file):
    with file.open("r") as f:
        reader = DictReader(f)
        rows = [row for row in reader]
    return rows, reader.fieldnames


def saveStrawToLPAL(file, position, straw):
    # Read-in current file
    rows, fieldnames = readRows(file)

    # Assemble new row
    new_row = {"Position": position, "Straw": straw, "Timestamp": int(time())}
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


def getOrCreateStraw(straw_id):
    straw = Straw.exists(straw_id=straw_id)
    msg = f"Straw {straw_id} not found in the DB."
    if not straw:
        if not getYN(msg + " Add a new straw to DB and continue?"):
            logger.warning(msg)
        else:
            straw = Straw(id=straw_id)
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

    # straw not found anywhere. possible that we just created this straw
    if len(straw_positions) == 0:
        msg = f"Straw ST{straw.id} not found present on any CPAL!"
        logger.warning(msg)
        if getYN("\nAre you sure you want to add this straw to this LPAL?"):
            return True
        else:
            return False
    # straw found on exactly 1 CPAL -- GOOD
    elif (
        len(straw_positions) == 1
        and straw_positions[0].getStrawLocationType() == "CPAL"
    ):
        cpal = removeStrawFromCurrentLocation(straw, straw_positions[0])
        cpals.add(cpal)  # record this cpal
        return True
    # straw found in more than one location
    else:
        logger.warning(
            f"Straw ST{straw.id} found present somewhere other than a single CPAL!"
        )
        logger.warning("\n".join([repr(i) for i in straw_positions]))
        if not getYN(f"Do you want to remove the straw from all of these locations?"):
            return False
        for p in straw_positions:
            straw_location = removeStrawFromCurrentLocation(straw, p)
            cpals.add(straw_location)  # record this straw location
        return True


def addStrawToLPAL(lpal, outfile, cpals):
    ########################################################################
    # Check: is the lPAL full?
    ########################################################################
    unfilled = getUnfilledPositions(outfile)  # from text file
    # print("filled",lpal.getFilledPositions())
    # print("unfilled",lpal.getUnfilledPositions())

    if unfilled != lpal.getUnfilledPositions():
        logger.warning(
            f"Text file {outfile} and database disagree on which LPAL positions are unfilled."
        )

    if len(unfilled) == 0:
        logger.info("All positions on this pallet have been filled.")
        if not getYN("Continue scanning straws?"):
            if getYN("Finish?"):
                return "finish"
    else:
        logger.info(f"Unfilled Positions:\n{unfilled}")
        if not getYN("Continue scanning straws?"):
            return "pause"

    ########################################################################
    # Scan LPAL position
    ########################################################################
    # format POS.0 - POS.99
    position = getInput(
        prompt="Scan position barcode",
        checkcondition=lambda s: len(s) in [5, 6]
        and s.upper().startswith("POS.")
        and s[4:].isnumeric()
        and int(s[4:]) % 2 == 0,
    )
    if not position:
        return "scanning"
    position = int(position[4:])

    if not position in unfilled:
        if not getYN("There is already a straw at this position. Continue?"):
            return "scanning"

    ########################################################################
    # Scan straw
    ########################################################################
    straw_id = getInput(
        prompt="Scan straw barcode",
        checkcondition=lambda s: len(s) == 7
        and s.upper().startswith("ST")
        and s[2:].isnumeric(),
    )
    if not straw_id:
        return "scanning"

    ########################################################################
    # Save to Text -- add straw to LPAL txt file
    ########################################################################
    saveStrawToLPAL(outfile, position, straw_id)

    ########################################################################
    # Save to DB
    ########################################################################
    # 1. Get Straw object
    straw = getOrCreateStraw(int(straw_id[2:]))
    if not straw:
        return "scanning"

    # 2. Remove straw from current CPAL (and any other pallets)
    if not removeStrawFromCurrentLocations(straw, cpals):
        return "scanning"

    # 3. Add straw to LPAL in the DB
    lpal.addStraw(straw, position)
    logger.info(
        f"Straw ST{straw_id} added to LPAL{lpal.number} at position {position}."
    )

    return "scanning"


# Our sqldp needs an object with these properties.
# Somewhat of a dummy object right now. Eventually, may want to turn this
# program into a full-fledged gui.
class FillLPALGUI(QObject):
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


def run():
    print(
        """
    \n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n
    | |   |  _ \ / \  | |     | |    ___   __ _  __| | ___ _ __ 
    | |   | |_) / _ \ | |     | |   / _ \ / _` |/ _` |/ _ \ '__|
    | |___|  __/ ___ \| |___  | |__| (_) | (_| | (_| |  __/ |   
    |_____|_| /_/   \_\_____| |_____\___/ \__,_|\__,_|\___|_|                                                   
    """
    )
    ############################################################################
    # Scan-in LPAL Info
    ############################################################################
    lpalid = getInput(
        prompt="Please scan the LPALID (LPALID##)",
        checkcondition=lambda s: len(s) == 8
        and s.startswith("LPALID")
        and s[-2:].isnumeric(),
    )
    if lpalid is None:
        return

    lpal_number = getInput(
        prompt="Please scan the LPAL (LPAL####)",
        checkcondition=lambda s: len(s) == 8
        and s.startswith("LPAL")
        and s[-4:].isnumeric(),
    )
    if lpal_number is None:
        return

    ############################################################################
    # Start the database procedure
    #
    # Internally, use the lpal number (lpalgui.getPalletNumber) and id
    # (lpalgui.getPalletID) to create the straw_location object
    ############################################################################
    lpalgui = FillLPALGUI()
    lpalgui.setPalletID(lpalid)
    lpalgui.setPalletNumber(lpal_number)
    lpalgui.startTimer()
    DP = SQLDP(gui=lpalgui, stage="straws")
    DP.saveStart()
    DP.saveResume()

    # Retrieve the LoadingPallet(StrawLocation) object that the DP just made
    lpal = DP.procedure.getStrawLocation()

    ############################################################################
    # Get outfile
    ############################################################################
    outfile = getLPALFile(lpal.pallet_id, lpal.number)

    ############################################################################
    # Scan-in straws
    # Remove them from their CPALs and add them to the LPAL.
    # Do so continuously until we either finish or break.
    ############################################################################
    cpals = set()  # straw location objects from which this lpal was filled
    status = "scanning"
    while status == "scanning":
        print("\n")
        status = addStrawToLPAL(lpal, outfile, cpals)

    lpalgui.stopTimer()

    if status == "finish":
        logger.info(f"LPAL{lpal.number} loading marked as finished. Goodbye")
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
