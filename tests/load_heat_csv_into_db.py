# ===============================================================================
# Load a heat CSV file into the local database
# ===============================================================================

import sqlalchemy as sqla  # for interacting with db
import sys, csv
from datetime import datetime as dt

from guis.common.getresources import GetProjectPaths, GetLocalDatabasePath

kPROCESSES = list(range(1, 8))

# Given a panel and process, access the DB to get the procedure ID
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


# Deprecated
def WriteSingleMeasurementToDB(connection, pid, t1, t2, timestamp):
    query = f"""
    INSERT INTO panel_heat (procedure, temp_paas_a, temp_paas_bc, timestamp)
    VALUES ('{pid}','{t1}','{t2}','{timestamp}')
    """
    print(query)
    connection.execute(query)

    # to_db = [(i['col1'], i['col2']) for i in dr]
    # cur.executemany("INSERT INTO t (col1, col2) VALUES (?, ?);", to_db)
    # con.commit()


def run(panel, process):
    database = GetLocalDatabasePath()

    print(f"Writing to heat data to local database {database}")

    db_check = input("PRESS <ENTER> TO VERIFY THIS DATABASE, ELSE PRESS CTRL-C\n")
    if db_check:
        sys.exit("DB not verified, exiting")

    engine = sqla.create_engine("sqlite:///" + database)  # create engine

    with engine.connect() as connection:
        pid = GetProcedureID(connection, int(panel), int(process))

        print(f"Found procedure ID for panel {panel} process {process}: {pid}")

        # data_file = "MN109_2021-04-02.csv"
        data_file = (
            "MN"
            + str(panel)
            + "_"
            + dt.now().strftime("%Y-%m-%d")
            + "_pro"
            + str(process)
            + ".csv"
        )

        data_file = GetProjectPaths()["heatdata"] / data_file

        print(f"Reading data file {data_file}")

        try:
            assert data_file.is_file()
        except AssertionError:
            print(f"data file {data_file} not found!")

        query = """
        INSERT OR IGNORE INTO panel_heat (procedure, temp_paas_a, temp_paas_bc, timestamp)
        VALUES (?, ?, ?, ?);
        """

        with open(data_file, "r") as f:
            dr = csv.DictReader(f)

            # an entry of dr looks like:
            # OrderedDict([('Date', '2021-07-02_073223'), ('PAASA_Temp[C]', '-242.02'), ('2ndPAAS_Temp[C]', '-99.00'), ('Epoc', '1625229143.7965412')])
            to_db = [
                (pid, i["PAASA_Temp[C]"], i["2ndPAAS_Temp[C]"], int(float(i["Epoc"])))
                for i in dr
            ]

            # to_db = to_db[:5]

            try:
                r_set = connection.execute(query, to_db)
            except sqla.exc.OperationalError as e:
                print(e)
                error = str(e.__dict__["orig"])
                print(error)
            except sqla.exc.IntegrityError as e:
                # print(e)
                error = str(e.__dict__["orig"])
                print(error)
                print(
                    "ERROR: At least one datapoint in this CSV file already exists in the DB."
                )
                print("ERROR: Was this CSV file already loaded?")
                print("ERROR: Tell Ben if this is unexpected or otherwise a problem.")
            else:
                print(
                    f"Loaded {r_set.rowcount} heat data points into the local DB for panel {panel} process {process}"
                )
