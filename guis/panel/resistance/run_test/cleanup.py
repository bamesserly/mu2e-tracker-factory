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

pd.set_option("mode.use_inf_as_na", True)  # set all inf --> NaN

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


def RenameColumns(df):
    df.columns = df.columns.str.strip()
    df = df.rename(columns={"resistance": "resistance_err"})
    df = df.rename(columns={"ADC values...": "resistance"})
    df = df.rename(columns={"wire/straw": "wire-straw"})
    df = df.rename(columns={"Position": "position"})
    df = df.drop(columns=["PASS?"])
    return df


# Make a df from a measurement csv file, f
def MakeMeasurementDF(f,fname,panel_dir):
    df = pd.DataFrame()

    # read in csv, skip empty files
    try:
        df = pd.read_csv(f, skiprows=4)  # column names are in the 5th row
        assert not df.empty
    except pd.errors.EmptyDataError:
        # print(f"INFO: {f.stem} is empty. Skipping.")
        return pd.DataFrame()
    except AssertionError:
        # print(f"WARNING: {f.stem} produced empty df. Skipping this file.")
        return pd.DataFrame()

    # some files have messed up headers
    # '# Position'   wire/straw   ADC values...   resistance   PASS?
    if "# Position" not in df.columns.str.strip():
        return pd.DataFrame()

    # add panel, date, process info to df
    df["panel"] = fname[1]
    df["date"] = fname[2]
    df["pro"] = fname[3]

    return df


def ConsolidatePanelData(panel_dir):
    dfs = []

    for f in Path(panel_dir).rglob("*.csv"):
        df = pd.DataFrame()
        fname = f.stem.split("_")

        # new format filename ["resistance_test", "MN115", "20210628", "pro3"]
        if len(fname) == 4:
            # make sure this file belongs in this folder
            if fname[1] == panel_dir.name:
                df = MakeMeasurementDF(f, fname, panel_dir)
            else:
                print(
                    f"WARNING: {f.stem} found in {panel_dir.name} dir.\n"
                    f"Panel file and dir do not match. Skipping this file."
                )

        # old format ["resistance_test", "20210628"]
        elif len(fname) == 2:
            # print(f"INFO: {f.name} is old format. Skipping.")
            # most panels that have measurements in this format are old and
            # won't have corresponding pro2/3 measurements, so we don't care
            # about them right now.
            pass

        # Unknown file format
        else:
            # print(f"ERROR: parsing filename {f.name}.")
            pass

        if not df.empty:
            dfs.append(df)

    if dfs:
        print(f"{panel_dir.name}: {len(dfs)} measurements found.")
        return pd.concat(dfs)
    else:
        return pd.DataFrame()


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
    # Loop panels
    for panel_dir in Path(topdir).glob("*"):
        if not panel_dir.is_dir() or panel_dir.name.startswith("."):
            continue

        if panel_dir.name  != "MN112":
           continue
        print(panel_dir.name)

        # let's start by just looking at clean panels that have a single pro2, pro3, and QC measurements
        # meas_parsed = [m.stem.split("_") for m in measurements]
        # if (any("pro2" in i for i in meas_parsed) and
        #    any("pro3" in i for i in meas_parsed) and
        #    any("finalQC" in i for i in meas_parsed)):
        #    print(f"    {panel_dir.name} has all three measurements.", len(measurements))

        # add all the measurements for this panel to single df
        panel_df = ConsolidatePanelData(panel_dir)
        if panel_df.empty:
            continue

        # drop NaNs
        panel_df = panel_df.dropna()

        # column names in raw data are wrong
        panel_df = RenameColumns(panel_df)

        print(panel_df.to_string())


def main():
    # ParseAll() # done
    IntermediateClean()
    # datafilename = parse_log(raw_data)
    # print("Data file and plots are at", datafilename)
    print("Hello world")
