################################################################################
#
# Read in panel leak rate raw data file straight off of labview.
# Plot it and fit it. Can specify the fitting and plotting limits.
# Accepts the "old" and "new" (circa 2020-09 15) data formats.
#
# Attempted 3 fitting methods. The numpy.statistics and sklearn models are
# identical. Third method just makes a line out of the first and last points.
# Enough randomness in those two points that it just serves as a sanity check.
#
# Next: pass the data to a function that loads the data into the DB.
#
################################################################################
import matplotlib.pyplot as plt
import optparse
from scipy import interpolate, stats, signal
import numpy as np
from sklearn.linear_model import LinearRegression
import os
import re
from guis.common.getresources import GetProjectPaths
from pathlib import Path
import sys
from guis.panel.leak.panel_leak_utilities import *
from guis.panel.leak.load_leak_csv_into_db import main as load_into_db

################################################################################
# Constants
################################################################################
# Default relative time after which the fit begins (days)
kFIT_START_TIME = 0.2

# color scheme
cmap = plt.get_cmap("tab10")
color_box_temp = cmap(4)
color_room_temp = cmap(0)
color_pressure = cmap(1)
color_pressure_ref = cmap(5)
color_pressure_fill = cmap(6)
fit1_color = cmap(2)
fit2_color = cmap(3)


################################################################################
# ARGUMENTS/OPTIONS
# Parse input args - input filename, fit start/end times
################################################################################
def GetOptions():
    parser = optparse.OptionParser(usage="usage: %prog [options]")
    parser.add_option(
        "--infile", "-I", help="Full or relative path of input leak rate file."
    )
    parser.add_option(
        "--is_old_format",
        "-O",
        dest="is_new_format",
        action="store_false",
        default=True,
        help="Original csv data format.",
    )
    parser.add_option(
        "--t0",
        "--ti",
        "--fit_start_time",
        dest="fit_start_time",
        type="float",
        default=None,
        help="Fit start point, in days.",
    )
    parser.add_option(
        "--t1",
        "--tf",
        "--fit_end_time",
        dest="fit_end_time",
        type="float",
        default=None,
        help="Fit end point, in days.",
    )
    parser.add_option(
        "--min_diff_pressure",
        dest="min_diff_pressure",
        type="float",
        default=None,
        help="Set minimum differential pressure on vertical axis.",
    )
    parser.add_option(
        "--max_diff_pressure",
        dest="max_diff_pressure",
        type="float",
        default=None,
        help="Set maximum differential pressure on vertical axis.",
    )
    parser.add_option(
        "--min_ref_pressure",
        dest="min_ref_pressure",
        type="float",
        default=None,
        help="Set minimum reference/fill pressure on vertical axis.",
    )
    parser.add_option(
        "--max_ref_pressure",
        dest="max_ref_pressure",
        type="float",
        default=None,
        help="Set maximum reference/fill pressure on vertical axis.",
    )
    parser.add_option(
        "--no_fit",
        dest="do_fit",
        default=True,
        action="store_false",
        help="Don't do any fits.",
    )
    options, remainder = parser.parse_args()
    return options


################################################################################
# Helper functions
################################################################################
# Raw data file name: "201109_1257_MN061test6.txt"
def GetPanelIDFromFilename(filename):
    return re.search(r"MN\d\d\d", filename).group(0)


# If user did not provide a fit start time, determine as follows:
# total duration < 0.3 days --> t0 = 0
# total duration < 2 days   --> t0 = 0.2
# total duration >= 2 days  --> t0 = 0.1*total duration
def GetFitStartTime(total_duration):
    if total_duration < kFIT_START_TIME + 0.1:
        return 0.0
    elif total_duration * 0.1 < kFIT_START_TIME:
        return kFIT_START_TIME
    else:
        return total_duration * 0.1


################################################################################
# Plot full range of (just) data points -- used for stuff we don't fit, like
# temperature
################################################################################
def PlotDataPoints(df, column_name, axis, color=None, label=None):
    time = df["TIME(DAYS)"]
    yvals = df[column_name]
    # x_values = np.linspace(time.iloc[0], time.iloc[-1])

    markersize = 1
    # downsample temperatures
    if "TEMPERATURE" in column_name:
        yvals = np.array(yvals)
        temp_size = yvals.size
        yvals = signal.resample(yvals, 250)
        yvals = signal.resample(yvals, temp_size)
        label = column_name
        markersize = 2

    # plot
    axis.plot(
        np.array(time),
        np.array(yvals),
        "o",
        color=color,
        markersize=markersize,
        label=label,
    )


################################################################################
# Make a fit from a df and plot it
# (1) Straight-line fit using first and last points, and (2) straight-line fit
# using least squares
################################################################################
def DoFitAndPlot(df, fit_start_time, fit_end_time, axDiffP, axTemp):
    # Standard numpy least squares linear regression
    def FitAndPlot_1(df, axDiffP):
        time = df["TIME(DAYS)"]
        pressure = df["PRESSURE(PSI)"]
        slope, intercept, r_value, p_value, std_err = stats.linregress(time, pressure)
        print("slope intercept r_value p_value std_err")
        print(
            round(slope, 4),
            round(intercept, 4),
            round(r_value, 4),
            round(p_value, 7),
            round(std_err, 7),
        )
        y_values = intercept + slope * time
        leak_rate_in_sccm = round(slope * kPSI_PER_DAY_TO_SCCM, 4)
        axDiffP.plot(
            np.array(time),
            np.array(y_values),
            color=fit1_color,
            linewidth=3.0,
            label="Least Squares\n{0}+-{1} sccm\n$r^2$={2}".format(
                leak_rate_in_sccm, round(std_err, 4), round(r_value**2, 3)
            ),
        )
        return slope, intercept, r_value, p_value, std_err

    # From first and last point
    def FitAndPlot_2(df, axDiffP):
        time = df["TIME(DAYS)"]
        pressure = df["PRESSURE(PSI)"]
        x_i = time.iloc[0]
        y_i = pressure.iloc[0]
        x_f = time.iloc[-1]
        y_f = pressure.iloc[-1]
        x = np.array([x_i, x_f])
        y = np.array([y_i, y_f])
        coefficients = np.polyfit(x, y, 1)
        slope = coefficients[0]
        intercept = coefficients[1]
        print("slope:", round(slope, 4), "intercept:", round(intercept, 4))
        y_values = intercept + slope * time
        leak_rate_in_sccm = round(slope * kPSI_PER_DAY_TO_SCCM, 4)
        axDiffP.plot(
            np.array(time),
            np.array(y_values),
            color=fit2_color,
            linewidth=3.0,
            label="From first and last points\n{0} sccm".format(leak_rate_in_sccm),
        )

    # Restrict fit range by start and end time, then do fit and plot it
    df = df.loc[(df["TIME(DAYS)"] > fit_start_time) & (df["TIME(DAYS)"] < fit_end_time)]
    FitAndPlot_1(df, axDiffP)
    FitAndPlot_2(df, axDiffP)


################################################################################
# main
################################################################################
def main(options):
    # read raw data files into a dataframe
    df = ReadLeakRateFile(options.infile, options.is_new_format)

    # prep plots
    params = {"mathtext.default": "regular"}
    fig, axs = plt.subplots(2, figsize=(13, 11))
    axDiffP = axs[0]
    axTemp = axDiffP.twinx()
    axRefP = axs[1]

    # Plot data points
    PlotDataPoints(df, "PRESSURE(PSI)", axDiffP, color_pressure)
    try:
        PlotDataPoints(df, "ROOM TEMPERATURE(C)", axTemp, color_room_temp)
    except KeyError:
        pass
    try:
        PlotDataPoints(df, "BOX TEMPERATURE(C)", axTemp, color_box_temp)
    except KeyError:
        pass
    PlotDataPoints(df, "RefPSIA", axRefP, color_pressure_ref, "$P_{Ref}$")
    PlotDataPoints(df, "FillPSIA", axRefP, color_pressure_fill, "$P_{Fill}$")

    # get the start, end, and elapsed times over which to make the fit
    total_duration = df["TIME(DAYS)"].iat[-1]
    fit_start_time = (
        GetFitStartTime(total_duration)
        if not options.fit_start_time
        else options.fit_start_time
    )
    fit_end_time = total_duration if not options.fit_end_time else options.fit_end_time
    print("Total duration of leak test:", round(total_duration, 3))
    print(
        "Fit will be performed between",
        round(fit_start_time, 3),
        "and",
        round(fit_end_time, 3),
        "days",
    )

    # Do fit and plot it
    if options.do_fit:
        DoFitAndPlot(df, fit_start_time, fit_end_time, axDiffP, axTemp)

    # legends
    lines, labels = axDiffP.get_legend_handles_labels()
    lines2, labels2 = axTemp.get_legend_handles_labels()
    legend = axTemp.legend(lines + lines2, labels + labels2, loc=0)
    for handle in legend.legendHandles:
        handle.set(markersize=8)
        
    lines3, labels3 = axRefP.get_legend_handles_labels()
    legend3 = axRefP.legend(lines3, labels3, loc="lower left")
    for handle in legend3.legendHandles:
        handle.set(markersize=8)

    # axis labels
    title = Path(options.infile).stem
    plt.title(title)
    axDiffP.set_xlabel("DAYS", fontweight="bold")
    axDiffP.set_ylabel("DIFF PRESSURE (PSI)", fontweight="bold")
    axTemp.set_ylabel("TEMPERATURE (C)", fontweight="bold")
    axDiffP.yaxis.label.set_color(color_pressure)
    axTemp.yaxis.label.set_color("k")

    axRefP.set_ylabel("PRESSURE (PSI)", fontweight="bold")
    axRefP.yaxis.label.set_color("k")

    # Pressure axis - limits
    # Pymin,Pymax = axDiffP.get_ylim()
    axDiffP.relim()
    axDiffP.autoscale_view()
    if options.min_diff_pressure:
        axDiffP.set_ylim(bottom=options.min_diff_pressure)
    if options.max_diff_pressure:
        axDiffP.set_ylim(top=options.max_diff_pressure)

    if options.min_ref_pressure:
        axRefP.set_ylim(bottom=options.min_ref_pressure)
    if options.max_ref_pressure:
        axRefP.set_ylim(top=options.max_ref_pressure)

    # Temperature axis - limits
    ymin, ymax = axTemp.get_ylim()
    axTemp.relim()
    axTemp.set_ylim(0, ymax * 1.1)
    axTemp.autoscale_view()

    # Create outdir for panel pdfs
    panel_id = GetPanelIDFromFilename(options.infile)
    plots_dir = GetProjectPaths()["panelleak"] / panel_id
    plots_dir.mkdir(exist_ok=True, parents=True)

    # fit start/endtime tag
    fit_start_tag = (
        "_ti={0}days".format(options.fit_start_time) if options.fit_start_time else ""
    )
    fit_end_tag = (
        "_tf={0}days".format(options.fit_end_time) if options.fit_end_time else ""
    )

    # create plot filename
    title = "{0}{1}{2}.pdf".format(title, fit_start_tag, fit_end_tag)
    full_path = plots_dir / title

    # save plot
    print("Saving image", full_path)
    plt.savefig(full_path)

    # display plot
    plt.show()


################################################################################
# called when run like `python -m guis.panel.leak` (Used like this w/in PANGUI)
################################################################################
def RunInteractive():
    options = GetOptions()
    print("Specify options. Press <return> to skip an option and use the default.")
    options.infile = input("Input data file> ").strip(" '\t\n\"")
    try:
        assert options.infile
    except AssertionError:
        sys.exit("Must provide input data file.")
    try:
        print(Path(options.infile).resolve())
        assert Path(options.infile).is_file()
    except AssertionError:
        sys.exit("Input file not found.")

    def SetFloatOption(prompt, default_option):
        try:
            return float(input(prompt))
        except ValueError:
            return default_option

    options.fit_start_time = SetFloatOption("Fit start> ", options.fit_start_time)
    options.fit_end_time = SetFloatOption("Fit end> ", options.fit_end_time)
    options.min_diff_pressure = SetFloatOption(
        "Differential pressure y-axis min> ", options.min_diff_pressure
    )
    options.max_diff_pressure = SetFloatOption(
        "Differential pressure y-axis max> ", options.max_diff_pressure
    )
    options.min_ref_pressure = SetFloatOption(
        "Reference pressure y-axis min> ", options.min_ref_pressure
    )
    options.max_ref_pressure = SetFloatOption(
        "Reference pressure y-axis max> ", options.max_ref_pressure
    )
    print(options)

    # If we can't find a procedure ID, give up
    try:
        load_into_db(options.infile)
    except TypeError:
        print("\nDATA NOT LOADED INTO DB. PROBABLY BECAUSE PANEL DOESN'T EXIST IN DB.")

    main(options)


################################################################################
# called when run directly like `python -m guis.panel.leak.PlotLeakRate <flags>
################################################################################
if __name__ == "__main__":
    options = GetOptions()
    main(options)
