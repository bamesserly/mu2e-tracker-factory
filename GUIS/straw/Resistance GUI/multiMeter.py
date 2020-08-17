#
#   multiMeter.py
#
#   Author:            Joseph Dill
#   Email:         <kampa041@umn.edu>
#   Institution: University of Minnesota
#   Project:              Mu2e
#   Date:				6/19/17
#
#   This is a modified version of: 2-WireStrawResistanceMeasurement.py
#
#   Author:             Cole Kampa
#   Email:         <kampa041@umn.edu>
#   Institution: University of Minnesota
#   Project:              Mu2e
#   Date:				6/19/17
#
#   Description:
#   A Python 3 script using VISA to control an Agilent 34410A Digital MultiMeter (DMM).
#   Takes 5 data sets of 20 resistance measurements each. Returns the average of the minimum from each set.
#
#   Libraries: pyvisa (with NI-VISA backend) 
#

import visa
import pyvisa
import time
from datetime import datetime

class MultiMeter:
    def __init__(self):
        ##**Initializing VISA & DMM**##
        self.rm = visa.ResourceManager()
        try:
            self.dmm = self.rm.open_resource('USB0::0x0957::0x0607::MY47003138::INSTR')
            self.dmm.write("*rst; status:preset; *cls")
        except pyvisa.errors.VisaIOError:
            raise MultiMeterNotTurnedOn("TURN ON THE MULTIMETER!")

    def measure(self):
        try:
            return float(self.dmm.query_ascii_values('MEAS:RES?')[-1])
        except pyvisa.errors.VisaIOError:
            raise MultiMeterNotTurnedOn("TURN ON THE MULTIMETER!")

class MultiMeterNotTurnedOn(Exception):
    pass

def main():
    while True:
        while True:
            try:
                m = MultiMeter()
                break
            except MultiMeterNotTurnedOn:
                m = None
                input("The multimeter is not connect to the computer. Make sure it is turned on, then press ENTER to reconnect.")
        print("Multimeter connected!")
        while True:
            input("Press ENTER to collect data.")
            try:
                print(format(m.measure(),"3.2f"))
            except MultiMeterNotTurnedOn:
                break

if __name__=="__main__":
    main()