import sys, sqlalchemy as sqla
from csv import DictReader, DictWriter
import time
from guis import panel
from guis.common.getresources import GetProjectPaths, GetLocalDatabasePath
from guis.common.db_classes.straw import Straw
from guis.common.db_classes.straw_location import StrawLocation, LoadingPallet, StrawPresent, StrawPosition
from guis.common.panguilogger import SetupPANGUILogger
import logging

logger = logging.getLogger("root")

def read_file(lpal_file):
    with open(lpal_file,"r") as f:
        reader = DictReader(line for line in f if line.split(",")[0])
        rows = [row for row in reader]
    return rows, reader.fieldnames

# make sure straw exists and return it
# from load_lpal_to_db_from_file.py
def get_or_create_straw(straw_id):
    straw = Straw.exists(straw_id=straw_id)
    if not straw:
        #logger.info("Straw not found in DB, creating straw.")
        straw = Straw.Straw(id=straw_id)
    assert straw
    return straw



def run(lpal_file):

    # make sure user wants to proceed
    logger.info('Warning: This script will potentially modify the database.  Enter "Y" to continue.')
    response = input()
    if not(response == "Y" or response =="y"):
        logger.info("Script aborted.")
        return

    # get rows and fields from lpal file
    rows, fields = read_file(lpal_file)

    # get LPAL location ID
    lpalLoc = StrawLocation.query().filter(StrawLocation.location_type == 'LPAL').filter(StrawLocation.number == int((sys.argv[1])[4:8]))

    # for each straw (row) from the file...
    for row in rows:
        logger.info(f'Straw{(row["Straw"])[2:]}')
        # get the number and make sure it exists
        straw = get_or_create_straw((row["Straw"])[2:])

        
        # search for any location that is a panel
        inPanel = any(str(e).find("MN") for e in straw.locate())
        # if there's a panel entry in straw_present for this straw get the time it entered the panel
        if inPanel:
            print("Skip here")
            panelInTime = -1
            #panelEntry = StrawPresent._queryObject().filter(StrawPresent.straw == straw.id).join(StrawPosition, StrawPosition.id == StrawPresent.id).join(StrawLocation, StrawLocation.id == StrawPosition.location).filter(StrawLocation.location_type == "MN")
            #panelEntry = straw.query().filter(StrawPresent.straw == straw.id).join(StrawPosition, StrawPosition.id == StrawPresent.id).join(StrawLocation, StrawLocation.id == StrawPosition.location).filter(StrawLocation.location_type == "MN")


        # also search for presence in an LPAL
        # if this is true, there's already an LPAL entry in straw_present for this
        #   straw and it could be skipped (although we could verify the accuracy...)
        inLPAL = any(str(e).find("LPAL") for e in straw.locate())
        if inLPAL:
            # verify data here
            continue # possibly heresy
        else:
            logger.info(f"Submitting straw ST{straw.id} to DB with values:")
            logger.info(f"Straw: {straw.id}, Position: {42}, Present: {not inPanel}, time_in: {row['Timestamp']}, time_out: {panelInTime if inPanel else None}")
            #StrawPresent.StrawPresent(straw.id, lpalLoc, not inPanel, row['Timestamp'], (panelInTime if inPanel else None))





    return 0




'''
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
def integrityCheck(straw, connection, numErrors, isInitital):
    initOrNo = "Initial" if isInitital else "Secondary"
    # check integrity of this straw in straw_present
    integrity = s_util.checkStrawIntegrity(straw,connection)
    # checkStrawIntegrity returns 0 if all is good, 1-3 for error codes
    if integrity==0:
        logger.info(f"{initOrNo} integrity check: {straw.id} passes.")
    elif integrity == 1:
        logger.error(f"{initOrNo} integrity check: {straw.id} has multiple of the same locaiton.")
        numErrors += 1
        return 1
    elif integrity == 2:
        logger.error(f"{initOrNo} integrity check: {straw.id} is present in multiple locations.")
        numErrors += 1
        return 1
    elif integrity == 3:
        logger.error(f"{initOrNo} integrity check: {straw.id} has conflicting timestamps.")
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

    # get LPAL location ID
    lpalLoc = StrawLocation.query().filter(StrawLocation.location_type == 'LPAL').filter(StrawLocation.number == int((sys.argv[1])[4:8]))

    # collect number of errors
    numErrors = 0

    for row in rows:
        #logger.info(f'Straw{(row["Straw"])[2:]}')
        # get the number and make sure it exists
        straw = s_util.get_or_create_straw((row["Straw"])[2:])

        # check integrity on straw_present
        if integrityCheck(straw, connection, numErrors, True):
            # error found, skip straw
            continue
        
        # search for any location that is a panel
        inPanel = any(str(e).find("MN") for e in straw.locations())
        inLPAL = any(str(e).find("LPAL") for e in straw.locations())
        

        # if in a panel get the in time
        if inPanel:
            panelEntry = straw.currentPresence()
            # if straw isn't present here
            if panelEntry[2] is not 1:
                # throw error or something
                continue
            # otherwise get the in time to be submitted later
            panelInTime = panelEntry[3]
        
        if not inLPAL:
            logger.info(f"Submitting straw ST{straw.id} to DB with values:")
            logger.info(f"Straw: {straw.id}, Position: {lpalLoc}, Present: {not inPanel}, time_in: {row['Timestamp']}, time_out: {panelInTime if inPanel else None}")
            result=s_util.newEntry(
                straw.id,
                lpalLoc,
                (not inPanel),# needs revisiting, DEFAULTS TO TRUE (1) IF NO PANEL FOUND
                connection,
                time_in=row["Timestamp"],
                time_out=(panelInTime if inPanel else None)
            )

        # check integrity on straw_present
        if integrityCheck(straw, connection, numErrors, False):
            # error found, skip straw
            continue




    return
'''

if __name__ == "__main__":
    logger = SetupPANGUILogger("root", "LoadLPALToStrawPresentData")
    run(sys.argv[1])

