import pyautogui
import time
import os
import csv
import sys
from guis.common.getresources import GetProjectPaths
from pathlib import Path


def GetLastLineOfFile(file):
    # Files are only few lines, so OK to read like this
    with open(file, "r") as f:
        last_line = f.readlines()[-1]
    return last_line


class StrawFailedError(Exception):
    # Raised when attempting to test a straw that has failed a previous step, but was not removed
    def __init__(self, message):
        super().__init__(self, message)
        self.message = message


class Check:
    def __init__(self):
        self.palletDirectory = GetProjectPaths()["pallets"]

    def findPalletFiles(self, CPAL):
        pfiles = []
        for file in Path(self.palletDirectory).rglob("*"):
            if file.is_file() and file.suffix == ".csv" and file.stem == CPAL:
                pfiles.append(file)
        return pfiles

    def strawPass(self, CPAL, straw, step):
        PASS = False
        for pfile in self.findPalletFiles(CPAL):
            # get the file contents
            history = []
            with open(pfile, "r") as file:
                dummy = csv.reader(file)
                for line in dummy:
                    if line != []:
                        history.append(line)

            for line in history:
                # find the line corresponding to this step
                if line[1].lower() == step.lower():
                    # find the straw, and check the character right after it
                    for index in range(len(line)):
                        if line[index] == straw and line[index + 1] == "P":
                            PASS = True
                # IDK what this is
                if line[1] == "adds":
                    for index in range(len(line)):
                        if line[index] == straw and line[index + 1].startswith("CPAL"):
                            PASS = self.strawPass(line[index + 1], straw, step)
                        if line[index] == straw and line[index + 1].startswith("ST"):
                            PASS = self.strawPass(CPAL, line[index + 1], step)

        return PASS

    def strawPassAll(self, CPAL, straw):
        PASS = False
        results = []
        steps = ["prep", "ohms", "C-O2", "leak", "lasr", "leng", "silv"]
        for step in steps:
            results.append(self.strawPass(CPAL, straw, step))
        if results == []:
            return False
        return all(results)

    def palletPass(self, CPAL, step):
        PASS = False
        results = []
        straws = []
        straws2 = []

        # get all straws
        straws.extend(
            [
                e
                for e in GetLastLineOfFile(pfile).split(",")
                if e.upper().startswith("ST")
            ]
        )

        # get entire file contents
        for pfile in self.findPalletFiles(CPAL):
            history = []
            with open(pfile, "r") as file:
                dummy = csv.reader(file)
                for line in dummy:
                    if line != []:
                        history.append(line)

        assert straws == straws2

        # check each straw
        # TODO this is so bad: it opens the same file for every one of these
        # straws. SO slow.
        for straw in straws:
            results.append(self.strawPass(CPAL, straw, step))
        if results == []:
            return False
        return all(results)

    def palletPassAll(self, CPAL):
        PASS = False
        results = []
        steps = ["prep", "ohms", "C-O2", "leak", "lasr", "leng", "silv"]
        for step in steps:
            results.append(self.palletPass(CPAL, step))
        if results == []:
            return False
        return all(results)

    def check(self, CPAL, steps):
        results = [self.palletPass(CPAL, s) for s in steps]
        steps1 = [
            "made",
            "prep",
            "ohms",
            "C-O2",
            "infl",
            "leak",
            "lasr",
            "leng",
            "silv",
        ]
        steps2 = [
            "Straw Made",
            "Straw Prep",
            "Resistance Test",
            "CO2 End Piece Epoxy",
            "Inflation",
            "Leak Test",
            "Laser Cut",
            "Length Measurement",
            "Silver Epoxy",
        ]

        steps_dict = {}

        for index, step in enumerate(steps1):
            steps_dict[step] = steps2[index]

        if all(results):
            return
        else:
            failed = []
            for i, step in enumerate(steps):
                if not results[i]:
                    failed.append(step)
            names = list(map(lambda x: steps_dict[x], failed))
            raise StrawFailedError(CPAL + " failed step(s): " + ", ".join(names))
