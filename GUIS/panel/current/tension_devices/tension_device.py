class TensionDevice:
    pass


class StrawTensionWindow(QMainWindow):

    getMeasurement = pyqtSignal(int, float, float)

    """ GUI to display data from Arduino Uno and Vernier force sensor DFS-BTA """

    def __init__(
        self, saveMethod, calibration=None, maxdatas=8824, wait=50.0, parent=None
    ):
        super(StrawTensionWindow, self).__init__(parent)
        self.thdl = None  ## data thread
        self.temp, self.uncertainty = [], []
        self.interval = QTimer()  ## wait interval between data points
        self.calibration = calibration
        self.maxdatas, self.wait = maxdatas, wait
        self.ui = Ui_MainWindow()  ## set up GUI and plot axes
        self.ui.setupUi(self)

        # SAVING DATA
        self.saveMethod = saveMethod
        self.getMeasurement.connect(self.saveMeasurement)
        self.callSaveMeasurement = lambda pos, ten, unc: self.getMeasurement.emit(
            pos, ten, unc
        )

        ## READ IN TENSION LIMITS FROM CSV
        directory = os.path.dirname(os.path.realpath(__file__)) + "\\"
        with open(f"{directory}straw_tensionvalues.csv", "r") as f:
            self.straw_tensionvalues = np.array(
                [row for row in csv.reader(f, delimiter=",")][1:]
            )

        self.straw_number = self.ui.strawnumbox.value()
        self.hmd = self.ui.hmd_label.text()  ## relative humidity (%)
        self.min_tension = self.straw_tensionvalues[:, 2].astype(
            float
        )  ## minimum tension

        self.tmpplot, self.tmpcurve = self.dynamic_plot(
            "Tension (grams)", self.straw_tensionvalues, "lime"
        )

        self.ui.tplot_layout.addWidget(self.tmpplot)
        self.ui.realtime_display.clicked.connect(self.start_data)  ## set up buttons
        self.interval.timeout.connect(self.next)

        ## to add reset, send "1" to Arduino

        self.offset_zero = 0.0
        self.calmode = False
        self.ui.setzero.clicked.connect(self.zero)
        # self.ui.pause_display.setEnabled(False)

        ## adding force sensor zero as required startup step
        self.ui.realtime_display.setDisabled(True)
        # self.ui.statusbar.showMessage("Arduino connected: Press Tension Straw to begin")
        self.ui.statusbar.showMessage(
            "Arduino connected. Set switch on force sensor to 10N. Click Set Force Sensor Zero to begin."
        )
        print("initialized")

    def saveMeasurement(self, straw_position, tension, uncertainty):

        # Before saving measurement, verify with user
        buttonreply = QMessageBox.question(
            self,
            "Save",
            f"Save tension measurement?\nStraw:\t{straw_position}\nTension:\t{tension}\nUncertainty\t{uncertainty}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        # If user presses yes, call the inherited save method
        if buttonreply == QMessageBox.Yes:
            self.saveMethod(straw_position, tension, uncertainty)

    def start_data(self):
        """ Start data collection """
        self.ui.statusbar.showMessage("")
        if self.ui.autoincrement.isChecked():  ## auto-increment straw number by two
            x = self.ui.strawnumbox.value()
            self.ui.strawnumbox.setValue(x + 2)

        self.straw_number = self.ui.strawnumbox.value()
        self.nom_tension = float(
            self.straw_tensionvalues[self.straw_number, 3]
        ) - float(self.hmd)
        self.ui.nominal_label.setText("%5.2f" % float(self.nom_tension))

        self.temp, self.uncertainty = [], []  ## clear plot of previous straw's tension
        com = self.getPortLocation()["Vernier Force Sensor"][0]

        qs = queue.Queue()

        # Method to emit

        ## baud rate 9600 for Vernier sensor
        if self.calmode:  ## use raw data (no offset) to find offset
            self.thdl = GetDataThread(
                self.callSaveMeasurement, self.straw_number, qs, 0.0, com, 9600
            )
        else:  ## includes offset subtraction
            self.thdl = GetDataThread(
                self.callSaveMeasurement,
                self.straw_number,
                qs,
                self.offset_zero,
                com,
                9600,
            )
        self.thdl.start()
        self.ui.realtime_display.setEnabled(False)
        self.ui.setzero.setEnabled(False)
        self.interval.start(self.wait)

    def dynamic_plot(self, data_type, st, color, xaxis=True):
        plot = qwt.QwtPlot(self)
        plot.setCanvasBackground(Qt.black)
        if xaxis:
            plot.setAxisTitle(qwt.QwtPlot.xBottom, "Time (s)")
        plot.setAxisScale(qwt.QwtPlot.xBottom, 0, 10, 1)
        plot.setAxisTitle(qwt.QwtPlot.yLeft, data_type)
        plot.setAxisScale(qwt.QwtPlot.yLeft, 18, 28, 2)
        plot.replot()
        curve = qwt.QwtPlotCurve("")
        curve.setRenderHint(qwt.QwtPlotItem.RenderAntialiased)
        pen = QPen(QColor(color), 2)
        curve.setPen(pen)
        curve.attach(plot)
        ## add max straw tension, 850g for all straws
        curvemax = qwt.QwtPlotCurve("max_tension")
        curvemax.attach(plot)
        penlim = QPen(QColor("yellow"), 2)
        curvemax.setPen(penlim)
        curvemax.setData(np.arange(100), 850 * np.ones(100))
        ## add min straw tension, depends on straw length
        self.curvemin = qwt.QwtPlotCurve("min_tension")
        self.curvemin.attach(plot)
        self.curvemin.setPen(penlim)
        self.curvemin.setData(
            np.arange(100),
            (float(self.min_tension[int(self.straw_number)]) - float(self.hmd))
            * np.ones(100),
        )
        plot.replot()
        return plot, curve

    def next(self):
        """ Add next data to the plots """
        data_list = list(self.thdl.transfer(self.thdl.qs))
        if len(data_list) > 0 and data_list[-1][0][1] != "nan":  ## skip blank data
            data = dict(
                tension=data_list[-1][0][0],
                uncertainty=data_list[-1][0][1],
                timestamp=data_list[-1][1],
            )
            if self.calmode:  ## use raw data in calibration mode
                caltmp = float(data["tension"])
            else:  ## data with offset subtracted
                caltmp = float(
                    data["tension"]
                )  ## includes subtraction of offset at zero
            calhmd = float(data["uncertainty"])
            state = data_list[-1][2]

            self.ui.tension_label.setText("%5.2f" % caltmp)  ## tension in label box
            self.ui.unc_label.setText(str(calhmd))  ## uncertainty in label
            if caltmp <= 850.0 and caltmp >= float(
                self.min_tension[int(self.straw_number)]
            ) - float(self.hmd):
                self.ui.rangepanel.setStyleSheet("background-color: green")
                message = "Straw tension acceptable: move to next straw"
            else:
                self.ui.rangepanel.setStyleSheet("background-color: red")
                message = "Straw tension outside acceptable range: repull straw"

            self.temp.append((data["timestamp"], caltmp))
            self.uncertainty.append((data["timestamp"], calhmd))
            if len(self.temp) > self.maxdatas:
                self.temp.pop(0), self.uncertainty.pop(0)
            t = [x[0] for x in self.temp]  ## time (s)
            tmp = [float(t[1]) for t in self.temp]  ## tension (grams force)
            hmd = [float(h[1]) for h in self.uncertainty]  ## uncertainty (grams force)
            ave = [sum(y) / float(len(y)) for y in [tmp]]
            self.curvemin.setData(
                np.arange(100),
                (float(self.min_tension[(self.straw_number)]) - float(self.hmd))
                * np.ones(100),
            )
            for a in [[self.tmpplot, tmp, self.tmpcurve]]:
                a[0].setAxisScale(qwt.QwtPlot.xBottom, t[0], max(8, t[-1]))
                ymin, ymax = min(a[1]) - 3.0, max(max(a[1]) + 4.0, a[1][-1])
                a[0].setAxisScale(qwt.QwtPlot.yLeft, 0, 1000, 100)
                a[2].setData(t, a[1])  ## add new data to the plots
                a[0].replot()
            self.ui.ave_temp.setText("%5.2f" % tmp[-1])
            self.ui.ave_temp.setStyleSheet("color: lime")

            if state == b"end":
                self.pause_data()
                self.ui.statusbar.showMessage(message)

            if self.calmode:
                if len(self.temp) > 50:
                    print("gathered 50 values")
                    caldata = np.array(self.temp)
                    if np.nanstd(caldata[:, 1]) > 5:
                        print("Uncertainty > 5g. Recalibrating")
                        self.temp = []
                    else:
                        self.pause_data()
                        self.offset_zero = np.nanmean(caldata[:, 1])
                        print(
                            "Calibration data collected: {:.2f}g offset at zero".format(
                                self.offset_zero
                            )
                        )
                        self.calmode = False
                        self.ui.setzero.setEnabled(True)
                        self.ui.realtime_display.setEnabled(True)
                        self.ui.statusbar.showMessage(
                            "Force sensor zero set. Ready to tension straw."
                        )

    def pause_data(self):
        """ Pause data collection """
        if self.thdl:  ## must stop thread if it's running
            self.thdl.join(0.1)  ## make thread timeout
            self.thdl = None
        self.interval.stop()
        QTimer.singleShot(180, lambda: self.ui.realtime_display.setEnabled(True))
        # self.ui.pause_display.setEnabled(False)
        QTimer.singleShot(180, lambda: self.ui.setzero.setEnabled(True))

    def zero(self):
        """ Set zero by subtracting sensor offset at zero tension. """
        self.ui.setzero.setEnabled(False)
        self.calmode = True
        self.start_data()

    @staticmethod
    def getPortLocation():
        arduino_ports = [
            p.device
            for p in serial.tools.list_ports.comports()
            if "Arduino" in p.description
        ]

        if len(arduino_ports) == 0:  ## fix for Day2/Day3 General Nanosystems Computers
            arduino_ports = [
                p.device
                for p in serial.tools.list_ports.comports()
                if "USB Serial" in p.description
            ]

        if len(arduino_ports) < 1:
            raise ArduinoNotFound(
                "No Arduino found, check USB connection and try again."
            )

        elif len(arduino_ports) > 1:
            raise TooManyArduinos(
                "More than one Arduino found. Disconnect the ones not in use and try again."
            )

        print("Arduino at {}".format(arduino_ports[0]))
        ## Locations of sensors
        return {"Vernier Force Sensor": [arduino_ports[0], 0]}


class WireTension(QMainWindow):
    """ GUI to interface with load cell / stepper motor wire tensioner  """

    def __init__(self, port, parent=None, wait=10.0, networked=True):
        super(WireTension, self).__init__(parent)
        self.port = port

        ## Save Data ###################################
        # self.directory = os.path.dirname(os.path.realpath(__file__))+'\\'
        self.mu2ecart = "\\\MU2E-CART1\\Users\\Public\\Database Backup\\Panel data\\"
        if networked:  ## save data to MU2E-CART1
            self.directory = self.mu2ecart
            print("Saving data to %s" % self.directory)
        else:  ## option to run locally
            self.directory = os.path.dirname(os.path.realpath(__file__)) + "\\"
            print("Saving data to %s" % self.directory)
        #####################################################

        ## Setup UI
        self.ui = Ui_Dialog()  ## set up GUI window
        self.ui.setupUi(self)

        self.wait = wait
        self.interval = QTimer()  ## wait interval between data points
        self.interval.timeout.connect(self.next)
        self.ui.tension_harden.clicked.connect(
            lambda: self.tension_wire(pretension=True)
        )
        self.ui.tension_only.clicked.connect(
            lambda: self.tension_wire(pretension=False)
        )
        self.ui.resetmotor.clicked.connect(self.reset)
        self.ui.next_straw.clicked.connect(self.increment_straw)
        self.ui.recordtension.clicked.connect(self.record)
        self.ui.tarebutton.clicked.connect(lambda: self.tareloadcell(tare=50))
        self.ui.tarebutton2.clicked.connect(lambda: self.tareloadcell(tare=0))
        self.ui.setcalbutton.clicked.connect(self.setcalibration)
        self.ui.strawnumbox.valueChanged.connect(
            lambda: self.ui.recordlabel.setText("")
        )

        print("testing")
        ## load current calibration factor
        self.micro = serial.Serial(port=self.port, baudrate=9600, timeout=0.08)
        self.micro.write(b"c")
        self.micro.write(b"\n")
        x = self.micro.readline()
        print(x)
        self.initcal = float(x.split()[1])
        print(self.initcal)
        self.micro.close()
        self.ui.calibfactor.setText(str(self.initcal))
        print("testing")
        self.ui.statuslabel.setText(
            "Initialized. Ready to work harden and tension wire."
        )
        self.start_data()

    def start_data(self):
        """ Monitor data continuously through GUI """
        self.wire_number = self.ui.strawnumbox.value()
        print("wire", self.wire_number)
        qs = queue.Queue()
        self.thdl = GetDataThread(qs, self.port)
        self.thdl.start()
        self.interval.start(self.wait)
        self.wirestarttime = int(time.time())

    def tareloadcell(self, tare=50):
        """ Tare load cell. Default tare for calibration is with 50g reference mass. """
        print("tare load cell")
        self.thdl.join()
        self.micro = serial.Serial(port=self.port, baudrate=9600, timeout=0.08)
        print(self.micro.readline())
        self.micro.write(b"\n")
        if tare == 0:  ## tare at 0g
            self.micro.write(b"z2")
        else:  ## tare at 50g for calibration
            self.micro.write(b"z")
        self.micro.write(b"\n")
        print(self.micro.readline())
        self.micro.write(b"\n")
        print(self.micro.readline())
        self.micro.write(b"\n")
        self.micro.close()
        self.ui.calibmode.setText("Tared")
        if tare == 50:
            self.ui.statuslabel.setText("Hang 100g mass and click set")
        self.start_data()

    def setcalibration(self):
        print("setting calbration factor")
        self.thdl.join()
        self.micro = serial.Serial(port=self.port, baudrate=9600, timeout=0.08)
        self.micro.write(b"s")
        self.micro.write(b"\n")
        time.sleep(2)
        cal = self.initcal
        for i in range(30):
            x = self.micro.readline()
            print(x)
            if x != b"":
                x = x.split()
                if x[0] == b"calibration_factor":
                    print(x)
                    cal = x[1]
                    self.ui.calibfactor.setText(str(float(cal)))
                    break
        print(cal, self.initcal)
        if float(cal) == float(self.initcal):
            self.ui.statuslabel.setText("Error updating calibration")
        print("setting calibration", cal)
        # self.ui.calibfactor.setText(str(float(x)))
        self.micro.close()
        self.start_data()
        self.ui.calibmode.setText("Set")
        self.ui.statuslabel.setText("Calibration factor set.")

    def record(self):
        """ Save date, panel, wire, tension (grams), timer (seconds), epoc time, calibration """
        if self.ui.panelID.text() == "":
            self.panelID = "MN000"
        else:
            self.panelID = self.ui.panelID.text().upper()
        self.wiredata = "_".join(
            [self.panelID, "wire_initial_tension", datetime.now().strftime("%Y%m%d")]
        )
        if not os.path.isfile(
            self.directory + "wire_tensioner_data\\" + self.wiredata + ".csv"
        ):
            with open(
                self.directory + "wire_tensioner_data\\" + self.wiredata + ".csv", "w"
            ) as f:
                f.write(
                    "Date,Panel,WirePosition,Tension(grams),WireTimer(seconds),Epoc,Calibration\n"
                )
        with open(
            self.directory + "wire_tensioner_data\\" + self.wiredata + ".csv", "a+"
        ) as f:
            f.write(
                ",".join(
                    [
                        datetime.now().strftime("%Y%m%d_%H%M"),
                        self.panelID,
                        str(self.ui.strawnumbox.value()),
                        self.ui.tensionlabel.text().strip("-"),
                        self.ui.strawtimelabel.text(),
                        str(time.time()),
                        self.ui.calibfactor.text(),
                    ]
                )
                + "\n"
            )
        self.ui.recordlabel.setText(
            "Wire %s tension recorded" % self.ui.strawnumbox.value()
        )

    def tension_wire(self, pretension=True):
        self.thdl.join()
        self.wirestarttime = int(time.time())
        self.ui.statuslabel.setText("Tensioning wire")
        self.ui.tensionlabel.setText("")
        self.micro = serial.Serial(port=self.port, baudrate=9600, timeout=0.08)
        if pretension:
            self.micro.write(b"p")
            self.micro.write(b"\n")
        self.micro.write(b"t")
        self.micro.write(b"\n")
        self.micro.close()
        self.start_data()
        self.ui.statuslabel.setText("Wire tensioned")

    def next(self):
        """ Update GUI with new data """
        data_list = list(self.thdl.transfer(self.thdl.qs))
        if len(data_list) > 0:
            tension = "%.2f" % data_list[0][1]
            self.ui.tensionlabel.setText(tension)
        wiretimer = int(time.time()) - self.wirestarttime
        self.ui.strawtimelabel.setText(str(wiretimer))

    def increment_straw(self):
        """ increment straw number by 2 if straw layer selected """
        self.thdl.join()
        if self.ui.topcheck.isChecked() or self.ui.bottomcheck.isChecked():
            self.ui.strawnumbox.setValue(self.ui.strawnumbox.value() + 2)
        else:
            self.ui.strawnumbox.setValue(self.ui.strawnumbox.value() + 1)
        self.reset()  # rest motor and start data
        self.ui.recordlabel.setText("")

    def reset(self):
        """ reset stepper motor to fully extended postion """
        self.thdl.join()  # end current thread
        self.wirestarttime = int(time.time())
        self.ui.statuslabel.setText("Resetting motor")
        self.ui.tensionlabel.setText("")
        self.micro = serial.Serial(port=self.port, baudrate=9600, timeout=0.08)
        self.micro.write(b"r")
        self.micro.write(b"\n")
        self.micro.close()
        self.start_data()
        self.ui.statuslabel.setText("Motor reset")

    def closeEvent(self, *args, **kwargs):
        """ End continuous data monitoring and free Arduino when GUI is closed """
        super(QMainWindow, self).closeEvent(*args, **kwargs)
        self.reset()
        self.thdl.join()
