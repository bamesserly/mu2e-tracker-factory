# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'WORKER.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialogw(object):
    def setupUi(self, Dialogw):
        Dialogw.setObjectName("Dialogw")
        Dialogw.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialogw.resize(172, 115)
        Dialogw.setAutoFillBackground(True)
        Dialogw.setStyleSheet("")
        self.label = QtWidgets.QLabel(Dialogw)
        self.label.setGeometry(QtCore.QRect(20, 20, 121, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.lineEdit = QtWidgets.QLineEdit(Dialogw)
        self.lineEdit.setGeometry(QtCore.QRect(20, 40, 131, 20))
        self.lineEdit.setMaxLength(7)
        self.lineEdit.setObjectName("lineEdit")
        self.okayButton = QtWidgets.QPushButton(Dialogw)
        self.okayButton.setGeometry(QtCore.QRect(20, 70, 61, 23))
        self.okayButton.setDefault(True)
        self.okayButton.setObjectName("okayButton")
        self.cancelButton = QtWidgets.QPushButton(Dialogw)
        self.cancelButton.setGeometry(QtCore.QRect(90, 70, 61, 23))
        self.cancelButton.setObjectName("cancelButton")

        self.retranslateUi(Dialogw)
        self.cancelButton.clicked.connect(Dialogw.deleteLater)
        QtCore.QMetaObject.connectSlotsByName(Dialogw)

    def retranslateUi(self, Dialogw):
        _translate = QtCore.QCoreApplication.translate
        Dialogw.setWindowTitle(_translate("Dialogw", "Dialog"))
        self.label.setText(_translate("Dialogw", "Enter worker ID:"))
        self.okayButton.setText(_translate("Dialogw", "Okay"))
        self.cancelButton.setText(_translate("Dialogw", "Cancel"))

import images_rc
