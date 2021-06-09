################################################################################
# Before laser cutting is run, arbitrarily replace any straw on a CPAL with any
# other straw, by scanning in all 24 straws that shall now make up this new
# CPAL.
#
# Expected use is to replace failed straws with misc re-tested straws of
# appropriate length.
#
# After scanning in the 24 new straws that shall make up the CPAL, laser and
# length rows are added to the CPAL file with all "passes". This sort of
# retires the laser cut gui. Because folks are expected to manually cut their
# straws now.
#
# Many todos: re-implement the cutting pyautogui automation, make sure you
# didn't scan the same straw twice, make sure everything is formatted
# correctly, useful errors for when the CPAL file is missing.
################################################################################
from datetime import datetime
import os, sys, subprocess
from guis.common.getresources import GetProjectPaths
from guis.common.panguilogger import SetupPANGUILogger

################################################################################
# Global stuff
################################################################################
logger = SetupPANGUILogger("root", tag="straw_consolidate")

leaktest_dir = GetProjectPaths()["strawleakdata"]
summary_file = leaktest_dir / "LeakTestResults.csv"
try:
    assert summary_file.is_file()
except AssertionError:
    logger.error(f"Leak summary file {summary_file} not found!")

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


################################################################################
# Functions to determine whether a straw passed leak rate
################################################################################
# rate and error within acceptable limits
def rateIsAcceptable(leak_rate, leak_error):
    return (0 < leak_rate <= 9.65e-5) and (0 < leak_error <= 9.65e-6)


# search LeakTestResults for leak info
def checkSummaryFile(straw):
    leak_rate = -1
    leak_error = -1
    data_found = False
    with open(summary_file, "r") as leak_rate_data:
        for line in leak_rate_data:
            if straw.upper() in str(line).upper():
                logger.debug(line)
                try:
                    leak_rate = float(line.split(",")[5])
                    leak_error = float(line.split(",")[6])
                    data_found = True
                    break
                except ValueError:
                    logger.warning(
                        f"Invalid leak data found for {straw} in "
                        "LeakTestResults.csv."
                    )
                    pass

    if not data_found:
        logger.info(f"{straw} NOT found in LeakTestResults.csv.")
        return False
    else:
        if rateIsAcceptable(leak_rate, leak_error):  # data found and it's good
            return True
        else:  # data found and it is NOT good
            logger.info(
                f"{straw} found in LeakTestResults.csv, but leak rate "
                f"({leak_rate} +/- {leak_error}) isn't considered passing."
            )
            return False


# if acceptable, record info in summary LeakTestResults.csv
def checkAndRecord(
    summary_file, straw, worker, chamber, leak_rate, leak_error, data_location
):
    passed = rateIsAcceptable(leak_rate, leak_error)

    # option to override an unusual, manually-inputted rate
    if not passed and getYN(
        "The leak rate entered is unusual, proceed anyway? (otherwise "
        "enter a new straw)"
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
def checkPlots(straw):
    logger.info(f"Looking for {straw} plots in the raw_data folder.")
    data_found = False
    leak_dir = leaktest_dir / "raw_data"
    for file_name in os.listdir(leak_dir):
        if straw in file_name.upper() and "FIT.PDF" in file_name.upper():
            data_found = True
            f = str(leak_dir / file_name)
            logger.info(f"Opening pdf {f}")
            openFile(f)
    if not data_found:
        return False, None, None, None
    else:
        rate, err, chamber, data_location = getLeakInfoFromUser()
        return data_found, rate, err, chamber, data_location


################################################################################
# Check whether straw passed leak rate
################################################################################
def passedLeakTest(straw, worker):
    # First try LeakTestResults.csv
    if checkSummaryFile(straw):
        return True

    # Next try plots in the raw_data folder.
    found_plot, leak_rate, leak_err, chamber = checkPlots(straw)
    if found_plot:
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
    else:
        logger.info(f"{straw} plots NOT found {str(leaktest_dir)}.")
        print(
            "If straw was tested recently, you may need to mergedown on "
            "the leak computer, and then on this computer."
        )

    # Last chance – old data? old straw new name?
    use_other_data = getYN(
        "Do you want to manually input leak rate info (e.g. b/c this straw or "
        "its ancestor has been previously tested)?"
    )
    if use_other_data:
        leak_rate, leak_error, chamber, data_location = getLeakInfoFromUser()
        passed = checkAndRecord(
            summary_file, straw, worker, chamber, leak_rate, leak_error, data_location
        )
        if passed:
            return False

    return False


################################################################################
# Main
################################################################################
def run():
    logger.info("Beginning straw consolidation")
    now = datetime.now()
    date = now.strftime("%Y-%m-%d_%H:%M")
    header = "Time Stamp, Task, 24 Straw Names/Statuses, Workers, ***24 straws initially on retest pallet***\n"
    worker = input("Scan worker ID: ")
    cpal_id = input("Scan or type CPAL ID: ")
    cpal_id = cpal_id[-2:]
    cpal_num = input("Scan or type CPAL Number: ")
    cpal_num = cpal_num[-4:]
    logger.debug(f"{worker} logged in.")
    directory = GetProjectPaths()["pallets"] / f"CPALID{cpal_id}"
    cfile = directory / f"CPAL{cpal_num}.csv"
    logger.info(
        f"Saving leak and length status for CPALID{cpal_id}, CPAL#{cpal_num} "
        f"to file {cfile}"
    )

    # Scan-in straws
    straws_passed = ""
    for i in range(24):
        while True:
            straw = input("Scan barcode #" + str(i + 1) + " ")
            if passedLeakTest(straw, worker):
                logger.info(f"Straw {straw} is good!")
                straws_passed += straw + ",P,"
                break
            else:
                logger.info(
                    f"Straw {straw} couldn't be found or it was no "
                    f"good. Scan another straw #{i+1}."
                )
    logger.debug(straws_passed)

    # Record straws as all having passed length and laser steps in CPAL file
    with open(cfile, "a") as myfile:
        myfile.write(date + ",lasr," + straws_passed + worker + "\n")
        myfile.write(date + ",leng," + straws_passed + worker + "\n")

    logger.info("Finished")


if __name__ == "__main__":
    run()
