################################################################################
# Constants and functions serving the leak test gui and the leak test refit
# program.
#
# Read raw leak data, calculate slopes and leak rates, data on chamber volumes,
# chamber map to rows-columns, data and fit plotting, fit quality evaluation
################################################################################
from sys import exit
from enum import Enum
import numpy as np
import matplotlib.pyplot as plt
import datetime

# (conversion_rate*real_leak_rate=the_leak_rate_when_using_20/80_argon/co2 in
# chamber) Conversion rate proportional to amount of CO2 (1/5) Partial pressure
# of CO2 as 2 absolution ATM presure inside and 0 outside, chamber will be 1 to
# 0(1/2) Multiplied by 1.4 for the argon gas leaking as well conservative
# estimate (should we reduce?
LEAK_RATE_SCALING = 0.14  # unitless -- CO2 --> ArCO2 (*1/8), pressure diff (*1/2)
STRAW_VOLUME = 26.0  # ccs, uncut straw
EXCLUDE_RAW_DATA_SECONDS = 120  # skip first 2 minutes of raw data file
MIN_N_DATAPOINTS_FOR_FIT = 10
MAX_ALLOWED_LEAK_RATE = 0.00009645060  # cc/min
NOTIFY_LOW_LEAK_RATE = 0.00002  # cc/min
UPPER_GOOD_LEAK_RATE = 0.00007  # cc/min


CHAMBER_VOLUME = [
    [594, 607, 595, 605, 595],
    [606, 609, 612, 606, 595],
    [592, 603, 612, 606, 567],
    [585, 575, 610, 615, 587],
    [611, 600, 542, 594, 591],
    [598, 451, 627, 588, 649],
    [544, 600, 534, 594, 612],
    [606, 594, 515, 583, 601],
    [557, 510, 550, 559, 527],
    [567, 544, 572, 561, 578],
]  # ccs

CHAMBER_VOLUME_ERR = [
    [13, 31, 15, 10, 21],
    [37, 7, 12, 17, 15],
    [15, 12, 7, 4, 2],
    [8, 15, 6, 10, 11],
    [4, 3, 8, 6, 9],
    [31, 11, 25, 20, 16],
    [8, 8, 11, 8, 6],
    [6, 10, 8, 10, 8],
    [6, 8, 6, 9, 6],
    [7, 6, 8, 7, 6],
]  # ccs


class PassFailStatus(Enum):
    PASS = "P"
    FAIL = "F"
    UNKNOWN = "U"


# Get chamber number given row and column
def chamber_from_row_col(row, col):
    return row * 5 + col


# Get chamber's row and column given chamber number
def row_col_from_chamber(chamber):
    (row, col) = divmod(chamber, 5)
    return row, col


# Get chamber volumes and volume uncertainties
def get_chamber_info(which_info, *args):
    if len(args) == 1:
        row, col = row_col_from_chamber(args[0])
        return which_info[row][col]
    elif len(args) == 2:
        return which_info[args[0]][args[1]]
    else:
        exit("Chamber info invalid parameters. Either (row, col) or chamber#.")


# Get chamber volume from chamber number or from (row, column)
def get_chamber_volume(*args):
    return get_chamber_info(CHAMBER_VOLUME, *args)


# Get chamber volume uncertainty from chamber number or from (row, column)
def get_chamber_volume_err(*args):
    return get_chamber_info(CHAMBER_VOLUME_ERR, *args)


def calc_ppm_err(ppm):
    return ((ppm * 0.02) ** 2 + 20**2) ** 0.5


# Calculate leak rate from change in N millions of CO2 molecules
# [slope] = ppm/s, [chamber_volume] = ccs, [leak_rate] = ccs/min
# leak rate in cc/min = slope(PPM/sec) * chamber_volume(cc) * 10^-6(1/PPM) * 60 (sec/min) * scale
def calculate_leak_rate(slope, chamber_volume):
    return slope * chamber_volume * (10**-6) * 60 * LEAK_RATE_SCALING


# error = sqrt((lr/slope)^2 * slope_err^2 + (lr/ch_vol)^2 * ch_vol_err^2)
def calculate_leak_rate_err(
    leak_rate, slope, slope_err, chamber_volume, chamber_volume_err
):
    return (
        (leak_rate / slope) ** 2 * slope_err**2
        + (leak_rate / chamber_volume) ** 2 * chamber_volume_err**2
    ) ** 0.5


# Read leak raw data file, return ppms, ppm_err, and x-axis timestamps
def get_data_from_file(raw_data_fullpath):
    starttime = 0
    timestamps = []
    PPM = []
    PPM_err = []

    with open(raw_data_fullpath, "r+", 1) as readfile:
        # example line: <timestamp> <chamber> <reading> <human timestmap>
        for line in readfile:
            line = line.split()
            if not line:
                continue
            timestamp = float(line[0])
            ppm = float(line[2])

            # skip empty readings
            if ppm == "0.00":
                continue

            # set start time for this chamber
            if starttime == 0:
                starttime = timestamp

            # set time for this reading
            eventtime = timestamp - starttime

            # Don't record first two minutes of data
            if eventtime < EXCLUDE_RAW_DATA_SECONDS:
                continue

            timestamps.append(eventtime)
            PPM.append(ppm)
            PPM_err.append(calc_ppm_err(ppm))

    return timestamps, PPM, PPM_err


# return PassFailStatus object -- PASS, FAIL, UNKNOWN
def evaluate_leak_rate(npoints, leak_rate, leak_rate_err, end_timestamp):
    if npoints <= 20:
        return PassFailStatus.UNKNOWN
    # PASS. Acceptable leak rate and (acceptable error or 7.5 hrs of data)
    if (leak_rate < MAX_ALLOWED_LEAK_RATE) and (
        leak_rate_err < MAX_ALLOWED_LEAK_RATE / 10 or end_timestamp > 27000
    ):
        return PassFailStatus.PASS
    # FAIL. Unacceptable rate and (acceptable error or 7.5 hrs of data)
    elif (leak_rate > MAX_ALLOWED_LEAK_RATE) and (
        leak_rate_err < MAX_ALLOWED_LEAK_RATE / 10 or end_timestamp > 27000
    ):
        return PassFailStatus.FAIL
    # FAIL. Doesn't even pass within error bars.
    elif (leak_rate - 10 * leak_rate_err) > MAX_ALLOWED_LEAK_RATE:
        return PassFailStatus.FAIL
    # UNHANDLED PASS-FAIL CASE
    else:
        return PassFailStatus.UNKNOWN


# plot data and fit line
def plot(
    title,
    x_values,
    y_values,
    slope,
    slope_err,
    intercept,
    leak_rate,
    leak_rate_err,
    leak_status,
    outfile,
):
    currenttime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status_string = {
        PassFailStatus.PASS: "Passed leak requirement",
        PassFailStatus.FAIL: "Failed leak requirement",
        PassFailStatus.UNKNOWN: "unknown status",
    }[leak_status]
    x = np.linspace(0, max(x_values))
    y = slope * x + intercept
    plt.plot(x_values, y_values, "bo")
    # plt.errorbar(timestamp[f],PPM[f], yerr=PPM_err[f], fmt='o')
    plt.plot(x, y, "r")
    plt.xlabel("time (s)")
    plt.ylabel("CO2 level (PPM)")
    plt.title(title)
    info_string = (
        "Slope = %.2f +- %.2f x $10^{-3}$ PPM/sec \n"
        % (
            slope * 10**4,
            slope_err * 10**4,
        )
        + "Leak Rate = %.2f +- %.2f x $10^{-5}$ cc/min \n"
        % (
            leak_rate * (10**5),
            leak_rate_err * (10**5),
        )
        + status_string
        + "\n"
        + currenttime
    )
    plt.figtext(
        0.49,
        0.80,
        info_string,
        fontsize=12,
        color="r",
    )
    plt.savefig(outfile)
    plt.clf()
