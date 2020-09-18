# New data format as of 2020-09-16
# Attempted 3 fitting methods.
# The numpy.statistics and sklearn models are identical.
import pandas as pd
import matplotlib.pyplot as plt
import optparse
from scipy import interpolate,stats
import numpy as np
from sklearn.linear_model import LinearRegression

# Unit conversion factor for inches of water to psi.
kINCHES_H2O_PER_PSI = 27.6799048

# Unit conversion factor for PSI change per day to sccm
kPSI_PER_DAY_TO_SCCM = 0.17995993587933934

def GetOptions():
    parser = optparse.OptionParser(usage="usage: %prog [options]")
    parser.add_option("--infile", "-I", help="Full or relative path of input leak rate file.")
    options, remainder = parser.parse_args()
    return options

def ReadLeakRateFile(infile):
    # read input file
    df = pd.read_csv(infile, engine="python", header=1, sep='\t')

    # remove whitespace from column headers
    df.columns = df.columns.str.replace(" ", "")

    ## convert pressure from inches of water to psi
    df['Diff"H2O']=df['Diff"H2O']/kINCHES_H2O_PER_PSI
    df=df.rename(columns = {'Diff"H2O':'PRESSURE(PSI)'})

    df=df.rename(columns = {'Elapdays':'TIME(DAYS)'})

    return df

def PlotDataAndFit(df):
    total_duration = df["TIME(DAYS)"].iat[-1]
    first_segment_cutoff = 0.2
    first_segment_endtime = first_segment_cutoff if total_duration*0.1 < first_segment_cutoff else total_duration*0.1
    print("Total duration of leak test:", total_duration)
    print("Performing bilinear fit -- first segment ends at",first_segment_endtime, "days")

    # Plot full range of data points
    def PlotDataPoints(df):
        time = df['TIME(DAYS)']
        pressure = df['PRESSURE(PSI)']
        x_values = np.linspace(time.iloc[0], time.iloc[-1])
        plt.plot(time, pressure, "o", markersize=1)

    # Standard numpy least squares linear regression
    def FitAndPlot_1(df, first_segment_endtime):
        # constrict values of fit
        df = df.loc[df["TIME(DAYS)"] > first_segment_endtime]
        time = df['TIME(DAYS)']
        pressure = df['PRESSURE(PSI)']
        slope, intercept, r_value, p_value, std_err = stats.linregress(time, pressure)
        print("slope intercept r_value p_value std_err")
        print(slope, intercept, r_value, p_value, std_err)
        y_values = intercept + slope * time
        leak_rate_in_sccm = round(slope*kPSI_PER_DAY_TO_SCCM,4)
        plt.plot(time, y_values, label="Least Squares\n{0}+-{1}sccm\nr2={2}".format(leak_rate_in_sccm, round(std_err,3),round(r_value**2, 3),))
        return slope, intercept, r_value, p_value, std_err

    # From first and last point
    def FitAndPlot_2(df, first_segment_endtime):
        df = df.loc[df["TIME(DAYS)"] > first_segment_endtime]
        time = df['TIME(DAYS)']
        pressure = df['PRESSURE(PSI)']
        x_i = time.iloc[0]
        y_i = pressure.iloc[0]
        x_f = time.iloc[-1]
        y_f = pressure.iloc[-1]
        x=np.array([x_i, x_f])
        y=np.array([y_i, y_f])
        coefficients =  np.polyfit(x,y,1)
        slope = coefficients[0]
        intercept = coefficients[1]
        print("slope: ", slope, "intercept: ", intercept)
        y_values = intercept + slope * time
        leak_rate_in_sccm = round(slope*kPSI_PER_DAY_TO_SCCM,5)
        plt.plot(time, y_values, "g", label="From first and last points\n{0} sccm".format(leak_rate_in_sccm))

    # Uses the same as method 1 under the hood
    def FitAndPlot_3(df, first_segment_endtime):
        df = df.loc[df["TIME(DAYS)"] > first_segment_endtime]
        time = df['TIME(DAYS)'].to_numpy().reshape((-1,1))
        pressure = df['PRESSURE(PSI)'].to_numpy()
        model = LinearRegression().fit(time,pressure)
        print(model)
        r_sq = model.score(time, pressure)
        slope = model.coef_
        intercept = model.intercept_
        print("slope: ", slope, "intercept: ", intercept)
        y_values = intercept + slope * time
        leak_rate_in_sccm = round(slope[0]*kPSI_PER_DAY_TO_SCCM,5)
        plt.plot(time, y_values, "r", label="least squares 2\n{0} sccm\n(r2={1})".format(leak_rate_in_sccm, round(r_sq,3)))

    PlotDataPoints(df)
    FitAndPlot_1(df, first_segment_endtime)
    FitAndPlot_2(df, first_segment_endtime)
    #FitAndPlot_3(df, first_segment_endtime)

def main():
    options = GetOptions()

    df = ReadLeakRateFile(options.infile)

    PlotDataAndFit(df)

    title = options.infile.split("\\")[-1]
    title = title.partition(".")[0]
    plt.title(title)
    plt.legend()
    plt.show()

if __name__ == '__main__':
    main()
