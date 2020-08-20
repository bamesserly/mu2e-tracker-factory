from least_square_linear import *
from WriteToFile import *
import csv

class RefitLeakData:
    def __init__(self):
        self.directory = "Z:\\Production_Environment\\GUIS\\straws\\Leak Test GUI\\Leak Test Results\\"
        self.leak_rate = 0
        self.leak_rate_err = 0
        self.error = False
        self.file = ''
        self.skip = 0
        self.excluded_time = 120

    def refit(self):
        PPM = []
        PPM_err = []
        starttime = 0
        timestamp = []
        slope = []
        slope_err = []
        intercept = []
        intercept_err = []
        conversion_rate = 0.14
        chamber_volume = [594,607,595,605,595,606,609,612,606,595,592,603,612,606,567,585,575,610,615,587,611,600 \
        ,542,594,591,598,451,627,588,649,544,600,534,594,612,606,594,515,583,601,557,510,550,559,527,567,544,572,561,578]
        chamber_volume_err = [13,31,15,10,21,37,7,12,17,15,15,12,7,4,2,8,15,6,10,11,4,3,8,6,9,31,11,25,20,16,8,8,11,8,6,6,10,8,10,8,6,8,6,9,6,7,6,8,7,6]
        try:
            chamber = int(self.file[15:17])
        except:
            chamber = int(self.file[15:16])

        try:
            with open(self.directory + self.file + '.txt',"r+",1) as readfile :
                index = 0

                for line in readfile:
                    numbers_float = line.split()[:3]
                    index = index + 1
                    if numbers_float[2] == '0.00' or index <= self.skip: 
                        continue
                    if starttime == 0 :
                        starttime = float(numbers_float[0])
                    eventtime = float(numbers_float[0]) - starttime
                    if eventtime > self.excluded_time :
                        timestamp.append(eventtime)
                        PPM.append(float(numbers_float[2]))
                        PPM_err.append(((float(numbers_float[2])*0.02)**2+20**2)**0.5)

            slope = get_slope(timestamp, PPM, PPM_err)
            if slope == 0:
                slope = 1e-100
            slope_err = get_slope_err(timestamp,PPM,PPM_err)
            intercept = get_intercept(timestamp,PPM,PPM_err)
            intercept_err = get_intercept_err(timestamp,PPM,PPM_err)
            self.leak_rate = slope*chamber_volume[chamber]*(10**-6)*60 * conversion_rate
            self.leak_rate_err = ((self.leak_rate/slope)**2 * slope_err**2 +
                                (self.leak_rate/chamber_volume[chamber])**2 * chamber_volume_err[chamber]**2)**0.5
        except Exception as e:
            print(e)
            self.error = True

    def main(self):
        self.file = input("\nEnter file name (no extension): ").strip().lower()
        self.skip = int(input("Enter number of data points to skip: ").strip())
        self.refit()
        if self.error:
            print("\nSomething went wrong.\n")
        else:
            print("\nLeak Rate and Error: ")
            print(round(self.leak_rate,7), round(self.leak_rate_err,8))
            input("\nPress enter to continue.")

if __name__=="__main__": 
    app = RefitLeakData()
    app.main()
