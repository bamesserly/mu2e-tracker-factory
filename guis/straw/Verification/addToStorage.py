import sys
import csv
import os
from datetime import datetime

# sys.path.insert(0, '//MU2E-CART1/Database Backup/workers/credentials')
# from credentials import *
# from fixChildStraws import VerifyPrep
def main():
    total_date = str(datetime.today())
    date = total_date[5:7] + "/" + total_date[8:10] + "/" + total_date[0:4]
    string_hours = total_date[11:13]
    int_hours = int(string_hours)
    if int_hours > 12:
        int_hours = int_hours - 12
    string_hours = str(int_hours)
    time = string_hours + ":" + total_date[14:16]
    if date[0] == "0":
        date = date[1:]
    date = date + " " + time
    print(date)
    palID = input("CPALID: ").upper()
    palNum = input("CPAL: ").upper()
    worker = input("Worker ID: ")
    # lst = getFailedStraws()
    # cred = Credentials('leng')
    # if not cred.checkCredentials(worker):
    # print("Sorry, I guess you aren't qualified")
    # input("Press enter to exit")
    # return
    pal = palNum[-4:]
    p = int(pal)
    position = 94
    if p % 2 == 0:
        position = 92
    pathToPallet = (
        os.path.dirname(__file__)
        + "\\..\\..\\..\\Data\\Pallets\\"
        + palID
        + "\\"
        + palNum
        + ".csv"
    )
    with open(pathToPallet) as csvf:
        reader = csv.reader(csvf)
        for line in reader:
            if not line:
                continue
            if not line[1] == "silv":
                continue
            pathToStorage = (
                os.path.dirname(__file__)
                + "\\..\\..\\..\\Data\\Straw storage\\storage.csv"
            )
            storage = open(pathToStorage, "a+")
            for j in line:
                if not (j[0:2] == "ST"):
                    if j == "_______":
                        position = position - 4
                    continue
                # if j in lst:
                #    position = position - 4
                #    continue
                string_input = (
                    str(position) + "," + j + "," + date + "," + worker + "\n"
                )
                storage.write(string_input)
                position = position - 4
    # fixer = VerifyPrep(palID,palNum)
    # fixer.main()


def getFailedStraws():
    flag = True
    straws = []
    while input("Did any straws fail silver epox? y/n: ").lower() == "y":
        straws += [input("Enter the straw number (ex. ST06969): ").upper()]
    return straws


main()
