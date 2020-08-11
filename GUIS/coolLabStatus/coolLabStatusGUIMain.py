import sys, time, tkinter, tkinter.messagebox # for opening new app, time formatting, popup messages
from coolLabStatusGUI import Ui_MainWindow # for importing UI
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QTableWidget, QGridLayout, QScrollArea, QWidget, QComboBox, QListWidget, QListWidgetItem, QCheckBox, QPushButton, QTableWidgetItem
from PyQt5.QtGui import QBrush
# for GUI widget management^
from PyQt5.QtCore import Qt, QRect, QObject # for gui window management
from datetime import datetime   # for time formatting
import sqlalchemy as sqla   # for interacting with db
import sqlite3  # for connecting with db


class labGUI(QMainWindow):
    def __init__(self, ui_layout):
        # setup UI
        QMainWindow.__init__(self)  # initialize superclass
        self.ui = ui_layout         # make ui member
        ui_layout.setupUi(self)     # apply ui to window
        self.tkRoot = tkinter.Tk()  # make tkinter root for popup messages
        self.tkRoot.withdraw()      # hide root, it's necessary for popups to work, but it's just a blank window otherwise

    # make engine, connection, and metadata objects to interact with database
    def connectToDB(self):

        # override connect to return a read-only DB connection, MUST use path starting at C drive
        # more on this: https://github.com/sqlalchemy/sqlalchemy/issues/4863
        tkinter.messagebox.showinfo(
            title='Connecting',
            message=f'Connecting to network database...'
        )    
        def connectSpecial():
            return sqlite3.connect("file:Z:\Production_Environment\Database\database.db?mode=ro", uri=True)
            #return sqlite3.connect("file:/spa-mu2e-network/Files/Production_Environment/Database/database.db?mode=ro", uri=True)
        self.engine = sqla.create_engine('sqlite://Z:/Production_Environment/Database/database.db', creator=connectSpecial)    # create engine

        # try to use read only mode
        # If the path above is wrong, read-only will fail.  I could see a mergedown or misplaced file easily screwing up the path.
        # If read-only fails, it'll use the regular SQLAlchemy connection.  The regular connection shouldn't write to the DB, but
        # having read-only mode is a good safety net.
        try:
            self.connection = self.engine.connect()     # connect engine with DB
        except:
            tkinter.messagebox.showerror(
                title='Error',
                message=f'Read-only mode failed.  The network is not mapped as the Z drive.  Contact a member of the software team for help.'
            )                                           # show error message
            self.connection = self.engine.connect()     # connect engine with DB

        self.metadata = sqla.MetaData()             # create metadata










if __name__ == "__main__":
    app = QApplication(sys.argv)    # make an app

    window = labGUI(Ui_MainWindow())   # make a window
    window.setWindowTitle("Cool Lab Status GUI")
    window.showMaximized()  # open in maximized window (using show() would open in a smaller one with weird porportions)
    window.connectToDB()

    app.exec_() # run the app!