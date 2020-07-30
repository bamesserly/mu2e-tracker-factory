import serial
import time
from time import gmtime
import calendar
from datetime import datetime, date, timedelta
import csv
import os
import sys

com = "COM9"
ser = serial.Serial(com, 9600)  # port on computer

# filepath = 'C:\\Users\\LArTPC\\Desktop\\temphumid\\data\\464B_data\\'
filepath = "//spa-mu2e-network/Files/Production_Environment/Data/temp_humid_data/464B/"
filename = "464B_" + datetime.now().strftime("%Y-%m-%d_%H%M%S") + ".csv"
date0 = date.today()


f = open(filepath + filename, "w")
print("464B temperature and humidity")
time.sleep(3)

# send character '5' to arduino
# when arduino gets it, it takes data and sends
f.write("date, temp (C), RH (%), epoch time (s)\n")
# try:
while True:
    try:
        ser.write(b"5")  # send arduino the number '5' in ascii
        time.sleep(10)  # wait 2 seconds
        data = str(ser.readline())  # get data from arduino serial
        data = data[2:]
        x = data.split(",")
        temp = x[0]
        humid = x[1]
        humid = humid[:5]

        print("464B -- Temp = " + temp + " C  Humid = " + humid + "%")

        # write to file
        f.write(datetime.now().strftime("%Y-%m-%d_%H%M%S"))
        f.write(",")
        f.write(temp)
        f.write(",")
        f.write(humid)
        f.write(",")
        f.write(str(time.time()))
        f.write("\n")
        f.flush()

        # start new file after midnight
        datecheck = date.today() - date0
        if (datecheck.days) > 0:
            filename = "464B_" + datetime.now().strftime("%Y-%m-%d_%H%M%S") + ".csv"
            date0 = date.today()
            f.close()
            f = open(filepath + filename, "w")
    except Exception as e:
        f.close()  # close file
        ser.close()
        sys.exit(1)


f.close()  # close file
ser.close()
