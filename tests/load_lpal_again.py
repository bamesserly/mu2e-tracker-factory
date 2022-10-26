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

# connect to the database and return both the engine and connection
def connectDB():
    database = GetLocalDatabasePath()
    engine = sqla.create_engine("sqlite:///" + database)
    connection = engine.connect()

    return engine, connection

# make sure straw exists and return it
# from load_lpal_to_db_from_file.py
def get_or_create_straw(straw_id):
    straw = Straw.exists(straw_id=straw_id)
    if not straw:
        #logger.info("Straw not found in DB, creating straw.")
        straw = Straw.Straw(id=straw_id)
    assert straw
    return straw

# submit a new entry to the straw_present table
# returns "Success" if success, error message if failed
def newEntry(strawID, position, present, connection, time_in=None, time_out=None):
    # get the time for a timestamp
    t = time.time()
    # sqla doesn't appreciate having time_out be None so make sure you only use that column if it's not None
    if time_out == None:
        query = (
            "INSERT OR IGNORE INTO straw_present (id, straw, position, present, time_in, timestamp)"
            f"VALUES ({int(float(t)*1e6)}, {strawID}, {position}, {present}, {time_in}, {int(t)});"
        )
    else:
        query = (
            "INSERT OR IGNORE INTO straw_present (id, straw, position, present, time_in, time_out, timestamp)"
            f"VALUES ({int(float(t)*1e6)}, {strawID}, {position}, {present}, {time_in}, {time_out}, {int(t)});"
        )
    # attempt to commit to DB
    try:
        sendIt = connection.execute(query)
    except sqla.exc.OperationalError as e:
        return e
    except sqla.exc.IntegrityError as e:
        return e

    return "Success"

def findSpecial(search, find):
    if str(search).find(find) == -1:
        return 0
    else:
        return str(search).find(find)


###################################################################################################


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
    lpalLoc = StrawLocation.query().filter(StrawLocation.location_type == 'LPAL').filter(StrawLocation.number == int((sys.argv[1])[4:8])).one_or_none()

    # for each straw (row) from the file...
    for row in rows:
        # get the number and make sure it exists
        straw = get_or_create_straw((row["Straw"])[2:])

        # get the id of the correct position
        position = StrawPosition.query().filter(StrawPosition.location == lpalLoc.id).filter(StrawPosition.position_number == row["Position"]).one_or_none()
        
        # search for any location that is a panel
        inPanel = any(findSpecial(e, "MN") for e in straw.locate())
        # if there's a panel entry in straw_present for this straw get the time it entered the panel
        if inPanel:
            panelEntry = StrawPresent.query().filter(StrawPresent.straw == straw.id).join(StrawPosition, StrawPosition.id == StrawPresent.position).join(StrawLocation, StrawLocation.id == StrawPosition.location).filter(StrawLocation.location_type == "MN").one_or_none()
            panelInTime = panelEntry.time_in


        # also search for presence in an LPAL
        # if this is true, there's already an LPAL entry in straw_present for this
        #   straw and it could be skipped (although we could verify the accuracy...)
        inLPAL = any(findSpecial(e, "LPAL") for e in straw.locate())
        if inLPAL:
            # verify data here... ?
            continue # possibly heresy
        else:
            logger.info(f"Submitting straw ST{straw.id} to DB with values:")
            logger.info(f"Straw: {straw.id}, Position: {lpalLoc}, Present: {not inPanel}, time_in: {row['Timestamp']}, time_out: {panelInTime if inPanel else None}")
            newEntry(straw.id, position, not inPanel, connection, row['Timestamp'], (panelInTime if inPanel else None))
            #StrawPresent(straw.id, position, not inPanel, row['Timestamp'], (panelInTime if inPanel else None))
            



    return 0

if __name__ == "__main__":
    logger = SetupPANGUILogger("root", "LoadLPALToStrawPresentData")
    run(sys.argv[1])

