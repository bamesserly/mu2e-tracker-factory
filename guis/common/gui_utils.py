from PyQt5.QtWidgets import QMessageBox
import sys

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
