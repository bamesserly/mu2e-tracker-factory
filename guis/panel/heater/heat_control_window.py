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
        MainWindow.resize(935, 486)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.start_button = QtWidgets.QPushButton(self.centralwidget)
        self.start_button.setGeometry(QtCore.QRect(20, 320, 191, 71))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.start_button.setFont(font)
        self.start_button.setObjectName("start_button")
        self.paas2_box = QtWidgets.QComboBox(self.centralwidget)
        self.paas2_box.setGeometry(QtCore.QRect(20, 90, 191, 51))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.paas2_box.setFont(font)
        self.paas2_box.setObjectName("paas2_box")
        self.paas2_box.addItem("")
        self.paas2_box.addItem("")
        self.paas2_box.addItem("")
        self.paas2_box.addItem("")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(20, 20, 161, 51))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(220, 20, 20, 421))
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(20, 40, 181, 61))
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName("label_2")
        self.tempPA = QtWidgets.QLineEdit(self.centralwidget)
        self.tempPA.setEnabled(True)
        self.tempPA.setGeometry(QtCore.QRect(740, 100, 141, 51))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.tempPA.setFont(font)
        self.tempPA.setReadOnly(True)
        self.tempPA.setObjectName("tempPA")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(740, 40, 151, 71))
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
        self.tempP2.setGeometry(QtCore.QRect(740, 220, 141, 51))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.tempP2.setFont(font)
        self.tempP2.setReadOnly(True)
        self.tempP2.setObjectName("tempP2")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(740, 160, 151, 71))
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
        self.end_data.setGeometry(QtCore.QRect(20, 400, 191, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.end_data.setFont(font)
        self.end_data.setObjectName("end_data")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(740, 280, 161, 161))
        self.label_5.setWordWrap(True)
        self.label_5.setObjectName("label_5")
        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        self.label_7.setGeometry(QtCore.QRect(20, 160, 191, 51))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.label_8 = QtWidgets.QLabel(self.centralwidget)
        self.label_8.setGeometry(QtCore.QRect(130, 190, 51, 51))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.labelsp = QtWidgets.QLabel(self.centralwidget)
        self.labelsp.setGeometry(QtCore.QRect(260, 420, 181, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.labelsp.setFont(font)
        self.labelsp.setWordWrap(True)
        self.labelsp.setObjectName("labelsp")
        self.setpt_box = QtWidgets.QComboBox(self.centralwidget)
        self.setpt_box.setGeometry(QtCore.QRect(20, 200, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.setpt_box.setFont(font)
        self.setpt_box.setObjectName("setpt_box")
        self.setpt_box.addItem("")
        self.setpt_box.addItem("")
        self.setpt_box.addItem("")
        self.label_9 = QtWidgets.QLabel(self.centralwidget)
        self.label_9.setGeometry(QtCore.QRect(20, 230, 181, 61))
        self.label_9.setWordWrap(True)
        self.label_9.setObjectName("label_9")
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
        self.paas2_box.setItemText(1, _translate("MainWindow", "PAAS-B (Process 2)"))
        self.paas2_box.setItemText(2, _translate("MainWindow", "PAAS-C (Process 6)"))
        self.paas2_box.setItemText(3, _translate("MainWindow", "None (Process 1)"))
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
                "<html><head/><body><p>Calibration: PAAS RTDs are in peripheral locations where temperature can be 5-8C lower than bulk surface. Heat control program corrects for this such that bulk surfaces reach selected setpoint and track each other within 5C. Thus expect RTD readings in plot to be lower than 55C setpoint. Bulk surface temperature can be verified with thermocouples.</p></body></html>",
            )
        )
        self.label_7.setText(_translate("MainWindow", "Temperature Setpoint"))
        self.label_8.setText(
            _translate(
                "MainWindow",
                "<html><head/><body><p><span style=\" font-family:'Futura Md BT,sans-serif';\">°C</span></p></body></html>",
            )
        )
        self.labelsp.setText(_translate("MainWindow", "Current setpoint:"))
        self.setpt_box.setItemText(0, _translate("MainWindow", "Select..."))
        self.setpt_box.setItemText(1, _translate("MainWindow", "55"))
        self.setpt_box.setItemText(2, _translate("MainWindow", "34"))
        self.label_9.setText(
            _translate(
                "MainWindow",
                "Use 55C for all processes except for funnels. For straw installation, use 34C while funnels are in place and change to 55C after funnel removal.",
            )
        )
