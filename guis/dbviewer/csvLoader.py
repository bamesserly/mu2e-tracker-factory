import sys, tkinter, tkinter.messagebox, csv, pandas as pd
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

        # for storing excel sheets as data frames
        self.sheets = {}

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

    # called at the end of dropEvent()
    def readFile(self, file):
        xlFile = pd.ExcelFile(file)
        self.sheets = {}

        for name in xlFile.sheet_names:
            df = pd.read_excel(xlFile, name)
            self.sheets[name] = df

        self.setupSheetComboBox()
        return

    # called at the end of readFile()
    def setupSheetComboBox(self):
        for key in self.sheets:
            self.ui.sheetCB.addItem(key)

        self.populateDataTable()
        return

    def populateDataTable(self):
        
        return

    #def populateDataTable(self):
    #    shCopy = self.sheets[self.ui.sheetCB.currentText()]
    #    for col in enumerate(shCopy.columns):
    #        self.ui.table.insertColumn(col[0])

    #    header = [col for col in shCopy.columns]
    #    if (tkinter.messagebox.askquestion (
    #        'Header',
    #        f'Does the following look like a header? (Position, current, etc)\n{header}',
    #        icon = 'info'
    #        )) == 'yes':
    #        self.ui.table.setHorizontalHeaderLabels(header)
    #    else:
    #        header = shCopy.iloc[0].values.flatten().tolist()
    #        print(header)
    #        self.ui.table.setHorizontalHeaderLabels(header)
    #        shCopy = shCopy.iloc[1: , :]


    #    shCopy = shCopy.reset_index()
    #    for index, row in shCopy.iterrows():
    #        self.ui.table.insertRow(index)
    #        for col in enumerate(shCopy.columns):
    #            i = shCopy[col[1]].values[index]
    #            #print(i)
    #            newI = QTableWidgetItem(str(i))
    #            self.ui.table.setItem(index,col[0],newI)

    #    print(shCopy.index)
    #    return




def run():
    app = QApplication(sys.argv)  # make an app
    app.setStyle(QStyleFactory.create("Fusion"))  # aestetics
    window = csvLoader(Ui_MainWindow())  # make a window

    #window.showMaximized()  # open in maximized window (using show() would open in a smaller one with weird porportions)
    window.show()

    app.exec_()  # run the app!


if __name__ == "__main__":
    run()