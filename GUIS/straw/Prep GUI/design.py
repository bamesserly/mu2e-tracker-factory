#
# design.py
# implemented in: PrepGUI.py
# 
# Straw Prep (Paper Pull) GUI v. 2.1
# 
# Author: Joe Dill
# email: dillx031@umn.edu
#
# Last Editted: 10.4.18
#

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
        self.tab_widget.setGeometry(QtCore.QRect(10, 10, 771, 991))
        self.tab_widget.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tab_widget.setTabsClosable(False)
        self.tab_widget.setObjectName("tab_widget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.portal3 = QtWidgets.QPushButton(self.tab)
        self.portal3.setGeometry(QtCore.QRect(50, 380, 231, 41))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.portal3.setFont(font)
        self.portal3.setObjectName("portal3")
        self.PortalButtons = QtWidgets.QButtonGroup(MainWindow)
        self.PortalButtons.setObjectName("PortalButtons")
        self.PortalButtons.addButton(self.portal3)
        self.portal4 = QtWidgets.QPushButton(self.tab)
        self.portal4.setGeometry(QtCore.QRect(520, 380, 231, 41))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.portal4.setFont(font)
        self.portal4.setObjectName("portal4")
        self.PortalButtons.addButton(self.portal4)
        self.portal2 = QtWidgets.QPushButton(self.tab)
        self.portal2.setGeometry(QtCore.QRect(520, 130, 231, 41))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.portal2.setFont(font)
        self.portal2.setObjectName("portal2")
        self.PortalButtons.addButton(self.portal2)
        self.portal1 = QtWidgets.QPushButton(self.tab)
        self.portal1.setGeometry(QtCore.QRect(50, 130, 231, 41))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.portal1.setFont(font)
        self.portal1.setObjectName("portal1")
        self.PortalButtons.addButton(self.portal1)
        self.label_2 = QtWidgets.QLabel(self.tab)
        self.label_2.setGeometry(QtCore.QRect(520, 70, 81, 16))
        self.label_2.setObjectName("label_2")
        self.label = QtWidgets.QLabel(self.tab)
        self.label.setGeometry(QtCore.QRect(50, 70, 81, 16))
        self.label.setObjectName("label")
        self.label_3 = QtWidgets.QLabel(self.tab)
        self.label_3.setGeometry(QtCore.QRect(50, 320, 81, 16))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.tab)
        self.label_4.setGeometry(QtCore.QRect(520, 320, 81, 16))
        self.label_4.setObjectName("label_4")
        self.frame = QtWidgets.QFrame(self.tab)
        self.frame.setGeometry(QtCore.QRect(520, 340, 231, 41))
        self.frame.setAutoFillBackground(False)
        self.frame.setStyleSheet("background : rgb(255, 255, 255);\n"
"border-style : solid;\n"
"border-color: rgb(170, 255, 255);\n"
"border-width : 2px;")
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.Current_worker4 = QtWidgets.QLabel(self.frame)
        self.Current_worker4.setGeometry(QtCore.QRect(0, 0, 231, 41))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.Current_worker4.setFont(font)
        self.Current_worker4.setText("")
        self.Current_worker4.setObjectName("Current_worker4")
        self.frame_4 = QtWidgets.QFrame(self.tab)
        self.frame_4.setGeometry(QtCore.QRect(50, 90, 231, 41))
        self.frame_4.setAutoFillBackground(False)
        self.frame_4.setStyleSheet("background : rgb(255, 255, 255);\n"
"border-style : solid;\n"
"border-color: rgb(170, 255, 255);\n"
"border-width : 2px;")
        self.frame_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.Current_worker1 = QtWidgets.QLabel(self.frame_4)
        self.Current_worker1.setGeometry(QtCore.QRect(0, 0, 231, 41))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.Current_worker1.setFont(font)
        self.Current_worker1.setText("")
        self.Current_worker1.setObjectName("Current_worker1")
        self.frame_3 = QtWidgets.QFrame(self.tab)
        self.frame_3.setGeometry(QtCore.QRect(520, 90, 231, 41))
        self.frame_3.setAutoFillBackground(False)
        self.frame_3.setStyleSheet("background : rgb(255, 255, 255);\n"
"border-style : solid;\n"
"border-color: rgb(170, 255, 255);\n"
"border-width : 2px;")
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.Current_worker2 = QtWidgets.QLabel(self.frame_3)
        self.Current_worker2.setGeometry(QtCore.QRect(0, 0, 231, 41))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.Current_worker2.setFont(font)
        self.Current_worker2.setText("")
        self.Current_worker2.setObjectName("Current_worker2")
        self.frame_2 = QtWidgets.QFrame(self.tab)
        self.frame_2.setGeometry(QtCore.QRect(50, 340, 231, 41))
        self.frame_2.setAutoFillBackground(False)
        self.frame_2.setStyleSheet("background : rgb(255, 255, 255);\n"
"border-style : solid;\n"
"border-color: rgb(170, 255, 255);\n"
"border-width : 2px;")
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
        self.tab_widget.addTab(self.tab, "")
        
        self.tab_2 = QtWidgets.QWidget()
        
        self.label_strawBatch = QtWidgets.QLabel(self.tab_2)
        self.label_strawBatch.setGeometry(QtCore.QRect(30, 30, 121, 20))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_strawBatch.setFont(font)
        self.label_strawBatch.setAlignment(QtCore.Qt.AlignCenter)
        
        self.start = QtWidgets.QPushButton(self.tab_2)
        self.start.setGeometry(QtCore.QRect(410, 100, 330, 90))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.start.setFont(font)
        
        self.hour_disp = QtWidgets.QLCDNumber(self.tab_2)
        self.hour_disp.setGeometry(QtCore.QRect(410, 190, 110, 110))
        
        self.min_disp = QtWidgets.QLCDNumber(self.tab_2)
        self.min_disp.setGeometry(QtCore.QRect(520, 190, 110, 110))
        
        self.sec_disp = QtWidgets.QLCDNumber(self.tab_2)
        self.sec_disp.setGeometry(QtCore.QRect(630, 190, 110, 110))
        
        self.finishPull = QtWidgets.QPushButton(self.tab_2)
        self.finishPull.setEnabled(False)
        self.finishPull.setGeometry(QtCore.QRect(410, 300, 330, 90))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.finishPull.setFont(font)
        
        self.commentBox = QtWidgets.QPlainTextEdit(self.tab_2)
        self.commentBox.setEnabled(True)
        self.commentBox.setGeometry(QtCore.QRect(410, 430, 330, 160))
        self.commentBox.setPlainText("")
        
        self.label_comments = QtWidgets.QLabel(self.tab_2)
        self.label_comments.setGeometry(QtCore.QRect(410, 400, 330, 20))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label_comments.setFont(font)
        
        self.finish = QtWidgets.QPushButton(self.tab_2)
        self.finish.setEnabled(False)
        self.finish.setGeometry(QtCore.QRect(410, 600, 330, 90))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.finish.setFont(font)

        self.reset = QtWidgets.QPushButton(self.tab_2)
        self.reset.setGeometry(QtCore.QRect(410, 700, 330, 90))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.reset.setFont(font)
        
        self.label_strawID = QtWidgets.QLabel(self.tab_2)
        self.label_strawID.setGeometry(QtCore.QRect(155, 30, 101, 20))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_strawID.setFont(font)
        self.label_strawID.setAlignment(QtCore.Qt.AlignCenter)
        
        self.label_ppg = QtWidgets.QLabel(self.tab_2) #ppg = paper pull grade
        self.label_ppg.setGeometry(QtCore.QRect(280, 30, 101, 20))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_ppg.setFont(font)
        self.label_ppg.setAlignment(QtCore.Qt.AlignCenter)
        
        self.label_palletID = QtWidgets.QLabel(self.tab_2)
        self.label_palletID.setGeometry(QtCore.QRect(410, 30, 160, 20))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_palletID.setFont(font)
        self.label_palletID.setAlignment(QtCore.Qt.AlignCenter)
        
        self.input_palletID = QtWidgets.QLineEdit(self.tab_2)
        self.input_palletID.setGeometry(QtCore.QRect(410, 60, 160, 25))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.input_palletID.setFont(font)
        
        self.label_palletNumber = QtWidgets.QLabel(self.tab_2)
        self.label_palletNumber.setGeometry(QtCore.QRect(580, 30, 160, 20))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_palletNumber.setFont(font)
        self.label_palletNumber.setAlignment(QtCore.Qt.AlignCenter)
        
        self.input_palletNumber = QtWidgets.QLineEdit(self.tab_2)
        self.input_palletNumber.setGeometry(QtCore.QRect(580, 60, 160, 25))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.input_palletNumber.setFont(font)

        self.input_list_strawBatch = []
        self.input_list_strawID = []
        self.input_list_paperPullGrade = []

        for i in range(24):
            font_input = QtGui.QFont()
            font_input.setPointSize(12)
            
            new_input_ID = QtWidgets.QLineEdit(self.tab_2)
            new_input_ID.setGeometry(QtCore.QRect(155, 60 + (30*i), 120, 25))
            new_input_ID.setFont(font_input)
            self.input_list_strawID.append(new_input_ID)

            new_input_strawBatch = QtWidgets.QLineEdit(self.tab_2)
            new_input_strawBatch.setGeometry(QtCore.QRect(30, 60 + (30*i), 120, 25))
            new_input_strawBatch.setFont(font_input)
            self.input_list_strawBatch.append(new_input_strawBatch)

            new_input_paperPullGrade = QtWidgets.QLineEdit(self.tab_2)
            new_input_paperPullGrade.setGeometry(QtCore.QRect(280, 60 + (30*i), 120, 25))
            new_input_paperPullGrade.setFont(font_input)
            self.input_list_paperPullGrade.append(new_input_paperPullGrade)
        
        self.tab_widget.addTab(self.tab_2, "")
        MainWindow.setCentralWidget(self.centralWidget)

        self.retranslateUi(MainWindow)
        self.tab_widget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.portal3.setText(_translate("MainWindow", "Log In"))
        self.portal4.setText(_translate("MainWindow", "Log In"))
        self.portal2.setText(_translate("MainWindow", "Log In"))
        self.portal1.setText(_translate("MainWindow", "Log In"))
        self.label_2.setText(_translate("MainWindow", "Current Worker:"))
        self.label.setText(_translate("MainWindow", "Current Worker:"))
        self.label_3.setText(_translate("MainWindow", "Current Worker:"))
        self.label_4.setText(_translate("MainWindow", "Current Worker:"))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab), _translate("MainWindow", "Worker Portal"))
        
        self.label_strawBatch.setText(_translate("MainWindow", "Straw Batch"))
        self.start.setText(_translate("MainWindow", "Start Paper Pull"))
        self.finishPull.setText(_translate("MainWindow", "Finish Paper Pull"))
        self.label_comments.setText(_translate("MainWindow", "Comments (optional):"))
        self.finish.setText(_translate("MainWindow", "Finish"))        
        self.reset.setText(_translate("MainWindow", "Reset"))
        self.label_strawID.setText(_translate("MainWindow", "Straw ID"))
        self.label_ppg.setText(_translate("MainWindow", "Grade"))
        self.label_palletID.setText(_translate("MainWindow", "Pallet ID"))
        self.input_palletID.setPlaceholderText(_translate("MainWindow", "CPALID##"))
        self.label_palletNumber.setText(_translate("MainWindow", "Pallet Number"))
        self.input_palletNumber.setPlaceholderText(_translate("MainWindow", "CPAL####"))

        for i in range(24):
            self.input_list_strawID[i].setPlaceholderText(_translate("MainWindow", "ST#####"))
            self.input_list_strawID[i].setEnabled(False)
            self.input_list_paperPullGrade[i].setPlaceholderText(_translate("MainWindow", "PP._"))
            self.input_list_paperPullGrade[i].setEnabled(False)
            self.input_list_strawBatch[i].setPlaceholderText(_translate("MainWindow", "MMDDYY.B#"))
            self.input_list_strawBatch[i].setEnabled(False)
            
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_2), _translate("MainWindow", "Straw Prep"))

