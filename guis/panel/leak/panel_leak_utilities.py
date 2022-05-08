import pandas as pd
import datetime

################################################################################
# Constants
################################################################################
# Unit conversion factor for inches of water to psi.
kINCHES_H2O_PER_PSI = 27.6799048

# Unit conversion factor for PSI change per day to sccm
kPSI_PER_DAY_TO_SCCM = 0.17995993587933934

kPROCESSES = list(range(1, 9))

################################################################################
# Helper functions
################################################################################
def ConvertInchesH2OToPSI(pressure_inches_h2O):
    return pressure_inches_h2O / kINCHES_H2O_PER_PSI


################################################################################
# READ INPUT
# Read the raw data (old or new format) into a dataframe
# dataframe format:
# TIME(DAYS)  FillPSIA  RefPSIA  PRESSURE(PSI)  BOX TEMPERATURE(C)  ROOM TEMPERATURE(C)  Heater%
################################################################################
def ReadLeakRateFile(infile, is_new_format=True, fix_lv_config_box=-1):
    if is_new_format:
        # read input file
        df = pd.read_csv(infile, engine="python", header=1, sep="\t")

        # remove whitespace from column headers
        df.columns = df.columns.str.replace(" ", "")

        # convert pressure from inches of water to psi
        # 2022-05 note: we don't use this recorded diff value
        df['Diff"H2O'] = ConvertInchesH2OToPSI(df['Diff"H2O'])
        df = df.rename(columns={'Diff"H2O': "PRESSURE(PSI)"})

        # rename time
        df = df.rename(columns={"Elapdays": "TIME(DAYS)"})

        # rename temps
        df = df.rename(columns={"RoomdegC": "ROOM TEMPERATURE(C)"})
        df = df.rename(columns={"EncldegC": "BOX TEMPERATURE(C)"})

        # Labview data collection parameters changed.
        # "period A" === pre Dec 27, 2021
        # "period B" === Dec 28, 2021 - May 4, 2022
        # "period C" === May 5, 2022 - Now
        #
        # Reason to think the params changed erroneously for period B.
        #
        # Pressures coming off the DAQ are undergo a linear calibration shift:
        #       recorded_pressure = raw_pressure * gain + offset
        #
        # Params are channel dependent.
        #
        # Only the offsets (not the gains) changed:
        #
        # BOX 1
        #           | panel offset (chan 101) |  ref offset (chan 102)
        # period A  |         -0.015          |       -7.510
        # period B  |          0.000          |       -7.500
        #
        # BOX 2
        #           | panel offset (chan 103) |  ref offset (chan 104)
        # period A  |         -7.530          |       -7.500
        # period B  |         -7.500          |       -7.460
        if fix_lv_config_box == 1:
            df["FillPSIA"] = df["FillPSIA"] - 0.015
            df["RefPSIA"]  = df["RefPSIA"]  - 0.010
        elif fix_lv_config_box == 2:
            df["FillPSIA"] = df["FillPSIA"] - 0.030
            df["RefPSIA"]  = df["RefPSIA"]  - 0.040


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

        # rename temp
        df = df.rename(columns={"TEMPERATURE(C)": "BOX TEMPERATURE(C)"})

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
        # df['PSI/degC'] = df["PRESSURE(PSI)"]/df["ROOM TEMPERATURE(C)"]

        return df
