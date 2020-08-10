#### run_heat_control.py
#### python interface to collect and visualize data from [PAAS_heater_0624.ino]

import serial   ## from pyserial
import serial.tools.list_ports
import time, csv, sys, os
from datetime import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import traceback
import threading

from PyQt5.QtCore import * 
from PyQt5.QtGui import * 
from PyQt5.QtWidgets import *
#from heat_control_window import Ui_MainWindow  ## edit via heat_control_window.ui in Qt Designer

import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

 

class HeatControl(QMainWindow):
    """ Python interface to collect and visualize data from PAAS heater control system """
    def __init__(self, port, panel, wait=60000, ndatapts=600, parent=None):
        super(HeatControl, self).__init__(parent)
        if port == "GUI":                           # PANGUI doesn't have a get port function
            port = getport('VID:PID=2341:8037')     # opened in PANGUI w/ port = "GUI"
        self.port = port
        self.panel = panel
        self.wait=wait              # wait interval between data points 
        self.ndatapts=ndatapts      # number data points to collect 
        self.hct = None             # heater control data thread
        self.interval = QTimer()    # timer for interval between data points

        ## records for realtime plot
        self.timerec = []   # measurement collection times
        self.tempArec = []  # PAAS-A temperature [C]
        self.temp2rec = []  # 2nd PAAS temperature [C]

        ## set up GUI
        self.ui = Ui_MainWindow()   
        self.ui.setupUi(self)
        self.ui.start_button.clicked.connect(self.start_data)
        self.testplot3()
        
        ## 2nd PAAS type selection required before start of data collection
        self.ui.paas2_box.currentIndexChanged.connect(self.selectpaas)
        self.ui.start_button.setDisabled(True)
        self.ui.end_data.clicked.connect(self.endtest)
        print('initialized')

##        ## development only speed setup
##        self.wait = 2500
##        self.ui.paas2_box.setCurrentIndex(1)
##        self.ui.start_button.click()


    def saveMethod_placeholder(self):
        ## self.tempArec = PAAS-A temperatures
        ## self.temp2rec = PAAS-B or PAAS-C temperatures
        print('last temperature measurements:',self.tempArec[-1],self.temp2rec[-1])
        

    def selectpaas(self):
        """ Enable start data collection if 2nd PAAS selected """
        if self.ui.paas2_box.currentText()!='Select...':
            self.ui.start_button.setEnabled(True)
        else:
            self.ui.start_button.setDisabled(True)


    def start_data(self):
        """ Start serial interface and data collection thread """
        self.ui.start_button.setDisabled(True)
        self.ui.paas2_box.setDisabled(True)
        self.paas2input = self.ui.paas2_box.currentText()
        ## map combobox entries to character to send via serial
        paas2dict = {'PAAS-B':'b','PAAS-C':'c','None':'0'}
        micro_params = {'port':self.port,'baudrate':2000000,'timeout':0.08}
        self.micro = serial.Serial(**micro_params)
        ## trigger paas2 input request
        time.sleep(0.2)
        self.micro.write(b'\n')          
        test=self.micro.readline()
        while test==b'' or test==b'\r\n':  # skip blank lines if any
            self.micro.write(b'\n')          
            test=self.micro.readline()
        ## send character that determines second PAAS plate
        self.paastype = paas2dict[self.paas2input].encode('utf8')
        ## plot will have time since start of test
        self.t0 = time.time()

        ## run data collection from separate thread to avoid freezing GUI
        self.interval.timeout.connect(self.next)
        self.hct = DataThread(self.micro,self.panel,self.paastype) 
        self.hct.start()
        self.interval.start(self.wait) # get data at every timeout

    def next(self):
        """ Add next data to the GUI display """
        ## get the most recent measurement held in thread
        data_list = list(self.hct.transfer())
        if len(data_list)>0: # should only have one set of measurements
            ## display values in GUI, include values in record (for realtime plot)
            self.ui.tempPA.setText(str(data_list[0][0]))
            self.tempArec.append(float(data_list[0][0]))
            if self.paas2input!='None':
                self.temp2rec.append(float(data_list[0][1]))
                self.ui.tempP2.setText(str(data_list[0][1]))
            else: # PAAS-A only
                self.temp2rec.append(0.0) # (avoid -242 or 988)  
            self.timerec.append((time.time()-self.t0)/60.0)
            if len(self.timerec)>self.ndatapts:
                self.endtest()
            else:
                self.hct.savedata()
                ## update plot display
                self.testplot2()
            self.saveMethod_placeholder()

    def testplot3(self):
        """ Set up canvas for plotting temperature vs. time """
        self.ui.data_widget = QWidget(self.ui.graphicsView)
        layout = QHBoxLayout(self.ui.graphicsView)
        self.z = np.array([[-10,-10]])
        self.canvas = DataCanvas(self.ui.data_widget,data=self.z,width=5, height=4, dpi=100,
                                 xlabel='Time since start [minutes]',ylabel='Temperature [C]')
        layout.addWidget(self.canvas)
        self.ui.data_widget.repaint()

    def testplot2(self):
        """ Update plot: new [time,temperature] array """
        self.z = np.array([self.timerec,self.tempArec,self.temp2rec]).T
        self.canvas.read_data(self.z,self.paas2input)
        self.ui.data_widget.repaint() 

    def closeEvent(self,event):
        """ Prevent timer and thread from outliving main window, close serial """
        self.endtest()
            
    def endtest(self):
        """ Join data collection thread to end or reset test """
        self.interval.stop()
        if self.hct: ## must stop thread if it's running
               self.hct.join(0.1) ## make thread timeout
               self.hct = None


class DataThread(threading.Thread):
    """ Read data from Arduino in temperature control box """
    def __init__(self, micro, panel, paastype): 
        threading.Thread.__init__(self)
        self.running = threading.Event() 
        self.running.set()
        self.micro = micro
        self.paastype=paastype
        self.directory = os.path.dirname(os.path.realpath(__file__))+'\\'
        self.datafile = self.directory+'heat_control_data\\'+panel +'_'+ dt.now().strftime("%Y-%m-%d")+'.csv'
        ## create file if needed and write header
        if not os.path.isfile(self.datafile):        
            with open(self.datafile,'a+',newline='') as file:
                file.write(','.join(['Date','PAASA_Temp[C]','2ndPAAS_Temp[C]','Epoc\n']))
        print('saving data to',self.datafile)
        
    def run(self):
        print('thread running')
        n,nmax=0,40
        while self.running.isSet():
            self.micro.write(self.paastype)
            self.micro.write(b'\n')
            ## extract measurements
            temp1,temp2='',''
            while not (temp1 and temp2) and n<nmax:   
                test = self.micro.readline().decode('utf8')
                if test=='':
                    n+=1
                    self.micro.write(self.paastype)
                    self.micro.write(b'\n')
                    continue
                if test.strip().split()[1]=='1':
                    temp1 = test.strip().split()[-1]  # PAAS-A temperature [C]
                elif test.strip().split()[1]=='2':
                    temp2 = test.strip().split()[-1] # 2nd PAAS temperature [C]
                # other values from serial not used in this test (time, duty cycles)
                n+=1
                time.sleep(1)
            if n==nmax: # probable error with serial connection
                print('Error with serial connection ->')
                # clear temps to not send old value if requested by GUI
                self.temp1 = 'error'
                self.temp2 = 'error'
                n=0 
                return
            else: 
                print('PAAS-A temp:',temp1)
                print('2nd PAAS temp:',temp2)
                self.temp1 = temp1
                self.temp2 = temp2
                n=0 
        print('thread running check')
        ## close serial if thread joined
        if self.micro:
            self.micro.close()

    def savedata(self):
        if self.temp1 and self.temp2:
            with open(self.datafile,'a+',newline='') as file:
                cw = csv.writer(file)
                cw.writerow([dt.now().strftime("%Y-%m-%d_%H%M%S"),
                             str(self.temp1),str(self.temp2),
                             str(time.time())])
        else: print('failed saving measurement: temperature data not collected')

    def transfer(self):
        try:
            yield [self.temp1,self.temp2]
        except:
            return

    def join(self, timeout=None): 
        self.running.clear() 
        threading.Thread.join(self, timeout)
        print('thread joined')


class DataCanvas(FigureCanvas):
    """Each canvas class will use this to embed a matplotlib in the PyQt5 GUI"""
    def __init__(self, parent=None, data=None, width=2, height=2, dpi=100,
                 xlabel='xlabel',ylabel='ylabel'):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.axes.clear() 
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,QSizePolicy.Expanding,QSizePolicy.Expanding) 
        FigureCanvas.updateGeometry(self)
        self.axes.grid(True)
        self.axes.set_ylabel(ylabel)
        self.axes.set_xlabel(xlabel)
        box = self.axes.get_position()
        self.axes.set_position([box.x0+box.width*0.05, box.y0+box.height*0.05,
                 box.width*1., box.height*1.])
        self.prev=None;self.prev2=None

    def read_data(self,data,p2):
        if p2=='None': # only PAAS-A
            if self.prev:
                self.prev.remove()
            self.prev, = self.axes.plot(data[:,0], data[:,1],'g.')
        else: # plot temperature for 2 PAAS plates
            if self.prev:
                self.prev.remove()
                self.prev2.remove()
            self.prev, = self.axes.plot(data[:,0], data[:,1],'g.',label='PAAS-A')
            self.prev2, = self.axes.plot(data[:,0], data[:,2],'b.',label=p2)
            self.axes.legend()
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

######################################################################################

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
        self.label_2.setText(_translate("MainWindow", "Choose PAAS to heat with PAAS-A. If heating PAAS-A only, choose \'None\'."))
        self.label_3.setText(_translate("MainWindow", "PAAS-A Temperature [C]"))
        self.label_4.setText(_translate("MainWindow", "Temperature vs. Time"))
        self.label_6.setText(_translate("MainWindow", "2nd PAAS Temperature [C]"))
        self.end_data.setText(_translate("MainWindow", "End Data Collection"))
        self.label_5.setText(_translate("MainWindow", "Calibration: PAAS-B/C RTDs in corners where temperature can be 5-8C lower than bulk surface. Expect apparent 5-8C difference with PAAS-A reading, due to calibration such that bulk surface will track PAAS-A to within 5C."))

######################################################################################


def getport(hardwareID):
    """ Get COM port number. Distinguish Arduino types when multiple devices are connected
        (also works on General Nanosystems where Arduinos recognized as "USB Serial")."""
    ports = [p.device for p in serial.tools.list_ports.comports()
             if hardwareID in p.hwid]
    if len(ports)<1:
        print('Arduino not found \nPlug device into any USB port')
        time.sleep(2)
        print("Exiting script")
        sys.exit()
    return ports[0]


if __name__=='__main__':
    # heater control uses Arduino Micro: hardware ID 'VID:PID=2341:8037'
    port = getport('VID:PID=2341:8037')
    print("Arduino Micro at {}".format(port))

    # view traceback if error causes GUI to crash
    sys.excepthook = traceback.print_exception

    # GUI 
    app = QApplication(sys.argv) 
    ctr = HeatControl(port, panel='MN000')
    ctr.show() 
    app.exec_()






