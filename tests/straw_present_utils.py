import os
import sqlalchemy as sqla
from guis.common.getresources import GetProjectPaths, GetLocalDatabasePath

# get all occurances of a certain straw ID in straw_present
# returns list of tuples
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
        f"WHERE straw_present.id = {presentID} AND straw_present.present = 1"
    )

    ret = connection.execute(query)
    result = ret.fetchone()

    return result







def run():
    if os.getlogin() != 'Adam':
        print(os.getlogin())
        print("Don't try this on a lab machine")
        print("Add your username to the first if in run() to use your own machine")
        return


    # get database path and make the engine and connection
    database = GetLocalDatabasePath()
    engine = sqla.create_engine("sqlite:///" + database)
    connection = engine.connect()


    # test1
    print(strawIsPresent(20474, connection))
    #test2
    print(entryLocation(16328391116816108,connection))

    return

if __name__ == "__main__":
    run()