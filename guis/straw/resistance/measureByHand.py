import logging

logger = logging.getLogger("root")

from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.QtGui import *
from PyQt5.QtCore import pyqtSlot
from guis.straw.resistance.multiMeter import MultiMeter
import time
from pyvisa.errors import VisaIOError


class MeasureByHandPopup(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        # this init fails for some reason :(
        # CLASS VARIABLES#
        self.multiMeter = None

        # Data collection variables
        self.return_meas = float()
        self.return_bool = bool()
        self.ready_to_save = False
        self.trials_collected = 0
        self.eval_expression = None

        # UI DESIGN#

        # Window
        self.resize(300, 180)
        self.setWindowTitle("By-Hand Measurement")

        # Measurement label
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(20, 20, 260, 20))
        self.label.setText("")
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        # LED
        self.led = QtWidgets.QLabel(self)
        self.led.setGeometry(QtCore.QRect(20, 55, 40, 40))
        self.led.setText("")
        self.led.setPixmap(QPixmap("images/white.png"))

        # LineEdit
        self.measurement = QtWidgets.QLineEdit(self)
        self.measurement.setGeometry(QtCore.QRect(80, 60, 200, 30))
        self.measurement.setReadOnly(True)

        # Set Fonts
        font_labels = QtGui.QFont()
        font_labels.setPointSize(10)
        self.label.setFont(font_labels)
        self.measurement.setFont(font_labels)

        # Collect Data Button
        self.button_collectData = QtWidgets.QPushButton(self)
        self.button_collectData.setGeometry(QtCore.QRect(165, 120, 115, 40))
        self.button_collectData.setText("Collect Data")

        # Keep Measurement Button
        self.button_keepMeas = QtWidgets.QPushButton(self)
        self.button_keepMeas.setGeometry(QtCore.QRect(20, 120, 115, 40))
        self.button_keepMeas.setText("Keep Measurement")

        # Set Fonts
        font_buttons = QtGui.QFont()
        font_buttons.setPointSize(12)
        self.label.setFont(font_buttons)
        self.measurement.setFont(font_buttons)

        # Configure Button Group
        self.button_group = QButtonGroup()
        self.button_group.setExclusive(True)
        self.button_group.addButton(self.button_collectData)  # index 0
        self.button_group.addButton(self.button_keepMeas)  # index 1
        self.button_group.buttonClicked.connect(self.evaluateButtonClick)

    def setLabels(self, position, strawID, meas_type_label):
        # Prepares popup to display measurement-specific info (strawID,etc...)
        display_str = "Position " + str(position) + "(" + strawID + ")"
        display_str += meas_type_label + ":"
        self.label.setText(display_str)
        self.button_keepMeas.setEnabled(False)

    def displayData(self, measurement, pass_fail):
        self.measurement.setText(str(measurement))
        if pass_fail:
            self.led.setPixmap(QPixmap("images/green.png"))
        else:
            self.led.setPixmap(QPixmap("images/red.png"))

    def displayProcessing(self):
        self.measurement.setText("")
        self.measurement.setPlaceholderText("processing...")
        self.led.setPixmap(QPixmap("images/yellow.png"))

    def evaluateButtonClick(self, button):

        label = button.text()

        if label == "Collect Data":
            self.displayProcessing()
            self.getMultiMeter()
            meas = self.multiMeter.measure()  # Get meas
            pass_fail = self.eval_expression(meas)  # Evaluate meas
            self.displayData(meas, pass_fail)  # Display meas
            self.return_meas = meas
            self.return_bool = pass_fail
            # self.trials_collected += 1
            self.updateButtons()

        if label == "Keep Measurement":
            self.ready_to_save = True
            self.reject()

    def getMultiMeter(self):
        if self.multiMeter:
            return
        try:
            self.multiMeter = MultiMeter()
        except VisaIOError:
            self.multiMeter = None

    def updateButtons(self):
        self.button_keepMeas.setEnabled(bool(self.return_meas))
        self.button_collectData.setEnabled(bool(self.trials_collected < 5))

    def reset(self):
        # Data values
        self.return_meas = float()
        self.return_bool = bool()
        self.ready_to_save = False
        self.trials_collected = 0
        self.eval_expression = None
        # Display
        self.led.setPixmap(QPixmap("images/white.png"))
        self.measurement.setText("")
        self.measurement.setPlaceholderText("")

    def byHand_main(self, eval_expression):
        # Connect to multimeter
        self.multiMeter = MultiMeter()
        # If this fails, send error message
        if self.multiMeter == None:
            error_message = "Make sure that the multimeter is connected and powered on."
            QMessageBox.about(self, "Connect Multimeter", error_message)
            return None, None
        else:
            #logger.debug("got multiMeter!")
            self.reset()
            #logger.debug("values reset")
            self.eval_expression = (
                eval_expression  # lambda expression for that meas_type
            )
            logger.info("Got a by-hand measurement!")
            self.exec_()  # Display Window
            return self.return_meas, self.return_bool
