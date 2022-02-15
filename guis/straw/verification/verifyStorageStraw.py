import os
import subprocess
import csv
import checkLaserCut
import makeLeakRateFile  # Makes new leak_rate data file
import time
from datetime import datetime
from calibratedRLS import CalibratedRLS
from tempHumid import getTempHumid
from multiMeter import MultiMeter
from guis.common.getresources import GetProjectPaths


class verifyStorageStraw:
    def __init__(self):
        self.printMu2e()
        # Data Storage
        self.storage_directory = GetProjectPaths()['strawstorage']
        self.verification_files = {
            "verified": "StorageVerified.csv",
            "rejected": "StorageRejected.csv",
            "storage": "Storage.csv",
        }
        self.verification_file = (
            lambda key: self.storage_directory / self.verification_files[key]
        )

        self.storage = list()
        self.verified_straws = list()
        self.rejected_straws = list()

        # Length measurement
        self.rls = CalibratedRLS()
        self.sampleMeasurements = False

        self.verified = {
            "strawID": False,
            "position": False,
            "leng": False,
            "ohms": False,
            "leak": False,
            "undamaged": True,
        }

        # Straw Variables
        self.workerID = ""
        self.strawID = ""
        self.position = None  # not a valid position
        self.ii = None
        self.oo = None
        self.leak_rate = None
        self.leak_error = None
        self.desired_length = None
        self.length = None
        self.difference = None
        self.comments = ""

    def connectRLS(self):
        while (
            not self.rls.connectEncoder()
        ):  # Tries to connect. If unsuccessful, runs code below.
            if input("Couldn't connect to RLS. Try again? (y/n").strip().lower() == "n":
                break

    def getStraws(self, key):
        if key == True:
            key = "verified"
        if key == False:
            key = "rejected"

        strawList = list()

        with open(self.verification_file(key), newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for line in reader:
                strawList.append(line["straw"].upper())

        return strawList

    # Runs getStraws() for all three keys ['storage', 'verified', 'rejected']
    def getAllStraws(self):
        self.storage = self.getStraws("storage")
        self.verified_straws = self.getStraws("verified")
        self.rejected_straws = self.getStraws("rejected")

    # Function based on positioncheck.py
    def checkLaserCutData(self, straw, pos):
        path = GetProjectPaths()['laserdata']
        for pal in os.listdir(path):
            with open(path / pal) as csvf:
                reader = csv.reader(csvf)
                line = reader.__next__()
                line = reader.__next__()
                cutt = line[2]
                cut = int(cutt[1])
                line = reader.__next__()
                for i in range(24):
                    if line[i] == straw:
                        pos = 92 - 4 * i + cut
                        return pos
            csvf.close()
        return False

    def printMu2e(self):
        print(" __  __       ___       ")
        print("|  \/  |     |__ \      ")
        print("| \  / |_   _   ) |___  ")
        print("| |\/| | | | | / // _ \ ")
        print("| |  | | |_| |/ /|  __/ ")
        print("|_|  |_|\____|____\___| ")

    # Given strawID, returns ((float) ii, (float) oo, (bool) pass_fail)
    def checkResistanceData(self, strawID):
        strawID = strawID.upper()
        resistance_dir = GetProjectPaths()['strawresistance']
        res_data = {
            "ii": float(),
            "io": float(),
            "oi": float(),
            "oo": float(),
        }
        res_evaluation = {
            "ii": lambda data: (50.0 <= data <= 250.0),
            "oo": lambda data: (50.0 <= data <= 250.0),
            "io": lambda data: (data > 1000),
            "oi": lambda data: (data > 1000),
        }
        pass_fail = {
            "ii": False,
            "io": False,
            "oi": False,
            "oo": False,
        }
        for filename in os.listdir(resistance_dir):
            if filename.endswith(".csv") and strawID[:5] in filename.upper():
                with open(resistance_dir / filename) as f:
                    reader = csv.DictReader(f)
                    for line in reader:
                        if line["Straw Number"].upper() == strawID.upper():
                            res_data[line[" Measurement Type"].strip().lower()] = float(
                                line[" Resistance(Ohms)"].lower()
                            )

        for key in res_data.keys():
            if res_data[key] == float():
                res_data[key] = self.measureResistanceByHand(key)

        for key in res_data.keys():
            pass_fail[key] = res_evaluation[key](res_data[key])

        return (res_data["ii"], res_data["oo"], pass_fail)

    def measureResistanceByHand(self, measurement_type):
        print("\n---MEASURE RESISTANCE BY HAND---")
        print("TURN ON THE DIGITAL MULTIMETER")
        time.sleep(2)
        input("Press ENTER to measure " + measurement_type + " resistance.")
        return MultiMeter().collect_data()

    def checkLeakData(self, strawID):
        data_found = False
        leaktest_dir = GetProjectPaths()['strawleakdata']

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
            leak_dir = GetProjectPaths()['strawleakdata'] / "raw_data"

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
                                    input(
                                        "Enter leak rate error(ex: '9.999e-6'): "
                                    ).strip()
                                )
                                self.leak_error = leak_error
                                break
                            except ValueError:
                                print("Invalid input.")

                        chamber = input(
                            "What chamber was the straw tested in? (If unknown, enter '??')"
                        )

                        # Record findings in leak_ratefile.csv
                        with open(GetProjectPaths()["strawleakdata"] / "LeakTestResults.csv", "a") as leak_rate_file:
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
                        with open(GetProjectPaths()["strawstorage"] / "BenRecalculateLeakTest.txt", "a") as f:
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

    def measureLength(self):

        self.desired_length = self.getDesiredStrawLength()
        self.length = float()

        while not self.length:

            if self.position >= 4:
                self.length = self.rls.measure("mm")
            else:
                self.length = self.measureWithRuler("mm")

            self.difference = self.length - self.desired_length

            print("Desired Length:  " + format(self.desired_length, "7.2f") + " mm")
            print("Measured Length: " + format(self.length, "7.2f") + " mm")
            print("Difference:      " + format(self.difference, "7.2f") + " mm")
            print("Tolerance:       " + format(0.50, "7.2f") + " mm")

            self.verified["leng"] = -0.500 <= self.difference <= 0.500

            if self.verified["leng"]:
                print("Length is within tolerance!")
            else:
                # Check if straw is within tolerance at any surrounding position
                for pos in range(0, 95, 2):
                    if -0.500 <= self.length - self.getDesiredStrawLength(pos) <= 0.500:
                        print(
                            "\nThis straw is within tolerance for position "
                            + str(pos)
                            + " ¯\_(*-*)_/¯"
                        )

                        if self.getYN("Do you want to change this straw's position?"):
                            print("Go get a new position barcode for this tube.")
                            self.position = pos
                            self.verified["leng"] = True

                if not self.verified["leng"]:
                    print("Length is outside tolerance :(")
                    if self.getYN("Do you want to try measuring again?"):
                        self.length = float()  # loop 'while run_program:' again

    def measureWithRuler(self, units="mm"):
        print("\n\n---Measure Length with Ruler---")
        print(
            "\nThis straw is too long to measure with the RLS. You will need to measure it with the ruler."
        )
        print("\nA  -n[]|=======================|[]n-  B")
        print('Measure "brass-to-brass": A [<---->] B')

        inch_A = float(input("Enter inches reading on side A: "))
        prec_A = float(input("Enter 64ths reading on side A:  ")) / 64
        inch_B = float(input("Enter inches reading on side B: "))
        prec_B = float(input("Enter 64ths reading on side B:  ")) / 64

        length = (
            self.rls.convert_in_to_mm((inch_B + prec_B) - (inch_A + prec_A)) + 16.00
        )
        if units == "in":
            length = self.rls.convert_mm_to_in(length)

        return length

    def getDesiredStrawLength(self, pos=None):

        if pos == None:
            pos = self.position

        nominal_length = float()

        with open(GetProjectPaths()['strawverificationcode'] / "nominal_lengths.csv", "r") as nominal_lengths:
            reader = csv.DictReader(nominal_lengths)
            for line in reader:
                if int(line["position"]) == pos:
                    nominal_length = float(line["length"])

        temp_bas, humid_bas = 68.0, 0.0
        temp_now, humid_now = getTempHumid("F")
        temp_cor, humid_cor = 0.0000094, 0.0000096

        # Apply length-adjustment formula
        adjusted_length = nominal_length * (
            1.0
            + (temp_cor * (temp_now - temp_bas))
            + (humid_cor * (humid_now - humid_bas))
        )

        return (
            self.rls.convert_in_to_mm(adjusted_length) + 20.0
        )  # Convert to mm and account for endpieces

    def getYN(self, message):

        response = ""
        while response not in ["y", "n"]:
            print("\r")
            response = input(message + " (y/n)").strip().lower()

        return response == "y"

    def verifyWorkerID(self):
        return self.workerID.startswith("WK-") and self.workerID[-2:].isnumeric()

    def verifyStrawID(self, string):
        return (
            len(string) == 7
            and string.upper().startswith("ST")
            and string[2:].isnumeric()
        )

    def getValidStrawID(self):

        while True:
            strawID = input("\nScan straw ID (ST#####): ").strip().upper()
            if self.verifyStrawID(strawID):
                return strawID
            print("Invalid entry. StrawID must be of the form ST#####")

    def verificationSort(self, line):
        return str(line["position"]) + str(line["straw"])

    def recordVerification(self, key):

        ## Before recording data in verification, remove straw from rejects file (if necessary)
        ## If straw is rejected a second time, both sets of data will be saved.
        if self.strawID in self.rejected_straws:
            print("previously rejected. Removing from rejects")
            self.removeFromRejects(self.strawID)

        fieldnames = [
            "timestamp",
            "straw",
            "position",
            "workers",
            "ohms",
            "ii",
            "oo",
            "leakRate",
            "leakError",
            "desiredLength",
            "measuredLength",
            "difference",
            "comments",
        ]
        data = list()
        with open(self.verification_file(key), "r") as f:
            reader = csv.DictReader(f)
            for straw in reader:
                data.append(straw)

        data.append(self.getDataAsDict())  # add new data to existing data
        data = sorted(data, key=self.verificationSort)  # re-sort table

        with open(self.verification_file(key), "w") as f:
            # writer = csv.DictWriter(f,previous_data[0]) # previous_data[0] is the header
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for straw in data:
                writer.writerow(straw)  # rewrite data that was read in

    def removeFromRejects(self, strawID):

        with open(self.verification_file("rejected"), "r") as f:
            reader = csv.DictReader(f)
            reject_data = [straw for straw in reader]

        with open(self.verification_file("rejected"), "w") as f:
            writer = csv.DictWriter(f, reject_data[0].keys())
            writer.writeheader()
            for straw in reject_data:
                if straw["straw"].upper() != strawID.upper():
                    writer.writerow(straw)

    def resetVerified(self):
        for key in self.verified.keys():
            self.verified[key] = False

    def resetData(self):
        self.strawID = ""
        self.position = None  # not a valid position
        self.ii = None
        self.oo = None
        self.leak_rate = None
        self.leak_error = None
        self.desired_length = None
        self.length = None
        self.difference = None
        self.comments = ""

    def strawsLeft(self):
        return (
            len(self.getStraws("storage"))
            - len(self.getStraws("verified"))
            - len(self.getStraws("rejected"))
        )

    def getDataAsDict(self):

        ## Straw ID String
        if self.verifyStrawID(self.strawID):
            strawID = str(self.strawID)
        else:
            strawID = "_______"

        ## Position String
        position = None
        try:
            if int(self.position) in range(0, 95, 2):
                position = format(self.position, "02.0f")
        except ValueError:
            pass
        if position == None:
            position = "__"

        ## WorkerID
        if self.verifyWorkerID():
            workerID = format(self.workerID, "13").upper()
        else:
            workerID = "_______________"

        ## Resistance
        if self.verified["ohms"]:
            res_pass_fail = "PASS"
        else:
            res_pass_fail = "FAIL"
        try:
            ii = format(float(self.ii), "6.2f")
        except ValueError:
            if self.ii:
                ii = self.ii
            else:
                ii = "______"
        except TypeError:
            if self.ii:
                ii = self.ii
            else:
                ii = "______"
        try:
            oo = format(float(self.oo), "6.2f")
        except ValueError:
            if self.oo:
                oo = self.oo
            else:
                oo = "______"
        except TypeError:
            if self.ii:
                oo = self.oo
            else:
                oo = "______"

        ## Leak Rate
        if self.leak_rate == "*missing":
            leak_rate = self.leak_rate
        else:
            try:
                leak_rate = format(self.leak_rate, ".2E")
            except SyntaxError:
                leak_rate = "________"
            except ValueError:
                leak_rate = "________"
            except TypeError:
                leak_rate = "________"

        ## Leak Error
        if self.leak_error == "*missing":
            leak_error = self.leak_error
        else:
            try:
                leak_error = format(self.leak_error, ".2E")
            except SyntaxError:
                leak_error = "________"
            except ValueError:
                leak_error = "________"
            except TypeError:
                leak_error = "________"

        ## Desired Length
        try:
            desired_length = format(self.desired_length, "7.2f")
        except ValueError:
            desired_length = "_______"
        except SyntaxError:
            desired_length = "_______"
        except TypeError:
            desired_length = "_______"

        ## Measured Length
        if self.length == None:
            length = "_______"
        else:
            length = format(self.length, "7.2f")

        ## Length Difference
        if self.difference == None:
            difference = "_____"
        else:
            difference = format(self.difference, "+5.2f")

        new_data_dict = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "straw": strawID,
            "position": position,
            "workers": workerID,
            "ohms": res_pass_fail,
            "ii": ii,
            "oo": oo,
            "leakRate": leak_rate,
            "leakError": leak_error,
            "desiredLength": desired_length,
            "measuredLength": length,
            "difference": difference,
            "comments": "".join(
                [ch for ch in self.comments if ch != ","]
            ).upper(),  # self.comments, but uppercase and without any ","
        }

        return new_data_dict

    def main(self):

        ## Print program header
        for _ in range(50):
            print()
        self.printMu2e()

        ## Make sure RLS measurement device is connected
        if not self.rls.isConnected:
            self.connectRLS()

        print("\nBegin verifying straws currently in storage!")

        ## Get Worker ID
        while not self.verifyWorkerID():
            self.workerID = input("\nPlease scan you worker ID: ").strip().upper()
            if self.verifyWorkerID():
                if not self.getYN(
                    "Double-check. Is " + self.workerID + " your worker ID?"
                ):
                    self.workerID = ""
            else:
                print("Invalid worker ID. Please try again.")
        if not self.workerID:
            quit()

        print("\nWelcome, ", self.workerID, " :)")

        run_program = True

        while run_program:

            self.getAllStraws()
            self.resetVerified()
            self.resetData()

            while (
                True
            ):  # Code-block only gets run once. Breaks as soon as a test fails.

                self.strawID = self.getValidStrawID()

                self.verified[
                    "strawID"
                ] = None  # This is (1) a valid straw ID, (2) that needs to be verified

                for straw in self.verified_straws:
                    if straw.upper() == self.strawID:
                        print(
                            "\nStraw "
                            + self.strawID
                            + " has already been verified! You can put it back in storage."
                        )
                        self.verified["strawID"] = False  # Doesn't need to be tested
                        break

                if self.verified["strawID"] == None:
                    for straw in self.rejected_straws:
                        if straw.upper() == self.strawID:
                            print("\nThis straw is recorded as rejected.")
                            self.verified["strawID"] = self.getYN(
                                "Do you want to test it again?"
                            )
                            break

                if self.verified["strawID"] == None:
                    for straw in self.storage:
                        if straw.upper() == self.strawID:
                            print(
                                "\nI found straw " + str(self.strawID) + " in storage!"
                            )
                            self.verified["strawID"] = True
                            break

                if self.verified["strawID"] == None:
                    print(
                        "\nStraw "
                        + self.strawID
                        + " isn't recorded in the storage file."
                    )
                    self.verified["strawID"] = self.getYN(
                        "Are you SURE that you entered the correct straw ID?"
                    )

                if not self.verified["strawID"]:
                    print("\nFailed straw ID.")
                    break

                # Get position

                self.position = None

                with open(self.verification_file("storage"), "r") as storageFile:
                    storage = csv.DictReader(storageFile)
                    for straw in storage:
                        if straw["straw"].strip().upper() == self.strawID:
                            self.position = int(straw["position"])
                            self.verified["position"] = True

                while self.position == None:
                    pos = input(
                        "\nI couldn't find this straw's position. Please enter it: "
                    ).strip()
                    while True:
                        if pos.isnumeric() and int(pos) in range(0, 95, 2):
                            self.verified["position"] = True
                            break
                        pos = input(
                            "Invalid postion-- must be an even number from 0-94. Try again."
                        )
                    self.position = int(pos)
                    print("(Grab a new position barcode if you need it)")

                print("\nStraw: " + self.strawID)
                print("Position: " + str(self.position))

                # Check for damage
                if self.getYN("Can you see any damage on the straw? "):
                    self.comments += input(
                        "Describe the damage. Press ENTER to submit.\n"
                    ).upper()
                    self.verified["undamaged"] = False
                else:
                    self.verified["undamaged"] = True

                if not self.verified["undamaged"]:
                    break

                if not self.getYN("Are the endpieces properly aligned? "):
                    self.comments += "ENDPIECES MISALIGNED"
                    self.verified["undamaged"] = False
                else:
                    self.verified["undamaged"] = True

                if not self.verified["undamaged"]:
                    break

                # Check resistance data
                ii, oo, pass_fail = self.checkResistanceData(self.strawID)

                self.verified["ohms"] = pass_fail
                self.ii = ii
                self.oo = oo
                print("\nii:  " + str(ii))
                print("oo:  " + str(oo))

                if not pass_fail:
                    print("Failed resistance.")
                    break
                else:
                    print("Passed resistance test!")

                # Check leak data
                self.verified["leak"] = self.checkLeakData(self.strawID)

                print("\nLeak rate: " + str(self.leak_rate))
                print("Error:     " + str(self.leak_error))

                if not self.verified["leak"]:
                    print("\nStraw " + self.strawID + " failed the leak test.")
                    break
                else:
                    print("\nStraw " + self.strawID + " passed the leak test!")

                # Measure length

                print(
                    "\nMeasure the length of the straw using the RLS measurement device."
                )

                self.measureLength()  # Records length and updates self.verified['leng']

                if not self.verified["leng"]:
                    break

                break  # Break out of loop- all tests are done

            # After breaking out of loop, evaluate and record results.

            self.comments += (
                " "
                + input(
                    "\nType any additional comments. Press ENTER to submit:\n"
                ).upper()
            )

            print("Please put the straw back in its tube.")

            # Check for damage again
            if all(self.verified.values()):

                time.sleep(10)  # While user puts straw back

                if self.getYN("Was the straw damaged while testing today?"):
                    self.comments += input(
                        "Describe the damage. Press ENTER to submit."
                    ).upper()
                    self.verified["undamaged"] = False
                else:
                    self.verified["undamaged"] = True

            # Save
            if all(self.verified.values()):

                self.recordVerification("verified")
                print("\nStraw " + self.strawID + " looks good!")
                print("\nPlease put the straw back in its tube and return to storage.")

            else:
                if self.verified["strawID"]:
                    self.recordVerification("rejected")
                    print("\nThis straw did not pass. DO NOT put it back in storage.")

                else:
                    print("No data saved. Couldn't obtain straw ID.")

            print("\nThere are " + str(self.strawsLeft()) + " straws left to verify.")

            run_program = self.getYN("Do you want to test another straw?")


if __name__ == "__main__":
    app = verifyStorageStraw()
    app.main()
