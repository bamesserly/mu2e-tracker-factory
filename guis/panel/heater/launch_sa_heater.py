from guis.panel.heater.PanelHeater import HeatControl
from guis.common.panguilogger import SetupPANGUILogger
from PyQt5.QtWidgets import QApplication
import serial  ## from pyserial
import sys, traceback, time

logger = SetupPANGUILogger("root", "HeaterStandalone")


"""
lambda temp_paas_a, temp_paas_bc: (
    self.DP.savePanelTempMeasurement(temp_paas_a, temp_paas_bc)
)
"""


def getport(hardwareID):
    """Get COM port number. Distinguish Arduino types when multiple devices are connected
    (also works on General Nanosystems where Arduinos recognized as "USB Serial")."""
    ports = [
        p.device for p in serial.tools.list_ports.comports() if hardwareID in p.hwid
    ]
    if len(ports) < 1:
        logger.error("Arduino not found \nPlug device into any USB port")
        time.sleep(2)
        sys.exit()
    return ports[0]


def run():
    # heater control uses Arduino Micro: hardware ID 'VID:PID=2341:8037'
    port = getport("VID:PID=2341:8037")
    logger.debug("Arduino Micro at {}".format(port))

    # view traceback if error causes GUI to crash
    sys.excepthook = traceback.print_exception

    # Data Processor
    self.DP = DataProcessor(
        gui=self,
        save2txt=SAVE_TO_TXT,
        save2SQL=SAVE_TO_SQL,
        lab_version=LAB_VERSION,
        sql_primary=bool(PRIMARY_DP == "SQL"),
    )

    # GUI
    app = QApplication(sys.argv)
    ctr = HeatControl(port, panel="MN000")
    ctr.show()
    app.exec_()


if __name__ == "__main__":
    run()
