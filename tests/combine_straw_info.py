# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# # Combine straw info into a couple of csvs
# Initial processing of two types of straw info.
#
# Two sources of info:
# 1. leak rate raw data files: tens of thousands of txt files -- more than one for each straw
# 2. database, which contains batch, ppg, and panel info for most straws since 173
#
# Do a little processing of (1) here: re-extract the leak rates and combine them into a df.
#
# Save to CSVs so they can be imported from another sheet for analysis.

import pandas as pd
from pathlib import Path
import sys

sys.path.append("/Users/Ben/Projects/mu2e-tracker-factory/")

# ## 1. Leak Rate of every straw
# - Loop all 40,000 raw data files and fit the data to get a leak rate
# - Takes ~minutes
# - End result: a data frame with columns: straw, raw data file, fit value, fit error, fit status
# - Minimal cleaning: remove UNKNOWN, FAILED fits, and unphysical leaks < 0.

# indir, location of raw data
# from guis.common.getresources import GetProjectPaths
# indir = GetProjectPaths()["strawleakdata"] / "raw_data"
indir = Path(
    "/Users/Ben/Projects/mu2e-tracker-factory/data/all_straw_leak_data"
)  # collected ALL the data
print(indir)
print(indir.is_dir())

# fitting function
from calc_straw_leak import refit, NotEnoughData

# one row for each file – many rows for one straw are allowed.
leak_data = []
for raw_data_file in indir.rglob("*.txt"):
    straw = str(raw_data_file.name)[2:7]

    # if straw != "23842":
    #    continue

    try:
        straw = int(straw)
    except ValueError:
        print("BAD FILE (FILENAME)", raw_data_file.name)
        continue

    try:
        leak_rate, leak_rate_err, leak_status, chamber = refit(raw_data_file)
    except NotEnoughData:
        continue
    except IndexError as e:
        print("BAD FILE (INDEX)", e, raw_data_file.name)
    except ValueError as e:
        print("BAD FILE (VALUE)", raw_data_file.name)
        # print(e)
        continue

    leak_data.append(
        {
            "straw": straw,
            "leak_data_file": str(raw_data_file.name),
            "rate": leak_rate,
            "rate_err": leak_rate_err,
            #'status':leak_status.value,
            "status": leak_status,
            "chamber": chamber,
        }
    )

leak_df = pd.DataFrame(leak_data)
leak_df["status"] = leak_df["status"].apply(lambda x: x.value)
leak_df

# save all rates to csv for chamber analysis
leak_df.drop(leak_df[leak_df["status"] == "U"].index, inplace=True)
leak_df.to_csv("all_leak_tests_2022-06.csv")
leak_df

# +
# remove lines with negative leak values
leak_df.drop(leak_df[leak_df["rate"] <= 0].index, inplace=True)

# leak_df = leak_df.rename_axis(None)

# remove failed, unknown tests
leak_df.drop(leak_df[leak_df["status"] == "F"].index, inplace=True)
leak_df.drop(leak_df[leak_df["status"] == "U"].index, inplace=True)
leak_df

# +
# Keep one test/rate per file
# Na, don't do this any more. We can do it in the analysis.

# show straws with multiple tests
# straw_df = straw_df.rename_axis(None)
# straw_df[straw_df.straw.duplicated(keep=False)].sort_values(by=['straw'])

# only keep the tests with the smallest leaks
# straw_df = straw_df.groupby('straw', group_keys=False).apply(lambda x: x.loc[x.rate.idxmin()])

# show that we've removed all but the smallest rates
# straw_df[straw_df.straw.duplicated(keep=False)].sort_values(by=['straw']) # throwing error. maybe no duplicates.

# straw_df.sort_values(by=['straw'])
# -

# ## 2. Panel, batch, and PPG info

# +
# organized by their panel; includes batch, position number
# straw_list_file = Path("straws_on_panels.csv")
# straw_list_file = Path("2022-04-07_straws_on_panels.csv")
# straw_list_file = Path("2022-04-15_straws_on_panels.csv") # include paper pull grade
straws_on_panels_file = Path(
    "2022-06-16_straws_on_panels.csv"
)  # extends data up to MN244
assert straws_on_panels_file.is_file()

db_df = pd.read_csv(straws_on_panels_file, sep=",")
db_df.columns = db_df.columns.str.replace(" ", "")
db_df = db_df.rename(columns={"id": "straw"})
# -

# ## Combine data

# add leak info to every straw that has an associated panel
straws_on_panels_df = db_df.merge(leak_df, on=["straw"], how="left")
straws_on_panels_df

# add panel info to every leak test
all_straws_df = leak_df.merge(db_df, on=["straw"], how="left")
all_straws_df

# ## Make csvs

straws_on_panels_df.to_csv("straws_on_panels_MN173_MN244.csv")
all_straws_df.to_csv("all_straws_2022-06-13.csv")

leak_df.to_csv("all_passing_leak_tests_2022-06.csv")
