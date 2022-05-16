from datetime import datetime

# from guis.common.getresources import GetProjectPaths
from guis.common.gui_utils import except_hook
from guis.common.panguilogger import SetupPANGUILogger
import sys
from time import sleep


def run():
    sys.excepthook = except_hook  # crash, don't hang when an exception is raised
    print(
        """
    \n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n
     |  \/  | __|_   _| || | /_\ | \| | __| |_   _| __/ __|_   _|
     | |\/| | _|  | | | __ |/ _ \| .` | _|    | | | _|\__ \ | |
     |_|  |_|___| |_| |_||_/_/ \_\_|\_|___|   |_| |___|___/ |_|
    """
    )
    sleep(1)
    worker = input("Scan worker ID: ")
    cpal_id = input("Scan or type CPAL ID: ")
    cpal_id = cpal_id[-2:]
    cpal_num = input("Scan or type CPAL Number: ")
    cpal_num = cpal_num[-4:]

    is_first_test = True
    while True:
        response = input(
            "First time testing this pallet?\n[a] first time\n[b] second time\n> "
        ).lower()
        if response == "a" or response == "b":
            is_first_test = True if response == "a" else False
            break

    logger = SetupPANGUILogger(
        "root", tag="Methane", be_verbose=False, straw_location=cpal_num
    )

    logger.info(
        f"worker:{worker}, cpalid:{cpal_id}, cpal:{cpal_num}, first_test:{is_first_test}"
    )

    start_time = datetime.now()

    print("\nScan or type the first straw you're testing.")
    print("\nAnd continue scanning straws as you test them.")
    print('\nPress ctrl-c or enter "quit" to log out.\n')
    n_straws_scanned = 0
    while True:
        straw = "ST00000"
        try:
            straw = input(f"Straw {n_straws_scanned+1}: ").upper()
            if straw.lower() == "quit":
                break
            assert len(straw) == 7 and "ST" in straw and int(straw[2:])
            logger.debug(f"Straw #{n_straws_scanned+1}: {straw}")
            n_straws_scanned += 1
        except AssertionError:
            logger.error(f"Invalid straw entered {straw}")
            continue
        except KeyboardInterrupt:
            print("\n")
            break
    logger.info("Finishing.")
    logger.info(f"{n_straws_scanned} straws scanned.")
    logger.debug(f"elapsed_time:{datetime.now()-start_time}")
    print("Exiting in 5 seconds. Goodbye.")
    sleep(5)
    sys.exit()


if __name__ == "__main__":
    run()

"""
    now = datetime.now()
    date = now.strftime("%Y-%m-%d_%H:%M")
    header = "Time Stamp, Task, 24 Straw Names/Statuses, Workers, ***24 straws initially on retest pallet***\n"
    logger.debug(f"{worker} logged in.")




    now = datetime.now()
    date = now.strftime("%Y-%m-%d_%H:%M")
    header = "Time Stamp, Task, 24 Straw Names/Statuses, Workers, ***24 straws initially on retest pallet***\n"
    workers = "wk-kballs-b01,wk-ajamal01"
    cpal_id = input("Scan or type CPAL ID: ")
    cpal_id = cpal_id[-2:]
    cpal_num = input("Scan or type CPAL Number: ")
    cpal_num = cpal_num[-4:]
    # if this code is ever uncommented this should use
    # "from guis.common.getresources import GetProjectPaths"
    # and "self.palletDirectory = paths["pallets"]" to get a path to the pallets directory
    # otherwise bad things happen with the strawroom and merges and stuff
    # with the two previous lines the next could be like this:
    # "directory = ("C:self.palletDirectory\\CPALID" + cpal_id + "\\")

    directory = (
        "C:\\Users\\Mu2e\Desktop\\Production\\Data\\Pallets\\CPALID" + cpal_id + "\\"
    )
    mystring = ""
    for i in range(24):
        while True:
            straw = input("Scan barcode #" + str(i + 1) + " ")
            if "st" in straw.lower() and straw in mystring:
                print("***********************************************")
                print("WARNING DUPLICATE STRAW NUMBER ENTERED.")
                print("DUPLICATE STRAW HAS NOT BEEN SAVED.")
                print("IF THIS WAS SCANNED IN ERROR, PLEASE CONTINUE.")
                print("ELSE IF THERE ARE TWO IDENTICAL STRAWS ON THIS PALLET,")
                print("THIS IS BAD. CONTACT KLARA OR BEN.")
                print("***********************************************")
                continue
            else:
                mystring += straw + ",P,"
                break

    with open(directory + "CPAL" + cpal_num + ".csv", "w") as myfile:
        myfile.write(header)
        myfile.write(date + ",prep," + mystring + workers + "\n")
        myfile.write(date + ",ohms," + mystring + workers + "\n")
        myfile.write(date + ",C-O2," + mystring + workers + "\n")

    print("Finished")




################################################################################
################################################################################
from datetime import datetime
import os, sys, subprocess

################################################################################
# Global stuff
################################################################################
logger = SetupPANGUILogger("root", tag="straw_consolidate")

leaktest_dir = GetProjectPaths()["strawleakdata"]
summary_file = GetProjectPaths()["leaktestresults"]
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
        return False, None, None, None, None
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
    found_plot, leak_rate, leak_error, chamber, data_location = checkPlots(straw)
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
def finalizeStraws(straws_passed, worker):
    finalized = False
    while not finalized:
        # show the user the current state of the CPAL
        for i in range(len(straws_passed)):
            print(f"#{i+1} {straws_passed[i]}")

        # check done
        finalized = getYN("Is this CPAL ready to go?")
        if finalized:
            continue

        # User wants to make changes - get which straw should be replaced from
        # user input.
        while True:
            try:
                replace_straw_idx = (
                    int(input("Which straw do you want to replace? (1-24) ")) - 1
                )
                assert replace_straw_idx in range(24)
                break
            except AssertionError:
                logger.warning("Invalid straw. Must be #1-#24")
            except ValueError:
                logger.warning("Invalid straw. Just looking for a number 1-24")

        # Enter the new straw and make sure it passes
        replace_straw = input("Enter or scan new straw> ")
        if passedLeakTest(replace_straw, worker):
            logger.info(f"Straw {replace_straw} is good!")
            straws_passed[replace_straw_idx] = replace_straw
        else:
            logger.info(
                f"Straw {replace_straw} couldn't be found or its data was no "
                f"good. Scan another replace_straw #{i+1}."
            )

    return straws_passed


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
    straws_passed = []
    for i in range(24):
        while True:
            straw = input("Scan barcode #" + str(i + 1) + " ")
            if passedLeakTest(straw, worker):
                logger.info(f"Straw {straw} is good!")
                straws_passed.append(straw)
                break
            else:
                logger.info(
                    f"Straw {straw} couldn't be found or its data was no "
                    f"good. Scan another straw #{i+1}."
                )

    # Finalize this CPAL
    logger.debug(f"Initial straws submitted: {straws_passed}")

    straws_passed = finalizeStraws(straws_passed, worker)

    logger.debug(f"Finalized straws: {straws_passed}")

    straws_passed_str = ",P,".join(straws_passed) + ",P,"

    logger.debug(straws_passed_str)

    # Record straws as all having passed length and laser steps in CPAL file
    with open(cfile, "r+") as myfile:
        text = (
            myfile.readlines()
        )  # read whole file so next write will be at end of file
        if (
            text[-1][-1] != "\n"
        ):  # if last character of last line is not newline, add it
            myfile.write("\n")
        myfile.write(date + ",lasr," + straws_passed_str + worker + "\n")
        myfile.write(date + ",leng," + straws_passed_str + worker + "\n")

    logger.info("Finished")
"""
