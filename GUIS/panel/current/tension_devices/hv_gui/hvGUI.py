# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'hvGUI.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 413)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMaximumSize(QtCore.QSize(1500, 16777215))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../../mu2e.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.gridLayout_4 = QtWidgets.QGridLayout()
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout_4.addWidget(self.label, 0, 0, 1, 1, QtCore.Qt.AlignLeft)
        self.panelNumLE = QtWidgets.QLineEdit(self.centralwidget)
        self.panelNumLE.setMaximumSize(QtCore.QSize(120, 16777215))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.panelNumLE.setFont(font)
        self.panelNumLE.setMaxLength(5)
        self.panelNumLE.setObjectName("panelNumLE")
        self.gridLayout_4.addWidget(self.panelNumLE, 0, 1, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_4, 0, 0, 1, 2)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout_55 = QtWidgets.QGridLayout()
        self.gridLayout_55.setObjectName("gridLayout_55")
        self.label_37 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_37.setFont(font)
        self.label_37.setObjectName("label_37")
        self.gridLayout_55.addWidget(self.label_37, 0, 0, 1, 1)
        self.label_39 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_39.setFont(font)
        self.label_39.setObjectName("label_39")
        self.gridLayout_55.addWidget(self.label_39, 0, 1, 1, 1)
        self.label_40 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_40.setFont(font)
        self.label_40.setObjectName("label_40")
        self.gridLayout_55.addWidget(self.label_40, 0, 2, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout_55, 0, 0, 1, 1)
        self.scrollAreaHV = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollAreaHV.setEnabled(True)
        self.scrollAreaHV.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.scrollAreaHV.setFont(font)
        self.scrollAreaHV.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.scrollAreaHV.setLineWidth(1)
        self.scrollAreaHV.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollAreaHV.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.scrollAreaHV.setWidgetResizable(True)
        self.scrollAreaHV.setObjectName("scrollAreaHV")
        self.scrollContents = QtWidgets.QWidget()
        self.scrollContents.setGeometry(QtCore.QRect(0, 0, 680, 342))
        self.scrollContents.setObjectName("scrollContents")
        self.scrollAreaHV.setWidget(self.scrollContents)
        self.gridLayout_2.addWidget(self.scrollAreaHV, 1, 0, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_2, 0, 3, 8, 1)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout_3.addWidget(self.label_3, 1, 0, 1, 1, QtCore.Qt.AlignLeft)
        self.sideBox = QtWidgets.QComboBox(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.sideBox.setFont(font)
        self.sideBox.setObjectName("sideBox")
        self.sideBox.addItem("")
        self.sideBox.addItem("")
        self.sideBox.addItem("")
        self.gridLayout_3.addWidget(self.sideBox, 1, 1, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.gridLayout_3.addWidget(self.label_7, 2, 0, 1, 1, QtCore.Qt.AlignLeft)
        self.voltageBox = QtWidgets.QComboBox(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.voltageBox.setFont(font)
        self.voltageBox.setObjectName("voltageBox")
        self.voltageBox.addItem("")
        self.voltageBox.addItem("")
        self.voltageBox.addItem("")
        self.gridLayout_3.addWidget(self.voltageBox, 2, 1, 1, 1)
        self.subPanelButton = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.subPanelButton.setFont(font)
        self.subPanelButton.setObjectName("subPanelButton")
        self.gridLayout_3.addWidget(self.subPanelButton, 3, 0, 1, 2)
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_6.setFont(font)
        self.label_6.setText("")
        self.label_6.setObjectName("label_6")
        self.gridLayout_3.addWidget(self.label_6, 4, 0, 1, 1)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.tripBox = QtWidgets.QComboBox(self.centralwidget)
        self.tripBox.setMinimumSize(QtCore.QSize(0, 0))
        self.tripBox.setMaximumSize(QtCore.QSize(120, 16777215))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.tripBox.setFont(font)
        self.tripBox.setObjectName("tripBox")
        self.tripBox.addItem("")
        self.tripBox.addItem("")
        self.gridLayout.addWidget(self.tripBox, 4, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 3, 0, 1, 1, QtCore.Qt.AlignLeft)
        self.positionBox = QtWidgets.QSpinBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.positionBox.sizePolicy().hasHeightForWidth())
        self.positionBox.setSizePolicy(sizePolicy)
        self.positionBox.setMaximumSize(QtCore.QSize(60, 16777215))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.positionBox.setFont(font)
        self.positionBox.setObjectName("positionBox")
        self.gridLayout.addWidget(self.positionBox, 0, 1, 1, 1, QtCore.Qt.AlignRight)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1, QtCore.Qt.AlignLeft)
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 1, 0, 1, 2)
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 4, 0, 1, 1, QtCore.Qt.AlignLeft)
        self.ampsLE = QtWidgets.QLineEdit(self.centralwidget)
        self.ampsLE.setMinimumSize(QtCore.QSize(0, 0))
        self.ampsLE.setMaximumSize(QtCore.QSize(120, 16777215))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.ampsLE.setFont(font)
        self.ampsLE.setObjectName("ampsLE")
        self.gridLayout.addWidget(self.ampsLE, 3, 1, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout, 5, 0, 1, 2)
        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem, 5, 2, 1, 1)
        self.subStrawButton = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.subStrawButton.setFont(font)
        self.subStrawButton.setObjectName("subStrawButton")
        self.gridLayout_3.addWidget(self.subStrawButton, 6, 0, 1, 2)
        spacerItem1 = QtWidgets.QSpacerItem(20, 68, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_3.addItem(spacerItem1, 7, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.panelNumLE, self.ampsLE)
        MainWindow.setTabOrder(self.ampsLE, self.tripBox)
        MainWindow.setTabOrder(self.tripBox, self.positionBox)
        MainWindow.setTabOrder(self.positionBox, self.scrollAreaHV)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "Panel"))
        self.panelNumLE.setPlaceholderText(_translate("MainWindow", "MN***"))
        self.label_37.setText(_translate("MainWindow", "Straw"))
        self.label_39.setText(_translate("MainWindow", "Current (μA)"))
        self.label_40.setText(_translate("MainWindow", "Trip Status"))
        self.label_3.setText(_translate("MainWindow", "Side"))
        self.sideBox.setItemText(0, _translate("MainWindow", "None"))
        self.sideBox.setItemText(1, _translate("MainWindow", "Right"))
        self.sideBox.setItemText(2, _translate("MainWindow", "Left"))
        self.label_7.setText(_translate("MainWindow", "Voltage"))
        self.voltageBox.setItemText(0, _translate("MainWindow", "None"))
        self.voltageBox.setItemText(1, _translate("MainWindow", "1100V"))
        self.voltageBox.setItemText(2, _translate("MainWindow", "1500V"))
        self.subPanelButton.setText(_translate("MainWindow", "Start Session"))
        self.tripBox.setItemText(0, _translate("MainWindow", "Not Tripped"))
        self.tripBox.setItemText(1, _translate("MainWindow", "Tripped"))
        self.label_5.setText(_translate("MainWindow", "Current (μA)"))
        self.label_2.setText(_translate("MainWindow", "Straw"))
        self.label_4.setText(_translate("MainWindow", "Trip Status"))
        self.subStrawButton.setText(_translate("MainWindow", " Submit Straw"))
