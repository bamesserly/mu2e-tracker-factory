import resistance
from resistance import Resistance

v = "none"
input("press enter to start the test")
calibrator = Resistance()
calibrator.rMain()
for el in calibrator.strawList:
    el.calibPrint()
