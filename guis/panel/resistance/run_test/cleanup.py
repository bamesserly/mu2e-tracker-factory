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
def MakeMeasurementDF(f):
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

    print(df.columns.str.strip())

    # some files have messed up headers
    # '# Position'   wire/straw   ADC values...   resistance   PASS?
    if "# Position" not in df.columns.str.strip():
        return pd.DataFrame()

    return df


# combine all the data from list of files for panel into one df
def ConsolidatePanelData(files, panel):
    dfs = []
    for f in files:
        df = pd.DataFrame()
        fname = f.stem.split("_")

        # new format filename ["resistance_test", "MN115", "20210628", "pro3"]
        if len(fname) == 4:
            # make sure this file belongs in this folder
            if fname[1] == panel:
                df = MakeMeasurementDF(f)
                # add panel, date, process info to df
                df["panel"] = fname[1]
                df["date"] = fname[2]
                df["pro"] = fname[3]
            else:
                print(
                    f"WARNING: {f.stem} found in {panel} dir.\n"
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
        print(f"{panel}: {len(dfs)} usable measurements found.")
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
    panels = sorted(Path(topdir).glob("*"))
    panel_data = []
    # Loop panels
    for panel_dir in panels:
        if not panel_dir.is_dir() or panel_dir.name.startswith("."):
            continue

        if panel_dir.name != "MN120":
            continue

        # add all the measurements for this panel to single df
        files = sorted(Path(panel_dir).rglob("*.csv"))

        # require panel to have pro2, pro3, and qc measurements
        if (
            any("proc2" in i.stem.split("_") for i in files)
            and any("proc3" in i.stem.split("_") for i in files)
            and any("finalQC" in i.stem.split("_") for i in files)
        ):
            pass
            # print(f"    {panel_dir.name} has all three measurements.", len(files))
        else:
            # print(f"    {panel_dir.name} is missing a measurement.", len(files))
            continue

        # Collect all data into a single df
        panel_df = ConsolidatePanelData(files, panel_dir.name)
        if panel_df.empty:
            print(f"    empty df somehow for {panel_dir.name}.")
            continue

        # drop NaNs
        panel_df = panel_df.dropna()

        # column names in raw data are wrong
        panel_df = RenameColumns(panel_df)

        # require 50 measurements for each process
        n_pro2 = panel_df["pro"].astype(str).str.contains("proc2").sum()
        n_pro3 = panel_df["pro"].astype(str).str.contains("proc3").sum()
        n_qc = panel_df["pro"].astype(str).str.contains("finalQC").sum()
        if n_pro2 < 50 or n_pro3 < 50 or n_qc < 50:
            print("pro 2, 3, and qc datapoints:", n_pro2, n_pro3, n_qc)
            print("one of these is < 50 so skipping this panel", panel_dir.name)
            continue

        panel_data.append(panel_df)

        print(panel_df.to_string())

    return panel_data


def main():
    # ParseAll() # done, only needs to be done once
    # list of data frames for the resistance measurement of each panel
    panel_resistance_measurements = IntermediateClean()
    print("Done")
