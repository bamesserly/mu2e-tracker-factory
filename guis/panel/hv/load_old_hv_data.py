# ===============================================================================
# Load a hv data CSV file into the local database
# ===============================================================================


"""
Reminder: these are the columns that we need to submit
 procedure     INTEGER NOT NULL
 position      INTEGER NOT NULL, (a number 0-96)
 current_left  REAL,
 current_right REAL, (right or left may be specified. If not, choose left).
 voltage       REAL, (either 1500 or 1100)
 is_tripped    BOOLEAN DEFAULT (either 0 (false) or 1 (true))
 timestamp     INTEGER ("epoch" time (msec, sec), if no time avail, use file create datetime).

step 1: submit a single data point with random values for the above columns
"""


import logging

logger = logging.getLogger("root")


import sqlalchemy as sqla  # for interacting with db
import sys, csv
import time
from pathlib import Path
from datetime import datetime as dt

from guis.common.getresources import GetProjectPaths, GetLocalDatabasePath

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


def run(panel=100, process=3, data_file=None):
    # try:
    #    assert Path(data_file).is_file()
    # except AssertionError:
    #    print(f"Data file {data_file} not found!")

    database = GetLocalDatabasePath()
    engine = sqla.create_engine("sqlite:///" + database)  # create engine

    with engine.connect() as connection:
        pid = GetProcedureID(connection, int(panel), int(process))

        print(f"    Found PID for MN{panel} pro{process}: {pid}")

        queryRight = """
        INSERT OR IGNORE INTO measurement_pan5 (procedure, position, current_right, voltage, is_tripped, timestamp)
        VALUES (?, ?, ?, ?, ?, ?);
        """
        queryLeft = """
        INSERT OR IGNORE INTO measurement_pan5 (procedure, position, current_left, voltage, is_tripped, timestamp)
        VALUES (?, ?, ?, ?, ?, ?);
        """
        to_db = [(pid, 0, 0.5, 1500, 0, 123456)]

        try:
            r_set = connection.execute(queryLeft, to_db)
            print(r_set)
        except sqla.exc.OperationalError as e:
            logger.error(e)
            error = str(e.__dict__["orig"])
            logger.error(error)
        except sqla.exc.IntegrityError as e:
            logger.error(e)
            error = str(e.__dict__["orig"])
            logger.error(error)
        else:
            logger.info(f"    Loaded {r_set.rowcount} data points into local DB.")
            logger.info(
                "    To send it to the network (and see it in DBV) "
                "trigger an automerge."
            )


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2], sys.argv[3])

# with open(data_file, "r") as f:
#    dr = csv.DictReader(f)
#    # Entry of dr looks like
#    # OrderedDict([('Position', '68'), ('Current', '0.02'),
#    # ('Side', 'Right'), ('Voltage', '1500V'), ('IsTripped', '0'),
#    # ('Timestamp', '2021-04-13T14:07:16.219870')])

# to_db = [
#    (i["Position"], i["Current"], i["Voltage"], i["IsTripped"], i["Timestamp"])
#    for i in dr
# ]
