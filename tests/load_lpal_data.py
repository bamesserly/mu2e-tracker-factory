
# essentially load_lpal_to_db_from_file.py, but restarting with a blank slate
# will mark code copied from load_lpal_to_db_from_file.py as such
import sys, sqlalchemy as sqla
from csv import DictReader, DictWriter
import time
import tests.straw_present_utils as s_util
from guis.common.getresources import GetProjectPaths, GetLocalDatabasePath
from guis.common.db_classes.straw import Straw
from guis.common.panguilogger import SetupPANGUILogger
import logging

logger = logging.getLogger("root")


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

    #{'Position': '0', 'Straw': 'ST15659', 'Timestamp': '1621437796'}
    #{'Position': '2', 'Straw': 'ST15589', 'Timestamp': '1621363167'}
    #{'Position': '4', 'Straw': 'ST15658', 'Timestamp': '1621437810'}
    #{'Position': '6', 'Straw': 'ST15588', 'Timestamp': '1621363182'}

# make sure straw exists
# modified from load_lpal_to_db_from_file.py
def get_or_create_straw(straw_id):
    straw = Straw.exists(straw_id=straw_id)
    if not straw:
        logger.info("Straw not found in DB, creating straw.")
        straw = Straw.Straw(id=straw_id)
    assert straw

# happens twice in main, don't need double the amount of code
def integrityCheck(strawNum, connection, numErrors, isInitital):
    initOrNo = "Initial" if isInitital else "Secondary"
    # check integrity of this straw in straw_present
    integrity = s_util.checkStrawIntegrity(strawNum,connection)
    if integrity==0:
        # all is good if integrity = 0
        print("Integrity check = yey")
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
    
    return 0


# main function, takes name of lpal file (like LPAL0123_LPALID01.csv)
def run(lpal_file=None):

    # yall ready for this??
    logger.info('Warning: This script will potentially modify the database.  Enter "Y" to continue.')
    response = input()
    if not(response == "Y" or response =="y"):
        logger.info("Script aborted.")
        return

    # get LPAL number
    lpalNum = int((sys.argv[1])[4:8])

    # get rows and fields from lpal file
    rows, fields = read_file(lpal_file)

    # connect to DB
    engine, connection = connectDB()

    # count errors
    numErrors = 0

    # for each straw
    for row in rows:
        # get the number and make sure it exists
        strawNum = (row["Straw"])[2:]
        get_or_create_straw(strawNum)

        # check integrity of this straw in straw_present
        if integrityCheck(strawNum, connection, numErrors, True):
            # if we get an error code, skip this straw.
            continue

        # location names/numbers [(LPAL, 300),(MN, 135),etc...]
        locations = s_util.strawLocations(strawNum, connection)
        # entries in straw_present (the full thing plus a readable string for location)
        # list of tuples of the form:
        #   (<id>, <straw>, <LOCATION TYPE AS STRING>, <location>, <present>, <time_in>, <time_out>, <timestamp>)
        entries = s_util.strawPresencesReadable(strawNum, connection)

        
        # bools to mark panel and LPAL presence
        inPanel = False
        inLPAL = False

        # determine if there's a straw_present entry for LPAL and for panel
        for toop in locations:
            for thing in toop:
                if thing == "MN":
                    inPanel = True
                elif thing == "LPAL":
                    inLPAL = True

        # if panel found
        if inPanel:
            # variable to get the time_in from panel
            panelInTime = -1
            # if only one entry total
            if isinstance(entries[0], int):
                if entries[2] == "MN":
                    panelInTime = entries[5]
            # if multiple entries
            else:
                for toop in entries:
                    if toop[2] == "MN":
                        panelInTime = toop[5]
        
        # if no lpal entry found
        if not inLPAL:
            # get correct position id
            lpalID = s_util.getLPALID(lpalNum, connection)
            posID = s_util.getPositionID(lpalID, row["Position"], connection)
            # add the lpal entry
            logger.info(f"Submitting straw ST{strawNum} to DB with values:")
            logger.info(f"Straw: {strawNum}, Position: {posID}, Present: {not inPanel}, time_in: {row['Timestamp']}, time_out: {panelInTime if inPanel else None}")
            result=s_util.newEntry(
                strawNum,
                posID,
                (not inPanel),# needs revisiting, DEFAULTS TO TRUE (1) IF NO PANEL FOUND
                connection,
                time_in=row["Timestamp"],
                time_out=(panelInTime if inPanel else None)
            )
            logger.info(f'Straw ST{strawNum} Query result: {result}')
        else:
            logger.info(f"LPAL entry for ST{strawNum} already found.")
            

        # check integrity of this straw in straw_present
        if integrityCheck(strawNum, connection, numErrors, False):
            # if we get an error code, skip this straw.
            continue

    #END LOOP


# id                straw   position            present time_in time_out    timestamp
# 16488237931915190	16312	16488229872014158	0	1648823793	1648840911	1648840911
# 16488409115789145	16312	16486600691503178	1	1648840912	NULL        1648840912
        




    return

if __name__ == "__main__":
    logger = SetupPANGUILogger("root", "LoadLPALToPresentData")
    run(sys.argv[1])