import csv
import datetime

straws = list()
with open(
    "\\\\MU2E-CART1\\Database Backup\\Straw storage\\StorageRejected.csv", "r"
) as f:
    reader = csv.DictReader(f)
    headers = reader.fieldnames
    for straw in reader:
        straws.append(straw)
straws = sorted(straws, key=lambda row: row["timestamp"])
with open(
    "\\\\MU2E-CART1\\Database Backup\\Straw storage\\SortedStorageRejected.csv", "w"
) as f:
    writer = csv.DictWriter(f, headers)
    for line in straws:
        writer.writerow(line)
