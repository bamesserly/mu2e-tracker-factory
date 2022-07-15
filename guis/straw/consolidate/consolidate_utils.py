from guis.common.getresources import GetProjectPaths
import os, sys, subprocess
from datetime import datetime

import logging

logger = logging.getLogger("root")

kBLANKSTRAWSTRING = "_______"
kCONSOLIDATE_STEPS = ["lasr", "leng"]
kGENERATE_STEPS = ["prep", "ohms", "C-O2"]
kHEADER = "Time Stamp, Task, 24 Straw Names/Statuses, Workers, ***24 straws initially on retest pallet***\n"


################################################################################
# Generic Helpers
################################################################################
# E.g. open a PDF on mac, windows, or linux
def openFile(filename):
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])


def getYN(message):
    response = ""
    while response not in ["y", "n"]:
        print("\r")
        response = input(message + " (y/n)").strip().lower()
    return response == "y"


def get_start_info():
    now = datetime.now()
    date = now.strftime("%Y-%m-%d_%H:%M")
    worker = input("Scan worker ID: ")
    cpal_id = input("Scan or type CPAL ID: ")
    cpal_id = cpal_id[-2:]
    cpal_num = input("Scan or type CPAL Number: ")
    cpal_num = cpal_num[-4:]
    directory = GetProjectPaths()["pallets"] / f"CPALID{cpal_id}"
    pfile = directory / f"CPAL{cpal_num}.csv"

    return date, worker, cpal_id, cpal_num, pfile


################################################################################
# Functions to determine whether a straw passed leak rate
################################################################################
# rate and error within acceptable limits
def rateIsAcceptable(leak_rate, leak_error):
    return (2.0e-5 < leak_rate <= 9.65e-5) and (0 < leak_error <= 9.65e-6)


# if acceptable, record info in summary LeakTestResults.csv
def checkAndRecord(
    summary_file, straw, worker, chamber, leak_rate, leak_error, data_location
):
    passed = rateIsAcceptable(leak_rate, leak_error)

    # option to override an unusual, manually-inputted rate
    if not passed and getYN(
        "The leak rate entered is unusual, want to mark it as good anyway? "
        "(otherwise you can enter a new straw)"
    ):
        passed = True

    # record a new line in the leak rate summary file
    def recordNewRate(straw, worker, chamber, leak_rate, leak_error, data_location):
        # Record findings in leak_ratefile.csv
        with open(summary_file, "a") as leak_rate_file:
            try:
                leak_rate_file.write(straw + ",")  # Straw ID
                leak_rate_file.write(
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ","
                )  # Date and Time
                leak_rate_file.write("con" + ",")  # Where data is from
                leak_rate_file.write(worker + ",")  # Worker ID
                leak_rate_file.write("chamber" + str(chamber) + ",")  # Leak chamber
                leak_rate_file.write(format(leak_rate, ".2E") + ",")  # Leak rate
                leak_rate_file.write(
                    format(leak_error, ".2E") + ","
                )  # Leak rate measurement error
                leak_rate_file.write("DataLocation:" + data_location)  # Comments
                leak_rate_file.write("\n")
            except Exception as e:
                leak_rate_file.write("\n")
                logger.error(e.message)
                logger.error(e.args)

    if passed:
        recordNewRate(straw, worker, chamber, leak_rate, leak_error, data_location)

    return passed


# prompt user for leak rate info
def getLeakInfoFromUser():
    # Get leak rate
    leak_rate = None
    while not leak_rate:
        try:
            leak_rate = float(input("Enter leak rate (ex: '8.888e-5'): ").strip())
            leak_rate = leak_rate
            break
        except ValueError:
            logger.info(f"Invalid leak rate input {leak_rate}.")

    # Get leak error
    leak_error = None
    while not leak_error:
        try:
            leak_error = float(input("Enter leak rate error(ex: '9.999e-6'): ").strip())
            leak_error = leak_error
            break
        except ValueError:
            logger.info(f"Invalid leak error input {leak_error}.")

    # Get chamber
    chamber = input("What chamber was the straw tested in? (If unknown, enter '??')")

    data_location = input("Where did you find the leak rate data?")

    return leak_rate, leak_error, chamber, data_location


# search for leak plots, open them, and prompt user for containing info
def openPlots(straw, leak_dir):
    logger.info(f"Looking for {straw} plots in the raw_data folder.")
    data_found = False
    for file_name in os.listdir(leak_dir):
        if straw.upper() in file_name.upper() and "FIT.PDF" in file_name.upper():
            data_found = True
            f = str(leak_dir / file_name)
            logger.info(f"Opening pdf {f}")
            openFile(f)
    return data_found


# search LeakTestResults for leak info
def checkSummaryFile(straw, summary_file):

    found_data = []

    with open(summary_file, "r") as leak_rate_data:
        for line in leak_rate_data:
            if straw.upper() in str(line).upper():
                line = line.split(",")
                try:
                    dt = datetime.strptime(
                        line[1], "%m/%d/%Y %H:%M"
                    )  # "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    dt = datetime.strptime(line[1], "%Y-%m-%d %H:%M:%S")
                try:
                    leak_rate = float(line[5])
                    leak_error = float(line[6])
                    found_data.append([leak_rate, leak_error, dt])
                except ValueError:
                    logger.warning(
                        f"Invalid leak data found for {straw} in "
                        "LeakTestResults.csv."
                    )
                    pass
    logger.debug(f"All results found: {found_data}")

    if not found_data:
        logger.info(f"{straw} NOT found in LeakTestResults.csv.")
        return False
    else:
        most_recent_test = max(found_data, key=lambda data: data[2])
        logger.info(f"Most recent leak test found: {most_recent_test}")
        leak_rate, leak_error = most_recent_test[0], most_recent_test[1]
        if rateIsAcceptable(leak_rate, leak_error):  # data found and it's good
            return True
        else:  # data found and it is NOT good
            logger.info(
                f"{straw} found in LeakTestResults.csv, but leak rate "
                f"({leak_rate} +/- {leak_error}) isn't considered passing."
            )
            return False


################################################################################
# Check whether straw passed leak rate
################################################################################
def passedLeakTest(straw, worker):
    leak_dir = GetProjectPaths()["strawleakdata"] / "raw_data"
    summary_file = GetProjectPaths()["leaktestresults"]
    try:
        assert summary_file.is_file()
    except AssertionError:
        logger.error(f"Leak summary file {summary_file} not found!")

    # First open plot for review
    plots_found = openPlots(straw, leak_dir)

    if not plots_found:
        rate, err, chamber, data_location = None, None, None, None
        logger.info(f"{straw} plots NOT found {str(leak_dir)}.")
        print(
            "If straw was tested recently, you may need to mergedown on "
            "the leak computer, and then on this computer."
        )

    # Look for rate in master spreadsheet, LeakTestResults.csv
    if checkSummaryFile(straw, summary_file) and getYN(
        "Based on master spreadsheet, straw seems good. Confirm and proceed?"
    ):
        return True

    # Otherwise, user type in info from plots
    if plots_found:
        leak_rate, leak_error, chamber, data_location = getLeakInfoFromUser()
        passed = checkAndRecord(
            summary_file, straw, worker, chamber, leak_rate, leak_error, data_location
        )
        if passed:
            return True
        else:
            logger.info(
                "The data you entered manually is not acceptable, and "
                "you chose not to override."
            )

    # Last chance old data? old straw new name?
    use_other_data = getYN(
        "Do you want to manually input leak rate info?\n(e.g. b/c this straw "
        "or its ancestor has been previously tested)"
    )
    if use_other_data:
        leak_rate, leak_error, chamber, data_location = getLeakInfoFromUser()
        passed = checkAndRecord(
            summary_file, straw, worker, chamber, leak_rate, leak_error, data_location
        )
        if passed:
            return True

    return False


################################################################################
# Give user a chance to review the straws
################################################################################
def finalizeStraws(straws_passed, worker, require_leak_pass=True):
    while True:
        # show the user the current state of the CPAL
        for i in range(len(straws_passed)):
            print(f"#{i+1} {straws_passed[i]}")

        # check done
        if getYN("Is this CPAL ready to go?"):
            break

        # User wants to make changes - get which straw should be replaced from
        # user input.
        while True:
            try:
                replace_straw_idx = (
                    int(input("Which position do you want to replace? (1-24) ")) - 1
                )
                assert replace_straw_idx in range(24)
                break
            except AssertionError:
                logger.warning("Invalid position. Must be #1-#24")
            except ValueError:
                logger.warning("Invalid position. Just looking for a number 1-24")

        # Enter the new straw and make sure it passes if it needs to
        replace_straw = input("Enter or scan new straw> ")

        replace_straw_is_valid = (
            (replace_straw == kBLANKSTRAWSTRING)
            or (not require_leak_pass)
            or (passedLeakTest(replace_straw, worker))
        )

        if replace_straw_is_valid:
            logger.info(f"Straw {replace_straw} is good!")
            straws_passed[replace_straw_idx] = replace_straw
        else:
            logger.info(
                f"Straw {replace_straw} couldn't be found or its data was no "
                f"good. Scan another replace_straw #{i+1}."
            )

    return straws_passed


################################################################################
# Save
################################################################################
def save_to_csv(pfile, is_new_cpal, straws_passed, workers, steps):
    logger.debug(f"Finalized straws: {straws_passed}")
    now = datetime.now()
    date = now.strftime("%Y-%m-%d_%H:%M")
    straws_passed_str = ",P,".join(straws_passed) + ",P,"
    with open(pfile, "a+") as myfile:
        if is_new_cpal:
            myfile.write(kHEADER)
        else:
            # navigate to last character in file
            myfile.seek(myfile.tell() - 1)
            # make sure it's a newline
            if myfile.read() != "\n":
                myfile.write("\n")
        for step in steps:
            myfile.write(date + "," + step + "," + straws_passed_str + workers + "\n")


def save_to_db(straws_passed, pallet_id, pallet_number):
    from guis.common.db_classes.straw_location import StrawLocation, CuttingPallet
    from guis.common.db_classes.straw import Straw

    assert len(straws_passed) == 24

    # Get or create a cpal in the DB
    try:
        cpal = StrawLocation.CPAL(pallet_id=pallet_id, number=pallet_number)
    # can't make new pallet bc this id still has straws on it.
    except AssertionError as e:
        logger.debug(e)
        CuttingPallet.remove_straws_from_pallet_by_id(pallet_id)
        cpal = StrawLocation.CPAL(pallet_id=pallet_id, number=pallet_number)

    for position, straw_id in enumerate(straws_passed):
        if straw_id == kBLANKSTRAWSTRING:
            continue

        straw_number = int(straw_id[2:])
        if not Straw.exists(straw_number):
            logger.info(f"Straw ST{straw_number} doesn't exist! Creating it.")
            logger.info("If you see lots of these messages, stop and inform Ben.")

        # safely remove this straw from its current location(s), clear the
        # target position, and then add the straw
        cpal.forceAddStraw(Straw.Straw(id=straw_number).id, position)
