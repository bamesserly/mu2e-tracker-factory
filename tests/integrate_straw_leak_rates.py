import csv
from guis.common.getresources import GetProjectPaths
from pathlib import Path
import numpy as np
import collections
import pandas as pd

# straw leak raw data location
indir = GetProjectPaths()["strawleakdata"] / "raw_data"
print(indir)

# start with list of straws, which we get from a file
straw_list_file = Path("tests/straws_on_panels.csv")
straws_list = np.loadtxt(straw_list_file, delimiter=",", dtype=int, skiprows=1, usecols=range(1))
print(straws_list)
print(f"{len(straws_list)} straws found.")

# get list of raw leak data files organized by straw
# { strawid1 : [rawdatafile1, rawdatafile2, ...], strawid2 : { }, ...}
leak_raw_data_by_straw = collections.defaultdict(list)

#for straw in straws_list:
#    leak_raw_data_by_straw[straw] = [infile for infile in indir.glob("*.txt") if f"{straw:05d}" in infile]
#result = [i for i in indir.glob("*.txt") if f"{straw:05d}" in i]
#result = list(filter(lambda x: x in arr1, arr2)) 
#result = {straw:infile for straw in straws_list if f"{straw:05d}" in indir.glob("*.txt")}
#leak_raw_data_by_straw = {straw:


counter = 0
for straw in straws_list:
    if counter % 100 == 0:
        print(f"{counter} straws' files found.")
    #if straw < 21500 or straw > 22500:
    #   continue 
    #if straw < 22000:
    #    break
    st = f"{straw:05d}"
    for raw_data_file in indir.glob("*.txt"):
        if st in str(raw_data_file):
            leak_raw_data_by_straw[straw].append(raw_data_file)
    counter += 1
print("raw data found for", len(leak_raw_data_by_straw), "straws")

# open file for writing, "w" is writing
with open('dict.csv', 'w') as csv_file:
    writer = csv.writer(csv_file, delimiter=";")
    for key, value in leak_raw_data_by_straw.items():
        v = list(map(str,value))
        writer.writerow([key, v])

# get the list of files by straw from a file
leak_raw_data_by_straw_df = pd.read_csv('dict.csv',sep=';')
leak_raw_data_by_straw = dict(leak_raw_data_by_straw_df.values)

# refit function
import guis.straw.leak.straw_leak_utilities as util
from guis.straw.leak.least_square_linear import get_fit
def refit(raw_data_file_fullpath, n_skips_start = 0, n_skips_end = 0):
    leak_rate = 0
    leak_rate_err = 0

    slope = []
    slope_err = []
    intercept = []
    intercept_err = []

    # Get data
    timestamp, ppm, ppm_err = util.get_data_from_file(raw_data_file_fullpath)

    # Skip points at beginning and end
    def truncate(container, nstart, nend):
        return container[max(nstart - 1, 0) : len(container) - nend]

    timestamp = truncate(timestamp, n_skips_start, n_skips_end)
    ppm = truncate(ppm, n_skips_start, n_skips_end)
    ppm_err = truncate(ppm_err, n_skips_start, n_skips_end)

    # Calculate slopes, leak rates
    raw_data_filename = raw_data_file_fullpath.name
    try:
        chamber = int(raw_data_filename[15:17])
    except:
        chamber = int(raw_data_filename[15:16])
    slope, slope_err, intercept, intrcept_err = get_fit(timestamp, ppm, ppm_err)

    leak_rate = util.calculate_leak_rate(slope, util.get_chamber_volume(chamber))

    leak_rate_err = util.calculate_leak_rate_err(
        leak_rate,
        slope,
        slope_err,
        util.get_chamber_volume(chamber),
        util.get_chamber_volume_err(chamber),
    )

    # pass, fail, or unknown
    leak_status = util.evaluate_leak_rate(len(ppm), leak_rate, leak_rate_err, timestamp[-1])

    #print("\n  Status leak rate after refit:", leak_status)

    return leak_rate, leak_rate_err

# calculate leak rates
leak_rates_by_straw = collections.defaultdict(list)
for straw, raw_data_files in leak_raw_data_by_straw.items():
    raw_data_files = raw_data_files[1:-1].split(',')
    for f in raw_data_files:
        infile = f
        infile = infile.replace("\"","")
        infile = infile.replace("\'","")
        infile = infile.replace(" ","")
        infile = Path(infile)
        try:
            leak_rate, leak_rate_err = refit(infile)
        except IndexError as e:
            print(e,infile.name)
        leak_rates_by_straw[straw].append(str(leak_rate))
        leak_rates_by_straw[straw].append(str(leak_rate_err))
    #print(f"{straw}, {leak_rates_by_straw[straw]}")

with open('rates.csv', 'w') as csv_file:  
    writer = csv.writer(csv_file, delimiter=";")
    for straw, rates in leak_rates_by_straw.items():
        parsed_rates = ','.join(rates)
        writer.writerow([straw,parsed_rates])

## print
#for straw, rates in leak_rates_by_straw.items():
#    parsed_rates = ','.join(rates)
#    print(f"{straw}, {parsed_rates}")

leak_rates_by_straw_df = pd.read_csv("rates.csv", sep=",")
leak_rates_by_straw = dict(leak_rates_by_straw.values)
straws_by_panel_df = pd.read_csv("tests/straws_on_panels.csv", delimiter=",")
straws_by_panel = dict(straws_by_panel_df)
print(leak_rates_by_straw)
print(straws_by_panel)
