# Functions to save straw data to appropriate file

import os, time, datetime, csv
from guis.common.getresources import GetProjectPaths


class StrawNotFoundError(Exception):
    # Raised when no CPAL file contains the straw name
    pass


class MultipleStrawsFoundError(Exception):
    # Raised when a CPAL file contains a straw more than once
    def __init__(self, message=None):
        super().__init__(self, message)
        self.message = message


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


# Get list of all CPALs (CPALID, CPAL#), whose files contain strawname
def FindAllCPALs(strawname):
    cpal_return_pairs = []
    database_path = GetProjectPaths()["pallets"]
    for i in range(1, 25):
        files = []
        cpalid = "CPALID" + str(i).zfill(2)
        path = database_path / cpalid
        for (dirpath, dirnames, filenames) in os.walk(path):
            files.extend(filenames)
            break
        for filename in files:
            f = open(path / filename, "r")
            line = f.readline()
            while line != "":
                if strawname.lower() in line.lower():
                    cpal_return_pairs.append((cpalid, filename[:-4]))
                line = f.readline()
            f.close()
    return cpal_return_pairs


# Check each CPAL file to see if strawname is in the last test in the file and
# passed. If multiple good CPALs are found, raise/prompt user.
def GetBestCPAL(strawname, cpal_return_pairs):
    if not cpal_return_pairs:
        print("GetBestCPAL: no cpals given for", strawname)
        return None
    good_cpal_pairs = []
    for c in cpal_return_pairs:
        path = GetProjectPaths()["pallets"] / c[0] / str(c[1] + ".csv")
        with open(
            path, "r"
        ) as f:  # Files are only a handful of lines, so OK to read last line like this.
            last_line = f.readlines()[-1]
        last_line = last_line.split(",")

        # Find strawname in the final last line of the CPAL file.
        # Ensure exactly 1 straw with strawname is found.
        indices = [i for i, x in enumerate(last_line) if x.lower() == strawname.lower()]
        pass_fail_removed = None
        if len(indices) == 0:
            print(
                "GetBestCPAL: test straw",
                strawname,
                "not found in CPAL file",
                path,
                ".\nShouldn't be here.",
            )
            return None
        elif len(indices) > 1:
            raise MultipleStrawsFoundError(
                "Straw found more than once in CPAL file " + path
            )
        else:
            pass_fail_removed = last_line[
                indices[0] + 1
            ]  # P/F/R status comes after straw in the line

        # If pass, add it to good list
        if pass_fail_removed == "P":
            good_cpal_pairs.append(c)
        elif pass_fail_removed == "_" or pass_fail_removed == "F":
            pass
        else:
            print("WARNING: Unexpected straw status.", strawname, c)

    # make sure exactly one good cpal
    n = len(good_cpal_pairs)
    if n == 1:
        return good_cpal_pairs[0]
    elif n == 0 and cpal_return_pairs:
        print(
            "GetBestCPAL: cpals for",
            strawname,
            "were found, but straw didn't pass any of its latest tests.",
        )
        return None
    elif n > 1:
        print("GetBestCPAL:", strawname, "is in multiple CPALs", good_cpal_pairs)
        print("GetBestCPAL: remove straw from the old CPAL to resolve ambiguity.")
        return None


# Find the (CPALID, CPAL#) whose file contains strawname.
# In the case that multiple CPALs contain the straw, take the one with the
# largest value.
def FindCPAL(strawname):
    cpal_return_pairs = FindAllCPALs(strawname)

    if not cpal_return_pairs:
        raise StrawNotFoundError

    cpal_return_pairs = [
        i for i in cpal_return_pairs if i[1] != "CPAL9999"
    ]  # in case straw was added to bogus CPAL
    cpal_return_pairs = list(set(cpal_return_pairs))  # remove duplicates

    ret_pair = GetBestCPAL(strawname, cpal_return_pairs)
    # ret_pair = max(cpal_return_pairs, key=lambda pair: pair[1]) # Take the largest CPAL#
    return ret_pair


def UpdateStrawInfo(test, workers, strawname, result):
    # Save data to appropriate CPAL file
    database_path = GetProjectPaths()["pallets"]

    (cpalid, cpal) = FindCPAL(strawname)

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
            test = row[1]

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


# Make sure straw can (1) be found in a CPAL file and (2) attempted and passed
# its latest expected test.
#
# Redundant checks on (a) existance of the CPAL file, (b) existence of an
# attempt at the latest expected test, (c) did not fail last test, and (d) was
# indeed not removed from the pallet
def checkStraw(strawname, expected_previous_test, current_test):
    (cpalid, cpal) = FindCPAL(strawname)

    path = GetProjectPaths()["pallets"] / cpalid / str(cpal + ".csv")

    try:
        assert path.is_file()
    except AssertionError:
        print("Found a CPAL w/ this straw, but can't locate the CPAL file", path)
        raise StrawNotFoundError

    print(cpal, "found for straw", strawname, "with file", path)

    previous_test = findPreviousStep(path, expected_previous_test)
    if not previous_test:
        raise StrawNotTestedError

    failed = checkPass(path, strawname, current_test)
    if failed != []:
        raise StrawFailedError("Straw failed test(s): " + ", ".join(failed))

    straw_list = ExtractPreviousStrawData(path)[1]
    for straw in straw_list:
        if straw.lower() == strawname.lower():
            return

    print("CPAL file", path)

    raise StrawRemovedError


def validStraw(name):
    return (
        len(name) == 7
        and (name[0] == "s" or name[0] == "S")
        and (name[1] == "t" or name[1] == "T")
        and name[2:].isdigit()
    ) or (name == "_" * 7)
