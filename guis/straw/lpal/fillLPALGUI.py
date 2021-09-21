################################################################################
#
# Load Straws onto LPAL
#
# Next step: straws are done, onto panel production
#
#
################################################################################
from pathlib import Path
from csv import DictReader, DictWriter
from time import time

# from guis.common.db_classes.straw_location import LoadingPallet
from guis.common.dataProcessor import SQLDataProcessor as DP
from guis.common.timer import QLCDTimer
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLCDNumber


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
    print(straw + " added at position: " + str(position))


def getUnfilledPositions(file):
    # Read-in a file and return a list of the unfilled positions
    rows, _ = readRows(file)
    # Return the position of all rows that don't have a straw recorded
    return [int(row["Position"]) for row in rows if not row["Straw"]]


# Our sqldp needs an object with these properties
class LPALLoadingGUI:
    def __init__(self):
        # timer stuff
        timer_signal = pyqtSignal()
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

    # Set Pallet numbers/ids
    # def setCPALID(self, cpal_id):
    #    self.cpal_id = cpal_id

    # def setCPALNumber(self, cpal_number):
    #    self.cpal_number = cpal_number

    def setLPALID(self, lpal_id):
        self.lpal_id = lpal_id

    def setLPALNumber(self, lpal_number):
        self.lpal_number = lpal_number

    # Get Pallet numbers/ids
    # def getCPALID(self):
    #    return self.cpal_id

    # def getCPALNumber(self):
    #    return self.cpal_number

    def getLPALID(self):
        return self.lpal_id

    def getLPALNumber(self):
        return self.lpal_number


def run():
    lpalgui = LPALLoadingGUI()
    # Data Processor
    DP = DP(
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
    lpalgui.setLPALID(lpalid)

    # Scan in LPAL (LPAL####)
    lpal = getInput(
        prompt="Please scan the LPAL (LPAL###)",
        checkcondition=lambda s: len(s) == 8
        and s.startswith("LPAL")
        and s[-4:].isnumeric(),
    )
    if lpal is None:
        return
    lpalgui.setLPALNumber(lpal)

    self.DP.saveStart()  # initialize procedure and commit it to the DB
    # self.DP.procedure  # FillLPAL(StrawProcedure) object

    # Get file
    file = getFile(lpalid, lpal)

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

        straw = getInput(
            prompt="Scan straw barcode",
            checkcondition=lambda s: len(s) == 7
            and s.upper().startswith("ST")
            and s[2:].isnumeric(),
        )
        if straw is None:
            continue

        recordStraw(file, position, straw)


if __name__ == "__main__":
    run()
