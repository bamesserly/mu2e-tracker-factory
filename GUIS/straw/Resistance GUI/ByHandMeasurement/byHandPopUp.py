# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'byhandmeasurement.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_byHandMeasurement(object):
    def setupUi(self, byHandMeasurement):
        byHandMeasurement.setObjectName("byHandMeasurement")
        byHandMeasurement.resize(300, 180)
        
        self.byHand_led = QtWidgets.QLabel(byHandMeasurement)
        self.byHand_led.setGeometry(QtCore.QRect(20, 55, 40, 40))
        self.byHand_led.setText("")
        self.byHand_led.setObjectName("byHand_led")
        
        self.byHand_measurement = QtWidgets.QLineEdit(byHandMeasurement)
        self.byHand_measurement.setGeometry(QtCore.QRect(80, 60, 200, 30))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.byHand_measurement.setFont(font)
        self.byHand_measurement.setText("")
        self.byHand_measurement.setObjectName("byHand_measurement")
        
        self.button_nextStraw = QtWidgets.QPushButton(byHandMeasurement)
        self.button_nextStraw.setGeometry(QtCore.QRect(20, 120, 115, 40))
        self.button_nextStraw.setObjectName("button_nextStraw")
        
        self.button_tryAgain = QtWidgets.QPushButton(byHandMeasurement)
        self.button_tryAgain.setGeometry(QtCore.QRect(165, 120, 115, 40))
        self.button_tryAgain.setObjectName("button_tryAgain")
        
        self.byHand_label = QtWidgets.QLabel(byHandMeasurement)
        self.byHand_label.setGeometry(QtCore.QRect(20, 20, 260, 20))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.byHand_label.setFont(font)
        self.byHand_label.setText("")
        self.byHand_label.setAlignment(QtCore.Qt.AlignCenter)
        self.byHand_label.setObjectName("byHand_label")

        self.retranslateUi(byHandMeasurement)
        QtCore.QMetaObject.connectSlotsByName(byHandMeasurement)

    def retranslateUi(self, byHandMeasurement):
        _translate = QtCore.QCoreApplication.translate
        byHandMeasurement.setWindowTitle(_translate("byHandMeasurement", "byHandMeasurement"))
        self.button_nextStraw.setText(_translate("byHandMeasurement", "Next Straw"))
        self.button_tryAgain.setText(_translate("byHandMeasurement", "Try Again"))

