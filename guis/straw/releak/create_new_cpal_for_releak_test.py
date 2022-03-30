# ===============================================================================
# When straws fail leak test, they are methane tested, found holes are cut off,
# and then many such straws are re-co2-endpieced and consolidated onto a new
# CPAL in the 2000's range.
#
# This script consolidates those straws into a new such CPAL file.
# ===============================================================================

from datetime import datetime


def run():
    now = datetime.now()
    date = now.strftime("%Y-%m-%d_%H:%M")
    header = "Time Stamp, Task, 24 Straw Names/Statuses, Workers, ***24 straws initially on retest pallet***\n"
    workers = "wk-kballs-b01,wk-ajamal01"
    cpal_id = input("Scan or type CPAL ID: ")
    cpal_id = cpal_id[-2:]
    cpal_num = input("Scan or type CPAL Number: ")
    cpal_num = cpal_num[-4:]
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


if __name__ == "__main__":
    run()
