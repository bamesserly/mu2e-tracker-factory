from PyQt5.QtWidgets import QMessageBox
import sys
import sqlite3
import pandas as pd

import logging

logger = logging.getLogger("root")

"""
generateBox(type, title, text, question = False)

    Description: A function to handle generating error message boxes. A separate function was needed, as the default color scheme
                makes them nearly unreadable. This generates boxes with a white background and black text.

    Parameter: type - A string giving the type of the box to set the appropriate icon (question, warning, or critical)
    Parameter: title - A string giving the desired error box title text
    Parameter: text - A string giving the desired error box text
    Parameter: question - A boolean value that determines if this box asks a question. If it does, the box is given yes and no buttons

    Return: A QMessageBox with the desired input qualities
"""


def generateBox(type, title, text, question=False):
    iconDict = {
        "question": QMessageBox.Question,
        "warning": QMessageBox.Warning,
        "critical": QMessageBox.Critical,
    }
    box = QMessageBox()
    box.setWindowTitle(title)
    box.setText(text)
    box.setIcon(iconDict[type])
    box.setStyleSheet("color: black; background-color: white")

    if question:
        box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

    return box.exec_()


def except_hook(exctype, exception, tb):
    """
    except_hook(exctype, exception, traceback)

    Description: Enables exception handling that is more intuitive. By default, uncaught exceptions
                 cause PyQt GUIs to hang and then display the "Python has encountered and error and
                 needs to close" box. By defining this function (and setting sys.excepthook = except_hook
                 in the main function), uncaught exceptions immediately close the GUI, and display the
                 error message on screen (like a normal python script).

    Parameter: exctype - The class of the uncaught exception
    Parameter: exception - Exception object that went uncaught.
    Parameter: tb - The traceback of the exception that specifies where and why it happened.

    # saw this line in one of the implementations. might want it later.
    #sys.__excepthook__(exctype, exception, tb)
    """
    logger.error("Logging an uncaught exception", exc_info=(exctype, exception, tb))
    sys.exit()
    
    
# getter functions

def get_straw_location_panel(panel):
    con = sqlite3.connect('data/database.db')
    cursor = con.cursor()
    cursor.execute("SELECT * FROM straw_location WHERE number='"+str(panel)+"' AND location_type='MN'")  
    output = str(cursor.fetchall()[0][0])
    con.close()
    
    return output
    
def get_procedure_from_location(straw_location, procedure):
    con = sqlite3.connect('data/database.db')
    cursor = con.cursor()
    cursor.execute("SELECT * FROM procedure WHERE straw_location='"+straw_location+"' AND station='"+procedure+"'")
    output = str(cursor.fetchall()[0][0])
    con.close()
    
    return output
    
def get_trial(procedure, tag):
    con = sqlite3.connect('data/database.db')
    cursor = con.cursor()
    cursor.execute("SELECT * FROM panel_leak_test_details WHERE procedure='"+procedure+"' AND tag='"+tag+"'")
    output = str(cursor.fetchall()[0][0])
    con.close()
    
    return output
    
# get panel leak data as pandas df
def get_panel_leak_df(trial):
    con = sqlite3.connect('data/database.db')
    cursor = con.cursor()
    leak_df = pd.read_sql_query("SELECT * FROM measurement_panel_leak WHERE trial='"+trial+"'", con)
    return leak_df
    
    
################################################################################
# returns a list of leak test tags for an inputted panel
################################################################################

def get_leak_tags(panel):
    tag_list = []
    con = sqlite3.connect('data/database.db')
    cursor = con.cursor()
    
    # acquire straw location
    cursor.execute("SELECT * FROM straw_location WHERE number='"+str(panel)+"' AND location_type='MN'")
    straw_location = str(cursor.fetchall()[0][0])

    # use straw location to acquire procedure
    cursor.execute("SELECT * FROM procedure WHERE straw_location='"+straw_location+"' AND station='pan8'")
    result = cursor.fetchall()
    if len(result) > 0:
        procedure = str(result[0][0])
        
        # use procedure and tag to acquire trial
        cursor.execute("SELECT * FROM panel_leak_test_details WHERE procedure='"+procedure+"'")
        raw_list = cursor.fetchall()

        for i in raw_list: # sort out tags from raw_list and put in list to return
            tag_list.append(str(i[2]))
    
    return tag_list
    
    
    
    
    
    
    
    
    
    
    
