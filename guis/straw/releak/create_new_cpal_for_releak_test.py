# ===============================================================================
# When straws fail leak test, they are methane tested, found holes are cut off,
# and then many such straws are re-co2-endpieced and consolidated onto a new
# CPAL in the 2000's range.
#
# This script consolidates those straws into a new such CPAL file.
# ===============================================================================

from datetime import datetime
from guis.common.getresources import GetProjectPaths
from guis.common.panguilogger import SetupPANGUILogger


def run():
    pallet_dir = GetProjectPaths()["pallets"]
    now = datetime.now()
    date = now.strftime("%Y-%m-%d_%H:%M")
    header = "Time Stamp, Task, 24 Straw Names/Statuses, Workers, ***24 straws initially on retest pallet***\n"
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

    straw_pass_list = ""
    for i in range(24):
        while True:
            straw = input("Scan barcode #" + str(i + 1) + " ")

            # enforce basic straw format
            try:
                assert len(straw) == 7 and ("st" in straw.lower() or straw == "_______")
            except AssertionError:
                print("Invalid straw entered. Try again.")
                continue

            if straw in straw_pass_list and straw != "_______":
                print("***********************************************")
                print("WARNING DUPLICATE STRAW NUMBER ENTERED.")
                print("DUPLICATE STRAW HAS NOT BEEN SAVED.")
                print("IF THIS WAS SCANNED IN ERROR, PLEASE CONTINUE.")
                print("ELSE IF THERE ARE TWO IDENTICAL STRAWS ON THIS PALLET,")
                print("THIS IS BAD. CONTACT KLARA OR BEN.")
                print("***********************************************")
                continue
            else:
                straw_pass_list += straw.upper() + ",P,"
                break

    with open(pfile, "a+") as myfile:
        if is_new_cpal:
            myfile.write(header)
        else:
            # navigate to last character in file
            myfile.seek(myfile.tell() - 1)
            # make sure it's a newline
            if myfile.read() != "\n":
                myfile.write("\n")
        myfile.write(date + ",prep," + straw_pass_list + workers + "\n")
        myfile.write(date + ",ohms," + straw_pass_list + workers + "\n")
        myfile.write(date + ",C-O2," + straw_pass_list + workers + "\n")

    logger.info("Finished")


if __name__ == "__main__":
    run()
