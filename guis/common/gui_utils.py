from PyQt5.QtWidgets import QMessageBox

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
