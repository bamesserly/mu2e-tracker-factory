def main():
    while True:
        while True:
            strawID = input("\nscan straw id: ")

            usable = open(
                os.path.dirname(__file__)
                + "..\\..\\..\\Data\\Straw storage\\StorageRejected_Usable.csv",
                "r",
            )
            recut = open(
                os.path.dirname(__file__)
                + "..\\..\\..\\Data\\Straw storage\\StorageRejected_Recut.csv",
                "r",
            )
            practice = open(
                os.path.dirname(__file__)
                + "..\\..\\Data\\Straw storage\\StorageRejected_Practice.csv",
                "r",
            )

            found = False

            for line in usable:
                if strawID.upper() in line.upper():
                    print("Usable")
                    found = True

            if found:
                break

            for line in recut:
                if strawID.upper() in line.upper():
                    print("Re-Cut")
                    found = True

            if found:
                break

            for line in practice:
                if strawID.upper() in line.upper():
                    print("Practice")
                    found = True

            if not found:
                print("try again")
                break


if __name__ == "__main__":
    main()
