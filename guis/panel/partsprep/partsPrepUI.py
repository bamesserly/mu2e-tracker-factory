# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'partsPrepUI.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(869, 610)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.tabWidget.setFont(font)
        self.tabWidget.setObjectName("tabWidget")
        self.baseplate = QtWidgets.QWidget()
        self.baseplate.setObjectName("baseplate")
        self.tabWidget.addTab(self.baseplate, "")
        self.bir = QtWidgets.QWidget()
        self.bir.setObjectName("bir")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.bir)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.bir)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.birLE = QtWidgets.QLineEdit(self.bir)
        self.birLE.setObjectName("birLE")
        self.horizontalLayout.addWidget(self.birLE)
        self.gridLayout_8.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.bir1_1 = QtWidgets.QCheckBox(self.bir)
        self.bir1_1.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.bir1_1.setFont(font)
        self.bir1_1.setObjectName("bir1_1")
        self.gridLayout.addWidget(self.bir1_1, 2, 0, 1, 1)
        self.bir1_3 = QtWidgets.QCheckBox(self.bir)
        self.bir1_3.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.bir1_3.setFont(font)
        self.bir1_3.setObjectName("bir1_3")
        self.gridLayout.addWidget(self.bir1_3, 4, 0, 1, 1)
        self.bir1_5 = QtWidgets.QCheckBox(self.bir)
        self.bir1_5.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.bir1_5.setFont(font)
        self.bir1_5.setObjectName("bir1_5")
        self.gridLayout.addWidget(self.bir1_5, 6, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.bir)
        self.label_2.setEnabled(True)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.bir1_2 = QtWidgets.QCheckBox(self.bir)
        self.bir1_2.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.bir1_2.setFont(font)
        self.bir1_2.setObjectName("bir1_2")
        self.gridLayout.addWidget(self.bir1_2, 3, 0, 1, 1)
        self.bir1_4 = QtWidgets.QCheckBox(self.bir)
        self.bir1_4.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.bir1_4.setFont(font)
        self.bir1_4.setObjectName("bir1_4")
        self.gridLayout.addWidget(self.bir1_4, 5, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.bir2_1 = QtWidgets.QCheckBox(self.bir)
        self.bir2_1.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.bir2_1.setFont(font)
        self.bir2_1.setObjectName("bir2_1")
        self.gridLayout_3.addWidget(self.bir2_1, 1, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.bir)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.gridLayout_3.addWidget(self.label_3, 0, 0, 1, 1)
        self.bir2_4 = QtWidgets.QCheckBox(self.bir)
        self.bir2_4.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.bir2_4.setFont(font)
        self.bir2_4.setObjectName("bir2_4")
        self.gridLayout_3.addWidget(self.bir2_4, 7, 0, 1, 1)
        self.bir2_7 = QtWidgets.QCheckBox(self.bir)
        self.bir2_7.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.bir2_7.setFont(font)
        self.bir2_7.setObjectName("bir2_7")
        self.gridLayout_3.addWidget(self.bir2_7, 10, 0, 1, 1)
        self.bir2_5 = QtWidgets.QCheckBox(self.bir)
        self.bir2_5.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.bir2_5.setFont(font)
        self.bir2_5.setObjectName("bir2_5")
        self.gridLayout_3.addWidget(self.bir2_5, 8, 0, 1, 1)
        self.bir2_2 = QtWidgets.QCheckBox(self.bir)
        self.bir2_2.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.bir2_2.setFont(font)
        self.bir2_2.setObjectName("bir2_2")
        self.gridLayout_3.addWidget(self.bir2_2, 2, 0, 1, 1)
        self.bir2_3 = QtWidgets.QCheckBox(self.bir)
        self.bir2_3.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.bir2_3.setFont(font)
        self.bir2_3.setObjectName("bir2_3")
        self.gridLayout_3.addWidget(self.bir2_3, 4, 0, 1, 1)
        self.bir2_6 = QtWidgets.QCheckBox(self.bir)
        self.bir2_6.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.bir2_6.setFont(font)
        self.bir2_6.setObjectName("bir2_6")
        self.gridLayout_3.addWidget(self.bir2_6, 9, 0, 1, 1)
        self.bir2_10 = QtWidgets.QCheckBox(self.bir)
        self.bir2_10.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.bir2_10.setFont(font)
        self.bir2_10.setObjectName("bir2_10")
        self.gridLayout_3.addWidget(self.bir2_10, 13, 0, 1, 1)
        self.bir2_8 = QtWidgets.QCheckBox(self.bir)
        self.bir2_8.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.bir2_8.setFont(font)
        self.bir2_8.setObjectName("bir2_8")
        self.gridLayout_3.addWidget(self.bir2_8, 11, 0, 1, 1)
        self.bir2_9 = QtWidgets.QCheckBox(self.bir)
        self.bir2_9.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.bir2_9.setFont(font)
        self.bir2_9.setObjectName("bir2_9")
        self.gridLayout_3.addWidget(self.bir2_9, 12, 0, 1, 1)
        self.birImage2_3PB = QtWidgets.QPushButton(self.bir)
        self.birImage2_3PB.setMinimumSize(QtCore.QSize(0, 28))
        self.birImage2_3PB.setObjectName("birImage2_3PB")
        self.gridLayout_3.addWidget(self.birImage2_3PB, 5, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_3)
        self.gridLayout_8.addLayout(self.verticalLayout, 1, 0, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.birStartPB = QtWidgets.QPushButton(self.bir)
        self.birStartPB.setObjectName("birStartPB")
        self.horizontalLayout_2.addWidget(self.birStartPB)
        self.birStopPB = QtWidgets.QPushButton(self.bir)
        self.birStopPB.setEnabled(False)
        self.birStopPB.setObjectName("birStopPB")
        self.horizontalLayout_2.addWidget(self.birStopPB)
        self.gridLayout_8.addLayout(self.horizontalLayout_2, 0, 1, 1, 1)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gridLayout_4 = QtWidgets.QGridLayout()
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label_4 = QtWidgets.QLabel(self.bir)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.gridLayout_4.addWidget(self.label_4, 0, 0, 1, 1)
        self.bir3_1 = QtWidgets.QCheckBox(self.bir)
        self.bir3_1.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.bir3_1.setFont(font)
        self.bir3_1.setObjectName("bir3_1")
        self.gridLayout_4.addWidget(self.bir3_1, 1, 0, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout_4)
        self.gridLayout_5 = QtWidgets.QGridLayout()
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.label_5 = QtWidgets.QLabel(self.bir)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.gridLayout_5.addWidget(self.label_5, 0, 0, 1, 1)
        self.bir4_1 = QtWidgets.QCheckBox(self.bir)
        self.bir4_1.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.bir4_1.setFont(font)
        self.bir4_1.setObjectName("bir4_1")
        self.gridLayout_5.addWidget(self.bir4_1, 1, 0, 1, 1)
        self.bir4_2 = QtWidgets.QCheckBox(self.bir)
        self.bir4_2.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.bir4_2.setFont(font)
        self.bir4_2.setObjectName("bir4_2")
        self.gridLayout_5.addWidget(self.bir4_2, 2, 0, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout_5)
        self.gridLayout_6 = QtWidgets.QGridLayout()
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.label_6 = QtWidgets.QLabel(self.bir)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.gridLayout_6.addWidget(self.label_6, 0, 0, 1, 1)
        self.bir5_1 = QtWidgets.QCheckBox(self.bir)
        self.bir5_1.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.bir5_1.setFont(font)
        self.bir5_1.setObjectName("bir5_1")
        self.gridLayout_6.addWidget(self.bir5_1, 1, 0, 1, 1)
        self.bir5_2 = QtWidgets.QCheckBox(self.bir)
        self.bir5_2.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.bir5_2.setFont(font)
        self.bir5_2.setObjectName("bir5_2")
        self.gridLayout_6.addWidget(self.bir5_2, 2, 0, 1, 1)
        self.bir5_3 = QtWidgets.QCheckBox(self.bir)
        self.bir5_3.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.bir5_3.setFont(font)
        self.bir5_3.setObjectName("bir5_3")
        self.gridLayout_6.addWidget(self.bir5_3, 3, 0, 1, 1)
        self.bir5_4 = QtWidgets.QCheckBox(self.bir)
        self.bir5_4.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.bir5_4.setFont(font)
        self.bir5_4.setObjectName("bir5_4")
        self.gridLayout_6.addWidget(self.bir5_4, 4, 0, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout_6)
        self.gridLayout_7 = QtWidgets.QGridLayout()
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.label_7 = QtWidgets.QLabel(self.bir)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.gridLayout_7.addWidget(self.label_7, 0, 0, 1, 1)
        self.bir6_2 = QtWidgets.QCheckBox(self.bir)
        self.bir6_2.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.bir6_2.setFont(font)
        self.bir6_2.setObjectName("bir6_2")
        self.gridLayout_7.addWidget(self.bir6_2, 2, 0, 1, 1)
        self.bir6_1 = QtWidgets.QCheckBox(self.bir)
        self.bir6_1.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.bir6_1.setFont(font)
        self.bir6_1.setObjectName("bir6_1")
        self.gridLayout_7.addWidget(self.bir6_1, 1, 0, 1, 1)
        self.bir6_3 = QtWidgets.QCheckBox(self.bir)
        self.bir6_3.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.bir6_3.setFont(font)
        self.bir6_3.setObjectName("bir6_3")
        self.gridLayout_7.addWidget(self.bir6_3, 3, 0, 1, 1)
        self.bir6_4 = QtWidgets.QCheckBox(self.bir)
        self.bir6_4.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.bir6_4.setFont(font)
        self.bir6_4.setObjectName("bir6_4")
        self.gridLayout_7.addWidget(self.bir6_4, 4, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_7.addItem(spacerItem, 6, 0, 1, 1)
        self.birImage6_4PB = QtWidgets.QPushButton(self.bir)
        self.birImage6_4PB.setObjectName("birImage6_4PB")
        self.gridLayout_7.addWidget(self.birImage6_4PB, 5, 0, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout_7)
        self.gridLayout_8.addLayout(self.verticalLayout_2, 1, 1, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_8.addItem(spacerItem1, 2, 0, 1, 1)
        self.tabWidget.addTab(self.bir, "")
        self.frame = QtWidgets.QWidget()
        self.frame.setObjectName("frame")
        self.tabWidget.addTab(self.frame, "")
        self.mir = QtWidgets.QWidget()
        self.mir.setObjectName("mir")
        self.tabWidget.addTab(self.mir, "")
        self.mr = QtWidgets.QWidget()
        self.mr.setObjectName("mr")
        self.tabWidget.addTab(self.mr, "")
        self.gridLayout_2.addWidget(self.tabWidget, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 869, 22))
        self.menubar.setObjectName("menubar")
        self.menuPictures = QtWidgets.QMenu(self.menubar)
        self.menuPictures.setObjectName("menuPictures")
        self.menuBIR = QtWidgets.QMenu(self.menuPictures)
        self.menuBIR.setObjectName("menuBIR")
        self.menuWorkers = QtWidgets.QMenu(self.menubar)
        self.menuWorkers.setObjectName("menuWorkers")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionAutomatically_Open = QtWidgets.QAction(MainWindow)
        self.actionAutomatically_Open.setCheckable(True)
        self.actionAutomatically_Open.setChecked(False)
        self.actionAutomatically_Open.setObjectName("actionAutomatically_Open")
        self.actionBase_Plate = QtWidgets.QAction(MainWindow)
        self.actionBase_Plate.setObjectName("actionBase_Plate")
        self.actionFrame = QtWidgets.QAction(MainWindow)
        self.actionFrame.setObjectName("actionFrame")
        self.actionMIR = QtWidgets.QAction(MainWindow)
        self.actionMIR.setObjectName("actionMIR")
        self.actionMR = QtWidgets.QAction(MainWindow)
        self.actionMR.setObjectName("actionMR")
        self.actionAdd_Worker = QtWidgets.QAction(MainWindow)
        self.actionAdd_Worker.setObjectName("actionAdd_Worker")
        self.actionAddWorker = QtWidgets.QAction(MainWindow)
        font = QtGui.QFont()
        font.setItalic(True)
        self.actionAddWorker.setFont(font)
        self.actionAddWorker.setObjectName("actionAddWorker")
        self.actionbir2_3 = QtWidgets.QAction(MainWindow)
        self.actionbir2_3.setObjectName("actionbir2_3")
        self.actionbir6_4 = QtWidgets.QAction(MainWindow)
        self.actionbir6_4.setObjectName("actionbir6_4")
        self.menuBIR.addAction(self.actionbir2_3)
        self.menuBIR.addAction(self.actionbir6_4)
        self.menuPictures.addAction(self.actionAutomatically_Open)
        self.menuPictures.addAction(self.actionBase_Plate)
        self.menuPictures.addAction(self.menuBIR.menuAction())
        self.menuPictures.addAction(self.actionFrame)
        self.menuPictures.addAction(self.actionMIR)
        self.menuPictures.addAction(self.actionMR)
        self.menuWorkers.addAction(self.actionAddWorker)
        self.menubar.addAction(self.menuPictures.menuAction())
        self.menubar.addAction(self.menuWorkers.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.baseplate), _translate("MainWindow", "Base Plate"))
        self.label.setText(_translate("MainWindow", "BIR ID"))
        self.bir1_1.setText(_translate("MainWindow", "1.1 - Check flatness"))
        self.bir1_3.setText(_translate("MainWindow", "1.3 - Spot check thickness"))
        self.bir1_5.setText(_translate("MainWindow", "1.5 - Check groove with tool"))
        self.label_2.setText(_translate("MainWindow", "1- Dimension Check"))
        self.bir1_2.setText(_translate("MainWindow", "1.2 - Check groove with tool"))
        self.bir1_4.setText(_translate("MainWindow", "1.4 - Hole pattern check"))
        self.bir2_1.setText(_translate("MainWindow", "2.1 - Inspect Scotch Brite on drill end"))
        self.label_3.setText(_translate("MainWindow", "2 - De-oxidation"))
        self.bir2_4.setText(_translate("MainWindow", "2.4 - Apply vinegar to parts surface"))
        self.bir2_7.setText(_translate("MainWindow", "2.7 - Turn off drill"))
        self.bir2_5.setText(_translate("MainWindow", "2.5 - Turn on/adjust drill to the set speed"))
        self.bir2_2.setText(_translate("MainWindow", "2.2 - Load parts in sliding tray"))
        self.bir2_3.setText(_translate("MainWindow", "2.3 - Adjust Scotch Brite pressure on tray"))
        self.bir2_6.setText(_translate("MainWindow", "2.6 - Slide part under scotch brite"))
        self.bir2_10.setText(_translate("MainWindow", "2.10 - wipe/clean part with isopropyl alcohol"))
        self.bir2_8.setText(_translate("MainWindow", "2.8 - Flush and clean parts with water"))
        self.bir2_9.setText(_translate("MainWindow", "2.9 - Wipe/clean part with vinegar"))
        self.birImage2_3PB.setText(_translate("MainWindow", "Step 2.3 Image"))
        self.birStartPB.setText(_translate("MainWindow", "Start"))
        self.birStopPB.setText(_translate("MainWindow", "Stop"))
        self.label_4.setText(_translate("MainWindow", "3 - De-oxidation QC"))
        self.bir3_1.setText(_translate("MainWindow", "3.1 - Visually inspect processed surface for smoothness, cleanliness"))
        self.label_5.setText(_translate("MainWindow", "4 - Kapton Dots Masking"))
        self.bir4_1.setText(_translate("MainWindow", "4.1 - Pick up Kapton dots with a razor blade"))
        self.bir4_2.setText(_translate("MainWindow", "4.2 - Apply Kapton dots to all holes"))
        self.label_6.setText(_translate("MainWindow", "5 - Epoxy Pre-coating"))
        self.bir5_1.setText(_translate("MainWindow", "5.1 - Mix epoxy"))
        self.bir5_2.setText(_translate("MainWindow", "5.2 - Roll on epoxy with a roller"))
        self.bir5_3.setText(_translate("MainWindow", "5.3 - Clean up excess around edges (Kimwipe)"))
        self.bir5_4.setText(_translate("MainWindow", "5.4 - Put in oven and heat to 60C for >4 hours for glue to cure"))
        self.label_7.setText(_translate("MainWindow", "6 - Epoxy Pre-coating QC"))
        self.bir6_2.setText(_translate("MainWindow", "6.2 - Check/calibrate caliper or height gauge with gauge block"))
        self.bir6_1.setText(_translate("MainWindow", "6.1 - Check/calibrate scale with 100g reference weight"))
        self.bir6_3.setText(_translate("MainWindow", "6.3 - Visually inspect glue surface for smoothness, and no void spot"))
        self.bir6_4.setText(_translate("MainWindow", "6.4 - Spot check thickness < 4.86 mm"))
        self.birImage6_4PB.setText(_translate("MainWindow", "Step 6.4 Image"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.bir), _translate("MainWindow", "BIR"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.frame), _translate("MainWindow", "Frame"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.mir), _translate("MainWindow", "MIR"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.mr), _translate("MainWindow", "MR"))
        self.menuPictures.setTitle(_translate("MainWindow", "Pictures"))
        self.menuBIR.setTitle(_translate("MainWindow", "BIR"))
        self.menuWorkers.setTitle(_translate("MainWindow", "Workers"))
        self.actionAutomatically_Open.setText(_translate("MainWindow", "Automatically Open"))
        self.actionBase_Plate.setText(_translate("MainWindow", "Base Plate"))
        self.actionFrame.setText(_translate("MainWindow", "Frame"))
        self.actionMIR.setText(_translate("MainWindow", "MIR"))
        self.actionMR.setText(_translate("MainWindow", "MR"))
        self.actionAdd_Worker.setText(_translate("MainWindow", "Add Worker"))
        self.actionAddWorker.setText(_translate("MainWindow", "Add Worker"))
        self.actionbir2_3.setText(_translate("MainWindow", "Step 2.3"))
        self.actionbir6_4.setText(_translate("MainWindow", "Step 6.4"))