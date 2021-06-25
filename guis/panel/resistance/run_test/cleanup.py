################################################################################
# 1. Loop all resistance data files
# 2. Call the parse function to put them into readable, analyzable csv format
# 3. Consolidate up-to 3 data files for each panel into a single file of 96
# lines with all N measurements in columns
#
# pos | LPAL i-i | LPAL i-o | Panel i-i | Panel i-o | QC i/o | QC i/o (wire)
#  0  |          |          |           |           |  123.4 |  824.5
#  1  |          |          |           |           |  123.4 |  824.5
#  2  |          |          |           |           |  567.8 |  768.9
#  3  |          |          |           |           |  567.8 |  768.9
#
# The final columns will be grouped in pairs             ^        ^
################################################################################
from guis.panel.resistance.run_test.parse_log import parse_log
from guis.common.getresources import GetProjectPaths
from pathlib import Path
import os
import pandas as pd

# parse all logfiles into readable/analyzable csv files
# this overwrites!
def ParseAll():
    topdir = GetProjectPaths()["datatop"] / "PanelResistance_2021-06-22_2" / "RawData"
    for raw_datafile in Path(topdir).rglob("*.log"):
        print(raw_datafile)
        try:
            parsed_datafile = parse_log(str(raw_datafile))
        except ValueError:
            print("-----Failed to parse")

# Combine files for each panel
# pos | pro  |  r  | timestamp
#  0  | pro2 | 123 |   111
#  0  | pro2 | 456 |   111 
#  0  | pro2 | 456 |   222
#  0  | pro3 | 789 |   333
#  0  | qc   | 888 |   444
#  0  | qc(w)| 999 |   446
#  1  | pro2 | 124 |   114
#      .............
# We can almost just concatenate all the csv files.
# * need to skip old headers and write a new one
# * need to add the timestamp (from the filename) to a final column
def IntermediateClean():
    topdir = GetProjectPaths()["datatop"] / "PanelResistance_2021-06-22_2" / "RawData"
    for panel_dir in Path(topdir).glob("*"):
        if not panel_dir.is_dir() or panel_dir.name.startswith("."):
            continue
        if panel_dir.name  != "MN115":
            continue
        print(panel_dir.name)
        panel_df = pd.DataFrame(columns = ["Position","wire/straw","ADC values...","resistance","PASS?"])
        #dfs = []
        for f in Path(panel_dir).rglob("*.csv"):
            # skip empty files
            try:
                df = pd.read_csv(f,skiprows=4)
            except pd.errors.EmptyDataError:
                continue
            print(df)
            panel_df.append(df)
        # df = pd.concat(dfs, join="outer", axis=1, sort=False) # this puts dfs side-by-side. Not what I want.
        print(panel_df)
        # merged_data_file = ...
        # loop panel files
            # extract pro and timestamp from filename
            # df = from_csv
            # df + panel | time | pro
            # df[ADC] --> resistance
            # df[res] --> unccertainty

def main():
    #ParseAll() # done
    IntermediateClean()
    #datafilename = parse_log(raw_data)
    #print("Data file and plots are at", datafilename)
    print("Hello world")
