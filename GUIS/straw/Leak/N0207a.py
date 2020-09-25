# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'N0207a.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog.resize(172, 115)
        Dialog.setAutoFillBackground(True)
        Dialog.setStyleSheet("")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(20, 20, 121, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.lineEdit = QtWidgets.QLineEdit(Dialog)
        self.lineEdit.setGeometry(QtCore.QRect(20, 40, 131, 20))
        self.lineEdit.setMaxLength(7)
        self.lineEdit.setObjectName("lineEdit")
        self.okayButton = QtWidgets.QPushButton(Dialog)
        self.okayButton.setGeometry(QtCore.QRect(20, 70, 61, 23))
        self.okayButton.setDefault(True)
        self.okayButton.setObjectName("okayButton")
        self.cancelButton = QtWidgets.QPushButton(Dialog)
        self.cancelButton.setGeometry(QtCore.QRect(90, 70, 61, 23))
        self.cancelButton.setObjectName("cancelButton")

        self.retranslateUi(Dialog)
        self.cancelButton.clicked.connect(Dialog.deleteLater)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "Enter straw barcode:"))
        self.okayButton.setText(_translate("Dialog", "Okay"))
        self.cancelButton.setText(_translate("Dialog", "Cancel"))

import images_rc
