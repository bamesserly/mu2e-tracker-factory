from sys import exit

LEAK_RATE_SCALING = 0.14  # unitless -- CO2 --> ArCO2 (*1/8), pressure diff (*1/2)
STRAW_VOLUME = 26.0  # ccs, uncut straw
EXCLUDE_RAW_DATA_SECONDS = 120  # skip first 2 minutes of raw data file

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
    return ((ppm * 0.02) ** 2 + 20 ** 2) ** 0.5


# Calculate leak rate from change in N millions of CO2 molecules
# [slope] = ppm/s, [chamber_volume] = ccs, [leak_rate] = ccs/min
# leak rate in cc/min = slope(PPM/sec) * chamber_volume(cc) * 10^-6(1/PPM) * 60 (sec/min) * scale
def calculate_leak_rate(slope, chamber_volume):
    return slope * chamber_volume * (10 ** -6) * 60 * LEAK_RATE_SCALING


# error = sqrt((lr/slope)^2 * slope_err^2 + (lr/ch_vol)^2 * ch_vol_err^2)
def calculate_leak_rate_err(
    leak_rate, slope, slope_err, chamber_volume, chamber_volume_err
):
    return (leak_rate / slope) ** 2 * slope_err ** 2 + (
        leak_rate / chamber_volume ** 2 * chamber_volume_err ** 2
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
