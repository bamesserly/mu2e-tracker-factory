# ===============================================================================
# Launch the paas heater gui, which controls the heater arduino box.
# Save the data to a csv file in
# data/Panel\ Data/external_gui_data/heat_control_data
# ===============================================================================
from guis.panel.heater.PanelHeater import HeatControl
from guis.common.panguilogger import SetupPANGUILogger
from PyQt5.QtWidgets import QApplication
import serial  ## from pyserial
import sys, traceback, time, re

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
def check_panel_id(panelid):
    if not panelid:  # none provided so get from user input
        panelid = input("Panel ID> ")
    while True:
        panelid = re.sub("[^0-9]", "", str(panelid))  # strip alphas
        try:
            assert 1 <= int(panelid) and int(panelid) <= 999
            panelid = panelid.zfill(3)  # left pad with zeros
            assert len(panelid) == 3
            break
        except:
            print("Unable to parse panel ID. Enter a 3-digit panel number or MNXXX")

    return panelid


def run(panelid=None):

    # heater control uses Arduino Micro: hardware ID 'VID:PID=2341:8037'
    port = getport("VID:PID=2341:8037")

    # which panel
    panelid = check_panel_id(panelid)

    print(f"Heating panel MN{panelid}")

    logger.info("Arduino Micro at {}".format(port))

    # view traceback if error causes GUI to crash
    sys.excepthook = traceback.print_exception

    # GUI
    app = QApplication(sys.argv)
    ctr = HeatControl(port, panel=f"MN{panelid}")
    ctr.show()
    app.exec_()


if __name__ == "__main__":
    run(sys.argv[1])
