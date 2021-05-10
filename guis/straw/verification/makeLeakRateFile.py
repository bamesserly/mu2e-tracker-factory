import csv
import os
from guis.common.getresources import GetProjectPaths

leaktest_dir = GetProjectPaths()["strawleakdata"]
leaktest_dir_old = GetProjectPaths()["leakdata"]

pathlist = [
    leaktest_dir / "LeakTestResults.csv",
    leaktest_dir_old / "Leak Test Results.csv",
    leaktest_dir_old / "Leak test results old" / "Leak Test Results.csv",
    leaktest_dir_old / "Leak test results old" / "Old Leak Test Results.csv"
]

dataList = []
for el in pathlist:
    with open(el) as csvf:
        reader = csv.reader(csvf)
        while True:
            try:
                dataList.append(reader.__next__())
            except:
                break
csvf.close()
summary_file = leaktest_dir / "StrawLeakSummary.csv"
file = open(summary_file, "w")
file.close()
file = open(summary_file, "a")
file.write("straw, date/time, co2, worker, chamber, leakRate, error")
for el in dataList:
    string = ""
    for i in el:
        string += i + ", "
        string = string.lower()
    file.write(string + "\n")
file.close()
