# ===============================================================================
# Load a leak CSV file into the local database
# ===============================================================================
import sqlalchemy as sqla  # for interacting with db
import sys, csv
from pathlib import Path
from datetime import datetime as dt
import time, re
import string
from datetime import datetime as dt
import time, re

from guis.common.panguilogger import SetupPANGUILogger
from guis.common.getresources import GetProjectPaths, GetLocalDatabasePath
from guis.panel.leak.panel_leak_utilities import *
from random import randint
from guis.common.db_classes.procedure import Procedure

import logging

logger = logging.getLogger("root")

kFILENAME_DATE_FORMAT = "%y%m%d_%H%M"

DRY_RUN = False

################################################################################
# Misc Utilities
################################################################################
# Converts timestamp of one specific format to epoch time
# Does not include miliseconds
def convert_to_epoch(date_time):
    # "211012_1749"
    epoch = int(time.mktime(time.strptime(date_time, kFILENAME_DATE_FORMAT)))
    return epoch


# Given a panel and process, access the DB to get the procedure ID
def get_procedure_id(connection, panel_number, process):
    assert isinstance(panel_number, int) and panel_number <= 999
    # assert 131 <= panel_number
    assert process in kPROCESSES
    query = f"""
    SELECT procedure.id from procedure
    INNER JOIN straw_location on procedure.straw_location = straw_location.id
    WHERE straw_location.location_type = "MN"
    AND straw_location.number = {panel_number}
    AND procedure.station = "pan{process}"
    """
    result = connection.execute(query)
    result = result.first()
    try:
        assert result
    # procedure doesn't exist
    except AssertionError:
        input(
            f"Process 8 doesn't exist yet for MN{panel_number}. Press any key to create it or <ctrl-C> to quit> "
        )
        p = Procedure.PanelProcedure(process=process, panel_number=panel_number)
        result = p.id
    else:
        result = result[0]
    return result


# a leak test is defined uniquely by a procedure and a timestamp
def get_panel_leak_test_id(connection, procedure_id, timestamp):
    query = f"""
    SELECT panel_leak_test_details.id from panel_leak_test_details
    WHERE panel_leak_test_details.procedure = {procedure_id} AND
    panel_leak_test_details.timestamp = {timestamp}
    """
    result = connection.execute(query)
    result = result.first()
    return result


# lowercase, alphanum, no whitespace
def format_tag(tag):
    return "".join(filter(str.isalnum, tag)).lower()


# Extract date, panel, and tag from filename.
# Some validation on the results.
# "211012_1749_MN169 test 1.txt"
def parse_filename(filename):
    filename = Path(filename).stem  # remove txt suffix
    timestamp = filename[0:11]
    try:
        panel_number = re.search(r"MN\d\d\d", filename).group(0)[2:]
    except:
        panel_number = re.search(r"MN\d\d", filename).group(0)[2:]
    # tag = format_tag(filename[17:])
    tag_start_idx = filename.rfind(panel_number) + len(panel_number)
    tag = format_tag(filename[tag_start_idx:])
    return timestamp, panel_number, tag


# generic db query execute function
def execute_query(connection, query, entries):
    try:
        r_set = connection.execute(query, entries)
    except sqla.exc.OperationalError as e:
        logger.error(e)
        error = str(e.__dict__["orig"])
        logger.error(error)
    except sqla.exc.IntegrityError as e:
        # logger.error(e)
        error = str(e.__dict__["orig"])
        logger.error(error)
        logger.error(
            "    At least one datapoint in these entries already exists in the DB."
        )
    else:
        logger.info(f"Loaded {r_set.rowcount} data points into local DB.")
        # print(f"\nLOADED {r_set.rowcount} DATA POINTS INTO THE LOCAL DB.")


################################################################################
# Validate inputs
################################################################################
def timestamp_is_valid(timestamp):
    try:
        time.strptime(timestamp, kFILENAME_DATE_FORMAT)
        epoch_time = int(convert_to_epoch(timestamp))
        assert 1451628001 < epoch_time < 1672552801  # between 2016 and 2023
        return True
    except Exception as e:
        return False


def panel_number_is_valid(panel_number):
    try:
        assert 0 < int(panel_number) < 999
        return True
    except Exception as e:
        return False


def tag_is_valid(tag):
    try:
        assert (3 < len(tag) < 13) and ("test" in tag)
        return True
    except Exception as e:
        return False


# does file exist
def validate_data_file(data_file):
    # check infile exists
    try:
        assert Path(data_file).is_file()
    except AssertionError:
        logger.error(f"    Data file {data_file} not found!")


################################################################################
# Load leak data into the DB
################################################################################
# load an entry about a leak test into the panel_leak_test_details table
def load_test_details(connection, pid, timestamp, tag=None, elapsed_days=None):
    query = """
    INSERT OR IGNORE INTO panel_leak_test_details(id, procedure, tag, elapsed_days, timestamp)
    VALUES (?, ?, ?, ?, ?);
    """

    to_db = [(int(str(timestamp)+str(randint(1000,9999))), pid, tag, elapsed_days, timestamp)]

    execute_query(connection, query, to_db)


# load many entries from a leak rate test dataframe into the
# measurement_leak_rate table
def load_test_data(connection, df, test_id):
    query = """
    INSERT OR IGNORE INTO measurement_panel_leak(trial, pressure_fill, pressure_ref, pressure_diff, temp_box, temp_room, heater_pct, elapsed_days)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """

    to_db = [
        (
            test_id,
            entry["FillPSIA"],
            entry["RefPSIA"],
            entry["PRESSURE(PSI)"],
            entry["BOX TEMPERATURE(C)"],
            entry["ROOM TEMPERATURE(C)"],
            entry["Heater%"],
            entry["TIME(DAYS)"],
        )
        for index, entry in df.iterrows()
    ]
    # to_db = to_db[:5]

    execute_query(connection, query, to_db)


################################################################################
# main
################################################################################


def main(data_file):
    # print(
    #    f"\nLOADING LEAK TEST DATA INTO THE LOCAL DATABASE FROM FILE\n\n{data_file}\n"
    # )

    ############################################################################
    # Extract panel number, tag, and timestamp from filename
    ############################################################################
    validate_data_file(data_file)

    timestamp, panel_number, tag = parse_filename(data_file)

    logger.info(
        f"{Path(data_file).parent.name}/{Path(data_file).name}, {timestamp}, {panel_number}, {tag}"
    )

    while not timestamp_is_valid(timestamp):
        timestamp = input("enter timestamp in format YYMMDD_HHMM> ")
    while not panel_number_is_valid(panel_number):
        panel_number = input("enter panel_number XXX> ")
    while not tag_is_valid(tag):
        tag = input("enter tag like `test1`> ")

    panel_number = int(panel_number)
    epoch_time = convert_to_epoch(timestamp)

    # print(
    #    f"Test info:\n\ttimestamp: {timestamp}\n\tpanel: MN{panel_number}\n\ttag: {tag}"
    # )

    ############################################################################
    # Read leak csv data into data frame
    ############################################################################
    is_new_format = True
    df = ReadLeakRateFile(data_file, is_new_format)

    ############################################################################
    # Quit if this is a dry run
    ############################################################################
    if DRY_RUN:
        return

    ############################################################################
    # Set up DB  connection
    ############################################################################
    database = GetLocalDatabasePath()

    # db_check = input(f"PRESS <ENTER> TO CONFIRM THIS DATABASE\n{database}\nELSE PRESS CTRL-C\n")
    # if db_check:
    #    sys.exit("DB not verified, exiting")

    engine = sqla.create_engine("sqlite:///" + database)  # create engine

    ############################################################################
    # Save test meta info in panel_leak_test_details
    # Save raw data in measurement_panel_leak
    ############################################################################
    with engine.connect() as connection:
        # is record of this test already in the db? if so, do nothing
        procedure_id = get_procedure_id(connection, panel_number, 8)
        test_id = get_panel_leak_test_id(connection, procedure_id, epoch_time)
        if test_id:
            test_id = test_id[0]
            # print(
            #    f"\nRECORD OF THIS TEST ALREADY EXISTS IN THE DB. WILL ONLY LOAD NEW POINTS."
            # )
            logger.info(
                f"Found pre-existing leak test ID for MN{panel_number} {timestamp}: {test_id}."
            )
        else:
            # Get the elapsed time of the test
            elapsed_days = df["TIME(DAYS)"].max()
            assert elapsed_days < 6  # test shouldn't have gone over 4 days, right?

            # Load record of this test into the panel_leak_test_details table
            load_test_details(connection, procedure_id, epoch_time, tag, elapsed_days)

            # Look up the test_id that we just created
            test_id = get_panel_leak_test_id(connection, procedure_id, epoch_time)[0]

        # Load the data for this test into measurement_panel_leak table
        load_test_data(connection, df, test_id)

    print()


if __name__ == "__main__":
    logger = SetupPANGUILogger("root", "LoadPanelLeakData")
    try:
        main(sys.argv[1])
    except IndexError:
        sys.exit("Must provide input data file.")
