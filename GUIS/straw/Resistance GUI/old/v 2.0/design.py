# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog
from pynput.keyboard import Key, Controller


#GLOBAL CONSTANTS#
RES_MEAS = {
    0: "ii",
    1: "io",
    2: "oi",
    3: "oo"
    }

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1600, 900)
        self.centralWidget = QtWidgets.QWidget(MainWindow)

        ####TABS###

        #Tab Widget
        self.tab_widget = QtWidgets.QTabWidget(self.centralWidget)
        self.tab_widget.setGeometry(QtCore.QRect(0, 0, 1600, 900))
        self.tab_widget.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tab_widget.setTabsClosable(False)

            #Make New Tabs
        self.worker_portal_tab = QtWidgets.QWidget()
        self.resistance_tab = QtWidgets.QWidget()
        
            #Add New Tabs
        self.tab_widget.addTab(self.worker_portal_tab, "")
        self.tab_widget.addTab(self.resistance_tab, "")


        ###WORKER PORTAL TAB###
        
        #Buttons
        self.portal1 = QtWidgets.QPushButton(self.worker_portal_tab)
        self.portal2 = QtWidgets.QPushButton(self.worker_portal_tab)
        self.portal3 = QtWidgets.QPushButton(self.worker_portal_tab)
        self.portal4 = QtWidgets.QPushButton(self.worker_portal_tab)

            #Set Geometry        
        self.portal1.setGeometry(QtCore.QRect(50, 130, 231, 41))
        self.portal2.setGeometry(QtCore.QRect(520, 130, 231, 41))
        self.portal3.setGeometry(QtCore.QRect(50, 380, 231, 41))
        self.portal4.setGeometry(QtCore.QRect(520, 380, 231, 41))

            #Set Font
        font_portal = QtGui.QFont()
        font_portal.setBold(True)
        font_portal.setWeight(75)

        self.portal1.setFont(font_portal)
        self.portal2.setFont(font_portal)
        self.portal3.setFont(font_portal)
        self.portal4.setFont(font_portal)

        #Button Group
        self.portalButtons = QtWidgets.QButtonGroup(MainWindow)
            #Add portal buttons to group
        self.portalButtons.addButton(self.portal1)
        self.portalButtons.addButton(self.portal2)
        self.portalButtons.addButton(self.portal3)
        self.portalButtons.addButton(self.portal4)
        
        #Labels
        self.label1 = QtWidgets.QLabel(self.worker_portal_tab)
        self.label2 = QtWidgets.QLabel(self.worker_portal_tab)
        self.label3 = QtWidgets.QLabel(self.worker_portal_tab)
        self.label4 = QtWidgets.QLabel(self.worker_portal_tab)

            #Set Geometry
        self.label1.setGeometry(QtCore.QRect(50, 70, 81, 16))
        self.label2.setGeometry(QtCore.QRect(520, 70, 81, 16))
        self.label3.setGeometry(QtCore.QRect(50, 320, 81, 16))
        self.label4.setGeometry(QtCore.QRect(520, 320, 81, 16))

        #Frames
        self.frame1 = QtWidgets.QFrame(self.worker_portal_tab)
        self.frame2 = QtWidgets.QFrame(self.worker_portal_tab)
        self.frame3 = QtWidgets.QFrame(self.worker_portal_tab)
        self.frame4 = QtWidgets.QFrame(self.worker_portal_tab)

            #Set Geometry
        self.frame1.setGeometry(QtCore.QRect(50, 90, 231, 41))
        self.frame2.setGeometry(QtCore.QRect(520, 90, 231, 41))
        self.frame3.setGeometry(QtCore.QRect(50, 340, 231, 41))
        self.frame4.setGeometry(QtCore.QRect(520, 340, 231, 41))

            #Set Stylesheet
        stylesheet = "background : rgb(255, 255, 255);\n"
        stylesheet += "border-style : solid;\n"
        stylesheet += "border-color: rgb(170, 255, 255);\n"
        stylesheet += "border-width : 2px;"
        
        self.frame1.setStyleSheet(stylesheet)
        self.frame2.setStyleSheet(stylesheet)
        self.frame3.setStyleSheet(stylesheet)
        self.frame4.setStyleSheet(stylesheet)

            #Set Frameshape
        self.frame1.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame4.setFrameShape(QtWidgets.QFrame.StyledPanel)

            #Set Frame Shadow
        self.frame1.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame4.setFrameShadow(QtWidgets.QFrame.Raised)
        
        #Current Worker Input
        self.Current_worker1 = QtWidgets.QLabel(self.frame1)
        self.Current_worker2 = QtWidgets.QLabel(self.frame2)
        self.Current_worker3 = QtWidgets.QLabel(self.frame3)
        self.Current_worker4 = QtWidgets.QLabel(self.frame4)

            #Set Geometry
        self.Current_worker1.setGeometry(QtCore.QRect(0, 0, 231, 41))
        self.Current_worker2.setGeometry(QtCore.QRect(0, 0, 231, 41))
        self.Current_worker3.setGeometry(QtCore.QRect(0, 0, 231, 41))
        self.Current_worker4.setGeometry(QtCore.QRect(0, 0, 231, 41))

            #Set Font
        font_currentWorker = QtGui.QFont()
        font_currentWorker.setPointSize(16)
        font_currentWorker.setBold(True)
        font_currentWorker.setWeight(75)
        
        self.Current_worker1.setFont(font_currentWorker)        
        self.Current_worker2.setFont(font_currentWorker)        
        self.Current_worker3.setFont(font_currentWorker)        
        self.Current_worker4.setFont(font_currentWorker)

            #Set Text
        self.Current_worker1.setText("")
        self.Current_worker2.setText("")
        self.Current_worker3.setText("")
        self.Current_worker4.setText("")

        ###RESISTANCE TAB###

        #Error Box
        
            #Create QGroupBox Object
        self.errorBox = QtWidgets.QGroupBox(self.resistance_tab)

            #Set Geometry
        self.errorBox.setGeometry(QtCore.QRect(1340, 20, 200, 80))

            #Set Font
        box_font = QtGui.QFont()
        box_font.setPointSize(12)
        self.errorBox.setFont(box_font)

        #Buttons

            #Create QPushButton Objects
        self.byHand_button = QtWidgets.QPushButton(self.resistance_tab)  #calls measureByHand() in main.py
        self.collect_button = QtWidgets.QPushButton(self.resistance_tab) #calls collectData() in main.py
        self.reset_button = QtWidgets.QPushButton(self.resistance_tab)   #calls save() in main.py

            #Set Geometry
        self.collect_button.setGeometry(QtCore.QRect(40, 20, 180, 80))
        self.byHand_button.setGeometry(QtCore.QRect(260, 20, 180, 80))
        self.reset_button.setGeometry(QtCore.QRect(480, 20, 180, 80))

            #Set Font
        button_font = QtGui.QFont()
        button_font.setPointSize(16)
        self.collect_button.setFont(button_font)
        self.byHand_button.setFont(button_font)
        self.reset_button.setFont(button_font)

            #No Default Button
        self.collect_button.setAutoDefault(False)
        self.byHand_button.setAutoDefault(False)
        self.reset_button.setAutoDefault(False)

        
        #Error LED
        self.errorLED = QtWidgets.QLabel(self.errorBox)
        self.errorLED.setGeometry(10,25,180,45)


        #Straw Positions
        
            #QObject Lists
        self.boxlist = [QtWidgets.QGroupBox(self.resistance_tab) for n in range(24)]   #list of QGroupBox objects
        self.strawID_label_list = [] #list of QLabel objects
        self.meas_label_list = [[] for n in range(24)]   #list of QLabel objects
        self.meas_led_list = [[] for n in range(24)]  #list of QLabel objects for color indicators
        self.meas_input_list = [[] for n in range(24)] #list of QLineEdit objects

            #Constants to set positions
        screen_width = 1600
        screen_height = 900
        box_width = 250
        box_height = 160
        spacing_x = 10
        spacing_y = 5
        margin_x = (screen_width - (6*box_width) - (5*spacing_x))/2
        margin_y = screen_height - 120 - 4*(box_height + spacing_y)

        #Fonts
            #for boxes
        pos_box_font = QtGui.QFont()
        pos_box_font.setPointSize(12)
            #for inputs
        font_input = QtGui.QFont()
        font_input.setPointSize(10)

        #Iterate through each straw position define QObjects
        for pos_num in range(1,25):
            
            the_box = self.boxlist[pos_num-1] #get box
            
            #Set position and dimensions#
            column = (pos_num+5)%6
            row =  (pos_num-1)//6
            box_x = margin_x + column*(box_width + spacing_x)
            box_y = margin_y + row*(box_height + spacing_y)
            the_box.setGeometry(QtCore.QRect(box_x, box_y, box_width, box_height))
            the_box.setFont(pos_box_font)
            the_box.setAlignment(QtCore.Qt.AlignCenter)
            
            #Label box with straw ID#
            strawID_label = QtWidgets.QLabel(the_box)
            strawID_label.setGeometry(QtCore.QRect(5, 20, 150, 25))
            strawID_label.setAlignment(QtCore.Qt.AlignLeft)
            self.strawID_label_list.append(strawID_label)
            
            for i in range (0,4): #Iteratre through 4 measurement types
                
                #Meas Line#
                the_meas =  QtWidgets.QLineEdit(self.boxlist[pos_num-1])
                the_meas.setGeometry(QtCore.QRect(65, 50+(i*27), 175 , 20))
                the_meas.setFont(font_input)
                self.meas_input_list[pos_num-1].append(the_meas)                                
                
                #Label for LineEdit#
                the_label = QtWidgets.QLabel(self.boxlist[pos_num-1])
                the_label.setGeometry(QtCore.QRect(20, 50+(i*27), 40, 20))
                the_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
                self.meas_label_list[pos_num-1].append(the_label)
                
                #LED to show LineEdit Status#
                the_led = QtWidgets.QLabel(self.boxlist[pos_num-1])
                the_led.setGeometry(QtCore.QRect(10, 50+(i*27), 20, 20))
                self.meas_led_list[pos_num-1].append(the_led)
                
        self.mainToolBar = QtWidgets.QToolBar(MainWindow)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        
        self.retranslateUi(MainWindow)
        self.tab_widget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Resistance Test"))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.worker_portal_tab), _translate("MainWindow", "Worker Portal"))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.resistance_tab), _translate("MainWindow", "Resistance Test"))

        ###WORKER PORTAL TAB###
        self.portal1.setText(_translate("MainWindow", "Log In"))
        self.portal2.setText(_translate("MainWindow", "Log In"))
        self.portal3.setText(_translate("MainWindow", "Log In"))
        self.portal4.setText(_translate("MainWindow", "Log In"))

        self.label1.setText(_translate("MainWindow", "Current Worker:"))
        self.label2.setText(_translate("MainWindow", "Current Worker:"))
        self.label3.setText(_translate("MainWindow", "Current Worker:"))
        self.label4.setText(_translate("MainWindow", "Current Worker:"))

        ###RESISTANCE TAB###
        self.errorBox.setTitle(_translate("MainWindow", "Status Bar"))

        #Set Button Text
        self.collect_button.setText(_translate("MainWindow", "Collect Data"))
        self.byHand_button.setText(_translate("MainWindow", "Measure By Hand"))
        self.reset_button.setText(_translate("MainWindow", "Save and Reset"))
        
        for n in range(0,24):
            self.boxlist[n].setTitle(_translate("MainWindow", "Position " + str(n+1)))
            self.strawID_label_list[n].setText(_translate("MainWindow", "st####"))
            for i in range (0,4):
                self.meas_label_list[n][i].setText(_translate("MainWindow", RES_MEAS[i] + ":"))
                self.meas_input_list[n][i].setPlaceholderText(_translate("MainWindow", RES_MEAS[i]))
                self.meas_input_list[n][i].setReadOnly(True)
                self.meas_led_list[n][i].setPixmap(QPixmap('images/white.png'))
