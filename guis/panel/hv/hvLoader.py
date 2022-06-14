import sys, tkinter, tkinter.messagebox, csv, pandas as pd, re, os, random
#pip install openpyxl
#pip install xlrd==1.2.0


from PyQt5.QtWidgets import (
    QApplication,
    QListWidgetItem,
    QTableWidgetItem,
    QMainWindow,
    QLabel,
    QMessageBox,
    QStyleFactory,
)

# mostly for gui window management, QPen and QSize are for plotting
from PyQt5.QtGui import QBrush, QIcon, QPen
from PyQt5.QtCore import Qt, QPointF

import sqlalchemy as sqla  # for interacting with db
import sqlite3  # for connecting with db

from guis.common.getresources import GetProjectPaths, GetLocalDatabasePath

from guis.panel.hv.hvLoaderUI import Ui_MainWindow  # import raw UI
from guis.common.panguilogger import SetupPANGUILogger

import logging

logger = logging.getLogger("root")

'''
Reminder: these are the columns that we need to submit
 procedure     INTEGER NOT NULL
 position      INTEGER NOT NULL, (a number 0-96)
 current_left  REAL,
 current_right REAL, (right or left may be specified. If not, choose left).
 voltage       REAL, (either 1500 or 1100, or NULL)
 is_tripped    BOOLEAN DEFAULT (either 0 (false) or 1 (true))
 timestamp     INTEGER ("epoch" time (msec, sec), if no time avail, use file create datetime).
'''

# the same as int() but returns None or '' as 0
def intx(i):
    try:
        retval = int(i)
    except:
        retval = 0
    return retval



class hvLoader(QMainWindow):

    def __init__(self, ui_layout):
        # initialize superclass
        QMainWindow.__init__(self)
        # make ui member
        self.ui = ui_layout
        # apply ui to window
        ui_layout.setupUi(self)
        self.setAcceptDrops(True)

        # make tkinter root for popup messages
        self.tkRoot = tkinter.Tk()
        self.tkRoot.withdraw()

        self.dataArr = []
        self.panelNum = -1
        self.panelPro = -1
        self.fileNum = -1

        # clear button TODO RENAME IT
        self.ui.pushButton.clicked.connect(self.clear)
        self.ui.submitToDbPB.clicked.connect(self.submitData)

        self.connectToDB()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if self.ui.fileLE.text() != "":
            tkinter.messagebox.showerror(
                title="Error",
                message=f"A file is already loaded!  Please clear it if you wish to load another.",
            )
            return

        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if len(files) > 1:
            tkinter.messagebox.showerror(
                title="Error",
                message=f"Please only load one file at a time.",
            )
            return
        self.ui.fileLE.setText(f'{files[0]}')
        logger.info(f'File {files[0]} dropped in.')
        self.loadCSV(f'{files[0]}')

    def clear(self):
        self.ui.table.clear()
        self.ui.table.setRowCount(0)
        self.ui.table.setHorizontalHeaderLabels(
            [
                "position",
                "current_left",
                "current_right",
                "voltage",
                "is_tripped",
                "timestamp"
            ]
        )
        self.dataArr = []
        self.panelNum = -1
        self.panelPro = -1
        self.fileNum = -1
        self.ui.fileLE.clear()

    def connectToDB(self):
        db = GetLocalDatabasePath()
        self.engine = sqla.create_engine("sqlite:///"+db)
        self.connection = self.engine.connect()

        # Given a panel and process, access the DB to get the procedure ID
    def getProcedureID(self, panel, process):
        try:
            assert isinstance(panel, int) and panel <= 999
            assert process in range(1,9)
        except AssertionError:
            tkinter.messagebox.showerror(
                "Not Found",
                f'The procedure {process} could not be found for panel MN{panel}.'
            )
            logger.error(f'The procedure {process} could not be found for panel MN{panel}.')
            return -1

        query = f"""
        SELECT procedure.id from procedure
        INNER JOIN straw_location on procedure.straw_location = straw_location.id
        WHERE straw_location.location_type = "MN"
        AND straw_location.number = {panel}
        AND procedure.station = "pan{process}"
        """
        result = self.connection.execute(query)
        try:
            result = result.first()[0]
        except:
            tkinter.messagebox.showerror(
                "Not Found",
                f'The procedure {process} could not be found for panel MN{panel}.'
            )
            logger.error(f'The procedure {process} could not be found for panel MN{panel}.')
            return -1
        return result


    # loads the contents of the CSV into self.dataArr
    # doesn't handle parsing of data to the table
    def loadCSV(self, file):
        filename = file[-16:]
        logger.info(f'Loading {filename} into csvLoader...')
        self.panelNum = int(filename[2:5])
        self.panelPro = int(filename[9:10])
        self.fileNum = int(filename[11:12])
        self.ui.fileLE.setText(str(file))

        if self.panelPro not in [3,4,5,6]:
            tkinter.messagebox.showwarning(
                "Incorrect file name format.",
                f'The panel procedure must be 3, 4, 5, or 6.  The file you submitted provided "{self.panelPro}".'
            )
            logger.error(f'Unable to load file {file}.')
            self.clear()
            return

        if self.panelNum not in range(1,301):
            tkinter.messagebox.showwarning(
                "Incorrect file name format.",
                f'The panel number must be between 1 and 300.  The file you submitted provided "{self.panelNum}".'
            )
            logger.error(f'Unable to load file {file}.')
            self.clear()
            return


        with open(file) as file:
            reader = csv.reader(file)
            
            for row in reader:
                self.dataArr += [row]

        self.parseCSV()
        return

    def parseCSV(self):
        # column & row index
        # row starts at 1 to skip header
        #cI = 0
        rI = 1

        # get voltage - there must be an easier way than this...
        voltsLst = [i for i in self.dataArr[0][0] if i.isdigit()]
        volts = ""
        for i in voltsLst:
            volts += i

        # anything tripped?
        tripped = len(self.dataArr[0]) == 5


        for i in range(len(self.dataArr)-1):
            self.ui.table.insertRow(i)
        
        while rI < len(self.dataArr):

            for cI in range(6 if tripped else 5):
                # position or current
                if cI <3 :  # <3 <3 <3
                    newItem = QTableWidgetItem(str(self.dataArr[rI][cI]))
                    self.ui.table.setItem(rI-1,cI,newItem)
                # voltage
                elif cI == 3:
                    newItem = QTableWidgetItem(str(volts))
                    self.ui.table.setItem(rI-1,cI,newItem)
                # trip status or timestamp if not tripped
                elif cI == 4:
                    if tripped:
                        newItem = QTableWidgetItem(str(self.dataArr[rI][3]))
                        self.ui.table.setItem(rI-1,cI,newItem)
                    else:
                        newItem = QTableWidgetItem("0")
                        self.ui.table.setItem(rI-1,cI,newItem)
                        newItem = QTableWidgetItem(
                        str(self.dataArr[rI][int(4 if tripped else 3)])
                        )
                        self.ui.table.setItem(rI-1,cI+1,newItem)
                # timestamp if tripped
                else:
                    newItem = QTableWidgetItem(
                        str(self.dataArr[rI][int(4 if tripped else 3)])
                        )
                    self.ui.table.setItem(rI-1,cI,newItem)
            rI += 1

        self.ui.submitToDbPB.setEnabled(True)

    def submitData(self):

        logger.info(f'Attempting to submit {len(self.dataArr)-1} data points for MN{self.panelNum}, procedure {self.panelPro}')
        
        query = """
        INSERT OR IGNORE INTO measurement_pan5 (id, procedure, position, current_left, current_right, voltage, is_tripped, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """

        # anything tripped?
        tripped = len(self.dataArr[0]) == 5

        # get voltage - there must be an easier way than this...
        voltsLst = [i for i in self.dataArr[0][0] if i.isdigit()]
        volts = ""
        for i in voltsLst:
            volts += i

        # check voltage validity
        if int(volts) != 1100 and int(volts) != 1500:
            tkinter.messagebox.showwarning(
                "Unable to submit",
                f'Data could not be submitted due to invalid voltage: {volts}'
            )
            logger.error(f'Unable to submit.  Reason: Invalid voltage {volts}')
            return

        # get procedure ID
        proID = self.getProcedureID(self.panelNum, self.panelPro)

        # check procedure ID validity
        if proID < 1560000000000000:
            tkinter.messagebox.showwarning(
                "Unable to submit",
                f'Data could not be submitted due to invalid procudure ID: {proID}'
            )
            logger.error(f'Unable to submit.  Reason: Invalid procedure ID {proID}')
            return

        toCommit = [
            (
                int(i[4 if tripped else 3]) + int(self.panelNum)*13 + int(self.panelPro)*688 + int(i[0])*(self.fileNum+1) + intx(i[1]) + intx(i[2]),
                proID,
                i[0],
                i[1],
                i[2],
                volts,
                i[3] if tripped else False,
                i[4 if tripped else 3]
            )
            for i in self.dataArr[1:]
        ]

        try:
            r_set = self.connection.execute(query, toCommit)
        except sqla.exc.OperationalError as e:
            logger.error(e)
            error = str(e.__dict__["orig"])
            logger.error(error)
            logger.error(
                "Unable to submit.  Reason: Operational Error."
            )
        except sqla.exc.IntegrityError as e:
            logger.error(e)
            error = str(e.__dict__["orig"])
            logger.error(error)
            logger.error(
                "Unable to submit.  Reason: Integrity error, an identical data point was already in the DB."
            )
        else:
            logger.info(f'Successfully loaded {len(self.dataArr)-1} data points into the local DB.')
            tkinter.messagebox.showinfo(
                "Success!",
                f'Successfully loaded {len(self.dataArr)-1} data points into the local DB.  The data will now be cleared from this program.'
            )
            self.clear()
        return
        




def run():


    app = QApplication(sys.argv)  # make an app
    app.setStyle(QStyleFactory.create("Fusion"))  # aestetics
    window = hvLoader(Ui_MainWindow())  # make a window

    #window.showMaximized()  # open in maximized window (using show() would open in a smaller one with weird porportions)
    window.show()

    app.exec_()  # run the app!


if __name__ == "__main__":
    logger = SetupPANGUILogger("root", "csvLoader")
    run()