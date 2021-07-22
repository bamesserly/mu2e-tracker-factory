# ===============================================================================
# Launch the paas heater gui, which controls the heater arduino box.
# Save the data to a csv file in
# data/Panel\ Data/external_gui_data/heat_control_data
# ===============================================================================
from guis.panel.heater.PanelHeater import HeatControl
from guis.common.panguilogger import SetupPANGUILogger
from PyQt5.QtWidgets import QApplication
import serial  ## from pyserial
import sys, traceback, time

logger = SetupPANGUILogger("root", "HeaterStandalone")


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


# Return a string of length 3 of only numbers
# Ignore any and all alphas
def GetPanelFromUserInput():
    while True:
        panelid = input("Panel ID> ")
        import re

        panelid = re.sub("[^0-9]", "", str(panelid))  # strip alphas
        try:
            assert 1 <= int(panelid) and int(panelid) <= 999
            panelid = panelid.zfill(3)  # left pad with zeros
            assert len(panelid) == 3
            break
        except:
            print("Unable to parse panel ID. Enter a 3-digit panel number or MNXXX")

    return panelid


def GetProcessFromUserInput():
    while True:
        pro = input(
            "Which heating process?\n[1] Process 1, PAAS A only\n[2] Process 2, PAAS A and PAAS B\n[6] Process 6 PAAS A and PAAS C\n> "
        )
        try:
            assert pro in [1, 2, 6]
            break
        except:
            print("Invalid process, must be 1, 2, or 6")

    return pro


def run():

    # heater control uses Arduino Micro: hardware ID 'VID:PID=2341:8037'
    port = getport("VID:PID=2341:8037")

    # which panel
    panelid = GetPanelFromUserInput()

    ##which process
    # pro = GetProcessFromUserInput()

    print(f"Heating panel MN{panelid}")  # , process {pro}.")

    logger.info("Arduino Micro at {}".format(port))

    # view traceback if error causes GUI to crash
    sys.excepthook = traceback.print_exception

    # GUI
    app = QApplication(sys.argv)
    ctr = HeatControl(port, panel=f"MN{panelid}", saveMethod=lambda a, b: None)
    ctr.show()
    app.exec_()


if __name__ == "__main__":
    run()
