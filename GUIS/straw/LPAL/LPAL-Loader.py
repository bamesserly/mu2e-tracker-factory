from pathlib import Path
from csv import DictReader, DictWriter
from time import time
import os


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
    folder = os.path.dirname(__file__) + "..\\..\\..\\Data\\Loading Pallets\\"
    filename = f"{lpal}_{lpalid}.csv"  # Filename for this LPAL, LPALID
    file = folder + filename  # Full path

    if os.path.exists(file):
        # Return file
        return file
    # If it doesn't exist yet, writes a header and all the positions
    else:
        f = open(file, "w")
        f.write("Position,Straw,Timestamp\n")
        for i in range(0, 96, 2):
            f.write(f"{i},,\n")
        # Return file
        return file


def readRows(file):
    with open(file, "r") as f:
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
    with open(file, "w") as f:
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


def main():

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

    # Scan in LPAL (LPAL####)
    lpal = getInput(
        prompt="Please scan the LPAL (LPAL###)",
        checkcondition=lambda s: len(s) == 8
        and s.startswith("LPAL")
        and s[-4:].isnumeric(),
    )
    if lpal is None:
        return

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
    main()
