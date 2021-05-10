6  # Update 10/24/18 - Ben Hiltbrand
# Implemented new credentials system
# Properly checks validity of pallets
# Uploads to Mu2e Hardware database


import pyautogui
import time
import os
import csv
import sys
import threading
from datetime import datetime
from pathlib import Path
from PyQt5.QtCore import QRect, Qt, QTimer, QMetaObject, QCoreApplication
from PyQt5.QtGui import QFont, QPalette, QColor, QBrush
from PyQt5.QtWidgets import (
    QLabel,
    QFrame,
    QStackedWidget,
    QWidget,
    QPushButton,
    QSizePolicy,
    QCheckBox,
    QVBoxLayout,
    QLayout,
    QSpinBox,
    QLineEdit,
    QMainWindow,
    QApplication,
    QComboBox,
    QMessageBox,
)
from guis.straw.silverepoxy.silver import Ui_MainWindow  ## edit via Qt Designer
from guis.straw.remove import Ui_Dialogw
from guis.straw.removestraw import removeStraw
from guis.straw.checkstraw import *
from data.workers.credentials.credentials import Credentials
from guis.common.getresources import GetProjectPaths
from guis.common.save_straw_workers import saveWorkers

pyautogui.FAILSAFE = True  # Move mouse to top left corner to abort script


class Silver(QMainWindow):
    LockGUI = QtCore.pyqtSignal(bool)

    def __init__(self, paths, webapp=None, parent=None):
        super(Silver, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.palletDirectory = paths["pallets"]
        self.workerDirectory = paths["silverworkers"]
        self.silverDirectory = paths["silverdata"]
        self.boardPath = paths["board"]
        self.ui.PortalButtons.buttonClicked.connect(self.Change_worker_ID)
        self.Current_workers = [
            self.ui.Current_worker1,
            self.ui.Current_worker2,
            self.ui.Current_worker3,
            self.ui.Current_worker4,
        ]
        self.portals = [
            self.ui.portal1,
            self.ui.portal2,
            self.ui.portal3,
            self.ui.portal4,
        ]
        self.ui.start.clicked.connect(self.initialData)
        self.ui.finishInsertion.clicked.connect(self.timeUp)
        self.ui.finish.clicked.connect(self.saveData)
        self.ui.viewButton.clicked.connect(self.editPallet)
        self.palletID = ""
        self.palletNum = ""
        self.epoxyBatch = ""
        self.sessionWorkers = []
        self.straws = []
        self.temp = True
        self.ui.sec_disp.setNumDigits(2)
        self.ui.sec_disp.setSegmentStyle(2)
        self.ui.min_disp.setNumDigits(2)
        self.ui.min_disp.setSegmentStyle(2)
        self.ui.hour_disp.setNumDigits(2)
        self.ui.hour_disp.setSegmentStyle(2)
        self.justLogOut = ""
        saveWorkers(self.workerDirectory, self.Current_workers, self.justLogOut)

        self.LockGUI.connect(self.lockGUI)

        self.stationID = "silv"
        self.credentialChecker = Credentials(self.stationID)

        self.lockGUI(False)

        thread = threading.Thread(target=self.main, args=())
        thread.daemon = True
        thread.start()

    def Change_worker_ID(self, btn):
        label = btn.text()
        portalNum = 0
        if label == "Log In":
            portalNum = int(btn.objectName().strip("portal")) - 1
            Current_worker, ok = QInputDialog.getText(
                self, "Worker Log In", "Scan your worker ID:"
            )
            if not ok:
                return
            self.sessionWorkers.append(Current_worker)
            self.Current_workers[portalNum].setText(Current_worker)
            print("Welcome " + self.Current_workers[portalNum].text() + " :)")
            btn.setText("Log Out")
            # self.ui.tabWidget.setCurrentIndex(1)
        elif label == "Log Out":
            portalNum = int(btn.objectName().strip("portal")) - 1
            Current_worker = self.Current_workers[portalNum].text()
            self.justLogOut = self.Current_workers[portalNum].text()
            print("Goodbye " + self.Current_workers[portalNum].text() + " :(")
            self.sessionWorkers.remove(Current_worker)
            Current_worker = ""
            self.Current_workers[portalNum].setText(Current_worker)
            btn.setText("Log In")
        saveWorkers(self.workerDirectory, self.Current_workers, self.justLogOut)
        self.justLogOut = ""

    def checkCredentials(self):
        return self.credentialChecker.checkCredentials(self.sessionWorkers)

    def lockGUI(self, credentials):
        if credentials:
            self.ui.tabWidget.setTabText(1, "Silver Epoxy")
            self.ui.tabWidget.setTabEnabled(1, True)
        else:
            self.ui.tabWidget.setTabText(1, "Silver Epoxy *Locked*")
            self.ui.tabWidget.setTabEnabled(1, False)

    def updateBoard(self):
        status = []
        try:
            with open(self.boardPath + "Progression Status.csv") as readfile:
                data = csv.reader(readfile)
                for row in data:
                    for pallet in row:
                        status.append(pallet)
            status[int(self.palletID[6:]) - 1] == 100
            with open(self.boardPath + "Progression Status.csv", "w") as writefile:
                i = 0
                for pallet in status:
                    writefile.write(pallet)
                    if i != 23:
                        writefile.write(",")
                    i = i + 1
        except IOError:
            print(
                "Could not update board due to board file being accessed concurrently"
            )

    def initialData(self):
        self.palletNum = self.ui.palletNumInput.text()
        self.epoxyBatch = self.ui.epoxyBatchInput.text()

        valid = [True, True, True]

        if (
            not len(self.palletNum) == 8
            or not self.palletNum.startswith("CPAL")
            or not self.palletNum[4:].isnumeric()
        ):
            valid[1] = False

            if self.palletNum == "":
                self.ui.palletNumInput.setStyleSheet(
                    "background-color:rgb(149, 186, 255)"
                )
            else:
                self.ui.palletNumInput.setStyleSheet("background-color:rgb(255, 0, 0)")

        for palletid in os.listdir(self.palletDirectory):
            for pallet in os.listdir(self.palletDirectory / palletid):
                if self.palletNum + ".csv" == pallet:
                    self.palletID = palletid
                    valid[0] = True

        if (
            not len(self.epoxyBatch) == 12
            or not self.epoxyBatch.startswith("SE.")
            or not int(self.epoxyBatch[3:5]) in range(1, 13)
            or not int(self.epoxyBatch[5:7]) in range(1, 32)
            or not int(self.epoxyBatch[7:9])
            in range(17, (datetime.now().year - 2000) + 1)
            or not self.epoxyBatch[-2:].isnumeric()
        ):
            valid[2] = False

            if self.epoxyBatch == "":
                self.ui.epoxyBatchInput.setStyleSheet(
                    "background-color:rgb(149, 186, 255)"
                )
            else:
                self.ui.epoxyBatchInput.setStyleSheet("background-color:rgb(255, 0, 0)")

        if valid[1]:
            self.ui.palletNumInput.setStyleSheet("")
        if valid[2]:
            self.ui.epoxyBatchInput.setStyleSheet("")

        previousSteps = ["prep", "ohms", "C-O2", "leak", "lasr", "leng"]
        check = Check()

        passed = False

        while not passed:
            try:
                check.check(self.palletNum, previousSteps)
                passed = True
            except StrawFailedError as error:
                reply = QMessageBox.critical(
                    self,
                    "Testing Error",
                    "Unable to test this pallet:\n"
                    + error.message
                    + "\n\nRemove failed straws?",
                    QMessageBox.Yes,
                    QMessageBox.No,
                )

                if reply == QMessageBox.Yes:
                    self.editPallet()

                else:
                    self.resetGUI()
                    QMessageBox.critical(
                        self,
                        "Testing Error",
                        "Unable to test this pallet:\n"
                        + error.message
                        + "\n\nPlease remove all failed straws and try again",
                    )
                    break

        if all(valid) and passed:
            self.ui.palletNumInput.setDisabled(True)
            self.ui.epoxyBatchInput.setDisabled(True)
            self.ui.start.setDisabled(True)
            self.ui.viewButton.setEnabled(True)
            self.ui.finishInsertion.setEnabled(True)
            self.stopWatch()

    def stopWatch(self):
        begin = time.time()
        while self.temp:
            running = time.time() - begin
            self.ui.hour_disp.display(int(running / 3600))
            self.ui.min_disp.display(int(running / 60) % 60)
            self.ui.sec_disp.display(int(running) % 60)
            app.processEvents()
            time.sleep(0.1)
        self.temp = True
        self.ui.finishInsertion.setDisabled(True)
        self.ui.finish.setEnabled(True)

    def timeUp(self):
        self.temp = False

    def saveData(self):
        pfile = self.palletDirectory / self.palletID / str(self.palletNum + ".csv")
        if pfile.is_file():
            with open(pfile, "r") as palletFile:
                dummy = csv.reader(palletFile)
                pallet = []
                for line in dummy:
                    pallet.append(line)
                for row in range(len(pallet)):
                    if row == len(pallet) - 1:
                        for entry in range(len(pallet[row])):
                            if entry > 1 and entry < 50:
                                if entry % 2 == 0:
                                    self.straws.append(pallet[row][entry])

            with open(pfile, "a") as palletWrite:
                palletWrite.write("\n")
                palletWrite.write(datetime.now().strftime("%Y-%m-%d_%H:%M") + ",silv,")
                for straw in self.straws:
                    palletWrite.write(straw)

                    if straw != "_______":
                        palletWrite.write(",P,")
                    else:
                        palletWrite.write(",_,")

                palletWrite.write(",".join(self.sessionWorkers))

        sfile = self.silverDirectory / str(self.palletNum + ".csv")
        with open(sfile, "w+") as file:
            header = "Timestamp, Pallet ID, Epoxy Batch #, Endpiece Insertion time (H:M:S), Workers ***NEWLINE***: Comments (optional)\n"
            file.write(header)
            file.write(datetime.now().strftime("%Y-%m-%d_%H:%M") + ",")
            file.write(self.palletID + "," + self.epoxyBatch + ",")
            file.write(
                str(self.ui.hour_disp.intValue())
                + ":"
                + str(self.ui.min_disp.intValue())
                + ":"
                + str(self.ui.sec_disp.intValue())
                + ","
            )
            i = 0
            for worker in self.sessionWorkers:
                file.write(worker)
                if i != len(self.sessionWorkers) - 1:
                    file.write(",")
                i = i + 1
            if self.ui.commentBox.document().toPlainText() != "":
                file.write("\n" + self.ui.commentBox.document().toPlainText())

        reply = QMessageBox.question(
            self,
            "Failed Straws",
            "Were all the insertions successful?",
            QMessageBox.Yes,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.uploadData()
            self.resetGUI()
        else:
            QMessageBox.question(
                self,
                "Pallet cleaned?",
                "Please remove the failed straws.\n The edit pallet menu will pop up next.",
                QMessageBox.Ok,
            )
            self.editPallet()
            self.uploadData()
            self.resetGUI()

    ##        reply = QMessageBox.question(self, "Logout", "Do you want to logout?", QMessageBox.Yes, QMessageBox.No)
    ##
    ##        if reply == QMessageBox.Yes:
    ##            self.logOut()

    def getStraws(self):
        pfile = self.palletDirectory / self.palletID / str(self.palletNum + ".csv")
        with open(pfile, "r") as palletFile:
            dummy = csv.reader(palletFile)
            pallet = []
            for line in dummy:
                pallet.append(line)
            for row in range(len(pallet)):
                if row == len(pallet) - 1:
                    for entry in range(len(pallet[row])):
                        if entry > 1 and entry < 50:
                            if entry % 2 == 0:
                                self.straws.append(pallet[row][entry])

    def resetGUI(self):
        self.palletID = ""
        self.palletNum = ""
        self.epoxyBatch = ""
        self.straws = []
        self.temp = True
        # self.sessionWorkers = []
        self.ui.palletNumInput.setEnabled(True)
        self.ui.epoxyBatchInput.setEnabled(True)
        self.ui.palletNumInput.setText("")
        self.ui.epoxyBatchInput.setText("")
        self.ui.commentBox.document().setPlainText("")
        self.ui.start.setEnabled(True)
        self.ui.hour_disp.display(0)
        self.ui.min_disp.display(0)
        self.ui.sec_disp.display(0)
        self.ui.viewButton.setDisabled(True)
        self.ui.finishInsertion.setDisabled(True)
        self.ui.finish.setDisabled(True)

    def logOut(self):
        for i in range(len(self.Current_workers)):
            if self.Current_workers[i].text() != "":
                self.Change_worker_ID(self.portals[i])

    def editPallet(self):
        rem = removeStraw(self.sessionWorkers)
        rem.palletDirectory = self.palletDirectory
        CPAL, lastTask, straws, passfail = rem.getPallet(self.palletNum)
        rem.displayPallet(CPAL, lastTask, straws, passfail)
        rem.exec_()

    def closeEvent(self, event):
        event.accept()
        sys.exit(0)

    def main(self):
        changed = False
        while True:
            credentials = self.checkCredentials()

            if (credentials and not changed) or (not credentials and changed):
                self.LockGUI.emit(credentials)
                changed = not changed
            time.sleep(0.01)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)
    sys.exit()


def run():
    paths = GetProjectPaths()
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    ctr = Silver(paths)
    ctr.show()
    app.exec_()


if __name__ == "__main__":
    run()
