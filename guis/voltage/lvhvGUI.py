import sys
import pyqtgraph as pg

from lvhvUI import Ui_MainWindow
from channelWidgetUI import Ui_form
from channelMiniWidgetUI import Ui_Form as Ui_Form_Mini

# for GUI widget management
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QTableWidget,
    QGridLayout,
    QScrollArea,
    QWidget,
    QComboBox,
    QListWidget,
    QListWidgetItem,
    QCheckBox,
    QPushButton,
    QTableWidgetItem,
    QLineEdit,
    QMessageBox,
    QStyleFactory
)


class channelWidget(QWidget):
    def __init__(self, ui_layout=Ui_form, voltageType="hv", channelNum=-1, saveTo=None):
        # init widget
        QWidget.__init__(self)

        # create and setup widget ui
        self.wid = Ui_form()
        self.wid.setupUi(self)

        # change labels
        self.wid.channelLabel.setText(f'{voltageType.upper()} Channel {channelNum}')
        self.wid.saveToLabel.setText(f'Saving to {"nowhere" if saveTo is None else saveTo}')

        # init graph
        self.pItem = pg.PlotItem()
        self.plot = pg.plot()
        self.wid.graphVerticalLayout.addWidget(self.plot)

    def __repr__(self):
        return str(self.wid.channelLabel.text())

class channelMiniWidget(QWidget):
    def __init__(self, ui_layout=Ui_form, voltageType="hv", channelNum=-1):
        # init widget
        QWidget.__init__(self)

        # create and setup widget ui
        self.wid = Ui_Form_Mini()
        self.wid.setupUi(self)

        # change label
        self.wid.channelLabel.setText(f'{voltageType.upper()} Channel {channelNum}')



class lvhvGUI(QMainWindow):
    def __init__(self,ui_layout=Ui_MainWindow):
        # init window
        QMainWindow.__init__(self)

        # create and setup ui member
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.lvScrollAreaLayout.setContentsMargins(0,0,0,0)

        # current number of channels
        self.numChannels = 0


        self.ui.actionLow_Voltage.triggered.connect(
            lambda: self.addChannel("lv", self.numChannels+1)
        )
        self.ui.actionHigh_Voltage.triggered.connect(
            lambda: self.addChannel("hv", self.numChannels+1)
        )
        

    def addChannel(self, voltageType, channelNum):
        newChannel = channelWidget(voltageType=voltageType, channelNum=channelNum)
        newChannelMini = channelMiniWidget(voltageType=voltageType, channelNum=channelNum)
        self.numChannels += 1
        if voltageType == "lv":
            self.ui.lvScrollAreaLayout.addWidget(newChannel)
            self.ui.lvMiniScrollAreaLayout.addWidget(newChannelMini)
        else:
            self.ui.hvScrollAreaLayout.addWidget(newChannel)
            self.ui.hvMiniScrollAreaLayout.addWidget(newChannelMini)


def run():
    app = QApplication(sys.argv)  # make an app
    app.setStyle(QStyleFactory.create("Fusion"))  # aestetics

    window = lvhvGUI(Ui_MainWindow())  # make a window
    window.showMaximized() # show the gui

    app.exec_()  # run the gui


if __name__ == "__main__":
    run()
