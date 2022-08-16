from multiprocessing import connection
import os, time
import sqlalchemy as sqla
from guis.common.getresources import GetProjectPaths, GetLocalDatabasePath

# check if a straw id exists in straw
def strawExists(straw_id, connection):
    try:
        straw_id = int(straw_id)
    except:
        print('please ensure that straw_id is in integer format')
    
    query = f"SELECT * FROM straw WHERE id = {straw_id}"
    
    ret = connection.execute(query)
    lst = ret.fetchall()
    
    if len(lst) != 0:
        return True
    else:
        return False
        
# insert straw into straw table (not working for an odd reason quite yet)
def createStraw(straw_id, batch, timestamp, connection):
    try:
        straw_id = int(straw_id)
        batch = str(batch)
        timestamp = int(timestamp)
    except:
        print('please ensure that straw_id is in integer format')
        
    query = (
        f"INSERT INTO straw VALUES ({straw_id}, {batch}, {None}, {timestamp});"
    )
    
    connection.execute(query)
        
# get all occurances of a certain straw ID in straw_present
# returns list of tuples of the form
# (<id>, <straw>, <position>, <present>, <time_in>, <time_out>, <timestamp>)
def strawPresences(strawID, connection):
    query = f"SELECT * FROM straw_present WHERE straw = {strawID}"

    ret = connection.execute(query)
    lst = ret.fetchall()

    return lst

# get all occurances of a certain straw ID in straw_present
# returns list of tuples of the form
# (<id>, <straw>, <LOCATION TYPE AS STRING>, <location>, <present>, <time_in>, <time_out>, <timestamp>)
def strawPresencesReadable(strawID, connection):
    query = f"SELECT * FROM straw_present WHERE straw = {strawID}"

    ret = connection.execute(query)
    lst = ret.fetchall()

    retLst = []

    for entry in lst:
        newLoc = str(entryLocation(entry[0], connection, checkIntegrity=False)[0])
        retLst += (
            entry[0], # id
            entry[1], # straw number
            newLoc,   # location as a string, ex "MN" or "LPAL"
            entry[2], # location id
            entry[3], # present (1 or 0)
            entry[4], # time in (entered this position)
            entry[5], # time out (exited this position)
            entry[6]  # committed to DB timestamp
        )
    
    return retLst

# get the location mentioned in an entry in straw_present as a string and number ex ("MN", 200)
# takes id of an entry in straw_present
def entryLocation(presentID, connection, checkIntegrity=True):

    # doing this will allow fetchone to get all the results (since there should only be one)
    if checkIntegrity:
        if not checkStrawIntegrity(presentID, connection):
            return ("Integrity check failed")

    query = (
        "SELECT straw_location.location_type, straw_location.number\n"
        "FROM straw_location\n"
        "INNER JOIN straw_position ON straw_location.id=straw_position.location\n"
        "INNER JOIN straw_present ON straw_position.id=straw_present.position\n"
        f"WHERE straw_present.id = {presentID}"
    )

    ret = connection.execute(query)
    result = ret.fetchone()

    return result

# return list of all straw locations over time (present or not)
# list looks like: [("MN", 200), ("LPAL", 400)]
def strawLocations(strawID, connection):
    retList = []
    for toop in strawPresences(strawID, connection):
        retList += [entryLocation(toop[0], connection, checkIntegrity=False)]

    return retList

# get the current location of a straw
# returns (<location type>, number), ex ("MN", 200)
def strawCurrentLocation(strawID, connection, checkIntegrity=True):

    # doing this will allow fetchone to get all the results (since there should only be one)
    if checkIntegrity:
        if not checkStrawIntegrity(strawID, connection):
            return ("Integrity check failed")

    query = (
        "SELECT straw_location.location_type, straw_location.number\n"
        "FROM straw_location\n"
        "INNER JOIN straw_position ON straw_location.id=straw_position.location\n"
        "INNER JOIN straw_present ON straw_position.id=straw_present.position\n"
        f"WHERE straw_present.straw = {strawID} AND straw_present.present = 1"
    )

    ret = connection.execute(query)
    result = ret.fetchone()

    return result

# returns the ID of a position from a location and a position number for that location
# so if you want the database ID for position 50 on LPAL 500 use getPositionID(<LPAL500 id>, 50, connection)
# returns an int
def getPositionID(locationID, positionNum, connection):
    query = (
        "SELECT straw_position.id\n"
        "FROM straw_position\n"
        f"WHERE straw_position.location = {locationID} AND straw_position.position_number = {positionNum}"
    )
    ret = connection.execute(query)
    result = ret.fetchone()

    # return 0 index because it returns a tuple of the form (<data we want>,)
    return result[0]

# useful for getPositionID() if you don't know the database ID of an LPAL
# returns an int
def getLPALID(lpalNum, connection):
    query = (
        "SELECT straw_location.id\n"
        "FROM straw_location\n"
        f"WHERE straw_location.location_type = 'LPAL' AND straw_location.number = {lpalNum}"
    )
    ret = connection.execute(query)
    result = ret.fetchone()

    # return 0 index because it returns a tuple of the form (<data we want>,)
    return result[0]

# submit a new entry to the straw_present table
# returns "T" if success, error message if failed
def newEntry(strawID, position, present, connection, time_in=None, time_out=None):
    # ensure entry doesn't exist yet
    for toop in strawPresences(strawID, connection):
        if toop[2] == position:
            print("This straw/position combo is already in the database!")
            if toop[3] != present or toop[4] != time_in or toop[5] != time_out:
                print("FYI The entry you're trying to submit disagrees with the one already in the database.")
            return f"Already present, {toop[2]} = {position}"

    # do actual insertion (TWSS)
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

    try:
        sendIt = connection.execute(query)
    except sqla.exc.OperationalError as e:
        return e
    except sqla.exc.IntegrityError as e:
        return e

    return "T"

# check if straw has only one entry per position and one present = 1
# TODO: add check if timestamps line up or contradict each other?
# returns 0 if all is good
#         1 if two or more of the same position found
#         2 if two or more "present = 1" in straw_present for this straw
def checkStrawIntegrity(strawID, connection):
    # dict of positions
    positions = {}
    # bool for tracking number of "present = 1" found
    presentFound = False

    # loop through entries
    for toop in strawPresences(strawID, connection):
        # if key (position) exists in dict already --> two positions found
        if toop[2] in positions:
            print("Two locations detected")
            return 1

        # if straw is present at this position
        if toop[3] == 1:
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
        positions[toop[2]] = (toop[3], toop[4], toop[5])
    # end of loop body

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
    #test5, should return true
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