# New data format as of 2020-09-16
# Attempted 3 fitting methods.
# The numpy.statistics and sklearn models are identical.
import pandas as pd
import matplotlib.pyplot as plt
import optparse
from scipy import interpolate, stats, signal
import numpy as np
from sklearn.linear_model import LinearRegression
import datetime
import os
from datetime import datetime

# Unit conversion factor for inches of water to psi.
kINCHES_H2O_PER_PSI = 27.6799048

# Unit conversion factor for PSI change per day to sccm
kPSI_PER_DAY_TO_SCCM = 0.17995993587933934

# Default relative time after which the fit begins (days)
kFIT_START_TIME = 0.2

# color scheme
cmap = plt.get_cmap("tab10")
temperature_color = cmap(0)
pressure_color = cmap(1)
fit1_color = cmap(2)
fit2_color = cmap(3)


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
        "--min_pressure",
        dest="min_pressure",
        type="float",
        default=None,
        help="Set minimum pressure on vertical axis.",
    )

    parser.add_option(
        "--max_pressure",
        dest="max_pressure",
        type="float",
        default=None,
        help="Set maximum pressure on vertical axis.",
    )
    options, remainder = parser.parse_args()
    return options


def ConvertInchesH2OToPSI(pressure_inches_h2O):
    return pressure_inches_h2O / kINCHES_H2O_PER_PSI


# Raw data file name: "201109_1257_MN061test6.txt"
def GetPanelIDFromFilename(filename):
    return filename[12:17]


# If user did not provide a fit start time, determine as follows:
# total duration < 0.3 days --> t0 = 0
# total duration < 2 days   --> t0 = 0.2
# total duration >= 2 days  --> t0 = 0.1*total duration
def GetFitStartTime(total_duration):
    if total_duration < kFIT_START_TIME + 0.1:
        return 0.
    elif total_duration * 0.1 < kFIT_START_TIME:
        return kFIT_START_TIME
    else:
        return total_duration * 0.1


def ReadLeakRateFile(infile, is_new_format="true"):
    if is_new_format:
        # read input file
        df = pd.read_csv(infile, engine="python", header=1, sep="\t")

        # remove whitespace from column headers
        df.columns = df.columns.str.replace(" ", "")

        # convert pressure from inches of water to psi
        df['Diff"H2O'] = ConvertInchesH2OToPSI(df['Diff"H2O'])
        df = df.rename(columns={'Diff"H2O': "PRESSURE(PSI)"})

        # rename time
        df = df.rename(columns={"Elapdays": "TIME(DAYS)"})

        # rename temp
        df = df.rename(columns={"RoomdegC": "TEMPERATURE(C)"})

        ## make a new column: pressure/temp
        # df['PSI/degC'] = df["PRESSURE(PSI)"]/df["RoomdegC"]

        return df
    else:
        # read input file
        df = pd.read_csv(infile, engine="python", header=4, sep=",", encoding="cp1252")

        # remove whitespace from column headers
        df.columns = df.columns.str.replace(" ", "")
        df.columns = df.columns.str.replace("\t", "")
        df.columns = df.columns.str.replace(u"°", "")

        # convert pressure from inches of water to psi
        df["PRESSURE(INH20D)"] = ConvertInchesH2OToPSI(df["PRESSURE(INH20D)"])
        df = df.rename(columns={"PRESSURE(INH20D)": "PRESSURE(PSI)"})

        # convert absolute time to elapsed days
        def get_time(time_str):
            """Converts a time string from the datafile to UNIX time."""
            if "." in time_str:
                # More than 1 day has passed
                days, time_s = time_str.split(".")
            else:
                # Less than 1 day has passed
                days = "0"
                time_s = time_str
            days = int(days)
            hours, minutes, seconds = map(int, time_s.split(":"))

            td = datetime.timedelta(
                days=days, hours=hours, minutes=minutes, seconds=seconds
            )
            total_seconds = int(round(td.total_seconds()))

            return total_seconds / 24 / 60 / 60

        df["TIME(hh:mm:ss)"] = df["TIME(hh:mm:ss)"].apply(get_time)
        df = df.rename(columns={"TIME(hh:mm:ss)": "TIME(DAYS)"})

        ## make a new column: pressure/temp
        # print(df.columns)
        # df['PSI/degC'] = df["PRESSURE(PSI)"]/df["TEMPERATURE(C)"]

        return df


def PlotDataAndFit(df, fit_start_time, fit_end_time, axP, axT):
    # Plot full range of data points
    def PlotDataPoints(df, axP, axT):
        time = df["TIME(DAYS)"]
        pressure = df["PRESSURE(PSI)"]
        temperature = df["TEMPERATURE(C)"]
        # x_values = np.linspace(time.iloc[0], time.iloc[-1])

        # downsample temperature
        temperature = np.array(temperature)
        temp_size = temperature.size
        temperature = signal.resample(temperature, 250)
        temperature = signal.resample(temperature, temp_size)

        # plot
        axP.plot(
            np.array(time), np.array(pressure), "o", color=pressure_color, markersize=1
        )
        axT.plot(
            np.array(time), temperature, "o", color=temperature_color, markersize=1
        )

    # Standard numpy least squares linear regression
    def FitAndPlot_1(df, axP):
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
        axP.plot(
            np.array(time),
            np.array(y_values),
            color=fit1_color,
            linewidth=3.,
            label="Least Squares\n{0}+-{1} sccm\n$r^2$={2}".format(
                leak_rate_in_sccm, round(std_err, 4), round(r_value ** 2, 3)
            ),
        )
        return slope, intercept, r_value, p_value, std_err

    # From first and last point
    def FitAndPlot_2(df, axP):
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
        axP.plot(
            np.array(time),
            np.array(y_values),
            color=fit2_color,
            linewidth=3.,
            label="From first and last points\n{0} sccm".format(leak_rate_in_sccm),
        )

    # Uses the same as method 1 under the hood
    def FitAndPlot_3(df, axP):
        time = df["TIME(DAYS)"].to_numpy().reshape((-1, 1))
        pressure = df["PRESSURE(PSI)"].to_numpy()
        model = LinearRegression().fit(time, pressure)
        print(model)
        r_sq = model.score(time, pressure)
        slope = model.coef_
        intercept = model.intercept_
        print("slope: ", slope, "intercept: ", intercept)
        y_values = intercept + slope * time
        leak_rate_in_sccm = round(slope[0] * kPSI_PER_DAY_TO_SCCM, 5)
        axP.plot(
            np.array(time),
            np.array(y_values),
            color=cmap(6),
            linewidth=3.,
            label="least squares 2\n{0} sccm\n($r^2$={1})".format(
                leak_rate_in_sccm, round(r_sq, 3)
            ),
        )

    # Plot data points
    PlotDataPoints(df, axP, axT)

    # Constrain the DF to between fit start and end times
    total_duration = df["TIME(DAYS)"].iat[-1]
    if fit_start_time is None:
        fit_start_time = GetFitStartTime(total_duration)
    if fit_end_time is None:
        fit_end_time = total_duration
    print("Total duration of leak test:", round(total_duration, 3))
    print(
        "Fit will be performed between",
        round(fit_start_time, 3),
        "and",
        round(fit_end_time, 3),
        "days",
    )
    df = df.loc[(df["TIME(DAYS)"] > fit_start_time) & (df["TIME(DAYS)"] < fit_end_time)]
    FitAndPlot_1(df, axP)
    FitAndPlot_2(df, axP)
    # FitAndPlot_3(df, axP) #identical to 2


def main():
    options = GetOptions()

    df = ReadLeakRateFile(options.infile, options.is_new_format)

    # prep plots
    params = {"mathtext.default": "regular"}
    fig, axP = plt.subplots(figsize=(13, 11))
    axT = axP.twinx()

    PlotDataAndFit(df, options.fit_start_time, options.fit_end_time, axP, axT)

    # legend
    lines, labels = axP.get_legend_handles_labels()
    lines2, labels2 = axT.get_legend_handles_labels()
    axT.legend(lines + lines2, labels + labels2, loc=0)

    # axis labels
    title = options.infile.split("\\")[-1]
    title = title.partition(".")[0]
    plt.title(title)
    axP.set_xlabel("DAYS", fontweight="bold")
    axP.set_ylabel("PRESSURE (PSI)", fontweight="bold")
    axT.set_ylabel("ROOM TEMPERATURE (C)", fontweight="bold")
    axP.yaxis.label.set_color(pressure_color)
    axT.yaxis.label.set_color(temperature_color)

    # axis limits
    # Pymin,Pymax = axP.get_ylim()
    axP.relim()
    axP.autoscale_view()
    if options.min_pressure:
        axP.set_ylim(bottom=options.min_pressure)
    if options.max_pressure:
        axP.set_ylim(top=options.max_pressure)
    # ymin, ymax = axT.get_ylim()

    axT.relim()
    axT.set_ylim(0, ymax * 1.1)
    axT.autoscale_view()

    # Create outdir for panel pdfs
    panel_id = GetPanelIDFromFilename(options.infile)
    plots_dir = "../Data/Panel data/FinalQC/Leak/Plots/" + panel_id
    if not os.path.exists(plots_dir):
        os.makedirs(plots_dir)

    # datetime tag
    now = datetime.now()
    dt_string = now.strftime("%Y%m%d_%H%M")
    dt_tag = "_" + dt_string

    # fit start/endtime tag
    fit_start_tag = (
        "_ti={0}days".format(options.fit_start_time) if options.fit_start_time else ""
    )
    fit_end_tag = (
        "_tf={0}days".format(options.fit_end_time) if options.fit_end_time else ""
    )

    # create plot filename
    title = "{0}{1}{2}{3}.pdf".format(title, fit_start_tag, fit_end_tag, dt_tag)
    full_path = plots_dir + "/" + title

    # save plot
    print("Saving image", full_path)
    plt.savefig(full_path)

    # display plot
    plt.show()


if __name__ == "__main__":
    main()
