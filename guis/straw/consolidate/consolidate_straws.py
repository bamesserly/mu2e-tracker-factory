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

# Look in the leak summary file for whether this straw passed leak
def checkLeakData(strawID):
    data_found = False
    leaktest_dir = GetProjectPaths()["strawleakdata"]

    with open(leaktest_dir / "StrawLeakSummary.csv", "r") as leak_rate_data:
        for line in leak_rate_data:
            if strawID.upper() in str(line).upper():
                print("\nLeak rate data found!")
                print(line)
                try:
                    self.leak_rate = float(line.split(",")[5])
                    self.leak_error = float(line.split(",")[6])
                    data_found = True
                    break
                except ValueError:
                    pass

    if not data_found:
        leak_dir = GetProjectPaths()["strawleakdata"] / "raw_data"

        for file_name in os.listdir(leak_dir):
            if self.strawID in file_name.upper() and ".PDF" in file_name.upper():

                data_found = True

                print("\nI found a pdf of this straw's leak data.")
                print("Opening pdf...")
                subprocess.Popen(
                    [str(leak_dir / file_name)], shell=True
                )  # Opens leak plot pdf

                if self.getYN("Does this plot have reasonable data?"):
                    # Get leak rate
                    self.leak_rate = None
                    while not self.leak_rate:
                        try:
                            leak_rate = float(
                                input("Enter leak rate (ex: '8.888e-5'): ").strip()
                            )
                            self.leak_rate = leak_rate
                            break
                        except ValueError:
                            print("Invalid input.")

                    # Get leak error
                    self.leak_error = None
                    while not self.leak_error:
                        try:
                            leak_error = float(
                                input("Enter leak rate error(ex: '9.999e-6'): ").strip()
                            )
                            self.leak_error = leak_error
                            break
                        except ValueError:
                            print("Invalid input.")

                    chamber = input(
                        "What chamber was the straw tested in? (If unknown, enter '??')"
                    )

                    # Record findings in leak_ratefile.csv
                    with open(
                        GetProjectPaths()["strawleakdata"] / "LeakTestResults.csv", "a"
                    ) as leak_rate_file:
                        leak_rate_file.write("\n")  # Newline
                        leak_rate_file.write(self.strawID + ",")  # Straw ID
                        leak_rate_file.write(
                            datetime.now().strftime("%m/%d/%Y %H:%M") + ","
                        )  # Date and Time
                        leak_rate_file.write("ver" + ",")  # Where data is from
                        leak_rate_file.write(self.workerID + ",")  # Worker ID
                        leak_rate_file.write(
                            "chamber" + str(chamber) + ","
                        )  # Leak chamber
                        leak_rate_file.write(
                            format(self.leak_rate, ".2E") + ","
                        )  # Leak rate
                        leak_rate_file.write(
                            format(self.leak_error, ".2E") + ","
                        )  # Leak rate measurement error
                        leak_rate_file.write(
                            "Data location: "
                            + input("Where did you find the leak rate data?")
                        )  # Comments

                else:  # There's something funky with the plot
                    with open(
                        GetProjectPaths()["strawstorage"]
                        / "BenRecalculateLeakTest.txt",
                        "a",
                    ) as f:
                        f.write("\n" + self.strawID)
                    print("We'll have Ben look at it.")
                    self.comments += "abnormal leak plot- ben recalculate"
                    return False

                break

    if not data_found:  # Couldn't find it
        self.leak_rate = "*missing"
        self.leak_error = "*missing"
        return False

    return (0 < self.leak_rate <= 9.65e-5) and (0 < self.leak_error <= 9.65e-6)


def run():
    now = datetime.now()
    date = now.strftime("%Y-%m-%d_%H:%M")
    header = "Time Stamp, Task, 24 Straw Names/Statuses, Workers, ***24 straws initially on retest pallet***\n"
    worker = input("Scan worker ID: ")
    cpal_id = input("Scan or type CPAL ID: ")
    cpal_id = cpal_id[-2:]
    cpal_num = input("Scan or type CPAL Number: ")
    cpal_num = cpal_num[-4:]
    directory = GetProjectPaths()["pallets"] / f"CPALID{cpal_id}"
    mystring = ""
    for i in range(24):
        straw = input("Scan barcode #" + str(i + 1) + " ")
        mystring += straw + ",P,"

    cfile = directory / f"CPAL{cpal_num}.csv"
    print(
        f"Saving leak and length status for CPALID{cpal_id}, CPALnum{cpal_num} to file {cfile}"
    )
    with open(cfile, "a") as myfile:
        myfile.write(date + ",lasr," + mystring + worker + "\n")
        myfile.write(date + ",leng," + mystring + worker + "\n")

    print("Finished")


if __name__ == "__main__":
    run()
