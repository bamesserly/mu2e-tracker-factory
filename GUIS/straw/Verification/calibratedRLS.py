import time
import sys
from rls32019q import RLS_E2019Q
from tempHumid import getTemp

# Python class that handles calibration of RLS device
# Handles all units in "mm". Only converts to "in" as necessary for display purposes.

class CalibratedRLS(RLS_E2019Q):
    def __init__(self,com="COM7",baudrate=9600):
        super().__init__(com,baudrate)
        self.TIME_LIMIT = 15
        self.calibration_time = float()
        # self.calibration_slope = float()
        # self.calibration_intercept = float()
        self.difference = float()

    def checkCalibration(self):
        if time.time() - self.calibration_time > 60*self.TIME_LIMIT:
            if self.calibration_time != float():
                print("\nIt's been more than {t} minutes since the last calibration...".format(t=self.TIME_LIMIT))
            self.calibrate()

    def calibrate(self):
        print("\n\n---RLS CALIBRATION---")
        input("Press ENTER to Zero")
        self.setZeroPos()
        input("Press ENTER to mark the length of the 35.998\" calibration rod")
        self.difference = self.getEncPos("mm") - self.convert_in_to_mm(35.998)
        self.calibration_time = time.time()

    def correctedLength(self,L):
        return L - self.difference

    # This function is conducted in "in" to work with expansion formula.
    # Converts back to "mm" before returning.
    def getCalibrationRodLength(self,nominal_length):
        
        temp_bas = 68.0
        temp_now = getTemp("F")
        temp_cor = 0.0

        # Apply length-adjustment formula
        adjusted_length = nominal_length*(1.0 + (temp_cor*(temp_now-temp_bas)))

        return self.convert_in_to_mm(adjusted_length)

    def getLength(self):
        return self.correctedLength(self.getEncPos("mm"))

    def measure(self,units="mm"):

        self.checkCalibration()

        while True:
            if input("\nPress ENTER to measure length. To calibrate, first type 'c'.").strip().lower() == "c":
                self.calibrate()
            else:
                length = self.getLength()
                if units == "in":
                    length = self.convert_mm_to_in(length)
                return length

    # Proof that calibration is working correctly-- measure length of 24.002 in rod
    def main(self):
        dsrd_leng = float(input("Enter desired length (mm): "))
        meas_leng = self.measure("mm")
        difference = meas_leng-dsrd_leng
        print("Length:     " + format(meas_leng, "8.3f") + " mm")
        print("Difference: " + format(difference, ".5f") + " mm")

if __name__=="__main__":
    CalibratedRLS().main()
