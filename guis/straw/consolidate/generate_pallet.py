# ===============================================================================
# Generate a new pallet
# In the DB and in the CSV file with prep, resistance, and co2 endpieces steps
# completed.
#
# In the canonical case, a pallet will be created afresh as a csv file and in
# the DB during the prep gui/process. But also, when straws fail (usually leak)
# they undergo some debugging, and then get consolidated onto an entirely new
# or pre-existing pallet (whose own failed straws have been removed) to again
# undergo another round of leak testing. This is the script for that latter
# case.
#
# For the pallet CSV file, this script creates a new file and adds the prep,
# ohms, and CO-2 lines to it. For the DB, this script clears the pallet ID of
# any old straws and moves straws from previous straw locations to the pallet.
# ===============================================================================

from datetime import datetime
from guis.common.getresources import GetProjectPaths
from guis.common.panguilogger import SetupPANGUILogger
from guis.straw.consolidate.consolidate_utils import (
    finalizeStraws,
    save_to_csv,
    kGENERATE_STEPS,
    save_to_db,
)
from guis.common.db_classes.straw import Straw
from guis.common.db_classes.straw_location import StrawLocation, CuttingPallet
from guis.common.merger import isolated_automerge

import logging

def run():
    pallet_dir = GetProjectPaths()["pallets"]
    workers = input("Scan worker ID: ")
    cpal_id = input("Scan or type CPAL ID: ")
    cpal_id = cpal_id[-2:]
    cpal_num = input("Scan or type CPAL Number: ")
    cpal_num = cpal_num[-4:]
    pfile = pallet_dir / f"CPALID{cpal_id}" / f"CPAL{cpal_num}.csv"
    is_new_cpal = not pfile.is_file() and not pfile.exists()

    logger = SetupPANGUILogger(
        "root", tag="pallet_generator", be_verbose=False, straw_location=cpal_num
    )

    logger.info(
        f"worker:{workers}, cpalid:{cpal_id}, cpal:{cpal_num}, is_new_cpal:{is_new_cpal}"
    )

    straws_passed = []
    for i in range(24):
        while True:
            straw = input("Scan barcode #" + str(i + 1) + " ")

            # enforce basic straw format
            try:
                assert len(straw) == 7 and ("st" in straw.lower() or straw == "_______")
            except AssertionError:
                print("Invalid straw entered. Try again.")
                continue

            if straw in straws_passed and straw != "_______":
                print("***********************************************")
                print("WARNING DUPLICATE STRAW NUMBER ENTERED.")
                print("DUPLICATE STRAW HAS NOT BEEN SAVED.")
                print("IF THIS WAS SCANNED IN ERROR, PLEASE CONTINUE.")
                print("ELSE IF THERE ARE TWO IDENTICAL STRAWS ON THIS PALLET,")
                print("THIS IS BAD. CONTACT KLARA OR BEN.")
                print("***********************************************")
                continue
            else:
                straws_passed.append(straw.upper())
                break

    straws_passed = finalizeStraws(
        straws_passed=straws_passed, worker=None, require_leak_pass=False
    )

    save_to_csv(pfile, is_new_cpal, straws_passed, workers, kGENERATE_STEPS)
    save_to_db(straws_passed, cpal_id, cpal_num)

    isolated_automerge()

    logger.info("Finished")
    logger.info("See logfile for detailed straw transfer information.")


if __name__ == "__main__":
    run()
