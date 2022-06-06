import sys, tkinter, tkinter.messagebox, csv, pandas as pd, re, os
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

from guis.dbviewer.csvLoaderUI import Ui_MainWindow  # import raw UI

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


class csvLoader(QMainWindow):

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

        if "Adam" not in os.environ.get('USERNAME'):
            tkinter.messagebox.showwarning(
                title="Warning",
                message="This program is still very much in development, use it with caution."
                )

        # for storing excel sheets as 2D arrays
        # {<sheet name>: [<2D array of values>, <list of column names>]} 
        self.sheets = {}

        # auto load button TODO RENAME IT
        self.ui.pushButton_2.clicked.connect(self.autoLoad)
        # clear button TODO RENAME IT
        self.ui.pushButton.clicked.connect(self.clear)

        # put rows into the submit table
        for i in range(96):
            self.ui.submitTable.insertRow(i)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if len(files) > 1:
            tkinter.messagebox.showerror(
                title="Error",
                message=f"Please only load one file at a time.",
            )
            return
        self.ui.fileLE.setText(f'{files[0]}')
        self.readFile(f'{files[0]}')

    def clear(self):
        self.ui.table.clear()
        self.ui.submitTable.clearContents()
        self.sheets = {}
        self.ui.sheetCB.clear()

    # called at the end of dropEvent()
    # to avoid the absolute ridiculous overcomplexity of data frames...
    #   df.name = gets sheet name
    #   [col for col in df.columns] gets list of column names
    #   (df.values).tolist() gets 2D python array [[row0],[row1],[row2],...]
    #   I HATE NUMPY AND PANDAS
    def readFile(self, file):
        xlFile = pd.ExcelFile(file)
        self.sheets = {}

        for name in xlFile.sheet_names:
            df = pd.read_excel(xlFile, name)
            self.sheets[name] = [(df.values).tolist(), [col for col in df.columns]]
            print(f'----------{name}----------')
            print([namee for namee in df.columns])
            print(df.values)

        self.setupSheetComboBox()
        return

    # called at the end of readFile()
    def setupSheetComboBox(self):
        for key in self.sheets:
            self.ui.sheetCB.addItem(key)

        self.populateDataTable()
        return

    # maybe add name as a parameter, have it display whatever sheet it's told
    def populateDataTable(self):
        # self.sheets[name] = [df.values, [col for col in df.columns]]
        dataList = self.sheets[self.ui.sheetCB.currentText()]
        for col in enumerate(dataList[1]):
            self.ui.table.insertColumn(col[0])

        # figure out header
        usedFirstRow = False
        if (tkinter.messagebox.askquestion (
            'Header',
            f'Does the following look like a header? (Position, current, etc)\n{dataList[1]}',
            icon = 'info'
            )) == 'yes':
            self.ui.table.setHorizontalHeaderLabels(dataList[1])
        else:
            # try first row of data if "header" wasn't really a header
            if (tkinter.messagebox.askquestion (
                'Header',
                f'Does the following look like a header? (Position, current, etc)\n{dataList[0][0]}',
                icon = 'info'
                )) == 'yes':
                    self.ui.table.setHorizontalHeaderLabels(dataList[0][0])
                    usedFirstRow = True
            else:
                tkinter.messagebox.showerror("Well fuck", "-_-")


        self.ui.table.setHorizontalHeaderLabels(dataList[1])
        # for each data point
        for toop in enumerate(dataList[0]):
            # make a new row
            self.ui.table.insertRow(toop[0])
            # then for each index in that point
            for i in enumerate(toop[1]):
                # make a new table item
                newI = QTableWidgetItem(
                    "" if str(toop[1][i[0]]) == "nan" else str(toop[1][i[0]])
                    )
                self.ui.table.setItem(toop[0], i[0], newI)
                
        return

    # autoload button, picks data for the user the best the lowest-tier AI can do
    def autoLoad(self):
        if self.ui.sheetCB.currentText() == "":
            return
        dataList = self.sheets[self.ui.sheetCB.currentText()]

        # search for certain words in the titles of columns and get the index of the column in dataList[1]
        # so if position is in the first (left most) column, then colNames[0] = [0, 'position', 0]
        # [<col in left/input table>, <search item>, <col in right/output table>]
        colNames = [
            [-1, "position",0],
            [-1, "wire", 0],
            [-1, "left", 1],
            [-1, "current", 1], # current not marked as left/right is considered left
            [-1, "right", 2],
            [-1, "voltage", 3],
            #[-1, "1100"],
            #[-1, "1500"],
            [-1, "trip", 4],
            [-1, "time", 5]
        ]
        for toop in colNames:
            for col in enumerate(dataList[1]):
                #if re.search(col[1], toop[1], re.IGNORECASE):
                if (col[1].lower()).find((toop[1].lower())) != -1:
                    toop[0] = col[0]

        #print("!!!!!!!!!!!!!!!!!!!!\n",colNames)
        for col in colNames:
            print(col[1])
            if col[0] > -1:
                print(f"autoloading {col[1]}")
                self.autoLoadColumn(col[0], col[2], dataList[0])

        print(colNames)
        return

    # puts all the data from column <inp> in the left table into column <outp> in the right table
    def autoLoadColumn(self, inp, outp, dataLs):
        tempList = ["" for i in range(len(dataLs))]
        for toop in enumerate(dataLs):
            tempList[toop[0]] = toop[1][inp]

        for i in range(len(dataLs)):
            newI = QTableWidgetItem(str(tempList[i]))
            self.ui.submitTable.setItem(i, outp, newI)

        return
        
        




def run():


    app = QApplication(sys.argv)  # make an app
    app.setStyle(QStyleFactory.create("Fusion"))  # aestetics
    window = csvLoader(Ui_MainWindow())  # make a window

    #window.showMaximized()  # open in maximized window (using show() would open in a smaller one with weird porportions)
    window.show()

    app.exec_()  # run the app!


if __name__ == "__main__":
    run()