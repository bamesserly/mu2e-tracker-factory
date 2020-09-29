import pyautogui
import time
import os
import csv
import sys
from datetime import datetime


class checkLaserCut:
    def __init__(self):
        self.palletDirectory = (
            "\\\\MU2E-CART1\\Users\\Public\\Database Backup\\Pallets\\"
        )
        self.workerDirectory = "\\\\MU2E-CART1\\Users\\Public\\Database Backup\\workers\\straw workers\\CO2 endpiece insertion\\"
        self.epoxyDirectory = (
            "\\\\MU2E-CART1\\Users\\Public\\Database Backup\\CO2 endpiece data\\"
        )
        self.boardPath = (
            "\\\\MU2E-CART1\\Users\\Public\\Database Backup\\Status Board 464\\"
        )
        self.PASS = False

    def strawPass(self, CPAL, straw, step):
        self.PASS = False
        for palletid in os.listdir(self.palletDirectory):
            for pallet in os.listdir(self.palletDirectory + palletid + "\\"):
                if CPAL + ".csv" == pallet:
                    with open(
                        self.palletDirectory + palletid + "\\" + pallet, "r"
                    ) as file:
                        dummy = csv.reader(file)
                        history = []
                        for line in dummy:
                            if line != []:
                                history.append(line)
                        for line in history:
                            if line[1] == step:
                                for index in range(len(line)):
                                    if line[index] == straw and line[index + 1] == "P":
                                        self.PASS = True
                            if line[1] == "adds":
                                for index in range(len(line)):
                                    if line[index] == straw and line[
                                        index + 1
                                    ].startswith("CPAL"):
                                        self.PASS = self.strawPass(
                                            line[index + 1], straw, step
                                        )
                                    if line[index] == straw and line[
                                        index + 1
                                    ].startswith("ST"):
                                        self.PASS = self.strawPass(
                                            CPAL, line[index + 1], step
                                        )
        return self.PASS

    def strawPassAll(self, CPAL, straw):
        self.PASS = False
        results = []
        steps = ["prep", "ohms", "C-O2", "leak", "lasr", "leng", "silv"]
        for step in steps:
            results.append(self.strawPass(CPAL, straw, step))
        if results == []:
            return False
        return all(results)

    def palletPass(self, CPAL, step):
        self.PASS = False
        results = []
        straws = []
        for palletid in os.listdir(self.palletDirectory):
            for pallet in os.listdir(self.palletDirectory + palletid + "\\"):
                if CPAL + ".csv" == pallet:
                    with open(
                        self.palletDirectory + palletid + "\\" + pallet, "r"
                    ) as file:
                        dummy = csv.reader(file)
                        history = []
                        for line in dummy:
                            if line != []:
                                history.append(line)
                        for entry in history[len(history) - 1]:
                            if entry.startswith("ST"):
                                straws.append(entry)
        for straw in straws:
            results.append(self.strawPass(CPAL, straw, step))
        if results == []:
            return False
        return all(results)

    def palletPassAll(self, CPAL):
        self.PASS = False
        results = []
        steps = ["prep", "ohms", "C-O2", "leak", "lasr", "leng", "silv"]
        for step in steps:
            results.append(self.palletPass(CPAL, step))
        if results == []:
            return False
        return all(results)

    def main(self):
        print(self.palletPass("CPAL0000", "ohms"))


if __name__ == "__main__":
    check = checkStraw()
    check.main()
