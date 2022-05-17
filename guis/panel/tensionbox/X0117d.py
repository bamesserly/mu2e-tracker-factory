#### X0117d.py
#### Module for displaying plots in PyQt5 GUI

import sys, random, matplotlib
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *

matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class DataCanvas(FigureCanvas):
    """Each canvas class will use this to embed a matplotlib in the PyQt5 GUI"""

    def __init__(
        self,
        parent=None,
        data=None,
        width=2,
        height=2,
        dpi=100,
        xlabel="xlabel",
        ylabel="ylabel",
        ylabel2=None,
    ):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.axes.clear()
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.axes.grid(True)
        self.axes.set_xlabel(xlabel)
        self.axes.set_ylabel(ylabel)
        self.axes.set_xlim(-2, 96)
        self.axes.set_ylim(bottom=50, top=100)
        # self.axes.autoscale(enable=True, axis='y')
        box = self.axes.get_position()
        if ylabel2:
            self.rhs_axes = self.axes.twinx()
            self.rhs_axes.set_ylabel(ylabel2)
            self.rhs_axes.set_ylim(bottom=-2, top=700)
            self.rhs_axes.yaxis.label.set_color("r")
            # self.rhs_axes.autoscale(enable=True, axis='y')
            self.axes.set_position(
                [box.x0, box.y0 + box.height * 0.05, box.width * 0.95, box.height]
            )
        else:
            self.axes.set_position(
                [box.x0, box.y0 + box.height * 0.03, box.width * 1.1, box.height * 1.1]
            )

    def read_data(self, data, is_rhs=False):
        if is_rhs:
            if self.rhs_axes:
                self.rhs_axes.plot(data[:, 0], data[:, 1], "g.", color="r")
                # data_range = np.ptp(data[:,1])
                # self.rhs_axes.set_ylim(bottom=min(min(data[:,1])-data_range*0.9,0), top=max(data[:,1])*1.1)
                # self.rhs_axes.relim()
        else:
            self.axes.plot(data[:, 0], data[:, 1], "g.", color="k")
            # data_range = np.ptp(data[:,1])
            # self.axes.set_ylim(bottom=min(data[:,1])*0.9, top=max(data[:,1])+data_range*1.1)
            # self.axes.relim()
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()


class PlottingWindow(QDialog):
    """Main app: select plotting parameters and display data"""

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.testbutton.clicked.connect(self.test)
        self.z = np.array([[-10, -10]])
        self.data_widget = QWidget(self.graphicsView)
        layout = QHBoxLayout(self.graphicsView)
        self.canvas = DataCanvas(self.data_widget, data=None)
        layout.addWidget(self.canvas)
        self.data_widget.repaint()
        self.show()

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(500, 400)
        self.testbutton = QPushButton(Dialog)
        self.testbutton.setGeometry(QtCore.QRect(30, 370, 75, 23))
        self.testbutton.setObjectName("testbutton")
        self.graphicsView = QGraphicsView(Dialog)
        self.graphicsView.setGeometry(QtCore.QRect(10, 10, 480, 350))
        self.graphicsView.setObjectName("graphicsView")
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.testbutton.setText(_translate("Dialog", "Test"))

    def test(self):
        """Test point-by-point plot update"""
        n = random.randint(0, 100)
        t = random.random() * 100
        self.z = np.append(self.z, np.array([[n, t]]), axis=0)
        print(self.z)
        self.canvas.read_data(self.z)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ctr = PlottingWindow()
    ctr.show()
    sys.exit(app.exec_())
