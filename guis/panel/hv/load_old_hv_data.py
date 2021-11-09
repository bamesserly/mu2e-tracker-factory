# ===============================================================================
# Load a hv data CSV file into the local database
# ===============================================================================

import sqlalchemy as sqla  # for interacting with db
import sys, csv
import time
from pathlib import Path
from datetime import datetime as dt

# from guis.common.getresources import GetProjectPaths, GetLocalDatabasePath

kPROCESSES = list(range(1, 8))

# Given a panel and process, access the DB to get the procedure ID
# Taken from guis/panel/heater/load_heat_csv_into_db.py
def GetProcedureID(connection, panel, process):
    assert isinstance(panel, int) and panel <= 999
    assert process in kPROCESSES
    query = f"""
    SELECT procedure.id from procedure
    INNER JOIN straw_location on procedure.straw_location = straw_location.id
    WHERE straw_location.location_type = "MN"
    AND straw_location.number = {panel}
    AND procedure.station = "pan{process}"
    """
    result = connection.execute(query)
    result = result.first()[0]
    return result


# Converts timestamp of one specific format to epoch time
# Does not include miliseconds
def convert_to_epoch(date_time):
    dateFormat = "%Y-%m-%dT%H:%M:%S"
    epoch = int(time.mktime(time.strptime(date_time[0:18], dateFormat)))
    return epoch


def run(panel, process, data_file):
    # database = Path("dummy.db")
    try:
        assert Path(data_file).is_file()
    except AssertionError:
        print(f"Data file {data_file} not found!")
    # engine = sqla.create_engine("sqlite:///" + database)  # create engine

    # with engine.connect() as connection:
    #     pid = GetProcedureID(connection, int(panel), int(process))

    #     print(f"    Found PID for MN{panel} pro{process}: {pid}")

    #     queryRight = """
    #     INSERT OR IGNORE INTO measurement_pan5 (id, procedure, position, current_right, voltage, is_tripped, timestamp)
    #     VALUES (?, ?, ?, ?, ?, ?, ?);
    #     """
    #     queryLeft = """
    #     INSERT OR IGNORE INTO measurement_pan5 (id, procedure, position, current_left, voltage, is_tripped, timestamp)
    #     VALUES (?, ?, ?, ?, ?, ?, ?);
    #     """

    with open(data_file, "r") as f:
        dr = csv.DictReader(f)
        # Entry of dr looks like
        # OrderedDict([('Position', '68'), ('Current', '0.02'),
        # ('Side', 'Right'), ('Voltage', '1500V'), ('IsTripped', '0'),
        # ('Timestamp', '2021-04-13T14:07:16.219870')])

        # to_db = [
        #     (i["Position"], i["Current"], i["Voltage"], i["IsTripped"], i["Timestamp"])
        #     for i in dr
        # ]


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2], sys.argv[3])
