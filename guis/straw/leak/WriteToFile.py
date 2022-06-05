# Functions to save straw data to appropriate file

import os, time, datetime, csv
from guis.common.getresources import GetProjectPaths
from pathlib import Path

import logging

logger = logging.getLogger("root")


class StrawNotFoundError(Exception):
    # Raised when no CPAL file contains the straw name
    pass


class StrawRemovedError(Exception):
    # Raised when a tested straw was removed in previous step
    pass


class StrawNotTestedError(Exception):
    # Raised when the previous test was not performed on a straw
    pass


class StrawFailedError(Exception):
    # Raised when attempting to test a straw that has failed a previous step, but was not removed
    def __init__(self, message):
        super().__init__(self, message)
        self.message = message


def ExtractPreviousStrawData(path):
    with open(path, "r") as f:
        reader = csv.reader(f)
        last = list(reader)[-1]
        test_name = last[1]
        names = list(filter(validStraw, last))
        pf = list(filter(lambda x: len(x) == 1, last))
    return test_name, names, pf


# pass full path to pallet file and make sure it's in the right directory
# structure, filename format, etc.
def VerifyPalletFile(file):
    if not file.is_file() or not file.suffix == ".csv":
        return False

    cpalid = file.parent.name
    cpal = file.stem

    try:
        assert "CPALID" in cpalid and int(cpalid[-2:]) and len(cpalid) == 8
    except:
        logger.error(f"Problem with pallet folder structure {cpalid}.")
        logger.error(f"Please inform Ben.")
        sys.exit()

    try:
        assert "CPAL" in cpal and int(cpal[-4:]) and len(cpal) == 8
    except:
        # logger.debug(f"Bad CPAL file {file}.")
        return False

    return True


# Get list of all CPALs (CPALID, CPAL#), whose files contain strawname.
# This function gets called constantly by UpdateStrawInfo via
# FindCPALContainingStraw, so it must be efficient.
def FindAllCPALsContainingStraw(strawname):
    cpals = []
    # "LTG" == leak test GUI, i.e. local data folder
    pallets_data_dir = GetProjectPaths()["palletsLTG"]
    for file in Path(pallets_data_dir).rglob("*"):
        if not VerifyPalletFile(file):
            continue
        cpalid = file.parent.name
        cpal = file.stem
        with open(file, "r") as f:
            if strawname.lower() in f.read().lower():
                cpals.append((cpalid, cpal))
    return cpals


def GetLastLineOfPalletFile(cpalid, cpal):
    cpal_file = GetProjectPaths()["palletsLTG"] / cpalid / str(cpal + ".csv")
    assert cpal_file.is_file()
    # Files are only few lines, so OK to read like this
    with open(cpal_file, "r") as f:
        last_line = f.readlines()[-1]
    return last_line


# Get CPAL file containing straw name.
# If multiple, pick one with straw in final line or most recent.
# This function gets called constantly by UpdateStrawInfo, so it must be
# efficient.
def FindCPALContainingStraw(strawname):
    cpals = FindAllCPALsContainingStraw(strawname)

    cpals = [i for i in cpals if "CPAL9999" != i[1]]
    cpals = list(set(cpals))  # remove duplicates

    if not cpals:
        logger.error("FindCPALContainingStraw: no cpals found for {strawname}.")
        raise StrawNotFoundError

    # get cpals with strawname in final line
    cpals_with_straw_in_final_line = {}  # {(cpalid, cpal#) : timestamp, ...}
    for c in cpals:
        last_line = GetLastLineOfPalletFile(c[0], c[1])
        last_line = last_line.split(",")
        try:
            straw_idx = [i.lower() for i in last_line].index(strawname.lower())
        except ValueError:
            straw_idx = None

        if straw_idx != None and last_line[straw_idx + 1] == "P":
            timestamp_last_line = last_line[0]
            try:
                timestamp_last_line = datetime.datetime.strptime(
                    timestamp_last_line, "%Y-%m-%d_%H:%M"
                )
            except ValueError:
                logger.error(
                    "CPAL FILE WITH A DIFFERENT TIME FORMAT. PLEASE INFORM BEN."
                )
                sys.exit()
            cpals_with_straw_in_final_line[c] = timestamp_last_line

    # If just one such file, return that one
    # If multiple, return most recent one
    # returning (CPAL, CPALID)
    if len(cpals_with_straw_in_final_line) == 0:
        logger.error(
            f"Straw not found in final line of any of these cpal files {cpals}."
        )
        return StrawNotFoundError
    elif len(cpals_with_straw_in_final_line) == 1:
        # key of the first (and only in this case) element of a dict
        # i.e. (CPAL, CPALID)
        return list(cpals_with_straw_in_final_line.items())[0][0]
    else:
        # get the element of the dict which has the highest timestamp
        cpal_dict_entry = max(
            cpals_with_straw_in_final_line, key=cpals_with_straw_in_final_line.get
        )
        # key of the first (and only in this case) element of a dict
        # i.e. (CPAL, CPALID)
        ret_cpal = list(cpal_dict_entry.items())[0][0]
        logger.info(
            f"Straw {strawname} found in the final line of multiple pallet files."
        )
        logger.info(
            f"Choosing the pallet file with the most recent timestamp, {ret_cpal}"
        )
        return ret_cpal


def UpdateStrawInfo(test, workers, strawname, result):
    # Save data to appropriate CPAL file
    database_path = GetProjectPaths()["palletsLTG"]

    (cpalid, cpal) = FindCPALContainingStraw(strawname)

    path = database_path / cpalid / str(cpal + ".csv")

    previous_test, straw_list, pf = ExtractPreviousStrawData(path)

    write_line = ""

    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d_%H:%M")

    if previous_test != test:
        with open(path, "a") as f:
            f.write("\n")

            write_line += date + "," + test + ","

            for straw in straw_list:
                if strawname.lower() != straw.lower():
                    write_line += straw + ",_,"
                else:
                    write_line += strawname + "," + result + ","

            write_line += ",".join(workers)

            f.write(write_line)
    else:
        with open(path, "r") as f:
            reader = csv.reader(f)
            all_rows = list(reader)
            rows = all_rows[:-1]
            last = all_rows[-1]

        last[0] = date

        for index, entry in enumerate(last):
            if index > 1 and index % 2 == 0 and validStraw(entry):
                if entry == strawname:
                    last[index + 1] = result

        rows.append(last)
        rows = list(filter(lambda x: x != [], rows))

        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(rows)


def findPreviousStep(path, step):
    with open(path, "r") as f:
        reader = csv.reader(f)

        for row in reader:
            try:
                test = row[1]
            except IndexError:
                continue

            if test == step:
                return True

        return False
    """f = open(path, "r")

    line = f.readline()

    test = ""

    while line != "":
        index = 0
        delimiter = ','

        # Skip date
        while line[index] != delimiter:
            index += 1

        index += 1

        while line[index] != delimiter:
            if line[index] != delimiter:
                test += line[index]
                index += 1
            else:
                break
        if test == step:
            return 1

        index = 0
        test = ""
        line = f.readline()

    return 0"""


def checkPass(path, strawname, current_test):
    f = open(path, "r")

    line = f.readline()
    line = f.readline()
    length = len(line)
    delimiter = ","
    index = 0
    status = []

    while line.strip():
        found = False
        index = 0

        # Skip date
        while line[index] != delimiter:
            index += 1

        index += 1

        test_name = ""

        # Get test name
        while line[index] != delimiter and index < length:
            if line[index] != delimiter:
                test_name += line[index]
                index += 1
            else:
                break

        index += 1

        while index < length:
            if (line[index] == "s" or line[index] == "S") and (
                line[index + 1] == "t" or line[index + 1] == "T"
            ):

                name = line[index : (index + 7)]
                result = line[index + 8]

                if name == strawname.upper():
                    status.append((test_name, result))
                    found = True
                    break
            index += 10

        if not found:
            status.append((test_name, "R"))
            break

        line = f.readline()
        length = len(line)

    f.close()

    failed = []

    for pairs in status:
        if pairs[1] == "F":
            if pairs[0] != current_test:
                failed.append(pairs[0])

    if pairs[1] == "R":
        failed = []

    return failed


def checkStraw(strawname, expected_previous_test, current_test):
    database_path = GetProjectPaths()["palletsLTG"]

    (cpalid, cpal) = FindCPALContainingStraw(strawname)

    path = database_path / cpalid / str(cpal + ".csv")

    try:
        assert path.is_file()
    except AssertionError:
        logger.warning("cannot find pallet file", path)

    logger.info(cpal, "found for straw", strawname, "with file", path)

    straw_list = ExtractPreviousStrawData(path)[1]

    previous_test = findPreviousStep(path, expected_previous_test)

    failed = checkPass(path, strawname, current_test)

    if not previous_test:
        raise StrawNotTestedError

    if failed != []:
        raise StrawFailedError("Straw failed test(s): " + ", ".join(failed))

    for straw in straw_list:
        if straw.lower() == strawname.lower():
            return

    logger.error("CPAL file", path)

    raise StrawRemovedError


def validStraw(name):
    return (
        len(name) == 7
        and (name[0] == "s" or name[0] == "S")
        and (name[1] == "t" or name[1] == "T")
        and name[2:].isdigit()
    ) or (name == "_" * 7)
