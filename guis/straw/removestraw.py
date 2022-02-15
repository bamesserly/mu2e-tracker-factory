import logging

logger = logging.getLogger("root")

import time
import os
import csv
import sys
from datetime import datetime
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from guis.straw.remove import *
from guis.common.getresources import GetProjectPaths
from guis.common.db_classes.straw_location import StrawLocation


class removeStraw(QDialog):
    def __init__(self, webapp=None, parent=None):
        super(removeStraw, self).__init__(parent)
        self.ui = Ui_Dialogw()
        self.ui.setupUi(self)
        self.palletDirectory = GetProjectPaths()["pallets"]
        self.sessionWorkers = []
        self.strawLabels = [
            self.ui.straw_1,
            self.ui.straw_2,
            self.ui.straw_3,
            self.ui.straw_4,
            self.ui.straw_5,
            self.ui.straw_6,
            self.ui.straw_7,
            self.ui.straw_8,
            self.ui.straw_9,
            self.ui.straw_10,
            self.ui.straw_11,
            self.ui.straw_12,
            self.ui.straw_13,
            self.ui.straw_14,
            self.ui.straw_15,
            self.ui.straw_16,
            self.ui.straw_17,
            self.ui.straw_18,
            self.ui.straw_19,
            self.ui.straw_20,
            self.ui.straw_21,
            self.ui.straw_22,
            self.ui.straw_23,
            self.ui.straw_24,
        ]
        self.pfLabels = [
            self.ui.pf_1,
            self.ui.pf_2,
            self.ui.pf_3,
            self.ui.pf_4,
            self.ui.pf_5,
            self.ui.pf_6,
            self.ui.pf_7,
            self.ui.pf_8,
            self.ui.pf_9,
            self.ui.pf_10,
            self.ui.pf_11,
            self.ui.pf_12,
            self.ui.pf_13,
            self.ui.pf_14,
            self.ui.pf_15,
            self.ui.pf_16,
            self.ui.pf_17,
            self.ui.pf_18,
            self.ui.pf_19,
            self.ui.pf_20,
            self.ui.pf_21,
            self.ui.pf_22,
            self.ui.pf_23,
            self.ui.pf_24,
        ]
        self.ui.removeButtons.buttonClicked.connect(self.delete)  # "Remove Straw"
        self.ui.moveButtons.buttonClicked.connect(self.moveStraw)

    def getPallet(self, CPAL):
        lastTask = ""
        straws = []
        passfail = []
        CPALID = -1
        for pid in os.listdir(self.palletDirectory):
            for pallet in os.listdir(self.palletDirectory / pid):
                if CPAL + ".csv" == pallet:
                    CPALID = pid
                    pfile = self.palletDirectory / pid / pallet
                    with open(pfile, "r") as file:
                        dummy = csv.reader(file)
                        history = []
                        for line in dummy:
                            if line != []:
                                history.append(line)
                        lastTask = history[len(history) - 1][1]
                        for entry in range(len(history[len(history) - 1])):
                            if entry > 1 and entry < 50:
                                if entry % 2 == 0:
                                    if history[len(history) - 1][entry] == "_______":
                                        straws.append("Empty")
                                    else:
                                        straws.append(history[len(history) - 1][entry])
                                else:
                                    if history[len(history) - 1][entry] == "P":
                                        passfail.append("Pass")
                                    elif history[len(history) - 1][entry] == "_":
                                        passfail.append("Incomplete")
                                    else:
                                        passfail.append("Fail")
        return CPAL, lastTask, straws, passfail, CPALID

    def displayPallet(self, CPAL, lastTask, straws, passfail):
        for palletid in os.listdir(self.palletDirectory):
            for pallet in os.listdir(self.palletDirectory / palletid):
                if CPAL + ".csv" == pallet:
                    self.ui.palletIDLabel.setText("Pallet ID: " + palletid)
        self.ui.palletLabel.setText("Pallet: " + CPAL)
        steps1 = ["prep", "ohms", "C-O2", "leak", "lasr", "leng", "silv"]
        steps2 = [
            "Straw Prep",
            "Resistance",
            "CO2 End Pieces",
            "Leak Rate",
            "Laser Cut",
            "Length",
            "Silver Epoxy",
        ]
        self.ui.lastLabel.setText("Last Step: " + steps2[steps1.index(lastTask)])
        for pos in range(len(self.strawLabels)):
            self.strawLabels[pos].setText(straws[pos])
        for pos in range(len(self.pfLabels)):
            self.pfLabels[pos].setText(passfail[pos])

    ############################################################################
    # Remove Straw (from pallet)
    ############################################################################
    def delete(self, btn):
        position = int(btn.objectName().strip("remove_")) - 1
        # get pallet info from txt file
        CPAL, lastTask, straws, passfail, CPALID = self.getPallet(
            self.ui.palletLabel.text()[8:]
        )

        if straws[position] == "Empty":
            return
        buttonReply = QMessageBox.question(
            self,
            "Straw Removal Confirmation",
            "Are you sure you want to permanently remove "
            + straws[position]
            + " from "
            + CPAL
            + " ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if buttonReply != QMessageBox.Yes:
            return

        # remove straw from pallet in database
        cpal_number = int("".join(ch for ch in CPAL if ch.isdigit()))
        cpal = StrawLocation.CPAL(cpal_number)
        logger.debug(str(vars(cpal)).split(",")[1:])
        removed_straw_present = cpal.removeStraw(position=position)
        logger.info(f"Removed {removed_straw_present} from {CPAL}")

        # Remove straw from pallet txt file
        for palletid in os.listdir(self.palletDirectory):
            for pallet in os.listdir(self.palletDirectory / palletid):
                if CPAL + ".csv" == pallet:
                    pfile = self.palletDirectory / palletid / pallet
                    with open(pfile, "a") as file:
                        file.write("\n")
                        file.write(datetime.now().strftime("%Y-%m-%d_%H:%M") + ",")
                        file.write(lastTask + ",")
                        for place in range(len(straws)):
                            if place == position:
                                file.write("_______,_,")
                                continue
                            if straws[place] == "Empty":
                                file.write("_______,_,")
                                continue
                            file.write(straws[place] + ",")
                            if passfail[place] == "Pass":
                                file.write("P,")
                            elif passfail[place] == "Incomplete":
                                file.write("_,")
                            else:
                                file.write("F,")
                        i = 0
                        for worker in self.sessionWorkers:
                            file.write(worker)
                            if i != len(self.sessionWorkers) - 1:
                                file.write(",")
                            i = i + 1

        # Get new pallet info from updated txt file
        CPAL, lastTask, straws, passfail, CPALID = self.getPallet(CPAL)
        self.displayPallet(CPAL, lastTask, straws, passfail)

    def moveStraw(self, btn):
        pos = int(btn.objectName().strip("move_")) - 1
        CPAL, lastTask, straws, passfail, CPALID = self.getPallet(
            self.ui.palletLabel.text()[8:]
        )

        if straws[pos] == "Empty":
            return
        items = ("This Pallet", "Another Pallet")
        item, okPressed = QInputDialog.getItem(
            self,
            "Move Straw",
            "Where would you like to this straw to?",
            items,
            0,
            False,
        )

        if not okPressed:
            return

        if item == "This Pallet":
            newpos, okPressed = QInputDialog.getInt(
                self, "Move Straw", "New Straw Position:", pos, 0, 23, 1
            )
            if not okPressed:
                return
            if straws[newpos] != "Empty":
                buttonReply = QMessageBox.question(
                    self,
                    "Move Error",
                    "Position "
                    + str(newpos)
                    + " is already filled by straw "
                    + straws[newpos]
                    + " .",
                    QMessageBox.Ok | QMessageBox.Cancel,
                    QMessageBox.Cancel,
                )
                return
            buttonReply = QMessageBox.question(
                self,
                "Straw Move Confirmation",
                "Are you sure you want to move "
                + straws[pos]
                + " from position "
                + str(pos)
                + " to position "
                + str(newpos)
                + " ?",
                QMessageBox.Ok | QMessageBox.Cancel,
                QMessageBox.Cancel,
            )
            if buttonReply != QMessageBox.Ok:
                return
            for palletid in os.listdir(self.palletDirectory):
                for pallet in os.listdir(self.palletDirectory / palletid):
                    if CPAL + ".csv" == pallet:
                        pfile = self.palletDirectory / palletid / pallet
                        with open(pfile, "a") as file:
                            file.write("\n")
                            file.write(datetime.now().strftime("%Y-%m-%d_%H:%M") + ",")
                            file.write(lastTask + ",")
                            for place in range(len(straws)):
                                if place == pos:
                                    file.write("_______,_,")
                                    continue
                                if place == newpos:
                                    file.write(straws[pos] + ",")
                                    if passfail[pos] == "Pass":
                                        file.write("P,")
                                    elif passfail[pos] == "Incomplete":
                                        file.write("_,")
                                    else:
                                        file.write("F,")
                                    continue
                                if straws[place] == "Empty":
                                    file.write("_______,_,")
                                    continue
                                file.write(straws[place] + ",")
                                if passfail[place] == "Pass":
                                    file.write("P,")
                                elif passfail[place] == "Incomplete":
                                    file.write("_,")
                                else:
                                    file.write("F,")
                            i = 0
                            for worker in self.sessionWorkers:
                                file.write(worker)
                                if i != len(self.sessionWorkers) - 1:
                                    file.write(",")
                                i = i + 1

        if item == "Another Pallet":
            newpal, okPressed = QInputDialog.getText(
                self,
                "Move Straw",
                "Scan the pallet number of the pallet the straw will be moved to:",
                QLineEdit.Normal,
                "",
            )
            if not okPressed:
                return
            newpal, newlastTask, newstraws, newpassfail, CPALID = self.getPallet(newpal)
            if newlastTask != lastTask:
                buttonReply = QMessageBox.question(
                    self,
                    "Move Error",
                    "Pallet "
                    + CPAL
                    + " and pallet "
                    + newpal
                    + " are at different stages of production.",
                    QMessageBox.Ok | QMessageBox.Cancel,
                    QMessageBox.Cancel,
                )
                return
            newpos, okPressed = QInputDialog.getInt(
                self,
                "Move Straw",
                "New Straw Position on " + newpal + ":",
                pos,
                0,
                23,
                1,
            )
            if not okPressed:
                return
            if newstraws[newpos] != "Empty":
                buttonReply = QMessageBox.question(
                    self,
                    "Move Error",
                    "Position "
                    + str(newpos)
                    + " is already filled by straw "
                    + newstraws[newpos]
                    + " .",
                    QMessageBox.Ok | QMessageBox.Cancel,
                    QMessageBox.Cancel,
                )
                return
            for palletid in os.listdir(self.palletDirectory):
                for pallet in os.listdir(self.palletDirectory / palletid):
                    if newpal + ".csv" == pallet:
                        pfile = self.palletDirectory / palletid / pallet
                        with open(pfile, "a") as file:
                            file.write("\n")
                            file.write(datetime.now().strftime("%Y-%m-%d_%H:%M") + ",")
                            file.write("adds,")
                            for place in range(len(newstraws)):
                                if place == newpos:
                                    file.write(straws[pos] + "," + CPAL + ",")
                                else:
                                    file.write("_______,_,")
                            i = 0
                            for worker in self.sessionWorkers:
                                file.write(worker)
                                if i != len(self.sessionWorkers) - 1:
                                    file.write(",")
                                i = i + 1
                            file.write("\n")
                            file.write(datetime.now().strftime("%Y-%m-%d_%H:%M") + ",")
                            file.write(newlastTask + ",")
                            for place in range(len(newstraws)):
                                if place == newpos:
                                    file.write(straws[pos] + ",")
                                    if passfail[pos] == "Pass":
                                        file.write("P,")
                                    elif passfail[pos] == "Incomplete":
                                        file.write("_,")
                                    else:
                                        file.write("F,")
                                    continue
                                if newstraws[place] == "Empty":
                                    file.write("_______,_,")
                                    continue
                                file.write(newstraws[place] + ",")
                                if newpassfail[place] == "Pass":
                                    file.write("P,")
                                elif newpassfail[place] == "Incomplete":
                                    file.write("_,")
                                else:
                                    file.write("F,")
                            i = 0
                            for worker in self.sessionWorkers:
                                file.write(worker)
                                if i != len(self.sessionWorkers) - 1:
                                    file.write(",")
                                i = i + 1

        CPAL, lastTask, straws, passfail, CPALID = self.getPallet(CPAL)
        self.displayPallet(CPAL, lastTask, straws, passfail)
