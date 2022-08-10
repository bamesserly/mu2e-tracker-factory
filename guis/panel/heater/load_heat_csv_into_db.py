# ===============================================================================
# Load a heat CSV file into the local database
# ===============================================================================

import sqlalchemy as sqla  # for interacting with db
import sys, csv
from pathlib import Path
from datetime import datetime as dt
from guis.common.panguilogger import SetupPANGUILogger
from guis.common.merger import isolated_automerge

from guis.common.getresources import GetProjectPaths, GetLocalDatabasePath

import logging

logger = logging.getLogger("root")

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


def run(panel, process, data_file):
    database = GetLocalDatabasePath()

    logger.info(f"Saving heat data to local database {database}")

    # db_check = input("PRESS <ENTER> TO VERIFY THIS DATABASE, ELSE PRESS CTRL-C\n")
    # if db_check:
    #     sys.exit("DB not verified, exiting")

    logger.info(f"    Data from file {data_file}")
    try:
        assert Path(data_file).is_file()
    except AssertionError:
        logger.error(f"    Data file {data_file} not found!")

    engine = sqla.create_engine("sqlite:///" + database)  # create engine

    with engine.connect() as connection:
        pid = GetProcedureID(connection, int(panel), int(process))

        logger.debug(f"    Found PID for MN{panel} pro{process}: {pid}")

        query = """
        INSERT OR IGNORE INTO panel_heat (id, procedure, temp_paas_a, temp_paas_bc, timestamp)
        VALUES (?, ?, ?, ?, ?);
        """
        # mark that we got to the point right before opening the file
        logger.debug(f"Opening {data_file} in mode 'r'...")

        with open(data_file, "r") as f:

            # mark that we got to the point right after opening the file
            logger.debug(f"Opened {data_file} in mode 'r'!")

            measurements = csv.DictReader(f)

            # mark that the csv.dictreader is good
            logger.debug("Successfully initialized DictReader")

            # a row from measurements:
            # {"Date" : 2022-04-19_160641}, {"PAASA_Temp[C]" : 22.35}, 
            #   {"2ndPAAS_Temp[C]": -99.00}, {"Epoc" : 1650402401.968532}

            # take one row so we can see what it looks like
            for row in measurements:
                logger.debug(f'Sample row from measurements: {row}')
                # breaking after one iteration seems like heresy but it works for what I want to do
                # (Not sure if you can index a dict reader like an array)
                break

            to_db = [
                (
                    int(float(row["Epoc"])*1e6),
                    pid,
                    row["PAASA_Temp[C]"],
                    row["2ndPAAS_Temp[C]"],
                    int(float(row["Epoc"]))
                )
                for row in measurements
            ]

            logger.debug(f'Length of to_db: {len(to_db)}')

            try:
                logger.debug("Entering try/except/else block, executing")
                r_set = connection.execute(query, to_db)
            except sqla.exc.OperationalError as e:
                logger.error(e)
                error = str(e.__dict__["orig"])
                logger.error(error)
            except sqla.exc.IntegrityError as e:
                # logger.error(e)
                error = str(e.__dict__["orig"])
                logger.error(error)
                logger.error(
                    "    At least one datapoint in this CSV file already exists in the DB."
                )
                logger.error("    Was this CSV file already loaded?")
                logger.error(
                    "    Tell Ben if this is unexpected or otherwise a problem."
                )
            else:
                logger.info(f"    Loaded {r_set.rowcount} data points into local DB.")

    logger.info("Doing an automerge so you don't have to!")
    logger.info("Seriously the data will definitely be in the network DB and in the DBV after this.")
    isolated_automerge()
    logger.info("All done! You can close the heater window now.")


if __name__ == "__main__":
    logger = SetupPANGUILogger("root", "LoadHeatData")
    run(sys.argv[1], sys.argv[2], sys.argv[3])
