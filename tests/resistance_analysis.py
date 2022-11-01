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
import matplotlib.pyplot as plt
import numpy as np
from guis.common.panguilogger import SetupPANGUILogger

logger = SetupPANGUILogger("root", tag="res_ana")

pd.set_option("mode.use_inf_as_na", True)  # set all inf --> NaN
kMAXRES = 300  # cut resistance measurements above this
kNMINPOINTS = 25  # every good measurement must have at least 25 data points
kREQUIREALLMEASUREMENTS = (
    True  # require that there be at least one pro2, pro3, and qc measurement
)

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


# parsing program does not fix columns, so do it here.
def RenameColumns(df):
    df.columns = df.columns.str.strip()
    df = df.rename(columns={"resistance": "resistance_err"})
    df = df.rename(columns={"ADC values...": "resistance"})
    df = df.rename(columns={"wire/straw": "wire-straw"})
    df = df.rename(columns={"# Position": "position"})
    df = df.drop(columns=["PASS?"])
    return df


# old file format, file not in correct directory
def IsGoodFile(fname, panel):
    # new filename format ["resistance_test", "MN115", "20210628", "pro3"]
    # old file format ["resistance_test", "20210628"]
    if len(fname) != 4:
        return False

    # file in wrong folder?
    if fname[1] != panel:
        return False

    return True


# Make a df from a single csv file.
# If something goes wrong, return an empty csv, otherwise assume df is viable
def MakeDF(f, panel):
    fname = f.stem.split("_")

    if not IsGoodFile(fname, panel):
        # logger.debug(f"{panel} bad file")
        return pd.DataFrame()

    # read in csv, skip empty files
    # column names are in the 5th row
    df = pd.DataFrame()
    try:
        df = pd.read_csv(f, skiprows=4)
        assert not df.empty
    except pd.errors.EmptyDataError:
        # logger.debug(f"{panel} empty df during read")
        return pd.DataFrame()
    except AssertionError:
        # logger.debug(f"{panel} empty df after read")
        return pd.DataFrame()

    # some files have messed up headers
    # ' # Position' ' wire/straw' ' ADC values...'  ' resistance' ' PASS?'
    if "# Position" not in df.columns.str.strip():
        # logger.debug(f"{panel} columns problem after read")
        return pd.DataFrame()

    # add panel, date, process
    if not df.empty:
        df["panel"] = fname[1]
        df["date"] = fname[2]
        df["pro"] = fname[3]

    return df


# Make a data frame from all the csv resistance data in the given directory
# Return an empty df if something goes wrong
def CombineAllPanelData(panel_dir):
    # skip this dir if it's not a normal panel resistance dir
    if not panel_dir.is_dir() or panel_dir.name.startswith("."):
        return pd.DataFrame()

    # collect all the csv files
    files = sorted(Path(panel_dir).rglob("*.csv"))

    # require panel to have pro2, pro3, and qc measurements
    if kREQUIREALLMEASUREMENTS:
        if (
            any("proc2" in i.stem.split("_") for i in files)
            and any("proc3" in i.stem.split("_") for i in files)
            and any("finalQC" in i.stem.split("_") for i in files)
        ):
            pass
        else:
            # logger.debug(f"{panel_dir.name} not all three pro measurements")
            return pd.DataFrame()

    # get a df from each file
    dfs = []
    for f in files:
        df = MakeDF(f, panel_dir.name)
        if not df.empty:
            dfs.append(df)

    # combine all the panel's dfs
    if dfs:
        print(f"{panel_dir.name}: {len(dfs)} usable measurements found.")
        return pd.concat(dfs)
    else:
        return pd.DataFrame()


# pos | w/s | pro  |  r  | timestamp
#  0  |  0  | pro2 | 123 |   111     # wire-straw field not used in pros 2 + 3
#  0  |  0  | pro2 | 456 |   111
#  0  |  0  | pro2 | 456 |   222
#  0  |  0  | pro3 | 789 |   333
#  0  |  1  | qc   | 888 |   444
#  0  |  0  | qc(w)| 999 |   446
#  1  |  0  | pro2 | 124 |   114
def Clean(df):
    # column names in raw data are wrong
    df = RenameColumns(df)

    # force resistances to all be numbers, else turn them into NaN
    df["resistance"] = pd.to_numeric(df["resistance"], errors="coerce")
    df["position"] = pd.to_numeric(df["position"], errors="coerce")

    # drop NaNs
    df = df.dropna()

    # removing resistance outliers
    try:
        df = df[df["resistance"] < kMAXRES]
    except TypeError:
        print(df.to_string())

    # remove final QC //wire// measurements
    df = df.drop(df[(df["wire-straw"] == 1) & (df["pro"] == "finalQC")].index)

    # require kNMINPOINTS measurements for each process
    n_pro2 = df["pro"].astype(str).str.contains("proc2").sum()
    n_pro3 = df["pro"].astype(str).str.contains("proc3").sum()
    n_qc = df["pro"].astype(str).str.contains("finalQC").sum()
    if n_pro2 < kNMINPOINTS or n_pro3 < kNMINPOINTS or n_qc < kNMINPOINTS:
        print("pro 2, 3, and qc datapoints:", n_pro2, n_pro3, n_qc)
        print("one of these is < 50 so skipping this panel", panel_dir.name)
        return pd.DataFrame()

    df = df.reset_index(drop=True)

    return df


def Plot(panel, df):
    ## plot attempt #1
    # fig, ax = plt.subplots()
    # colors = {"proc2":"red", "proc3":"green","finalQC":"blue"}
    # ax.scatter(df['position'], df['resistance'],c=df['pro'].map(colors))#, cmap="viridis")

    # plot attempt #2
    fig, ax = plt.subplots()
    colors = {"proc2": "red", "proc3": "green", "finalQC": "blue"}
    grouped = df.groupby("pro")
    for key, group in grouped:
        try:
            group.plot(
                ax=ax,
                kind="scatter",
                x="position",
                y="resistance",
                label=key,
                c=colors[key],
            )
        except ValueError:
            print()
            print(df.to_string())
    plt.title(panel)
    ax.set_ylim(0, kMAXRES)
    # plt.show()
    plt.draw()
    plt.savefig(f"resistance_{panel}.png")


def main():
    # ParseAll() # done, only needs to be done once

    # list of directories - one for each panel
    topdir = GetProjectPaths()["datatop"] / "PanelResistance_2021-06-22_2" / "RawData"
    panel_directories = sorted(Path(topdir).glob("*"))

    # for each panel (directory):
    panel_data = {}
    for panel_dir in panel_directories:
        # 1. combine csv files into single data frame
        df = CombineAllPanelData(panel_dir)
        if df.empty:
            # logger.debug(f"{panel_dir.name} df did not pass CombineAllPanelData")
            continue

        # 2. clean
        df = Clean(df)
        if df.empty:
            # logger.debug(f"{panel_dir.name} df did not pass Clean")
            continue
        # panel_data[panel_dir.name] = df

        # 3. plot
        logger.info("Saving figures to CD.")
        Plot(panel_dir.name, df)

    print("Done")


if __name__ == "__main__":
    main()
