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

import logging

logger = logging.getLogger("root")


################################################################################
# Misc Utilities
################################################################################
# Converts timestamp of one specific format to epoch time
# Does not include miliseconds
def convert_to_epoch(date_time):
    # 2021-04-13T14:07:16.219870
    # "211012_1749"
    date_format = "%y%m%d_%H%M"
    epoch = int(time.mktime(time.strptime(date_time[0:18], date_format)))
    return epoch


# Given a panel and process, access the DB to get the procedure ID
def get_procedure_id(connection, panel, process):
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


# Extract date, panel, and tag from filename
# "211012_1749_MN169 test 1.txt"
def parse_filename(filename):
    logger.debug("Getting test info from input file.")
    filename = Path(filename).stem  # remove txt suffix
    timestamp = filename[0:11]
    panel_number = int(re.search(r"MN\d\d\d", filename).group(0)[2:])
    tag = format_tag(filename[17:])
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
        logger.debug(f"Loaded {r_set.rowcount} data points into local DB.")
        print(f"\nLOADED {r_set.rowcount} DATA POINTS INTO THE LOCAL DB.")


################################################################################
# Validate inputs
################################################################################
# is test timestamp valid? if not prompt user
def validate_timestamp(timestamp):
    # is the timestamp extracted from the filename correct?
    temp_timestamp = input(
        f"Found timestamp {timestamp}.\n"
        "If correct, press <return>, else enter timestamp in format YYMMDD_HHMM> "
    )
    timestamp = timestamp if temp_timestamp == "" else temp_timestamp

    # is the timestamp valid?
    while True:
        try:
            epoch_time = int(convert_to_epoch(timestamp))
            assert 1451628001 < epoch_time < 1672552801  # between 2016 and 2023
            return timestamp, epoch_time
        except ValueError:
            logger.error(
                f"The timestamp found/provided {timestamp} must be in the format YYMMDD_HHMM."
            )
            timestamp = input("enter timestamp in format YYMMDD_HHMM> ")
            continue
        except AssertionError:
            logger.error(
                f"The timestamp found/provided {timestamp} doesn't make sense."
            )
            timestamp = input("enter timestamp in format YYMMDD_HHMM> ")
            continue


# is panel valid? if not prompt user
def validate_panel_number(panel_number):
    temp_panel_number = input(
        f"Found panel_number {panel_number}. If correct, press <return>, else enter panel_number XXX> "
    )
    panel_number = panel_number if temp_panel_number == "" else temp_panel_number
    while True:
        try:
            assert 0 < int(panel_number) < 999
            return panel_number
        except ValueError:
            logger.error(
                f"The panel_number found/provided {panel_number} isn't an integer."
            )
            panel_number = input("enter panel_number XXX> ")
            continue
        except AssertionError:
            logger.error(
                f"The panel_number found/provided {panel_number} doesn't make sense."
            )
            panel_number = input("enter panel_number XXX> ")
            continue
        break


# user confirm tag (e.g. "test1") associated with this test
def validate_tag(tag):
    while True:
        temp_tag = input(
            f"Using tag {tag}.\n"
            f"If correct, press <return>,\n"
            f'else enter a tag like "test1" (whitespace and nonalphanum characters will be removed)> '
        )
        if temp_tag == "":
            return tag
        else:
            tag = temp_tag


# does file exist
def validate_data_file(data_file):
    logger.debug(f"Leak test datafile provided: {data_file}")

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
    print(
        f"\nLOADING LEAK TEST DATA INTO THE LOCAL DATABASE FROM FILE\n\n{data_file}\n"
    )

    # check input file, panel number, test timestamp, test tag
    validate_data_file(data_file)
    timestamp, panel_number, tag = parse_filename(data_file)
    logger.debug(f"{timestamp},{panel_number},{tag} extracted from filename.")
    print(
        f"Test info:\n\ttimestamp: {timestamp}\n\tpanel: MN{panel_number}\n\ttag: {tag}"
    )
    epoch_time = convert_to_epoch(timestamp)

    # timestamp, epoch_time = validate_timestamp(timestamp)
    # panel_number = validate_panel_number(panel_number)
    # tag = validate_tag(tag)

    # set up database
    database = GetLocalDatabasePath()

    logger.debug(f"Saving leak test data into the local database {database}")

    # db_check = input(f"PRESS <ENTER> TO CONFIRM THIS DATABASE\n{database}\nELSE PRESS CTRL-C\n")
    # if db_check:
    #    sys.exit("DB not verified, exiting")

    engine = sqla.create_engine("sqlite:///" + database)  # create engine

    # Read leak csv data into data frame
    is_new_format = True
    df = ReadLeakRateFile(data_file, is_new_format)

    # load up all the data within a database connection
    with engine.connect() as connection:
        # is record of this test already in the db? if so, do nothing
        procedure_id = get_procedure_id(connection, panel_number, 8)
        test_id = get_panel_leak_test_id(connection, procedure_id, epoch_time)
        if test_id:
            test_id = test_id[0]
            print(
                f"\nRECORD OF THIS TEST ALREADY EXISTS IN THE DB. WILL ONLY LOAD NEW POINTS."
            )
            logger.debug(
                f"Found pre-existing leak test ID for MN{panel_number} {timestamp}: {test_id}."
            )
        else:
            # Get the elapsed time of the test
            elapsed_days = df["TIME(DAYS)"].max()
            assert elapsed_days < 4  # test shouldn't have gone over 4 days, right?

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
