#### X0207b.py
#### Goal1: Integrate Arduino interface with leak test status GUI
#### Goal2: Pop-up box for straw selection

from PyQt5 import QtCore,QtGui
import time, sys, logging, random, os.path, shutil, functools
from PyQt5.QtWidgets import qApp, QApplication, QLabel, QWidget, QGridLayout, QPushButton,\
     QVBoxLayout, QMainWindow, QDialog, QPushButton, QLineEdit, QMessageBox
from PyQt5 import QtGui
import serial  ## Takes this from pyserial, not serial
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from least_square_linear import *  ## Contributes fit functions
from N0202a import Ui_MainWindow   ## Main GUI window
from N0207a import Ui_Dialog       ## Pop-up GUI window for straw selection
from WORKER import Ui_Dialogw
import inspect



class LeakTestStatus(QMainWindow):
    def __init__(self,COM,baudrate,arduino_input=False):
        super().__init__() 
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()
        self.arduino = [serial.Serial(COM,baudrate),serial.Serial("COM7",115200),serial.Serial("COM9",115200),
                        serial.Serial("COM12",115200),serial.Serial("COM6",115200),serial.Serial("COM10",115200),
                        serial.Serial("COM17",115200),serial.Serial("COM14",115200),serial.Serial("COM15",115200),
                        serial.Serial("COM16",115200)]
        self.COM = [COM,'COM7','COM9','COM12','COM6','COM10','COM17','COM14','COM15','COM16']
        self.baudrate = [baudrate,115200,115200,115200,115200,115200,115200,115200,115200,115200]
        for x in range(len(self.COM)):
            print('Arduino at port %s, baudrate %s' % (self.COM[x],self.baudrate[x]))

        self.number_of_chambers = 5
        self.directory = os.path.dirname(os.path.realpath(__file__))+'\\' 
        if os.path.exists(self.directory+'Leak Test Results\\'):
            self.directory = self.directory+'Leak Test Results\\'
        else:
            os.mkdir(self.directory+'Leak Test Results\\')
            self.directory = self.directory+'Leak Test Results\\'
            
        self.starttime = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

        self.chamber_id = { "ch0" : 0, "ch1" : 1, "ch2" : 2, "ch3" : 3, "ch4" : 4,
                            "ch5" : 5, "ch6" : 6, "ch7" : 7, "ch8" : 8, "ch9" : 9,
                            "ch10" : 10, "ch11" : 11, "ch12" : 12, "ch13" : 13, "ch14" : 14,
                            "ch15" : 15, "ch16" : 16, "ch17" : 17, "ch18" : 18, "ch19" : 19,
                            "ch20" : 20, "ch21" : 21, "ch22" : 22, "ch23" : 23, "ch24" : 24,
                            "ch25" : 25, "ch26" : 26, "ch27" : 27, "ch28" : 28, "ch29" : 29,
                            "ch30" : 30, "ch31" : 31, "ch32" : 32, "ch33" : 33, "ch34" : 34,
                            "ch35" : 35, "ch36" : 36, "ch37" : 37, "ch38" : 38, "ch39" : 39,
                            "ch40" : 40, "ch41" : 41, "ch42" : 42, "ch43" : 43, "ch44" : 44,
                            "ch45" : 45, "ch46" : 46, "ch47" : 47, "ch48" : 48, "ch49" : 49}

        self.Choosenames1 = ["empty0","empty1","empty2","empty3","empty4"]
        self.Choosenames2 = ["empty5","empty6","empty7","empty8","empty9"]
        self.Choosenames3 = ["empty10","empty11","empty12","empty13","empty14"]
        self.Choosenames4 = ["empty15","empty16","empty17","empty18","empty19"]
        self.Choosenames5 = ["empty20","empty21","empty22","empty23","empty24"]
        self.Choosenames6 = ["empty25","empty26","empty27","empty28","empty29"]
        self.Choosenames7 = ["empty30","empty31","empty32","empty33","empty34"]
        self.Choosenames8 = ["empty35","empty36","empty37","empty38","empty39"]
        self.Choosenames9 = ["empty40","empty41","empty45","empty46","empty47"]
        self.Choosenames10 = ["empty45","empty46","empty47","empty48","empty49"]
        self.Choosenames = [self.Choosenames1,self.Choosenames2,self.Choosenames3,self.Choosenames4,
                            self.Choosenames5,self.Choosenames6,self.Choosenames7,self.Choosenames8,
                            self.Choosenames9,self.Choosenames10]

        self.chambers_status1 = ["empty0","empty1","empty2","empty3","empty4"]
        self.chambers_status2 = ["empty5","empty6","empty7","empty8","empty9"]
        self.chambers_status3 = ["empty10","empty11","empty12","empty13","empty14"]
        self.chambers_status4 = ["empty15","empty16","empty17","empty18","empty19"]
        self.chambers_status5 = ["empty20","empty21","empty22","empty23","empty24"]
        self.chambers_status6 = ["empty25","empty26","empty27","empty28","empty29"]
        self.chambers_status7 = ["empty30","empty31","empty32","empty33","empty34"]
        self.chambers_status8 = ["empty35","empty36","empty37","empty38","empty39"]
        self.chambers_status9 = ["empty40","empty41","empty42","empty43","empty44"]
        self.chambers_status10 = ["empty45","empty46","empty47","empty48","empty49"]
        self.chambers_status = [self.chambers_status1,self.chambers_status2,self.chambers_status3,
                                self.chambers_status4,self.chambers_status5,self.chambers_status6,
                                self.chambers_status7,self.chambers_status8,self.chambers_status9,
                                self.chambers_status10]
        
        self.files = {}
        self.straw_list = [] ## Passed straws with saved data
        self.result = self.directory + 'Leak Test Results.csv'
        result = open(self.result,'a+',1)
        result.close()
#        self.result = self.directory + datetime.now().strftime("%Y-%m-%d_%H%M%S") + '_%s.csv' % self.COM

        self.chamber_volume1 = [594,607,595,605,595] ## For row 1 chambers
        self.chamber_volume2 = [606,609,612,606,595]
        self.chamber_volume3 = [592,603,612,606,567]
        self.chamber_volume4 = [585,575,610,615,587]
        self.chamber_volume5 = [611,600,542,594,591]
        self.chamber_volume6 = [598,451,627,588,649]
        self.chamber_volume7 = [544,600,534,594,612]
        self.chamber_volume8 = [606,594,515,583,601]
        self.chamber_volume9 = [557,510,550,559,527]
        self.chamber_volume10 = [567,544,572,561,578]
        self.chamber_volume = [self.chamber_volume1,self.chamber_volume2,self.chamber_volume3,
                               self.chamber_volume4,self.chamber_volume5,self.chamber_volume6,
                               self.chamber_volume7,self.chamber_volume8,self.chamber_volume9,
                               self.chamber_volume10]
        
        self.chamber_volume_err1 = [13,31,15,10,21]
        self.chamber_volume_err2 = [37,7,12,17,15]
        self.chamber_volume_err3 = [15,12,7,4,2]
        self.chamber_volume_err4 = [8,15,6,10,11]
        self.chamber_volume_err5 = [4,3,8,6,9]
        self.chamber_volume_err6 = [31,11,25,20,16]
        self.chamber_volume_err7 = [8,8,11,8,6]
        self.chamber_volume_err8 = [6,10,8,10,8]
        self.chamber_volume_err9 = [6,8,6,9,6]
        self.chamber_volume_err10 = [7,6,8,7,6]
        self.chamber_volume_err = [self.chamber_volume_err1,self.chamber_volume_err2,self.chamber_volume_err3,
                                   self.chamber_volume_err4,self.chamber_volume_err5,self.chamber_volume_err6,
                                   self.chamber_volume_err6,self.chamber_volume_err8,self.chamber_volume_err9,
                                   self.chamber_volume_err10]

        self.leak_rate = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        self.leak_rate_err = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        
        self.straw_volume = 26.0
        for n in range(len(self.chamber_volume)):
            for m in range(len(self.chamber_volume[n])):
                self.chamber_volume[n][m] = self.chamber_volume[n][m] - self.straw_volume
        #(conversion_rate*real_leak_rate=the_leak_rate_when_using_20/80_argon/co2 in chamber)
        #Conversion rate proportional to amount of CO2 (1/5)
        #Partial pressure of CO2 as 2 absolution ATM presure inside and 0 outside, chamber will be 1 to 0(1/2)
        #Multiplied by 1.4 for the argon gas leaking as well conservative estimate (should we reduce?
        self.conversion_rate = 0.14
        #max leak rate for straws
        straws_in_detector = 20736
        total_leak_detector = 6 #cc/min
        max_leakrate = float(total_leak_detector)/float(straws_in_detector)  #CC/min
        self.max_leakrate = max_leakrate/3

        self.excluded_time = 15 #wait 2 minutes before using data for fit
        self.max_time = 7200 #When time exceeds 2 hours stops fitting data (still saving it)
        self.min_number_datapoints = 10  #requires 10 datapoints before attempting to fit
        self.max_co2_level = 1800 # when PPM exceeds 1800 stops fitting and warns user of failure
        
        ## set of Arduino status boxes
        self.Arduinos = [self.ui.arduino1,self.ui.arduino2,self.ui.arduino3,self.ui.arduino4,self.ui.arduino5,
                         self.ui.arduino6,self.ui.arduino7,self.ui.arduino8,self.ui.arduino9,self.ui.arduino10]

        ## buttons for plotting belong to a QButtonGroup called PdfButtons
        self.ui.PdfButtons.buttonClicked.connect(self.Plot)
        for x in self.ui.PdfButtons.buttons():
            x.setText('Plot')
            x.setDisabled(True)
        
        ## buttons for loading/unloading straws to a QButtonGroup called ActionButtons
        self.ui.ActionButtons.buttonClicked.connect(self.Action)
        for x in self.ui.ActionButtons.buttons():
            x.setText('Load')
            x.setDisabled(True)

        ## buttons for saving data belong to a QButtonGroup called CsvButtons
#        self.ui.CsvButtons.buttonClicked.connect(self.SaveCSV)
#        for x in self.ui.CsvButtons.buttons():
#            #x.setText('Plot')
#            x.setDisabled(True)

        ## sets for chamber status boxes and status labels
        self.Chambers = [self.ui.ch0,self.ui.ch1,self.ui.ch2,self.ui.ch3,self.ui.ch4,
                         self.ui.ch5,self.ui.ch6,self.ui.ch7,self.ui.ch8,self.ui.ch9,
                         self.ui.ch10,self.ui.ch11,self.ui.ch12,self.ui.ch13,self.ui.ch14,
                         self.ui.ch15,self.ui.ch16,self.ui.ch17,self.ui.ch18,self.ui.ch19,
                         self.ui.ch20,self.ui.ch21,self.ui.ch22,self.ui.ch23,self.ui.ch24,
                         self.ui.ch25,self.ui.ch26,self.ui.ch27,self.ui.ch28,self.ui.ch29,
                         self.ui.ch30,self.ui.ch31,self.ui.ch32,self.ui.ch33,self.ui.ch34,
                         self.ui.ch35,self.ui.ch36,self.ui.ch37,self.ui.ch38,self.ui.ch39,
                         self.ui.ch40,self.ui.ch41,self.ui.ch42,self.ui.ch43,self.ui.ch44,
                         self.ui.ch45,self.ui.ch46,self.ui.ch47,self.ui.ch48,self.ui.ch49]
        
        self.ChamberLabels = [self.ui.label_ch0,self.ui.label_ch1,self.ui.label_ch2,self.ui.label_ch3,self.ui.label_ch4,
                              self.ui.label_ch5,self.ui.label_ch6,self.ui.label_ch7,self.ui.label_ch8,self.ui.label_ch9,
                              self.ui.label_ch10,self.ui.label_ch11,self.ui.label_ch12,self.ui.label_ch13,self.ui.label_ch14,
                              self.ui.label_ch15,self.ui.label_ch16,self.ui.label_ch17,self.ui.label_ch18,self.ui.label_ch19,
                              self.ui.label_ch20,self.ui.label_ch21,self.ui.label_ch22,self.ui.label_ch23,self.ui.label_ch24,
                              self.ui.label_ch25,self.ui.label_ch26,self.ui.label_ch27,self.ui.label_ch28,self.ui.label_ch29,
                              self.ui.label_ch30,self.ui.label_ch31,self.ui.label_ch32,self.ui.label_ch33,self.ui.label_ch34,
                              self.ui.label_ch35,self.ui.label_ch36,self.ui.label_ch37,self.ui.label_ch38,self.ui.label_ch39,
                              self.ui.label_ch40,self.ui.label_ch41,self.ui.label_ch42,self.ui.label_ch43,self.ui.label_ch44,
                              self.ui.label_ch45,self.ui.label_ch46,self.ui.label_ch47,self.ui.label_ch48,self.ui.label_ch49]
        
        self.StrawLabels = [self.ui.label_st0,self.ui.label_st1,self.ui.label_st2,self.ui.label_st3,self.ui.label_st4,
                            self.ui.label_st5,self.ui.label_st6,self.ui.label_st7,self.ui.label_st8,self.ui.label_st9,
                            self.ui.label_st10,self.ui.label_st11,self.ui.label_st12,self.ui.label_st13,self.ui.label_st14,
                            self.ui.label_st15,self.ui.label_st16,self.ui.label_st17,self.ui.label_st18,self.ui.label_st19,
                            self.ui.label_st20,self.ui.label_st21,self.ui.label_st22,self.ui.label_st23,self.ui.label_st24,
                            self.ui.label_st25,self.ui.label_st26,self.ui.label_st27,self.ui.label_st28,self.ui.label_st29,
                            self.ui.label_st30,self.ui.label_st31,self.ui.label_st32,self.ui.label_st33,self.ui.label_st34,
                            self.ui.label_st35,self.ui.label_st36,self.ui.label_st37,self.ui.label_st38,self.ui.label_st39,
                            self.ui.label_st40,self.ui.label_st41,self.ui.label_st42,self.ui.label_st43,self.ui.label_st44,
                            self.ui.label_st45,self.ui.label_st46,self.ui.label_st47,self.ui.label_st48,self.ui.label_st49]
        
        self.StrtData = [self.ui.StartData,self.ui.StartData_2,self.ui.StartData_3,self.ui.StartData_4,self.ui.StartData_5,
                         self.ui.StartData_6,self.ui.StartData_12,self.ui.StartData_13,self.ui.StartData_14,self.ui.StartData_11]
        self.StpData = [self.ui.StopData,self.ui.StopData_2,self.ui.StopData_3,self.ui.StopData_4,self.ui.StopData_5,
                        self.ui.StopData_6,self.ui.StopData_12,self.ui.StopData_13,self.ui.StopData_14,self.ui.StopData_11]

        self.ui.StartData.clicked.connect(self.startArduino1)
        self.ui.StartData_2.clicked.connect(self.startArduino2)
        self.ui.StartData_3.clicked.connect(self.startArduino3)
        self.ui.StartData_4.clicked.connect(self.startArduino4)
        self.ui.StartData_5.clicked.connect(self.startArduino5)
        self.ui.StartData_6.clicked.connect(self.startArduino6)
        self.ui.StartData_12.clicked.connect(self.startArduino7)
        self.ui.StartData_13.clicked.connect(self.startArduino8)
        self.ui.StartData_14.clicked.connect(self.startArduino9)
        self.ui.StartData_11.clicked.connect(self.startArduino10)
        self.ui.StopData.clicked.connect(self.handleStop1)
        self.ui.StopData_2.clicked.connect(self.handleStop2)
        self.ui.StopData_3.clicked.connect(self.handleStop3)
        self.ui.StopData_4.clicked.connect(self.handleStop4)
        self.ui.StopData_5.clicked.connect(self.handleStop5)
        self.ui.StopData_6.clicked.connect(self.handleStop6)
        self.ui.StopData_12.clicked.connect(self.handleStop7)
        self.ui.StopData_13.clicked.connect(self.handleStop8)
        self.ui.StopData_14.clicked.connect(self.handleStop9)
        self.ui.StopData_11.clicked.connect(self.handleStop10)

        for x in self.StpData:
            x.setDisabled(True)

        self.Current_worker = 'Unknown worker'
        self.ui.Log_out.setDisabled(True)
        self.ui.PortalButtons.buttonClicked.connect(self.Change_worker_ID)
        
        self._running = [False,False,False,False,False,False,False,False,False,False]
        #ROW starts at 0
        
    def startArduino1(self):
        self._running[0] = True
        self.StrtData[0].setDisabled(True)
        self.StpData[0].setEnabled(True)
        self.Arduinos[0].setStyleSheet("background-color: rgb(0, 170, 0);")
        for x in self.ui.ActionButtons.buttons():
            if int(x.objectName().strip('ActionButton')) < 5:
                x.setEnabled(True)
        for COL in range(self.number_of_chambers):
            self.update_name(0,COL)
        if ~any(self._running):
            self.handleStart()

    def startArduino2(self):
        self._running[1] = True
        self.StrtData[1].setDisabled(True)
        self.StpData[1].setEnabled(True)
        self.Arduinos[1].setStyleSheet("background-color: rgb(0, 170, 0);")
        for x in self.ui.ActionButtons.buttons():
            if 4 < int(x.objectName().strip('ActionButton')) < 10:
                x.setEnabled(True)
        for COL in range(self.number_of_chambers):
            self.update_name(1,COL)
        if ~any(self._running):
            self.handleStart()

    def startArduino3(self):
        self._running[2] = True
        self.StrtData[2].setDisabled(True)
        self.StpData[2].setEnabled(True)
        self.Arduinos[2].setStyleSheet("background-color: rgb(0, 170, 0);")
        for x in self.ui.ActionButtons.buttons():
            if 9 < int(x.objectName().strip('ActionButton')) < 15:
                x.setEnabled(True)
        for COL in range(self.number_of_chambers):
            self.update_name(2,COL)
        if ~any(self._running):
            self.handleStart()

    def startArduino4(self):
        self._running[3] = True
        self.StrtData[3].setDisabled(True)
        self.StpData[3].setEnabled(True)
        self.Arduinos[3].setStyleSheet("background-color: rgb(0, 170, 0);")
        for x in self.ui.ActionButtons.buttons():
            if 14 < int(x.objectName().strip('ActionButton')) < 20:
                x.setEnabled(True)
        for COL in range(self.number_of_chambers):
            self.update_name(3,COL)
        if ~any(self._running):
            self.handleStart()

    def startArduino5(self):
        self._running[4] = True
        self.StrtData[4].setDisabled(True)
        self.StpData[4].setEnabled(True)
        self.Arduinos[4].setStyleSheet("background-color: rgb(0, 170, 0);")
        for x in self.ui.ActionButtons.buttons():
            if 19 < int(x.objectName().strip('ActionButton')) < 25:
                x.setEnabled(True)
        for COL in range(self.number_of_chambers):
            self.update_name(4,COL)
        if ~any(self._running):
            self.handleStart()

    def startArduino6(self):
        self._running[5] = True
        self.StrtData[5].setDisabled(True)
        self.StpData[5].setEnabled(True)
        self.Arduinos[5].setStyleSheet("background-color: rgb(0, 170, 0);")
        for x in self.ui.ActionButtons.buttons():
            if 24 < int(x.objectName().strip('ActionButton')) < 30:
                x.setEnabled(True)
        for COL in range(self.number_of_chambers):
            self.update_name(5,COL)
        if ~any(self._running):
            self.handleStart()

    def startArduino7(self):
        self._running[6] = True
        self.StrtData[6].setDisabled(True)
        self.StpData[6].setEnabled(True)
        self.Arduinos[6].setStyleSheet("background-color: rgb(0, 170, 0);")
        for x in self.ui.ActionButtons.buttons():
            if 29 < int(x.objectName().strip('ActionButton')) < 35:
                x.setEnabled(True)
        for COL in range(self.number_of_chambers):
            self.update_name(6,COL)
        if ~any(self._running):
            self.handleStart()

    def startArduino8(self):
        self._running[7] = True
        self.StrtData[7].setDisabled(True)
        self.StpData[7].setEnabled(True)
        self.Arduinos[7].setStyleSheet("background-color: rgb(0, 170, 0);")
        for x in self.ui.ActionButtons.buttons():
            if 34 < int(x.objectName().strip('ActionButton')) < 40:
                x.setEnabled(True)
        for COL in range(self.number_of_chambers):
            self.update_name(7,COL)
        if ~any(self._running):
            self.handleStart()

    def startArduino9(self):
        self._running[8] = True
        self.StrtData[8].setDisabled(True)
        self.StpData[8].setEnabled(True)
        self.Arduinos[8].setStyleSheet("background-color: rgb(0, 170, 0);")
        for x in self.ui.ActionButtons.buttons():
            if 39 < int(x.objectName().strip('ActionButton')) < 45:
                x.setEnabled(True)
        for COL in range(self.number_of_chambers):
            self.update_name(8,COL)
        if ~any(self._running):
            self.handleStart()

    def startArduino10(self):
        self._running[9] = True
        self.StrtData[9].setDisabled(True)
        self.StpData[9].setEnabled(True)
        self.Arduinos[9].setStyleSheet("background-color: rgb(0, 170, 0);")
        for x in self.ui.ActionButtons.buttons():
            if 44 < int(x.objectName().strip('ActionButton')):
                x.setEnabled(True)
        for COL in range(self.number_of_chambers):
            self.update_name(9,COL)
        if ~any(self._running):
            self.handleStart()
        
    def handleStart(self):
        """Start data collection for all chambers connected to the Arduino"""
        #self.StrtData[0].setDisabled(True)
        #self._running[0] = True
        #for x in self.ui.ActionButtons.buttons():
        #    x.setEnabled(True)   
        pasttime = [time.time(),time.time(),time.time(),time.time(),time.time(),time.time(),time.time(),time.time(),time.time(),time.time()]
        while any(self._running):
            i=0
            for tf in self._running:
                #cycles through rows
                ROW = i
                i=i+1
                if tf == True:
                    ## Read Arduino and split into multiple files
                    ppms = self.arduino[ROW].readline().strip().split()
                    formattedList = ["%5.2f" % float(member) for member in ppms]
                    currenttime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    epoctime = [time.time(),time.time(),time.time(),time.time(),time.time(),time.time(),time.time(),time.time(),time.time(),time.time()]
                    file = int(float(formattedList[0]))
                    file = file + ROW*5
                    with open(self.files[file],'a+',1) as f:
                        f.write(str(format(epoctime[ROW],'.6f'))+'\t'+str(file)+'\t'
                                +str(formattedList[1])+'\t'+str(currenttime)+'\n')
                        f.flush() ## Needed to send data in buffer to file
                    #print(epoctime,'\t',file,'\t',formattedList[1],'\t',currenttime)
                    if epoctime[ROW] >= (pasttime[ROW] + 15.0) : ## Previously 15.0
                        print("")
                        print(self.COM[ROW])
                        pasttime[ROW] = epoctime[ROW]
                        PPM = {}
                        PPM_err = {}
                        timestamp = {}
#                        starttime = {}
                        slope = {}
                        slope_err = {}
                        intercept = {}
                        intercept_err = {}
                        for COL in range(self.number_of_chambers):
                            #cycles through columns
                            chamber = ROW*5 + COL
                            PPM[chamber] = []
                            PPM_err[chamber] = []
                            timestamp[chamber] = []
#                            starttime[chamber] = 0
                            slope[chamber] = 0
                            slope_err[chamber] = 0
                            intercept[chamber] = 0
                            intercept_err[chamber] = 0
                            with open(self.directory + self.Choosenames[ROW][COL] + '_rawdata.txt',"r+",1) as readfile :
                                for line in readfile:
                                    numbers_float = line.split()[:3]
                                    if numbers_float[2] == '0.00':  
                                        continue
                                    if self.starttime[chamber] == 0 :
                                        self.starttime[chamber] = float(numbers_float[0])
                                    eventtime = float(numbers_float[0]) - self.starttime[chamber]
                                    if eventtime > self.excluded_time :
                                        PPM[chamber].append(float(numbers_float[2]))
                                        PPM_err[chamber].append(((float(numbers_float[2])*0.02)**2 + 20**2)**0.5)
                                        timestamp[chamber].append(eventtime)
                                if (str(self.Choosenames[ROW][COL])[0:5] == "empty") :
                                    print("No straw in chamber %.0f" % (chamber))
                                    continue
                                if len(PPM[chamber]) < self.min_number_datapoints :
                                    print("Straw %s in chamber %.0f is in preparation stage. Please wait for more data" %(self.Choosenames[ROW][COL][:7],chamber))
                                    #self.ChamberLabels[f].setText('Processing')
                                    continue
                                for x in self.ui.PdfButtons.buttons():
                                    if int(x.objectName().strip('PdfButton')) == chamber:
                                          x.setEnabled(True)
                                if max(PPM[chamber]) > self.max_co2_level :
                                    print("CO2 in chamber %.0f exceed 1800. Significant leak?!? Please flush and remove straw" %chamber)
                                    self.Chambers[chamber].setStyleSheet("background-color: rgb(225, 40, 40);")
                                    continue
                                if max(timestamp[chamber]) > self.max_time :
                                    print("Straw %s has been in Chamber %.0f for over 2 hours.  Data is saving but no longer fitting." %(self.Choosenames[ROW][COL][:7],chamber))
                                    continue
                                slope[chamber] = get_slope(timestamp[chamber], PPM[chamber], PPM_err[chamber])
                                slope_err[chamber] = get_slope_err(timestamp[chamber],PPM[chamber],PPM_err[chamber])
                                intercept[chamber] = get_intercept(timestamp[chamber], PPM[chamber], PPM_err[chamber])
                                intercept_err[chamber] = get_intercept_err(timestamp[chamber],PPM[chamber],PPM_err[chamber])
                                #leak rate in cc/min = slope(PPM/sec) * chamber_volume(cc) * 10^-6(1/PPM) * 60 (sec/min) * conversion_rate
                                self.leak_rate[chamber] = slope[chamber]*self.chamber_volume[ROW][COL]*(10 ** -6)*60 * self.conversion_rate
                                #error = sqrt((lr/slope)^2 * slope_err^2 + (lr/ch_vol)^2 * ch_vol_err^2)
                                self.leak_rate_err[chamber] = ((self.leak_rate[chamber]/slope[chamber])**2 * slope_err[chamber]**2 +
                                                 (self.leak_rate[chamber]/self.chamber_volume[ROW][COL])**2 * self.chamber_volume_err[ROW][COL]**2) ** 0.5
                                straw_status = "unknown status"
                                print("Leak rate for straw %s in chamber %.0f is %.2f +- %.2f CC per minute * 10^-5"
                                      % (self.Choosenames[ROW][COL][:7],chamber,self.leak_rate[chamber] *(10**5),self.leak_rate_err[chamber]*(10**5)))
                                self.ChamberLabels[chamber].setText(str('%.2f ± %.2f' % ((self.leak_rate[chamber]*(10**5)),self.leak_rate_err[chamber]*(10**5))))
                                ## Passed straw
                                if len(PPM[chamber]) > 20 and self.leak_rate[chamber] < self.max_leakrate and self.leak_rate_err[chamber] < self.max_leakrate/10:
                                    print("Straw in chamber %.0f has Passed, Please remove" % chamber)
                                    straw_status = "Passed leak requirement"
                                    for x in self.ui.CsvButtons.buttons():
                                        if int(x.objectName().strip('CsvButton')) == chamber:
                                            x.setEnabled(True)
                                    self.Chambers[chamber].setStyleSheet("background-color: rgb(40, 225, 40);")
                                ## Failed straw
                                if len(PPM[chamber]) > 20 and self.leak_rate[chamber] > self.max_leakrate and self.leak_rate_err[chamber] < self.max_leakrate/10:
                                    print("FAILURE SHAME DISHONOR: Straw in chamber %.0f has failed, Please remove and reglue ends" % chamber)
                                    straw_status = "Failed leak requirement"
                                    for x in self.ui.CsvButtons.buttons():
                                        if int(x.objectName().strip('CsvButton')) == chamber:
                                            x.setEnabled(True)
                                    self.Chambers[chamber].setStyleSheet("background-color: rgb(225, 40, 40);")
                                    
                                ## Graph and save graph of fit
                                x = np.linspace(0,max(timestamp[chamber]))
                                y = slope[chamber]*x + intercept[chamber]
                                plt.plot(timestamp[chamber],PPM[chamber],'bo')
                                #plt.errorbar(timestamp[f],PPM[f], yerr=PPM_err[f], fmt='o')
                                plt.plot(x,y,'r')
                                plt.xlabel('time (s)')
                                plt.ylabel('CO2 level (PPM)')
                                plt.title(self.Choosenames[ROW][COL] + '_fit')
                                plt.figtext(0.49, 0.80,
                                            'Slope = %.2f +- %.2f x $10^{-3}$ PPM/sec \n' % (slope[chamber]*10**4,slope_err[chamber]*10**4) +\
                                            'Leak Rate = %.2f +- %.2f x $10^{-5}$ cc/min \n' % (self.leak_rate[chamber] *(10**5),self.leak_rate_err[chamber]*(10**5)) +\
                                            straw_status+"\t"+currenttime,
                                            fontsize = 12, color = 'r')
                                plt.savefig(self.directory + self.Choosenames[ROW][COL] + '_fit.pdf')
                                plt.clf()
                        
            qApp.processEvents()
            time.sleep(0.05)

    def handleStop1(self):
        print('Data collection paused')
        self._running[0] = False
        self.StrtData[0].setEnabled(True)
        self.StpData[0].setDisabled(True)
        for x in self.ui.ActionButtons.buttons():
            if int(x.objectName().strip('ActionButton')) < 5:
                x.setDisabled(True)
        for x in self.ui.PdfButtons.buttons():
            if int(x.objectName().strip('PdfButton')) < 5:
                x.setDisabled(True)
        self.ui.CsvButtons.buttonClicked.connect(self.SaveCSV)
        for x in self.ui.CsvButtons.buttons():
            if int(x.objectName().strip('CsvButton')) < 5:
                x.setDisabled(True)
        self.Arduinos[0].setStyleSheet("background-color: rgb(149, 186, 255);")

    def handleStop2(self):
        print('Data collection paused')
        self._running[1] = False
        self.StrtData[1].setEnabled(True)
        self.StpData[1].setDisabled(True)
        for x in self.ui.ActionButtons.buttons():
            if 4 < int(x.objectName().strip('ActionButton')) < 10:
                x.setDisabled(True)
        for x in self.ui.PdfButtons.buttons():
            if 4 < int(x.objectName().strip('PdfButton')) < 10:
                x.setDisabled(True)
        self.ui.CsvButtons.buttonClicked.connect(self.SaveCSV)
        for x in self.ui.CsvButtons.buttons():
            if 4 < int(x.objectName().strip('CsvButton')) < 10:
                x.setDisabled(True)
        self.Arduinos[1].setStyleSheet("background-color: rgb(149, 186, 255);")

    def handleStop3(self):
        print('Data collection paused')
        self._running[2] = False
        self.StrtData[2].setEnabled(True)
        self.StpData[2].setDisabled(True)
        for x in self.ui.ActionButtons.buttons():
            if 9 < int(x.objectName().strip('ActionButton')) < 15:
                x.setDisabled(True)
        for x in self.ui.PdfButtons.buttons():
            if 9 < int(x.objectName().strip('PdfButton')) < 15:
                x.setDisabled(True)
        self.ui.CsvButtons.buttonClicked.connect(self.SaveCSV)
        for x in self.ui.CsvButtons.buttons():
            if 9 < int(x.objectName().strip('CsvButton')) < 15:
                x.setDisabled(True)
        self.Arduinos[2].setStyleSheet("background-color: rgb(149, 186, 255);")

    def handleStop4(self):
        print('Data collection paused')
        self._running[3] = False
        self.StrtData[3].setEnabled(True)
        self.StpData[3].setDisabled(True)
        for x in self.ui.ActionButtons.buttons():
            if 14 < int(x.objectName().strip('ActionButton')) < 20:
                x.setDisabled(True)
        for x in self.ui.PdfButtons.buttons():
            if 14 < int(x.objectName().strip('PdfButton')) < 20:
                x.setDisabled(True)
        self.ui.CsvButtons.buttonClicked.connect(self.SaveCSV)
        for x in self.ui.CsvButtons.buttons():
            if 14 < int(x.objectName().strip('CsvButton')) < 20:
                x.setDisabled(True)
        self.Arduinos[3].setStyleSheet("background-color: rgb(149, 186, 255);")

    def handleStop5(self):
        print('Data collection paused')
        self._running[4] = False
        self.StrtData[4].setEnabled(True)
        self.StpData[4].setDisabled(True)
        for x in self.ui.ActionButtons.buttons():
            if 19 < int(x.objectName().strip('ActionButton')) < 25:
                x.setDisabled(True)
        for x in self.ui.PdfButtons.buttons():
            if 19 < int(x.objectName().strip('PdfButton')) < 25:
                x.setDisabled(True)
        self.ui.CsvButtons.buttonClicked.connect(self.SaveCSV)
        for x in self.ui.CsvButtons.buttons():
            if 19 < int(x.objectName().strip('CsvButton')) < 25:
                x.setDisabled(True)
        self.Arduinos[4].setStyleSheet("background-color: rgb(149, 186, 255);")

    def handleStop6(self):
        print('Data collection paused')
        self._running[5] = False
        self.StrtData[5].setEnabled(True)
        self.StpData[5].setDisabled(True)
        for x in self.ui.ActionButtons.buttons():
            if 24 < int(x.objectName().strip('ActionButton')) < 30:
                x.setDisabled(True)
        for x in self.ui.PdfButtons.buttons():
            if 24 < int(x.objectName().strip('PdfButton')) < 30:
                x.setDisabled(True)
        self.ui.CsvButtons.buttonClicked.connect(self.SaveCSV)
        for x in self.ui.CsvButtons.buttons():
            if 24 < int(x.objectName().strip('CsvButton')) < 30:
                x.setDisabled(True)
        self.Arduinos[5].setStyleSheet("background-color: rgb(149, 186, 255);")

    def handleStop7(self):
        print('Data collection paused')
        self._running[6] = False
        self.StrtData[6].setEnabled(True)
        self.StpData[6].setDisabled(True)
        for x in self.ui.ActionButtons.buttons():
            if 29 < int(x.objectName().strip('ActionButton')) < 35:
                x.setDisabled(True)
        for x in self.ui.PdfButtons.buttons():
            if 29 < int(x.objectName().strip('PdfButton')) < 35:
                x.setDisabled(True)
        self.ui.CsvButtons.buttonClicked.connect(self.SaveCSV)
        for x in self.ui.CsvButtons.buttons():
            if 29 < int(x.objectName().strip('CsvButton')) < 35:
                x.setDisabled(True)
        self.Arduinos[6].setStyleSheet("background-color: rgb(149, 186, 255);")

    def handleStop8(self):
        print('Data collection paused')
        self._running[7] = False
        self.StrtData[7].setEnabled(True)
        self.StpData[7].setDisabled(True)
        for x in self.ui.ActionButtons.buttons():
            if 34 < int(x.objectName().strip('ActionButton')) < 40:
                x.setDisabled(True)
        for x in self.ui.PdfButtons.buttons():
            if 34 < int(x.objectName().strip('PdfButton')) < 40:
                x.setDisabled(True)
        self.ui.CsvButtons.buttonClicked.connect(self.SaveCSV)
        for x in self.ui.CsvButtons.buttons():
            if 34 < int(x.objectName().strip('CsvButton')) < 40:
                x.setDisabled(True)
        self.Arduinos[7].setStyleSheet("background-color: rgb(149, 186, 255);")

    def handleStop9(self):
        print('Data collection paused')
        self._running[8] = False
        self.StrtData[8].setEnabled(True)
        self.StpData[8].setDisabled(True)
        for x in self.ui.ActionButtons.buttons():
            if 39 < int(x.objectName().strip('ActionButton')) < 45:
                x.setDisabled(True)
        for x in self.ui.PdfButtons.buttons():
            if 39 < int(x.objectName().strip('PdfButton')) < 45:
                x.setDisabled(True)
        self.ui.CsvButtons.buttonClicked.connect(self.SaveCSV)
        for x in self.ui.CsvButtons.buttons():
            if 39 < int(x.objectName().strip('CsvButton')) < 45:
                x.setDisabled(True)
        self.Arduinos[8].setStyleSheet("background-color: rgb(149, 186, 255);")

    def handleStop10(self):
        print('Data collection paused')
        self._running[9] = False
        self.StrtData[9].setEnabled(True)
        self.StpData[9].setDisabled(True)
        for x in self.ui.ActionButtons.buttons():
            if 44 < int(x.objectName().strip('ActionButton')):
                x.setDisabled(True)
        for x in self.ui.PdfButtons.buttons():
            if 44 < int(x.objectName().strip('PdfButton')):
                x.setDisabled(True)
        self.ui.CsvButtons.buttonClicked.connect(self.SaveCSV)
        for x in self.ui.CsvButtons.buttons():
            if 44 < int(x.objectName().strip('CsvButton')):
                x.setDisabled(True)
        self.Arduinos[9].setStyleSheet("background-color: rgb(149, 186, 255);")

    def lineno(self):
        """Call in debugging to get current line number"""
        return inspect.currentframe().f_back.f_lineno
        
    def Action(self,btn):
        """Load or unload straw depending on chamber contents"""
        chamber = int(btn.objectName().strip('ActionButton'))
        ROW = int(chamber/5)
        COL = chamber % 5
        if self.chambers_status[ROW][COL][:5] == 'empty':
            self.chambers_status[ROW][COL] = 'Processing'
            self.ChamberLabels[chamber].setText(self.chambers_status[ROW][COL])
            self.ChangeStraw(chamber)
            if self.Choosenames[ROW][COL][:5] != 'empty':
                btn.setText('Unload')
            else:
                self.chambers_status[ROW][COL] = 'empty'
                self.ChamberLabels[chamber].setText('Empty')
                self.StrawLabels[chamber].setText('No straw')
                btn.setText('Load')
                self.Chambers[chamber].setStyleSheet("background-color: rgb(149, 186, 255)")
                self.NoStraw(ROW,COL)
        elif self.chambers_status[ROW][COL][:5] != 'empty':
            self.SaveCSV(chamber)
            self.chambers_status[ROW][COL] = 'empty'
            self.leak_rate[chamber] = 0
            self.leak_rate_err[chamber] = 0
            self.ChamberLabels[chamber].setText('Empty')
            self.StrawLabels[chamber].setText('No straw')
            btn.setText('Load')
            self.Chambers[chamber].setStyleSheet("background-color: rgb(149, 186, 255)")
            self.NoStraw(ROW,COL)
            for x in self.ui.PdfButtons.buttons():
                if int(x.objectName().strip('PdfButton')) == chamber:
                    x.setDisabled(True)
            for x in self.ui.CsvButtons.buttons():
                if int(x.objectName().strip('CsvButton')) == chamber:
                    x.setDisabled(True)
            
    def NoStraw(self,ROW,COL):
        """Initialize chambers with no straws loaded"""
        wasrunning=bool()
        if self._running[ROW] == True:
            wasrunning = True
            self._running[ROW] = False
        else:
            wasrunning == False
        straw = "empty%s" % ((ROW)*5 + COL)
        self.Choosenames[ROW][COL] = straw
        self.update_name(ROW,COL)
        self._running[ROW] = wasrunning

    def ChangeStraw(self,chamber):
        """Update chamber contents with barcode scan or keyboard"""
        ROW = int(chamber/5)
        COL = chamber % 5
        if self._running[ROW] == True:
            wasrunning = True
            self._running[ROW] = False
        else:
            wasrunning == False
        ctr = StrawSelect() ## Generate pop-up window for straw selection
        ctr.exec_() ## windowModality = ApplicationModal. Main GUI blocked when pop-up is open
        straw = str(ctr.straw_load)
        self.StrawLabels[chamber].setText(straw)
        if straw == "empty" : # Empty chamber
                straw = "empty%s" % chamber
                self.Choosenames[ROW][COL] = straw
        else:
                self.Choosenames[ROW][COL] = straw + '_ch%.0f_' % chamber+datetime.now().strftime("%Y_%m_%d")
                self.starttime[chamber] = 0
        self.update_name(ROW,COL)
        self._running[ROW] = wasrunning

    def update_name(self,ROW,COL):
        """Change file name based on chamber contents"""
        chamber = ROW*5 + COL
        filename = self.directory+self.Choosenames[ROW][COL]
        self.files[chamber] = filename + '_rawdata.txt'
        x = open(self.files[chamber],'a+',1)
        print('Saving data to file %s' %self.Choosenames[ROW][COL])

    def Plot(self,btn):
        """Make and display a copy of the fitted data"""
        chamber = int(btn.objectName().strip('PdfButton'))
        ROW = int(chamber/5)
        COL = chamber % 5
        print('Plotting data for chamber', chamber)
        filepath = self.directory + self.Choosenames[ROW][COL] + '_fit.pdf' ## Data is still being saved here. Don't open
        filepath_temp = self.directory + self.Choosenames[ROW][COL] + '_fit_temp.pdf' ## Static snapshot. Safe to open
        if os.path.exists(filepath_temp):
            try:
                os.system("TASKKILL /F /IM AcroRd32.exe") ## ?Possibly find a better way to close file
            except:
                openplots = None
        if os.path.exists(filepath):
            shutil.copyfile(str(filepath),str(filepath_temp))
            os.startfile(filepath_temp,'open') 
        else:
            print('No fit yet for chamber', chamber,'data. Wait for more data.')

    def Change_worker_ID(self,btn):
        label = btn.objectName()
        if label == 'Log_in':
            wrkr = WorkerID()
            wrkr.exec_()
            self.Current_worker = str(wrkr.Worker_ID)
            self.ui.Current_worker.setText(self.Current_worker)
            self.ui.Current_worker.setStyleSheet("font: 14pt;")
            self.ui.Log_in.setDisabled(True)
            self.ui.Log_out.setEnabled(True)
        elif label == 'Log_out':
            self.Current_worker = 'Unknown worker'
            self.ui.Current_worker.setText(self.Current_worker)
            self.ui.Current_worker.setStyleSheet("font: 14pt;")
            self.ui.Log_out.setDisabled(True)
            self.ui.Log_in.setEnabled(True)
        
    def SaveCSV(self,chamber):
        """Save data to CSV file after straw passes or fails"""
        ROW = int(chamber/5)
        COL = chamber % 5
        if self.Choosenames[ROW][COL][:7] in self.straw_list: 
            print("Data for straw %s in chamber %s already saved" % (self.Choosenames[ROW][COL][:7],chamber))
        else:
            self.straw_list.append(self.Choosenames[ROW][COL][:7])
            currenttime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.result,'r+',1) as result:
                begining = result.read(1)
                first = False
                if begining == '':
                    first = True
                result.close()
            with open(self.result,'a+',1) as result:
                if not first:
                    result.write("\n")
                print('Saving chamber %s data to CSV file' % chamber)
                result.write(self.Choosenames[ROW][COL][:7] + ",")
                result.write(currenttime + ",")
                result.write("CO2"+",")
                result.write(self.Current_worker+",")
                result.write("ch" + str(chamber) + ",")
                #print(self.leak_rate)
                result.write(str(self.leak_rate[chamber]) + ",")
                result.write(str(self.leak_rate_err[chamber]))
                result.close()

    def closeEvent(self, event):
        print("Terminate leak tests and data collection?")
        quit_msg = "Are you sure you want to exit the program?"
        reply = QMessageBox.question(self, 'Message', 
                     quit_msg, QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
            sys.exit(0)
        else:
            event.ignore()

class StrawSelect(QDialog):
    """Pop-up window for entering straw barcode"""
    def __init__(self):
        super().__init__() 
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.show()
        self.ui.lineEdit.setMaxLength(7)
        self.straw_load = 'empty'
        self.ui.okayButton.clicked.connect(self.StrawInput)
    def StrawInput(self):
        self.straw_load = self.ui.lineEdit.text()
        if True:
#        if self.straw_load[:2]=='st' and all(ch.isdigit() for ch in self.straw_load[2:]):
            print('Straw',self.straw_load,'loaded')
            self.deleteLater()
        else:
            print('Not a valid straw barcode. Try formatting like st00023.')
            self.straw_load = 'empty'

class WorkerID(QDialog):
    """Pop-up window for entering straw worker ID"""
    def __init__(self):
        super().__init__() 
        self.ui = Ui_Dialogw()
        self.ui.setupUi(self)
        self.show()
        self.Worker_ID = 'Unknown worker'
        self.ui.okayButton.clicked.connect(self.WorkerIDInput)
    def WorkerIDInput(self):
        self.Worker_ID = self.ui.lineEdit.text()
        if True:
            print('Welcome',self.Worker_ID + '!')
            self.deleteLater()
        else:
            print('Not a valid worker ID.')
            self.Worker_ID = 'Unknown worker'
     
            

if __name__ == '__main__':
    app = QApplication(sys.argv)
    lts = LeakTestStatus("COM11",115200,arduino_input=True)
    lts.show()
    sys.exit(app.exec_())
