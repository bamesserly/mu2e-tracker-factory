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
from guis.straw.consolidate.consolidate_utils import finalizeStraws
from guis.common.db_classes.straw import Straw
from guis.common.db_classes.straw_location import StrawLocation, CuttingPallet
from guis.common.merger import isolated_automerge

import logging


def save_to_db(straws_passed_list, pallet_id, pallet_number):
    logger = logging.getLogger("root")
    assert len(straws_passed_list) == 24

    # Get or create a cpal in the DB
    try:
        cpal = StrawLocation.CPAL(pallet_id=pallet_id, number=pallet_number)
    # can't make new pallet bc this id still has straws on it.
    except AssertionError as e:
        logger.debug(e)
        CuttingPallet.remove_straws_from_pallet_by_id(pallet_id)
        cpal = StrawLocation.CPAL(pallet_id=pallet_id, number=pallet_number)

    for position, straw_id in enumerate(straws_passed_list):
        straw_number = int(straw_id[2:])
        if not Straw.exists(straw_number):
            logger.info(f"Straw ST{straw_number} doesn't exist! Creating it.")
            logger.info("If you see lots of these messages, stop and inform Ben.")

        # safely remove this straw from its current location(s), clear the
        # target position, and then add the straw
        cpal.forceAddStraw(Straw.Straw(id=straw_number).id, position)


def save_to_csv(pfile, is_new_cpal, straw_pass_list, workers):
    logger = logging.getLogger("root")
    now = datetime.now()
    date = now.strftime("%Y-%m-%d_%H:%M")
    header = "Time Stamp, Task, 24 Straw Names/Statuses, Workers, ***24 straws initially on retest pallet***\n"
    straws_passed_str = ",P,".join(straw_pass_list) + ",P,"
    logger.debug(straws_passed_str)
    with open(pfile, "a+") as myfile:
        if is_new_cpal:
            myfile.write(header)
        else:
            # navigate to last character in file
            myfile.seek(myfile.tell() - 1)
            # make sure it's a newline
            if myfile.read() != "\n":
                myfile.write("\n")
        myfile.write(date + ",prep," + straws_passed_str + workers + "\n")
        myfile.write(date + ",ohms," + straws_passed_str + workers + "\n")
        myfile.write(date + ",C-O2," + straws_passed_str + workers + "\n")


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

    straws_passed_list = []
    for i in range(24):
        while True:
            straw = input("Scan barcode #" + str(i + 1) + " ")

            # enforce basic straw format
            try:
                assert len(straw) == 7 and ("st" in straw.lower() or straw == "_______")
            except AssertionError:
                print("Invalid straw entered. Try again.")
                continue

            if straw in straws_passed_list and straw != "_______":
                print("***********************************************")
                print("WARNING DUPLICATE STRAW NUMBER ENTERED.")
                print("DUPLICATE STRAW HAS NOT BEEN SAVED.")
                print("IF THIS WAS SCANNED IN ERROR, PLEASE CONTINUE.")
                print("ELSE IF THERE ARE TWO IDENTICAL STRAWS ON THIS PALLET,")
                print("THIS IS BAD. CONTACT KLARA OR BEN.")
                print("***********************************************")
                continue
            else:
                straws_passed_list.append(straw.upper())
                break

    straws_passed_list = finalizeStraws(
        straws_passed=straws_passed_list, worker=None, require_leak_pass=False
    )

    save_to_csv(pfile, is_new_cpal, straws_passed_list, workers)
    save_to_db(straws_passed_list, cpal_id, cpal_num)

    isolated_automerge()

    logger.info("Finished")
    logger.info("See logfile for detailed straw transfer information.")


if __name__ == "__main__":
    run()
