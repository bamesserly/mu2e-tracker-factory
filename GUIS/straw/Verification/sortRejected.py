import csv


def hasData(straw):
    if straw["ohms"] == "FAIL":
        return False
    try:
        ii = float(straw["ii"])
        oo = float(straw["oo"])
        res_pass = lambda x: 50.0 <= x <= 250.0
        if not res_pass(ii) or not res_pass(oo):
            return False
    except ValueError:
        return False
    try:
        leak = float(straw["leakRate"])
        error = float(straw["leakError"])
        leak_pass = lambda l, e: (0 < l <= 9.65e-5) and (0 < e <= 9.65e-6)
        if not leak_pass(leak, error):
            return False
    except ValueError:
        return False
    return True


def hasUsableLength(straw):
    try:
        difference = float(straw["difference"])
        return abs(difference) <= 0.8
    except ValueError:
        return False


def main():

    practice = []
    use = []
    recut = []
    fieldnames = []

    with open(
        "\\\\MU2E-CART1\\Database Backup\\Straw storage\\StorageRejected.csv", "r"
    ) as rejected_file:
        reader = csv.DictReader(rejected_file)
        fieldnames = reader.fieldnames
        for straw in reader:
            has_data = hasData(straw)
            usable_length = hasUsableLength(straw)

            if has_data and usable_length:
                use.append(straw)

            elif has_data and not usable_length:
                recut.append(straw)

            else:
                practice.append(straw)

    with open(
        "\\\\MU2E-CART1\\Database Backup\\Straw storage\\StorageRejected_Usable.csv",
        "w",
    ) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for straw in use:
            writer.writerow(straw)

    with open(
        "\\\\MU2E-CART1\\Database Backup\\Straw storage\\StorageRejected_Recut.csv", "w"
    ) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for straw in recut:
            writer.writerow(straw)

    with open(
        "\\\\MU2E-CART1\\Database Backup\\Straw storage\\StorageRejected_Practice.csv",
        "w",
    ) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for straw in practice:
            writer.writerow(straw)


if __name__ == "__main__":
    main()
