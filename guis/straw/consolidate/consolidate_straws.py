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
import sys
from guis.common.getresources import GetProjectPaths
from guis.common.panguilogger import SetupPANGUILogger
import guis.straw.consolidate.consolidate_utils as utils
import guis.straw.consolidate.find_pmf as find_pmf
from guis.common.db_classes.straw import Straw
from guis.common.db_classes.straw_location import StrawLocation, CuttingPallet
from guis.common.merger import isolated_automerge

paths = GetProjectPaths()

logger = SetupPANGUILogger("root", tag="straw_consolidate")

def run():
    # acquire a list of pmf straws
    pmf_list = find_pmf.get_pmf_list()
    pmf_count = 0
    
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
        f"Saving leak and length status for CPALID{cpal_id}, CPAL{cpal_num} "
        f"to file {cfile}"
    )
    if not cfile.is_file():
        logger.error(
            f"{cfile} doesn't exist! find it or make it (say, with pallet generator) first."
        )
        print("sorry, exiting")
        sys.exit()

    # Scan-in straws
    straws_passed = []
    for i in range(24):
        while True:
            straw = input("Scan barcode #" + str(i + 1) + " ")
            if straw == utils.kBLANKSTRAWSTRING:
                logger.info(f"Empty straw position entered.")
                break
            elif utils.passedLeakTest(straw, worker):
                logger.info(f"Straw {straw} is good!")
                straws_passed.append(straw.upper())
                if straw in pmf_list:
                    pmf_count += 1
                break
            else:
                logger.info(
                    f"Straw {straw} couldn't be found or its data was no "
                    f"good. Scan another straw #{i+1}."
                )

    # Finalize this CPAL
    logger.debug(f"Initial straws submitted: {straws_passed}")

    straws_passed = utils.finalizeStraws(straws_passed, worker)
    straws_passed_list = straws_passed

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
        
    CuttingPallet.save_to_db(straws_passed_list, cpal_id, cpal_num)
    
    isolated_automerge()

    logger.info(str(pmf_count) + " out of " + str(len(straws_passed)) + " straws were pmf.")
    logger.info("Finished")


if __name__ == "__main__":
    run()
