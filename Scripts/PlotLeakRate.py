# New data format as of 2020-09-16
# Currently, just plots the pressure vs time.
import pandas as pd
import matplotlib.pyplot as plt
import optparse

# Unit conversion factor for inches of water to psi.
kINCHES_H2O_PER_PSI = 27.6799048

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

def PlotPressure(df, title):
    plt.close('all')
    df.plot(x="TIME(DAYS)", y="PRESSURE(PSI)")
    plt.title(title)
    plt.show()

def main():
    options = GetOptions()
    df = ReadLeakRateFile(options.infile)
    plot_title = options.infile.split("\\")[-1]
    plot_title = plot_title.partition(".")[0]
    PlotPressure(df, plot_title)

if __name__ == '__main__':
    main()
