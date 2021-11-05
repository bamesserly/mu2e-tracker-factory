from guis.straw.leak.least_square_linear import get_fit
from guis.common.getresources import GetProjectPaths
from resources.straw_leak_chamber_volumes import (
    get_chamber_volume,
    get_chamber_volume_err,
    calculate_leak_rate,
    calculate_leak_rate_err,
)
import csv
from pathlib import Path


def calc_ppm_err(ppm):
    return ((ppm * 0.02) ** 2 + 20 ** 2) ** 0.5


def get_data_from_file(raw_data_fullpath):
    excluded_time = 120  # ignore first 2 minutes of data
    starttime = 0
    timestamps = []
    PPM = []
    PPM_err = []

    with open(raw_data_fullpath, "r+", 1) as readfile:
        lines_read = 0
        for line in readfile:
            line = line.split()
            timestamp = float(line[0])
            ppm = float(line[2])

            lines_read = lines_read + 1
            if ppm == "0.00":
                continue
            if starttime == 0:
                starttime = timestamp
            eventtime = timestamp - starttime
            if eventtime < excluded_time:
                continue
            timestamps.append(eventtime)
            PPM.append(ppm)
            PPM_err.append(calc_ppm_err(ppm))

    return timestamps, PPM, PPM_err


def refit(raw_data_filename, n_skips_start, n_skips_end):
    directory = GetProjectPaths()["strawleakdata"] / "raw_data"
    leak_rate = 0
    leak_rate_err = 0

    slope = []
    slope_err = []
    intercept = []
    intercept_err = []

    # Get data
    timestamp, PPM, PPM_err = get_data_from_file(directory / raw_data_filename)

    # Skip points at beginning and end
    def truncate(container, nstart, nend):
        return container[nstart - 1 : len(container) - nend]

    timestamp = truncate(timestamp, n_skips_start, n_skips_end)
    PPM = truncate(PPM, n_skips_start, n_skips_end)
    PPM_err = truncate(PPM_err, n_skips_start, n_skips_end)

    # Calculate slopes, leak rates
    try:
        chamber = int(raw_data_filename[15:17])
    except:
        chamber = int(raw_data_filename[15:16])
    slope, slope_err, intercept, intrcept_err = get_fit(timestamp, PPM, PPM_err)

    leak_rate = calculate_leak_rate(slope, get_chamber_volume(chamber))

    leak_rate_err = calculate_leak_rate_err(
        leak_rate,
        slope,
        slope_err,
        get_chamber_volume(chamber),
        get_chamber_volume_err(chamber),
    )

    return leak_rate, leak_rate_err


def run():
    raw_data_filename = input("\nEnter file name: ").strip()
    n_points_to_skip_start = int(
        input("Enter number of data points to skip from start: ").strip() or 0
    )
    n_points_to_skip_end = int(
        input("Enter number of data points to skip at end: ").strip() or 0
    )
    leak_rate, leak_rate_err = refit(
        raw_data_filename, n_points_to_skip_start, n_points_to_skip_end
    )
    print("\nLeak Rate and Error: ")
    print(round(leak_rate, 7), round(leak_rate_err, 8))
    input("\nPress enter to continue.")


if __name__ == "__main__":
    run()