import csv
import datetime

straws = list()
with open(
    os.path.dirname(__file__) + "\\..\\..\\..\\Data\\Straw storage\\StorageRejected.csv",
    "r",
) as f:
    reader = csv.DictReader(f)
    headers = reader.fieldnames
    for straw in reader:
        straws.append(straw)
straws = sorted(straws, key=lambda row: row["timestamp"])
with open(
    os.path.dirname(__file__)
    + "\\..\\..\\..\\Data\\Straw storage\\StorageStorageRejected.csv",
    "w",
) as f:
    writer = csv.DictWriter(f, headers)
    for line in straws:
        writer.writerow(line)
