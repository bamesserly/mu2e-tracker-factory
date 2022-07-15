from pathlib import Path
from guis.common.getresources import GetProjectPaths, pkg_resources
import csv
from guis.common.panguilogger import SetupPANGUILogger

logger = SetupPANGUILogger("root", tag="find_pmf", be_verbose=False)

paths = GetProjectPaths()


def get_pmf_list():
    straws = []
    for file in Path(paths["palletsLTG"]).rglob("*.csv"):
        if file.is_file() and file.stem[4:5] == "3":
            f = open(file, "r")
            reader = csv.reader(f)
            for row in reader:
                for item in row:
                    if len(item) > 1:
                        if item[:2] == "ST":
                            straws.append(item)
    return straws


def is_pmf(straw):
    straws = get_pmf_list()
    if straw in straws:
        return True
    else:
        return False


if __name__ == "__main__":
    while True:
        straw = input("Please input the straw number: ")
        if is_pmf(straw) is True:
            logger.info(straw + " is a PMF.")
        else:
            logger.info(straw + " is not a PMF.")
