# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'co2.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(790, 850)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.widget = QtWidgets.QWidget(self.centralWidget)
        self.widget.setGeometry(QtCore.QRect(90, 530, 120, 80))
        self.widget.setObjectName("widget")
        self.tab_widget = QtWidgets.QTabWidget(self.centralWidget)
        self.tab_widget.setGeometry(QtCore.QRect(10, 10, 771, 831))
        self.tab_widget.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tab_widget.setTabsClosable(False)
        self.tab_widget.setObjectName("tab_widget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.portal1 = QtWidgets.QPushButton(self.tab)
        self.portal1.setGeometry(QtCore.QRect(80, 120, 231, 41))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.portal1.setFont(font)
        self.portal1.setObjectName("portal1")
        self.PortalButtons = QtWidgets.QButtonGroup(MainWindow)
        self.PortalButtons.setObjectName("PortalButtons")
        self.PortalButtons.addButton(self.portal1)
        self.label = QtWidgets.QLabel(self.tab)
        self.label.setGeometry(QtCore.QRect(80, 60, 81, 16))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.tab)
        self.label_2.setGeometry(QtCore.QRect(490, 60, 81, 16))
        self.label_2.setObjectName("label_2")
        self.portal4 = QtWidgets.QPushButton(self.tab)
        self.portal4.setGeometry(QtCore.QRect(490, 370, 231, 41))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.portal4.setFont(font)
        self.portal4.setObjectName("portal4")
        self.PortalButtons.addButton(self.portal4)
        self.label_3 = QtWidgets.QLabel(self.tab)
        self.label_3.setGeometry(QtCore.QRect(90, 310, 81, 16))
        self.label_3.setObjectName("label_3")
        self.portal2 = QtWidgets.QPushButton(self.tab)
        self.portal2.setGeometry(QtCore.QRect(490, 120, 231, 41))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.portal2.setFont(font)
        self.portal2.setObjectName("portal2")
        self.PortalButtons.addButton(self.portal2)
        self.portal3 = QtWidgets.QPushButton(self.tab)
        self.portal3.setGeometry(QtCore.QRect(90, 370, 231, 41))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.portal3.setFont(font)
        self.portal3.setObjectName("portal3")
        self.PortalButtons.addButton(self.portal3)
        self.label_4 = QtWidgets.QLabel(self.tab)
        self.label_4.setGeometry(QtCore.QRect(490, 310, 81, 16))
        self.label_4.setObjectName("label_4")
        self.frame = QtWidgets.QFrame(self.tab)
        self.frame.setGeometry(QtCore.QRect(80, 80, 231, 41))
        self.frame.setAutoFillBackground(False)
        self.frame.setStyleSheet(
            "background : rgb(255, 255, 255);\n"
            "border-style : solid;\n"
            "border-color: rgb(170, 255, 255);\n"
            "border-width : 2px;"
        )
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.Current_worker1 = QtWidgets.QLabel(self.frame)
        self.Current_worker1.setGeometry(QtCore.QRect(0, 0, 231, 41))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.Current_worker1.setFont(font)
        self.Current_worker1.setText("")
        self.Current_worker1.setObjectName("Current_worker1")
        self.frame_2 = QtWidgets.QFrame(self.tab)
        self.frame_2.setGeometry(QtCore.QRect(490, 80, 231, 41))
        self.frame_2.setAutoFillBackground(False)
        self.frame_2.setStyleSheet(
            "background : rgb(255, 255, 255);\n"
            "border-style : solid;\n"
            "border-color: rgb(170, 255, 255);\n"
            "border-width : 2px;"
        )
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.Current_worker2 = QtWidgets.QLabel(self.frame_2)
        self.Current_worker2.setGeometry(QtCore.QRect(0, 0, 231, 41))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.Current_worker2.setFont(font)
        self.Current_worker2.setText("")
        self.Current_worker2.setObjectName("Current_worker2")
        self.frame_3 = QtWidgets.QFrame(self.tab)
        self.frame_3.setGeometry(QtCore.QRect(90, 330, 231, 41))
        self.frame_3.setAutoFillBackground(False)
        self.frame_3.setStyleSheet(
            "background : rgb(255, 255, 255);\n"
            "border-style : solid;\n"
            "border-color: rgb(170, 255, 255);\n"
            "border-width : 2px;"
        )
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.Current_worker3 = QtWidgets.QLabel(self.frame_3)
        self.Current_worker3.setGeometry(QtCore.QRect(0, 0, 231, 41))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.Current_worker3.setFont(font)
        self.Current_worker3.setText("")
        self.Current_worker3.setObjectName("Current_worker3")
        self.frame_4 = QtWidgets.QFrame(self.tab)
        self.frame_4.setGeometry(QtCore.QRect(490, 330, 231, 41))
        self.frame_4.setAutoFillBackground(False)
        self.frame_4.setStyleSheet(
            "background : rgb(255, 255, 255);\n"
            "border-style : solid;\n"
            "border-color: rgb(170, 255, 255);\n"
            "border-width : 2px;"
        )
        self.frame_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.Current_worker4 = QtWidgets.QLabel(self.frame_4)
        self.Current_worker4.setGeometry(QtCore.QRect(0, 0, 231, 41))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.Current_worker4.setFont(font)
        self.Current_worker4.setText("")
        self.Current_worker4.setObjectName("Current_worker4")
        self.tab_widget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.label_6 = QtWidgets.QLabel(self.tab_2)
        self.label_6.setGeometry(QtCore.QRect(50, 30, 111, 16))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.palletNumInput = QtWidgets.QLineEdit(self.tab_2)
        self.palletNumInput.setGeometry(QtCore.QRect(160, 30, 113, 20))
        self.palletNumInput.setText("")
        self.palletNumInput.setObjectName("palletNumInput")
        self.epoxyBatchInput = QtWidgets.QLineEdit(self.tab_2)
        self.epoxyBatchInput.setGeometry(QtCore.QRect(160, 60, 111, 20))
        self.epoxyBatchInput.setText("")
        self.epoxyBatchInput.setObjectName("epoxyBatchInput")
        self.label_7 = QtWidgets.QLabel(self.tab_2)
        self.label_7.setGeometry(QtCore.QRect(10, 50, 141, 41))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.start = QtWidgets.QPushButton(self.tab_2)
        self.start.setGeometry(QtCore.QRect(50, 130, 271, 91))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.start.setFont(font)
        self.start.setObjectName("start")
        self.hour_disp = QtWidgets.QLCDNumber(self.tab_2)
        self.hour_disp.setGeometry(QtCore.QRect(50, 230, 91, 81))
        self.hour_disp.setObjectName("hour_disp")
        self.min_disp = QtWidgets.QLCDNumber(self.tab_2)
        self.min_disp.setGeometry(QtCore.QRect(140, 230, 91, 81))
        self.min_disp.setObjectName("min_disp")
        self.sec_disp = QtWidgets.QLCDNumber(self.tab_2)
        self.sec_disp.setGeometry(QtCore.QRect(230, 230, 91, 81))
        self.sec_disp.setObjectName("sec_disp")
        self.finishInsertion = QtWidgets.QPushButton(self.tab_2)
        self.finishInsertion.setEnabled(False)
        self.finishInsertion.setGeometry(QtCore.QRect(50, 320, 271, 91))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.finishInsertion.setFont(font)
        self.finishInsertion.setObjectName("finishInsertion")
        self.commentBox = QtWidgets.QPlainTextEdit(self.tab_2)
        self.commentBox.setEnabled(True)
        self.commentBox.setGeometry(QtCore.QRect(380, 60, 331, 251))
        self.commentBox.setObjectName("commentBox")
        self.label_9 = QtWidgets.QLabel(self.tab_2)
        self.label_9.setGeometry(QtCore.QRect(407, 30, 231, 21))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.finish = QtWidgets.QPushButton(self.tab_2)
        self.finish.setEnabled(False)
        self.finish.setGeometry(QtCore.QRect(397, 320, 271, 91))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.finish.setFont(font)
        self.finish.setObjectName("finish")
        self.viewButton = QtWidgets.QPushButton(self.tab_2)
        self.viewButton.setEnabled(False)
        self.viewButton.setGeometry(QtCore.QRect(200, 600, 271, 91))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.viewButton.setFont(font)
        self.viewButton.setObjectName("viewButton")
        self.label_8 = QtWidgets.QLabel(self.tab_2)
        self.label_8.setGeometry(QtCore.QRect(10, 80, 141, 41))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.DP190BatchInput = QtWidgets.QLineEdit(self.tab_2)
        self.DP190BatchInput.setGeometry(QtCore.QRect(160, 90, 111, 20))
        self.DP190BatchInput.setText("")
        self.DP190BatchInput.setObjectName("DP190BatchInput")
        self.tab_widget.addTab(self.tab_2, "")
        MainWindow.setCentralWidget(self.centralWidget)

        self.retranslateUi(MainWindow)
        self.tab_widget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.portal1.setText(_translate("MainWindow", "Log In"))
        self.label.setText(_translate("MainWindow", "Current Worker:"))
        self.label_2.setText(_translate("MainWindow", "Current Worker:"))
        self.portal4.setText(_translate("MainWindow", "Log In"))
        self.label_3.setText(_translate("MainWindow", "Current Worker:"))
        self.portal2.setText(_translate("MainWindow", "Log In"))
        self.portal3.setText(_translate("MainWindow", "Log In"))
        self.label_4.setText(_translate("MainWindow", "Current Worker:"))
        self.tab_widget.setTabText(
            self.tab_widget.indexOf(self.tab), _translate("MainWindow", "Worker Portal")
        )
        self.label_6.setText(_translate("MainWindow", "  Pallet #:"))
        self.label_7.setText(_translate("MainWindow", " Epoxy Batch:"))
        self.start.setText(_translate("MainWindow", "Start Endpiece Insertion"))
        self.finishInsertion.setText(
            _translate("MainWindow", "Finish Endpiece Insertion")
        )
        self.label_9.setText(_translate("MainWindow", "Comments (optional):"))
        self.finish.setText(_translate("MainWindow", "Finish"))
        self.viewButton.setText(_translate("MainWindow", "View/Edit Pallet"))
        self.label_8.setText(_translate("MainWindow", "DP190 Batch:"))
        self.tab_widget.setTabText(
            self.tab_widget.indexOf(self.tab_2),
            _translate("MainWindow", "CO2 Endpiece"),
        )
