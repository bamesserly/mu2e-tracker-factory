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
from guis.common.getresources import GetProjectPaths

def run():
    now=datetime.now()
    date = now.strftime("%Y-%m-%d_%H:%M")
    header="Time Stamp, Task, 24 Straw Names/Statuses, Workers, ***24 straws initially on retest pallet***\n"
    worker=input("Scan worker ID: ")
    cpal_id=input("Scan or type CPAL ID: ")
    cpal_id=cpal_id[-2:]
    cpal_num=input("Scan or type CPAL Number: ")
    cpal_num=cpal_num[-4:]
    directory=GetProjectPaths()['pallets'] / f"CPALID{cpal_id}"
    mystring=''
    for i in range(24):
        straw=input("Scan barcode #"+str(i+1)+" ")
        mystring+=(straw+",P,")
        
    cfile = directory / f"CPAL{cpal_num}.csv"
    print(f"Saving leak and length status for CPALID{cpal_id}, CPALnum{cpal_num} to file {cfile}")
    with open(cfile, "a") as myfile:
        myfile.write(date+",lasr,"+mystring+worker+"\n")
        myfile.write(date+",leng,"+mystring+worker+"\n")

    print("Finished")

if __name__ == "__main__":
    run()
