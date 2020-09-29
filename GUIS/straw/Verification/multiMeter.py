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

# import PyUSB
import visa
import pyvisa
import time
from datetime import datetime


class MultiMeter:
    def __init__(self):
        ##**Initializing VISA & DMM**##
        self.rm = (
            visa.ResourceManager()
        )  # This will fail if multimeter is not turned on

        if self.rm != None:
            self.dmm = self.rm.open_resource("USB0::0x0957::0x0607::MY47003138::INSTR")
            self.dmm.write("*rst; status:preset; *cls")
        # dmm = Digital Multi Meter

    ##**Functions**##
    def _res_meas(self):
        res = []
        num_of_samples = 20
        overload = 0
        for i in range(num_of_samples):
            if overload < 3:
                val = self.dmm.query_ascii_values("MEAS:RES?")
                res.extend(val)
                if res[i] > 9e37:
                    overload += 1
            else:
                return 9e37  # If 3 overloads are recorded, basically returns Infinity

        return min(res)  # Returns minimum of 20 samples

    def collect_data(self):
        resistance_measurements = list()

        # Gather data sets
        for _ in range(5):
            new_measurement = self._res_meas()
            if new_measurement == 9e37:
                return 9e37
            resistance_measurements.append(new_measurement)
            time.sleep(0.05)  # slight break between samples

        # Calculate average
        final_measurement = sum(resistance_measurements) / len(resistance_measurements)

        return final_measurement

    def main(self):
        while True:
            input("Press ENTER to measure resistance")
            print(self.collect_data())


if __name__ == "__main__":
    MultiMeter().main()
