import sys, sqlalchemy as sqla
from csv import DictReader, DictWriter
import time
import tests.straw_present_utils as s_util
from guis.common.getresources import GetProjectPaths, GetLocalDatabasePath
from guis.common.db_classes.straw import Straw
from guis.common.db_classes.straw_location import StrawLocation, LoadingPallet
from guis.common.panguilogger import SetupPANGUILogger
import logging

logger = logging.getLogger("root")

# connect to the database and return both the engine and connection
def connectDB():
    database = GetLocalDatabasePath()
    engine = sqla.create_engine("sqlite:///" + database)
    connection = engine.connect()

    return engine, connection

# from load_lpal_to_db_from_file.py
def read_file(lpal_file):
    with open(lpal_file,"r") as f:
        reader = DictReader(line for line in f if line.split(",")[0])
        rows = [row for row in reader]
    return rows, reader.fieldnames

# happens twice in main(run()), don't need double the amount of code
# returns 0 for no errors and 1 for errors
def integrityCheck(strawNum, connection, numErrors, isInitital):
    initOrNo = "Initial" if isInitital else "Secondary"
    # check integrity of this straw in straw_present
    integrity = s_util.checkStrawIntegrity(strawNum,connection)
    # checkStrawIntegrity returns 0 if all is good, 1-3 for error codes
    if integrity==0:
        logger.info(f"{initOrNo} integrity check: Straw ST{strawNum} passes.")
    elif integrity == 1:
        logger.error(f"{initOrNo} integrity check: Straw ST{strawNum} has multiple of the same locaiton.")
        numErrors += 1
        return 1
    elif integrity == 2:
        logger.error(f"{initOrNo} integrity check: Straw ST{strawNum} is present in multiple locations.")
        numErrors += 1
        return 1
    elif integrity == 3:
        logger.error(f"{initOrNo} integrity check: Straw ST{strawNum} has conflicting timestamps.")
        numErrors += 1
        return 1
    # no problems found
    return 0



def run(lpal_file):

    # make sure user wants to proceed
    logger.info('Warning: This script will potentially modify the database.  Enter "Y" to continue.')
    response = input()
    if not(response == "Y" or response =="y"):
        logger.info("Script aborted.")
        return


    # get rows and fields from lpal file
    rows, fields = read_file(lpal_file)

    # connect to DB
    engine, connection = connectDB()

    for row in rows:
        # get the number and make sure it exists
        straw = s_util.get_or_create_straw((row["Straw"])[2:])

        # returns list of all straws positions on straw_present
        print(straw.locate())




    return


if __name__ == "__main__":
    logger = SetupPANGUILogger("root", "LoadLPALToStrawPresentData")
    run(sys.argv[1])