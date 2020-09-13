# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'heat_control_window.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(935, 479)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.start_button = QtWidgets.QPushButton(self.centralwidget)
        self.start_button.setGeometry(QtCore.QRect(30, 220, 141, 71))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.start_button.setFont(font)
        self.start_button.setObjectName("start_button")
        self.paas2_box = QtWidgets.QComboBox(self.centralwidget)
        self.paas2_box.setGeometry(QtCore.QRect(30, 110, 141, 51))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.paas2_box.setFont(font)
        self.paas2_box.setObjectName("paas2_box")
        self.paas2_box.addItem("")
        self.paas2_box.addItem("")
        self.paas2_box.addItem("")
        self.paas2_box.addItem("")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(30, 30, 161, 51))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(223, 20, 20, 401))
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(30, 40, 181, 91))
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName("label_2")
        self.tempPA = QtWidgets.QLineEdit(self.centralwidget)
        self.tempPA.setEnabled(True)
        self.tempPA.setGeometry(QtCore.QRect(740, 110, 141, 51))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.tempPA.setFont(font)
        self.tempPA.setReadOnly(True)
        self.tempPA.setObjectName("tempPA")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(740, 50, 151, 71))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setWordWrap(True)
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(250, 0, 471, 51))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.tempP2 = QtWidgets.QLineEdit(self.centralwidget)
        self.tempP2.setEnabled(True)
        self.tempP2.setGeometry(QtCore.QRect(740, 250, 141, 51))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.tempP2.setFont(font)
        self.tempP2.setReadOnly(True)
        self.tempP2.setObjectName("tempP2")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(740, 190, 151, 71))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setWordWrap(True)
        self.label_6.setObjectName("label_6")
        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView.setGeometry(QtCore.QRect(250, 50, 471, 371))
        self.graphicsView.setOptimizationFlags(QtWidgets.QGraphicsView.DontClipPainter)
        self.graphicsView.setObjectName("graphicsView")
        self.end_data = QtWidgets.QPushButton(self.centralwidget)
        self.end_data.setGeometry(QtCore.QRect(30, 350, 141, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.end_data.setFont(font)
        self.end_data.setObjectName("end_data")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(740, 290, 171, 141))
        self.label_5.setWordWrap(True)
        self.label_5.setObjectName("label_5")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 935, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.start_button.setText(_translate("MainWindow", "Start"))
        self.paas2_box.setItemText(0, _translate("MainWindow", "Select..."))
        self.paas2_box.setItemText(1, _translate("MainWindow", "PAAS-B"))
        self.paas2_box.setItemText(2, _translate("MainWindow", "PAAS-C"))
        self.paas2_box.setItemText(3, _translate("MainWindow", "None"))
        self.label.setText(_translate("MainWindow", "2nd PAAS Type"))
        self.label_2.setText(
            _translate(
                "MainWindow",
                "Choose PAAS to heat with PAAS-A. If heating PAAS-A only, choose 'None'.",
            )
        )
        self.label_3.setText(_translate("MainWindow", "PAAS-A Temperature [C]"))
        self.label_4.setText(_translate("MainWindow", "Temperature vs. Time"))
        self.label_6.setText(_translate("MainWindow", "2nd PAAS Temperature [C]"))
        self.end_data.setText(_translate("MainWindow", "End Data Collection"))
        self.label_5.setText(
            _translate(
                "MainWindow",
                "Calibration: PAAS-B/C RTDs in corners where temperature can be 5-8C lower than bulk surface. Expect apparent 5-8C difference with PAAS-A reading, due to calibration such that bulk surface will track PAAS-A to within 5C.",
            )
        )
