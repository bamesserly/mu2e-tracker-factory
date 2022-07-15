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
from guis.common.merger import isolated_automerge
from tests.do_a_mergedown import run as do_a_mergedown

import logging

paths = GetProjectPaths()


def run():
    date, worker, cpal_id, cpal_num, pfile = utils.get_start_info()

    logger = SetupPANGUILogger(
        "root", tag="consolidate", be_verbose=False, straw_location=cpal_num
    )

    # download the latest DB to local.
    # mostly so that straws don't get erronously marked "new"
    do_a_mergedown()

    logger.info("Beginning straw consolidation")
    logger.info(
        f"Saving laser and length status for CPALID{cpal_id}, CPAL{cpal_num} "
        f"to file {pfile}"
    )

    if not pfile.is_file():
        logger.error(
            f"{pfile} doesn't exist! find it or make it (say, with pallet generator) first."
        )
        print("sorry, exiting")
        sys.exit()
    is_new_cpal = False

    # get existing pmf straws
    pmf_list = find_pmf.get_pmf_list()
    pmf_count = 0

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

    utils.save_to_csv(
        pfile, is_new_cpal, straws_passed, worker, utils.kCONSOLIDATE_STEPS
    )
    utils.save_to_db(straws_passed, cpal_id, cpal_num)

    isolated_automerge()

    logger.info(
        str(pmf_count) + " out of " + str(len(straws_passed)) + " straws were pmf."
    )
    logger.info("Finished")


if __name__ == "__main__":
    run()
