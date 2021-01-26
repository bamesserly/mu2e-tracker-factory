# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'laser.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(950, 1010)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.widget = QtWidgets.QWidget(self.centralWidget)
        self.widget.setGeometry(QtCore.QRect(90, 530, 120, 80))
        self.widget.setObjectName("widget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralWidget)
        self.tabWidget.setGeometry(QtCore.QRect(10, 10, 931, 991))
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.portal1 = QtWidgets.QPushButton(self.tab)
        self.portal1.setGeometry(QtCore.QRect(100, 210, 231, 41))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.portal1.setFont(font)
        self.portal1.setObjectName("portal1")
        self.PortalButtons = QtWidgets.QButtonGroup(MainWindow)
        self.PortalButtons.setObjectName("PortalButtons")
        self.PortalButtons.addButton(self.portal1)
        self.frame_2 = QtWidgets.QFrame(self.tab)
        self.frame_2.setGeometry(QtCore.QRect(100, 420, 231, 41))
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
        self.Current_worker3 = QtWidgets.QLabel(self.frame_2)
        self.Current_worker3.setGeometry(QtCore.QRect(0, 0, 231, 41))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.Current_worker3.setFont(font)
        self.Current_worker3.setText("")
        self.Current_worker3.setObjectName("Current_worker3")
        self.portal3 = QtWidgets.QPushButton(self.tab)
        self.portal3.setGeometry(QtCore.QRect(100, 460, 231, 41))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.portal3.setFont(font)
        self.portal3.setObjectName("portal3")
        self.PortalButtons.addButton(self.portal3)
        self.frame = QtWidgets.QFrame(self.tab)
        self.frame.setGeometry(QtCore.QRect(100, 170, 231, 41))
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
        self.frame_4 = QtWidgets.QFrame(self.tab)
        self.frame_4.setGeometry(QtCore.QRect(590, 170, 231, 41))
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
        self.Current_worker2 = QtWidgets.QLabel(self.frame_4)
        self.Current_worker2.setGeometry(QtCore.QRect(0, 0, 231, 41))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.Current_worker2.setFont(font)
        self.Current_worker2.setText("")
        self.Current_worker2.setObjectName("Current_worker2")
        self.portal2 = QtWidgets.QPushButton(self.tab)
        self.portal2.setGeometry(QtCore.QRect(590, 210, 231, 41))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.portal2.setFont(font)
        self.portal2.setObjectName("portal2")
        self.PortalButtons.addButton(self.portal2)
        self.portal4 = QtWidgets.QPushButton(self.tab)
        self.portal4.setGeometry(QtCore.QRect(590, 460, 231, 41))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.portal4.setFont(font)
        self.portal4.setObjectName("portal4")
        self.PortalButtons.addButton(self.portal4)
        self.label_4 = QtWidgets.QLabel(self.tab)
        self.label_4.setGeometry(QtCore.QRect(590, 400, 81, 16))
        self.label_4.setObjectName("label_4")
        self.label = QtWidgets.QLabel(self.tab)
        self.label.setGeometry(QtCore.QRect(100, 150, 81, 16))
        self.label.setObjectName("label")
        self.label_3 = QtWidgets.QLabel(self.tab)
        self.label_3.setGeometry(QtCore.QRect(100, 400, 81, 16))
        self.label_3.setObjectName("label_3")
        self.frame_3 = QtWidgets.QFrame(self.tab)
        self.frame_3.setGeometry(QtCore.QRect(590, 420, 231, 41))
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
        self.Current_worker4 = QtWidgets.QLabel(self.frame_3)
        self.Current_worker4.setGeometry(QtCore.QRect(0, 0, 231, 41))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.Current_worker4.setFont(font)
        self.Current_worker4.setText("")
        self.Current_worker4.setObjectName("Current_worker4")
        self.label_2 = QtWidgets.QLabel(self.tab)
        self.label_2.setGeometry(QtCore.QRect(590, 150, 81, 16))
        self.label_2.setObjectName("label_2")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.label_6 = QtWidgets.QLabel(self.tab_2)
        self.label_6.setGeometry(QtCore.QRect(200, 50, 261, 81))
        font = QtGui.QFont()
        font.setPointSize(48)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.commentBox = QtWidgets.QPlainTextEdit(self.tab_2)
        self.commentBox.setGeometry(QtCore.QRect(70, 670, 791, 121))
        self.commentBox.setPlaceholderText("")
        self.commentBox.setObjectName("commentBox")
        self.label_9 = QtWidgets.QLabel(self.tab_2)
        self.label_9.setGeometry(QtCore.QRect(70, 630, 231, 21))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.instructions = QtWidgets.QTextBrowser(self.tab_2)
        self.instructions.setGeometry(QtCore.QRect(250, 160, 401, 461))
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.instructions.setFont(font)
        self.instructions.setObjectName("instructions")
        self.palletNumInput = QtWidgets.QFrame(self.tab_2)
        self.palletNumInput.setGeometry(QtCore.QRect(510, 60, 331, 71))
        self.palletNumInput.setAutoFillBackground(False)
        self.palletNumInput.setStyleSheet(
            "background : rgb(255, 255, 255);\n"
            "border-style : solid;\n"
            "border-color: rgb(170, 255, 255);\n"
            "border-width : 2px;"
        )
        self.palletNumInput.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.palletNumInput.setFrameShadow(QtWidgets.QFrame.Raised)
        self.palletNumInput.setObjectName("palletNumInput")
        self.pallet = QtWidgets.QLabel(self.tab_2)
        self.pallet.setGeometry(QtCore.QRect(510, 60, 331, 71))
        font = QtGui.QFont()
        font.setPointSize(48)
        self.pallet.setFont(font)
        self.pallet.setText("")
        self.pallet.setObjectName("pallet")
        self.viewButton = QtWidgets.QPushButton(self.tab_2)
        self.viewButton.setEnabled(False)
        self.viewButton.setGeometry(QtCore.QRect(320, 840, 231, 71))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.viewButton.setFont(font)
        self.viewButton.setObjectName("viewButton")
        self.tabWidget.addTab(self.tab_2, "")
        MainWindow.setCentralWidget(self.centralWidget)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.portal1.setText(_translate("MainWindow", "Log In"))
        self.portal3.setText(_translate("MainWindow", "Log In"))
        self.portal2.setText(_translate("MainWindow", "Log In"))
        self.portal4.setText(_translate("MainWindow", "Log In"))
        self.label_4.setText(_translate("MainWindow", "Current Worker:"))
        self.label.setText(_translate("MainWindow", "Current Worker:"))
        self.label_3.setText(_translate("MainWindow", "Current Worker:"))
        self.label_2.setText(_translate("MainWindow", "Current Worker:"))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Worker Portal")
        )
        self.label_6.setText(_translate("MainWindow", "Pallet #:"))
        self.label_9.setText(_translate("MainWindow", "Comments (optional):"))
        self.instructions.setHtml(
            _translate(
                "MainWindow",
                '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n'
                '<html><head><meta name="qrichtext" content="1" /><style type="text/css">\n'
                "p, li { white-space: pre-wrap; }\n"
                "</style></head><body style=\" font-family:'MS Shell Dlg 2'; font-size:18pt; font-weight:600; font-style:normal;\">\n"
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Once the pallet is properly alligned on the cutting table, scan the FIRST barcode to initiate the first cut.</p>\n'
                '<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>\n'
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Next, scan the pallet number with format CPAL####. If this information is correct, the first cut will begin immediately. </p>\n'
                '<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>\n'
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Do not touch the mouse or keyboard for 60 seconds after scanning FIRST.</p></body></html>',
            )
        )
        self.viewButton.setText(_translate("MainWindow", "View/Edit Pallet"))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Laser")
        )
