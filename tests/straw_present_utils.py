from multiprocessing import connection
import os, time
import sqlalchemy as sqla
from guis.common.db_classes.straw import Straw
from guis.common.getresources import GetProjectPaths, GetLocalDatabasePath


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

# check if straw has only one entry per position and one present = 1
# returns   0 if all is good
#           1 if two or more of the same position found
#           2 if two or more "present = 1" in straw_present for this straw
#           3 if there's a timestamp conflict
def checkStrawIntegrity(straw, connection):
    # dict of positions
    positions = {}
    # bool for tracking number of "present = 1" found
    presentFound = False

    # loop through entries
    for toop in straw.presences():
        # if key (position) exists in dict already --> two positions found
        if toop[1] in positions:
            print("Two locations detected")
            return 1

        # if straw is present at this position
        if toop[2] == 1:
            # if it hasn't been found elsewhere yet
            if not presentFound:
                # mark that we found it
                presentFound = True
            # if it has been found elsewhere
            else:
                # it exists in two places which is bad
                print("Exists as present = 1 in multiple places")
                return 2
        
        # add to dict
        #        {position : (present, time_in, time_out)}
        positions[toop[1]] = (toop[2], toop[3], toop[4])
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
                print("Timestamp conflict")
                return 3
            if tr2[1] > tr1[0] and tr2[1] < tr1[1]:
                print("Timestamp conflict")
                return 3

                

    # didn't find any red flags
    return 0



def run():
    if os.getlogin() != 'Adam':
        print("Don't try this on a lab (production) machine")
        print("Add your username to the first if in run() to use your own machine")
        return

    # get database path and make the engine and connection
    database = GetLocalDatabasePath()
    engine = sqla.create_engine("sqlite:///" + database)
    connection = engine.connect()

    #test 1, should return two different locations, one not present and one present
    #print(strawPresences(20474, connection))
    #test 2, should return LPAL 360
    #print(entryLocation(16325227138278103,connection))
    #test 3, should return MN 173
    #print(strawCurrentLocation(20474,connection))
    #test 4
    #newEntry(99999, 42969, 1, connection, 0, 5)
    #test5, should return 0
    #print(checkStrawIntegrity(20474, connection))
    #test6,
    #print(strawLocations(20474, connection))
    #test7,
    #print(getLPALID(259, connection))

    #for toop in strawPresences(16312, connection):
    #    print(toop)

    return

if __name__ == "__main__":
    run()