# Functions to save straw data to appropriate file

import os, time, datetime, csv
from guis.common.getresources import GetProjectPaths


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


def FindCPAL(strawname):
    # Returns (CPALID, CPAL) of straw number
    # If a straw is associated with more than one CPALID, use the largest (i.e.
    # most recent) one.
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

    # return the (cpalid,cpal) pair that has the highest cpal.
    # e.g. max([('CPAL01', 'CPAL0123'), ('CPAL01, 'CPAL6798')]), the max
    # function is performed on 'CPAL0123' vs 'CPAL6789', and 'CPAL6789' wins.
    if cpal_return_pairs:
        cpal_return_pairs = [i for i in cpal_return_pairs if i[1] != "CPAL9999"]
        ret = max(cpal_return_pairs, key=lambda pair: pair[1])
        # print(ret)
        # print("CPAL", ret[1],"for straw", strawname, "found")
        return ret

    raise StrawNotFoundError


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


def checkStraw(strawname, expected_previous_test, current_test):
    database_path = GetProjectPaths()["pallets"]

    (cpalid, cpal) = FindCPAL(strawname)

    path = database_path / cpalid / str(cpal + ".csv")

    try:
        assert path.is_file()
    except AssertionError:
        print("cannot find pallet file", path)

    print(cpal, "found for straw", strawname, "with file", path)

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

    print("CPAL file", path)

    raise StrawRemovedError


def validStraw(name):
    return (
        len(name) == 7
        and (name[0] == "s" or name[0] == "S")
        and (name[1] == "t" or name[1] == "T")
        and name[2:].isdigit()
    ) or (name == "_" * 7)
