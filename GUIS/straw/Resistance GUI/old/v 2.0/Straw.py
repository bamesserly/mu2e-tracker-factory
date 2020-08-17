class Straw:
    def __init__(self):
        self.V5 = None #should always be 5 volts
        self.measurements = [] #the 4 unaltered Arduino measurements
        self.r2 = None #one number
        self.devRes = [] #the device resistance associated with every measurement
        self.perErr = [] #the % error for each measurement
        self.finalMeas = [] #the actual resistance value
        
    def setCalibInfo(self,V5,r2):
        self.V5 = float(V5)
        self.r2 = float(r2)

    def appendDevResistance(self,devResist,perE):
        self.devRes.append(float(devResist))
        self.perErr.append(float(perE))

    def appendMeasurement(self,data):
        self.measurements.append(float(data))
        
    def calibrateData(self):
        intermediate = []
        resistNum = []
        print("Begin Straw.calibrateData()")
        for el in self.measurements:
            dData = None
            if el == None:
                print('arduino problem')
            elif self.V5 == None:
                print('calib error')
            dData = el * self.V5 / 1023
            intermediate.append(dData)
        for el in intermediate:
            if el != 0:
                data = None
                data = self.r2 * (self.V5 - el) / el
                resistNum.append(data)
            else:
                resistNum.append(1000000)
        for i in range(len(resistNum)):
            final = (resistNum[i] / (1 - self.perErr[i])) - self.devRes[i]
            self.finalMeas.append(final)

    def printData(self): #for debugging
        print(self.V5)
        print('-------------------------')
        print(self.measurements)
        print('-------------------------')
        print(self.r2)
        print('-------------------------')
        print(self.devRes)
        print('-------------------------')
        print(self.perErr)
        print('-------------------------')
        print(self.finalMeas)

    def calibPrint(self):
        print(self.measurements)

    def reset(self):
        self.measurements = [] #the 4 unaltered Arduino measurements
        self.devRes = [] #the device resistance associated with every measurement
        self.perErr = [] #the % error for each measurement
        self.finalMeas = [] #the actual resistance value
        
