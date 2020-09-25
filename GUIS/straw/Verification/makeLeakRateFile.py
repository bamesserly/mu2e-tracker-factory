import csv
import os

dataList = []
leaktest_result_path = (
            os.path.dirname(__file__)
            + "/../../../Data/Leak test data/Leak Test Results/Leak Test Results.csv"
)
leaktest_result_old_path = (
            os.path.dirname(__file__)
            + "/../../../Data/Leak test data/Leak test results old/Leak Test Results.csv"
)
leaktest_old_result_old_path = (
            os.path.dirname(__file__)
            + "/../../../Data/Leak test data/Leak test results old/Old Leak Test Results.csv"
)

pathlist = [leaktest_result_path, leaktest_result_old_path, leaktest_old_result_old_path]
for el in pathlist:
    with open(el) as csvf:
        reader = csv.reader(csvf)
        while True:
            try:
                dataList.append(reader.__next__())
            except:
                break
csvf.close()
file = open("leakratefile.csv","w")
file.close()
file = open("leakratefile.csv","a")
file.write('straw, date/time, co2, worker, chamber, leakRate, error')
for el in dataList:
    string = ""
    for i in el:
        string += i + ', '
        string = string.lower()
    file.write(string + "\n")
file.close()
