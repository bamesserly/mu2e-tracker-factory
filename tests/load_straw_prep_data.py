from pathlib import Path
from guis.common.getresources import GetProjectPaths, pkg_resources
import csv


def parse_files():
    '''
    straws = []
    for file in Path(paths["prepdata"]).rglob("*.csv"):
        f = open(file, "r")
        reader = csv.reader(f)
        for row in reader:
            for item in row:
                if len(item) > 1:
                    if item[:2].upper() == "ST":
                        straws.append(item)
    return straws
    '''
    
    
    # format: time, cpalid, cpal, paper pull time, worker
    straws = []
    
    for file in Path(paths['prepdata']).rglob('*.csv'):
        f = open(file,'r')
        reader = csv.reader(f)
        prefix_list = []
        for row in reader:
            if len(str(row[0])) == 16 and 2015 < int(str(row[0])) < 2023:
                for i in range(0,5):
                    prefix_list[i] = str(row[i])
    

    