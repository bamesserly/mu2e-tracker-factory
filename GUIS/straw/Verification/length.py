class Length:
    def __init__(self,length=float(),units="mm"):
        self.length = length
        self.units = units
        self.switchUnits = {
            "mm": lambda x: x*25.4, # switches in to mm
            "in": lambda x: x/25.4  # switches mm to in
        }

    def getUnits(self):
        return self.units
    
    def getLength(self):
        return self.length

    def __add__(self,otherLength):
        print("called add")
        l = otherLength.getLength()
        if otherLength.getUnits() != self.units:
            print("switching units")
            l = self.switchUnits[self.units](l)
        self.length += l

    def __radd__(self,otherLength):
        self.__add__(otherLength)

    def __sub__(self,otherLength):
        self.__add__(Length(-otherLength.getLength(),otherLength.getUnits()))

    def __rsub__(self,otherLength):
        self.__sub__(otherLength)

def main():
    l1 = Length(5,"in")
    l2 = Length(100,"mm")
    l1 + l2
    print(l1.getLength())

if __name__=="__main__":
    main()
