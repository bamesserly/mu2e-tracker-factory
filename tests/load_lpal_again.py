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
        logger.error(e)
        return e
    except sqla.exc.IntegrityError as e:
        logger.error(e)
        return e

    return "Success"

def findSpecial(search, find):
    if str(search).find(find) == -1:
        return 0
    else:
        return str(search).find(find)


# check if any straw present entries for straw contradict eachother
#   i.e. check for timestamps that indicate it was in two places at once,
#   or if it supposedly exists in two places at once right now
# ret val | meaning
#       0 | no contradictions, all is good
#       1 | multiple of the same position
#       2 | marked as present in multiple places
#       3 | timestamp conflict
def checkStrawIntegrity(straw):
    # dict of positions
    positions = {}
    # bool for tracking number of "present = 1" found
    presentFound = False

    # loop through entries
    for thing in StrawPresent.query().filter(StrawPresent.straw == straw.id).all():
        # if key (position) exists in dict already --> two positions found
        if thing.position in positions:
            logger.error(f'Two of the same position detected for straw {straw}')
            return 1

        # if straw is present at this position
        if thing.present == 1:
            # if it hasn't been found elsewhere yet
            if not presentFound:
                # mark that we found it
                presentFound = True
            # if it has been found elsewhere
            else:
                # it exists in two places which is bad
                logger.error(f'Multiple present = 1 for straw {straw}')
                return 2
        
        # CPALs don't usually have out times so lets not include those
        cpals = StrawPresent.query().filter(StrawPresent.straw == straw.id).join(StrawPosition, StrawPosition.id == StrawPresent.position).join(StrawLocation, StrawLocation.id == StrawPosition.location).filter(StrawLocation.location_type == "CPAL").all()
        if len(cpals) == 0:
            # add to dict
            #   {position : (present, time_in, time_out)}
            positions[thing.position] = (thing.present, thing.time_in, thing.time_out)
    # end of loop body

    # check timestamps for weirdness
    # there is likely a faster way to do this, n^2 time is heresy
    # for each position
    for key1 in positions:
        # get the timestamps (tr abbreviation = time range)
        tr1 = (
            positions[key1][1] if positions[key1][1] is not None else -1,
            positions[key1][2] if positions[key1][2] is not None else 1e12
        )
        # for each other key
        for key2 in positions:
            # each OTHER key
            if key1 == key2:
                # skip if it's the same one
                continue
            # get the timestamps for another position
            tr2 = (
                positions[key2][1] if positions[key2][1] is not None else -1,
                positions[key2][2] if positions[key2][2] is not None else 1e12
            )
            # if tr2 start or end is within range of tr1 we have a problem
            if tr2[0] > tr1[0] and tr2[0] < tr1[1]:
                logger.error(f'Timestamp conflict for straw {straw}')
                return 3
            if tr2[1] > tr1[0] and tr2[1] < tr1[1]:
                logger.error(f'Timestamp conflict for straw {straw}')
                return 3



    # didn't find any red flags
    return 0


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
    # if no LPAL found
    if lpalLoc == None:
        logger.error(f'LPAL {(sys.argv[1])[4:8]} not found, aborting.')
        # bad ending :(
        return 1

    # for each straw (row) from the file...
    for row in rows:
        # get the number and make sure it exists
        straw = get_or_create_straw((row["Straw"])[2:])

        # get the id of the correct position
        position = (StrawPosition.query().filter(StrawPosition.location == lpalLoc.id).filter(StrawPosition.position_number == row["Position"]).one_or_none()).id

        # search for any location that is an LPAL, if found we can skip this one
        inLPAL = any(findSpecial(e, "LPAL") for e in straw.locate(current=False))
        if inLPAL:
            logger.info(f'Aborting submission for straw {straw.id}, LPAL entry already present.')
            # verify data accuracy here... ?
            continue # possibly heresy

        integrity = checkStrawIntegrity(straw)
        if integrity != 0:
            # problem found!
            logger.info(f'Aborting submission for straw {straw.id} due to integrity error.')
            continue
        
        # search for any location that is a panel (to get an out time for the LPAL)
        inPanel = any(findSpecial(e, "MN") for e in straw.locate())
        # if there's a panel entry in straw_present for this straw get the time it entered the panel
        if inPanel:
            panelEntry = StrawPresent.query().filter(StrawPresent.straw == straw.id).join(StrawPosition, StrawPosition.id == StrawPresent.position).join(StrawLocation, StrawLocation.id == StrawPosition.location).filter(StrawLocation.location_type == "MN").one_or_none()
            panelInTime = panelEntry.time_in



        if not inLPAL:
            logger.info(f"Submitting straw ST{straw.id} to DB with values:")
            logger.info(f"Straw: {straw.id}, Position: {position}, Present: {not inPanel}, time_in: {row['Timestamp']}, time_out: {panelInTime if inPanel else None}")
            newEntry(straw.id, position, not inPanel, connection, row['Timestamp'], (panelInTime if inPanel else None))
            #StrawPresent(straw.id, position, not inPanel, row['Timestamp'], (panelInTime if inPanel else None))

        integrity = checkStrawIntegrity(straw)
        if integrity != 0:
            # problem found!
            logger.info(f'The script may have corrupted the data for straw {straw.id}.  Sowwy! >_<')

    # end of for row in rows loop
    # !!! Loop contains two continue statements, one in the "if integrity != 0", and one in the "if inLPAL" block.


    # end of script
    return 0

if __name__ == "__main__":
    logger = SetupPANGUILogger("root", "LoadLPALToStrawPresentData")
    run(sys.argv[1])

