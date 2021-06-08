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

logger = SetupPANGUILogger("root", tag="straw_consolidate")

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


# Look in the leak summary file for whether this straw passed leak
def passedLeakTest(strawID):
    leak_rate = -1
    leak_error = -1
    data_found = False
    leaktest_dir = GetProjectPaths()["strawleakdata"]

    # first attempt: look at the leak rate summary file
    with open(leaktest_dir / "LeakTestResults.csv", "r") as leak_rate_data:
        for line in leak_rate_data:
            if strawID.upper() in str(line).upper():
                print("\nLeak rate data found!")
                logger.info(line)
                try:
                    leak_rate = float(line.split(",")[5])
                    leak_error = float(line.split(",")[6])
                    data_found = True  # won't get here if ValueError
                    break
                except ValueError:
                    logger.warning(
                        f"Invalid leak data found for {strawID} in "
                        "LeakTestResults.csv."
                    )
                    pass

    # second attempt: manually look at the PDF
    if not data_found:
        leak_dir = GetProjectPaths()["strawleakdata"] / "raw_data"

        for file_name in os.listdir(leak_dir):
            if strawID in file_name.upper() and ".PDF" in file_name.upper():
                data_found = True

                print("\nI found a pdf of this straw's leak data.")
                f = str(leak_dir / file_name)
                logger.info(f"Opening pdf {f}")
                openFile(f)

                # data in PDF looks good! (Update the CSV summary file)
                if getYN("Does this plot have reasonable data?"):
                    # Get leak rate
                    leak_rate = None
                    while not leak_rate:
                        try:
                            leak_rate = float(
                                input("Enter leak rate (ex: '8.888e-5'): ").strip()
                            )
                            leak_rate = leak_rate
                            break
                        except ValueError:
                            logger.info(f"Invalid leak rate input {leak_rate}.")

                    # Get leak error
                    leak_error = None
                    while not leak_error:
                        try:
                            leak_error = float(
                                input("Enter leak rate error(ex: '9.999e-6'): ").strip()
                            )
                            leak_error = leak_error
                            break
                        except ValueError:
                            logger.info(f"Invalid leak error input {leak_error}.")

                    chamber = input(
                        "What chamber was the straw tested in? (If unknown, enter '??')"
                    )

                    # Record findings in leak_ratefile.csv
                    with open(
                        GetProjectPaths()["strawleakdata"] / "LeakTestResults.csv", "a"
                    ) as leak_rate_file:
                        leak_rate_file.write(strawID + ",")  # Straw ID
                        leak_rate_file.write(
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ","
                        )  # Date and Time
                        leak_rate_file.write("con" + ",")  # Where data is from
                        leak_rate_file.write(workerID + ",")  # Worker ID
                        leak_rate_file.write(
                            "chamber" + str(chamber) + ","
                        )  # Leak chamber
                        leak_rate_file.write(
                            format(leak_rate, ".2E") + ","
                        )  # Leak rate
                        leak_rate_file.write(
                            format(leak_error, ".2E") + ","
                        )  # Leak rate measurement error
                        leak_rate_file.write(
                            "DataLocation:"
                            + input("Where did you find the leak rate data?")
                        )  # Comments

                # data in PDF looks bad!
                else:
                    logger.warning(
                        f"Unable to verify straw {strawID} for consolidation"
                    )
                    print("Please show the plot to Dan")
                    return False

                break

    if not data_found:  # Couldn't find it
        leak_rate = "*missing"
        leak_error = "*missing"
        return False

    return (0 < leak_rate <= 9.65e-5) and (0 < leak_error <= 9.65e-6)


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
        f"Saving leak and length status for CPALID{cpal_id}, CPAL#{cpal_num} to file {cfile}"
    )

    # Scan-in straws
    straws_passed = ""
    for i in range(24):
        while True:
            straw = input("Scan barcode #" + str(i + 1) + " ")
            if passedLeakTest(straw):
                straws_passed += straw + ",P,"
                break
            else:
                logger.info(f"Straw {straw} was no good. Scan another straw #{i+1}")
    logger.debug(straws_passed)

    # Record straws as all having passed length and laser steps in CPAL file
    with open(cfile, "a") as myfile:
        myfile.write(date + ",lasr," + straws_passed + worker + "\n")
        myfile.write(date + ",leng," + straws_passed + worker + "\n")

    logger.debug("Finished")


if __name__ == "__main__":
    run()
