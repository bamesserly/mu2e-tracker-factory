
# resistanceMeter Class
# talks to arduino to obtain resistance measurements

import serial
from datetime import datetime
import time
import csv
import os
from Straw import Straw
import sys

#os.system('mode con: cols=115 lines=50')
com = 'Com6'

calibFile = "calib.csv"
dataFile = None
measLet = 'abcdefghijklmnop'

average = 'average'

try:
    cereal = serial.Serial(com, 9600,timeout=10)
    print(cereal.readline().decode('utf-8').rstrip())
except:
    print("No Arduino Connected")
    sys.exit()

class Resistance:
    def __init__(self):
        self.strawList = [Straw() for i in range(24)]
        self.measurements = [[None for i in range(4)] for i in range(24)]
        
    def rMain(self):
        self.getCalibrationData()
        self.setAverage()
        self.getMeasurements()
        for pos in range(1,25):
            self.strawList[pos-1].calibrateData()
                #Record Measurement
            the_straw = self.strawList[pos-1]
            self.measurements[pos-1] = the_straw.finalMeas
                #after getting measurements, clear straw's measurement table
            self.strawList[pos-1].reset()
        return self.measurements        
        
    def setAverage(self):
        cereal.write(b'y')

    def getCalibrationData(self):
        #stores the calib data for each straw within its class
        r2_List = []
        V5 = 0
        Vin = 0
        with open(calibFile) as csvf:
            csvReader = csv.reader(csvf)
            lineCount = 0
            index = 0
            loop = True
            while loop:
                try:
                    text = csvReader.__next__()
                    if lineCount == 1:
                        Vin = float(text[0])
                        V5 = float(text[1])
                    elif lineCount == 3:
                        for el in text:
                            r2_List.append(float(el))
                    elif lineCount > 4:
                        if lineCount % 4 == 1:
                            self.strawList[index].setCalibInfo(V5,r2_List[index//4])
                        self.strawList[index].appendDevResistance(float(text[2]),float(text[1]))
                        if lineCount % 4 == 0:
                            index += 1
                except:
                    loop = False
                lineCount += 1

    def getMeasurements(self): #uses arduino to obtain all resistance measurements for the pallet of straws
        indexList = [[23,19,15,11,7,3],[22,18,14,10,6,2],[21,17,13,9,5,1],[20,16,12,8,4,0]]
        measNum = 1 #position number minus 1
        index = 0
        for char in measLet:
            appendList = indexList[index]
            cereal.write(bytes(char + 'r', 'ascii'))
            rawData = cereal.readline().decode('utf-8').rstrip().split(',')
            if rawData[0] != char:
                return False
            del rawData[0]
            for i in range(len(rawData)):
                strNum = appendList[i]
                self.strawList[strNum].appendMeasurement(rawData[i])
            if measNum % 4 == 0:
                index += 1
            measNum += 1
