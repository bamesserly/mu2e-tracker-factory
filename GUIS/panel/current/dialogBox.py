"""
This file defines a custom DialogBox class for use in the main panel GUI to
pause the day. A custom class was needed to add custom elements to the box.

Author(s): Ben Hiltbrand
Date of Last Update: 3/20/19
"""

import time
from datetime import datetime
from PyQt5 import QtCore, QtGui, QtWidgets
from datetime import datetime


class DialogBox(QtWidgets.QDialog):
    """
    __init__(Self, workers = [], parent=None)

    Description: Class constructor that sets up some class variables and the dialog box itself. The dialog box
                 is constructed with flags set so that the title bar help button is not there. The dialog
                 box is application modal, meaning no input to the GUI is allowed through when this dialog box
                 is open.

    Parameter: workers - String list giving the worker IDs of all the workers currently working on the panel
    Parameter: parent - QWidget giving the parent widget for this dialog box
    """

    def __init__(self, workers=[], parent=None):
        super(DialogBox, self).__init__(
            parent, QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint
        )
        self.setStyleSheet("color: black; background-color: white")

        self.pauseWorker = ""
        self.workers = workers
        self.workerButtons = []

        self.labels = []

        self.paused = False

        self.setWindowTitle("Pause Panel GUI")
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )

        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        # self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)

        self.setupTitle(0, "Paused by:")
        self.setupLayout()
        self.setupWorkerButtons()
        self.setupTitle(1, "Reason:")
        self.setupPlainTextEdit()
        self.setupPromptButtons()

        self.setModal(True)

    """
    createButtons(self)

    Description: Function used to create the QPushButtons used to control this dialog box. This includes
                 the pause, cancel, resume, and close GUI buttons.
    """

    def createButtons(self):
        self.pauseButton = QtWidgets.QPushButton()
        self.pauseButton.setText("Pause")
        self.pauseButton.setDisabled(True)
        self.pauseButton.clicked.connect(lambda: self.changeButtons(False))
        self.pauseButton.clicked.connect(lambda: self.setPaused(True))

        self.cancelButton = QtWidgets.QPushButton()
        self.cancelButton.setText("Cancel")
        self.cancelButton.clicked.connect(self.close)

        self.resumeButton = QtWidgets.QPushButton()
        self.resumeButton.setText("Resume")

        self.closeButton = QtWidgets.QPushButton()
        self.closeButton.setText("Close GUI")

    """
    setupTitle(self, number, text)

    Description: Function used to generate a QLabel used as a title on the dialog box.

    Parameter: number - Integer specifying the count of labels on the box (not including this one)
    Parameter: text - String specifying the label text
    """

    def setupTitle(self, number, text):
        horizontalLayout = QtWidgets.QHBoxLayout()
        horizontalLayout.setObjectName(f"hLayout_{number}")

        label = QtWidgets.QLabel()
        label.setObjectName(f"label{number}")
        label.setText(text)

        font = QtGui.QFont()
        font.setPointSize(12)

        label.setFont(font)

        self.labels.append(label)
        self.verticalLayout.addWidget(
            label,
            0,
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter,
        )

    """
    setupPlainTextEdit(self)

    Description: Sets up the comment box.
    """

    def setupPlainTextEdit(self):
        self.commentBox = QtWidgets.QPlainTextEdit(self)
        self.commentBox.setPlaceholderText("Enter comment")
        self.commentBox.setObjectName("commentBox")
        self.commentBox.setDisabled(True)
        self.commentBox.textChanged.connect(self.enablePauseButton)
        self.verticalLayout.addWidget(self.commentBox)

    """
    setupLayout(self)

    Description: Sets up the grid layout used for worker buttons to give them a nice presentation.
    """

    def setupLayout(self):
        self.gridLayoutWidget = QtWidgets.QWidget()
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.buttonLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.buttonLayout.setContentsMargins(0, 0, 0, 0)
        self.buttonLayout.setObjectName("buttonLayout")
        self.verticalLayout.addWidget(self.gridLayoutWidget)

    """
    setupWorkerButtons(self)

    Description: Sets up the worker buttons. These buttons tell who paused the GUI. The number of
                 buttons and their text is generated dynamically, depending on the number of workers.
    """

    def setupWorkerButtons(self):
        for i, worker in enumerate(self.workers):
            btn = QtWidgets.QPushButton(self.gridLayoutWidget)
            btn.setText(worker)
            btn.clicked.connect(lambda index=i: self.disableWorkerButtons(index))
            self.workerButtons.append(btn)
            self.buttonLayout.addWidget(btn, int(i / 2), i % 2, 1, 1)

        self.gridLayoutWidget.setLayout(self.buttonLayout)

    """
    setupPromptButtons(self)

    Description: Sets up the prompt buttons at the bottom of the dialog box. This includes
                 the pause, cancel, resume, and close GUI buttons.
    """

    def setupPromptButtons(self):
        self.createButtons()
        self.promptButtons = QtWidgets.QDialogButtonBox(self)
        self.promptButtons.addButton(
            self.pauseButton, QtWidgets.QDialogButtonBox.YesRole
        )
        self.promptButtons.addButton(
            self.cancelButton, QtWidgets.QDialogButtonBox.NoRole
        )
        self.promptButtons.addButton(
            self.resumeButton, QtWidgets.QDialogButtonBox.YesRole
        )
        self.promptButtons.addButton(
            self.closeButton, QtWidgets.QDialogButtonBox.NoRole
        )
        self.resumeButton.hide()
        self.closeButton.hide()
        self.verticalLayout.addWidget(self.promptButtons)
        # self.promptButtons.removeButton()

    """
    setWorkers(self, workers)

    Description: Sets the workers for the dialog box to workers.

    Parameter: workers - String list of worker IDs of workers currently working.
    """

    def setWorkers(self, workers):
        self.workers = workers

    """
    setPaused(self, paused)

    Description: Sets the "paused" flag to the value specified.

    Parameter: paused - Boolean value specifying whether the GUI has been paused or not
    """

    def setPaused(self, paused):
        self.paused = paused

    """
    getComment(self)

    Description: Gets the comment input into the comment box. Used to save comment to comment file.

    Returns: String of the comment input into the comment box.
    """

    def getComment(self):
        return self.commentBox.toPlainText()

    """
    changeButtons(self, default = True)

    Description: Changes the prompt buttons to one of the two configurations. Either "pause" and "cancel"
                 or "resume" and "close GUI".
    
    Parameter: default - Boolean value specifying whether to use the default configuration of "pause" and "cancel"
    """

    def changeButtons(self, default=True):
        if default:
            self.resumeButton.hide()
            self.closeButton.hide()
            self.pauseButton.show()
            self.cancelButton.show()
        else:
            self.pauseButton.hide()
            self.cancelButton.hide()
            self.resumeButton.show()
            self.closeButton.show()

        self.commentBox.setReadOnly(True)

    """
    connectClose(self, function)

    Description: Connects the clicked signal for the close button to the specified function.

    Parameter: function - A function name binding, will be called when the close button is clicked.
    """

    def connectClose(self, function):
        self.closeButton.clicked.connect(function)

    """
    connectResume(self, function)

    Description: Connects the clicked signal for the resume button to the specified function.

    Parameter: function - A function name binding, will be called when the resume button is clicked.
    """

    def connectResume(self, function):
        self.resumeButton.clicked.connect(function)

    """
    connectPause(self, function)

    Description: Connects the clicked signal for the pause button to the specified function.

    Parameter: function - A function name binding, will be called when the pause button is clicked.
    """

    def connectPause(self, function):
        self.pauseButton.clicked.connect(function)

    """
    disableWorkerButtons(self, index)

    Description: Hides and disables worker buttons after one button has been clicked. This ensures
                 the worker who paused the GUI is always known on the window. The worker button clicked
                 is disabled, while all others are hid. Also enables the comment box.
    
    Parameter: index - Integer specifying which worker button was clicked.
    """

    def disableWorkerButtons(self, index):
        for i, btn in enumerate(self.workerButtons):
            if i == index:
                btn.setDisabled(True)
                self.pauseWorker = btn.text()
            else:
                btn.hide()

        self.commentBox.setDisabled(False)

    """
    enablePauseButton(self)

    Description: Function to handle enabling the pause button. By default, it starts disabled, and should
                 only be enabled when a worker has been selected, and a comment has been input. To enable
                 the pause button, the comment box is required to not be blank, and not be only whitespace.
    """

    def enablePauseButton(self):
        if (
            self.commentBox.toPlainText() != ""
            and not self.commentBox.toPlainText().isspace()
        ):
            self.pauseButton.setDisabled(False)
        else:
            self.pauseButton.setDisabled(True)

    """
    closeEvent(self, event)

    Description: Function called when dialog box is being asked to close (through clicking the red X, for example).
                 If the GUI is paused, this is prevented, otherwise the dialog box is closed.

    Parameter: event - The event calling this function.
    """

    def closeEvent(self, event):
        if self.paused:
            event.ignore()
        else:
            event.accept()
