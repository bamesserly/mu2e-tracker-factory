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


def getFile(lpalid, lpal):
    # Generate the filename for this LPAL
    folder = Path(__file__).resolve().parent  # Directory of the file
    filename = f"{lpal}_{lpalid}.csv"  # Filename for this LPAL, LPALID
    file = folder / filename  # Full path

    # If it doesn't exist yet, writes a header and all the positions
    if not file.exists():
        with file.open("w") as f:
            f.write("Position,Straw,Timestamp\n")
            for i in range(0, 96, 2):
                f.write(f"{i},,\n")

    # Return file
    return file


def readRows(file):
    with file.open("r") as f:
        reader = DictReader(f)
        rows = [row for row in reader]
    return rows, reader.fieldnames


def recordStraw(file, position, straw):
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


# Our sqldp needs an object with these properties
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
    lpalgui = FillLPALGUI()
    # Data Processor
    DP = SQLDP(
        gui=lpalgui,
        stage="straws",
    )
    print(
        """
    \n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n
    | |   |  _ \ / \  | |     | |    ___   __ _  __| | ___ _ __ 
    | |   | |_) / _ \ | |     | |   / _ \ / _` |/ _` |/ _ \ '__|
    | |___|  __/ ___ \| |___  | |__| (_) | (_| | (_| |  __/ |   
    |_____|_| /_/   \_\_____| |_____\___/ \__,_|\__,_|\___|_|                                                   
    """
    )
    # Scan in LPALID (LPALID##)
    lpalid = getInput(
        prompt="Please scan the LPALID (LPALID##)",
        checkcondition=lambda s: len(s) == 8
        and s.startswith("LPALID")
        and s[-2:].isnumeric(),
    )
    if lpalid is None:
        return
    lpalgui.setPalletID(lpalid)

    # Scan in LPAL (LPAL####)
    lpal_number = getInput(
        prompt="Please scan the LPAL (LPAL####)",
        checkcondition=lambda s: len(s) == 8
        and s.startswith("LPAL")
        and s[-4:].isnumeric(),
    )
    if lpal_number is None:
        return
    lpalgui.setPalletNumber(lpal_number)

    # initialize procedure and commit it to the DB
    # internally, use the lpal number (lpalgui.getPalletNumber) and id
    # (lpalgui.getPalletID) to create the straw_location object
    DP.saveStart()
    # self.DP.procedure  # FillLPAL(StrawProcedure) object

    # get the straw location object that DP.saveStart just created.
    lpal = DP.procedure.getStrawLocation()

    # DB checks
    print(lpal.location_type, lpal.number, lpal.pallet_id)
    # print("is empty?", lpal._palletIsEmpty(lpal.pallet_id))
    # positions = lpal.getStrawPositions()
    # print(positions)
    # print(lpal._queryStrawPresents().all())
    # print(lpal._queryStrawPositions().all())
    print(f"Unfilled Positions:\n{lpal.getUnfilledPositions()}")
    print(f"Filled Positions:\n{lpal.getFilledPositions()}")

    # Get file
    file = getFile(lpal.pallet_id, lpal.number)

    cpals = set()

    # On a loop:
    while True:
        # Determine which positions are curently unfilled
        unfilled = getUnfilledPositions(file)
        if len(unfilled) == 0:
            print("All positions on this pallet have been filled.")
        else:
            print(f"Unfilled Positions:\n{unfilled}")

        if not getYN("continue?"):
            break

        # Scan position
        # format POS.0 - POS.99
        position = getInput(
            prompt="Scan position barcode",
            checkcondition=lambda s: len(s) in [5, 6]
            and s.upper().startswith("POS.")
            and s[4:].isnumeric()
            and int(s[4:]) % 2 == 0,
        )
        if position is None:
            continue
        position = int(position[4:])

        if not position in unfilled:
            if not getYN("There is already a straw at this position. Continue?"):
                continue  # Return to top of loop

        straw_id = getInput(
            prompt="Scan straw barcode",
            checkcondition=lambda s: len(s) == 7
            and s.upper().startswith("ST")
            and s[2:].isnumeric(),
        )
        if straw_id is None:
            continue

        recordStraw(file, position, straw_id)

        straw_id = int(straw_id[2:])

        # Get straw from DB
        straw = Straw.exists(straw_id=straw_id)

        msg = f"Straw {straw_id} not found in the DB."
        if not straw and not getYN(msg + "Add new straw to DB and continue?"):
            logger.warning(msg)
            continue

        # list of StrawPositions where this straw is marked present
        straw_positions = straw.locate()

        # Checking if this straw is already present in another straw location
        # 0 --> ask for confirmation
        # exactly 1 && CPAL --> good, remove from other pallet
        # exactly 1 && !CPAL --> ask for confirmation, remove from other pallet
        # more than 1 --> ask for confirmation, remove from all other pallets

        # straw not found anywhere. possible that we just created this straw
        if len(straw_positions) == 0:
            msg = f"Straw ST{straw_id} not found present on any CPAL!"
            logger.warning(msg)
            if not getYN(
                msg + "\nAre you sure you want to add this straw to this LPAL?"
            ):
                continue
        # straw found on exactly 1 CPAL -- GOOD
        elif (
            len(straw_positions) == 1
            and straw_positions[0].getStrawLocationType() == "CPAL"
        ):
            cpal = straw_positions[0].getStrawLocation()
            cpal.removeStraw(straw, straw_positions[0].position_number)
            logger.info(f"Straw {straw_id} removed from CPAL{cpal.number}")
            cpals.add(cpal)  # make note of which cpals have been used to load this LPAL
        # straw found in more than one location
        else:
            logger.warning(
                f"Straw ST{straw_id} found present in more than one straw location!"
            )
            logger.warning("\n".join([repr(i) for i in straw_positions]))
            if not getYN(
                f"Do you want to remove the straw from all of these loctions and add it to LPAL{lpal.number} position {position}?"
            ):
                continue
            for p in straw_positions:
                straw_location = p.getStrawLocation()
                straw_location.removeStraw(straw, p.position_number)
                logger.info(f"Straw ST{straw_id} removed from {repr(straw_location)}.")
                cpals.add(straw_location)

        logger.info(
            f"Straw ST{straw_id} added to LPAL{lpal.number} at position {position}."
        )

        lpal.addStraw(straw, position)

        # elif any(p.getStrawLocation().id == lpal.id for p in straw_positions]:
        # [position.getStrawLocation().removeStraw(straw, position.position_number, True) for position in straw_positions if position.getStrawLocation().location_type == "CPAL"]


if __name__ == "__main__":
    run()
