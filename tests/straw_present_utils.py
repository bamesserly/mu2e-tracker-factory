from multiprocessing import connection
import os, time
import sqlalchemy as sqla
from guis.common.getresources import GetProjectPaths, GetLocalDatabasePath

# get all occurances of a certain straw ID in straw_present
# returns list of tuples of the form
# (<id>, <straw>, <position>, <present>, <time_in>, <time_out>, <timestamp>)
def strawIsPresent(strawID, connection):
    query = f"SELECT * FROM straw_present WHERE straw = {strawID}"

    ret = connection.execute(query)
    lst = ret.fetchall()

    return lst

# get the location mentioned in an entry in straw_present
def entryLocation(presentID, connection):
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

# get the current location of a straw
def strawCurrentLocation(strawID, connection):
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

# submit a new entry to the straw_present table
# returns true if success, false if failed
def newEntry(strawID, position, present, connection, time_in=None, time_out=None):
    # ensure entry doesn't exist yet
    for toop in strawIsPresent(strawID, connection):
        if toop[2] == position:
            print("This straw/position combo is already in the database!")
            if toop[3] != present or toop[4] != time_in or toop[5] != time_out:
                print("FYI The entry you're trying to submit disagrees with the one already in the database.")
            return False

    # do actual insertion
    t = time.time()
    query = (
        "INSERT OR IGNORE INTO straw_present (id, straw, position, present, time_in, time_out, timestamp)"
        f"VALUES ({int(float(t)*1e6)}, {strawID}, {position}, {present}, {time_in}, {time_out}, {int(t)});"
    )

    try:
        sendIt = connection.execute(query)
    except:
        return False

    return True

# check if straw has only one entry per position and one present = 1
# TODO: add check if timestamps line up or contradict each other
def checkStrawIntegrity(strawID, connection):
    # dict of positions
    positions = {}
    # bool for tracking number of "present = 1" found
    presentFound = False

    # loop through entries
    for toop in strawIsPresent(strawID, connection):
        # if key (position) exists in dict already --> two positions found
        if toop[2] in positions:
            print("Two locations detected")
            return False

        # if straw is present at this position
        if toop[3] == 1:
            # if it hasn't been found elsewhere yet
            if not presentFound:
                # mark that we found it
                presentFound = True
            # if it has been found elsewhere
            else:
                # it exists in two places which is bad
                print("Two presences detected")
                return False
        

        # add to dict
        #        {position : (present, time_in, time_out)}
        positions[toop[2]] = (toop[3], toop[4], toop[5])
    # end of loop body

    # didn't find any red flags
    return True



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
    print(strawIsPresent(20474, connection))
    #test 2, should return MN173
    print(entryLocation(16328391116816108,connection))
    #test 3, should return MN173
    print(strawCurrentLocation(20474,connection))
    #test 4
    #newEntry(99999, 42969, 1, connection, 0, 5)
    #test5
    print(checkStrawIntegrity(99999, connection))

    return

if __name__ == "__main__":
    run()