# ===============================================================================
# utility functions for jupyter analysis
#
# in particular: calculate straw leak rate given raw data file
# todo: I forget, is this copy-pasted from the utilities functions? if so, why
# didn't I just import them in the first place?
# whatever
# ===============================================================================
import guis.straw.leak.straw_leak_utilities as util
from guis.straw.leak.least_square_linear import get_fit

# in runtime jupyter, this how we could refresh the import
# import importlib
# importlib.reload(util)

# Skip points at beginning and end
def truncate(container, nstart, nend):
    return container[max(nstart - 1, 0) : len(container) - nend]


class NotEnoughData(Exception):
    pass


# We won't use the skip-start/endpoints functionality, but leaving it around just in case.
def refit(raw_data_file_fullpath, n_skips_start=0, n_skips_end=0):
    leak_rate = 0
    leak_rate_err = 0

    slope = []
    slope_err = []
    intercept = []
    intercept_err = []

    # Get data from raw data file
    timestamp, ppm, ppm_err = util.get_data_from_file(raw_data_file_fullpath)

    timestamp = truncate(timestamp, n_skips_start, n_skips_end)
    ppm = truncate(ppm, n_skips_start, n_skips_end)
    ppm_err = truncate(ppm_err, n_skips_start, n_skips_end)

    # not enough data
    if not timestamp:
        raise NotEnoughData

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
    leak_status = util.evaluate_leak_rate(
        len(ppm), leak_rate, leak_rate_err, timestamp[-1]
    )

    # print("\n  Status leak rate after refit:", leak_status)

    return leak_rate, leak_rate_err, leak_status, chamber
