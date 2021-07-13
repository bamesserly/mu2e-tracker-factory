#===============================================================================
# Load a heat CSV file into the database
#===============================================================================

import sqlalchemy as sqla  # for interacting with db
import sys, csv

kPROCESSES = list(range(1, 8))

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources
import data, resources

from guis.common.getresources import GetProjectPaths


def LoadLocalDatabasePath():
    with pkg_resources.path(data, "database.db") as p:
        return str(p.resolve())


# Given a panel and process, access the DB to get the procedure ID
def GetProcedureID(connection, panel, process):
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


def WriteTempsToDB(connection, pid, t1, t2, timestamp):
    query = f"""
    INSERT INTO panel_heat (procedure, temp_paas_a, temp_paas_bc, timestamp)
    VALUES ('{pid}','{t1}','{t2}','{timestamp}')
    """
    print(query)
    connection.execute(query)

    # to_db = [(i['col1'], i['col2']) for i in dr]
    # cur.executemany("INSERT INTO t (col1, col2) VALUES (?, ?);", to_db)
    # con.commit()


def run():
    database = LoadLocalDatabasePath()

    print(f"Writing to {database}")

    db_check = input("PRESS <ENTER> TO VERIFY THIS DATABASE, ELSE PRESS CTRL-C\n")
    if db_check:
        sys.exit("DB not verified, exiting")


    engine = sqla.create_engine("sqlite:///" + database)  # create engine

    with engine.connect() as connection:

        pid = GetProcedureID(connection, panel=100, process=1)

        data_file = GetProjectPaths()["heatdata"] / "MN142_2021-07-01.csv"

        with open (data_file,'r') as f:
            dr = csv.DictReader(f)

            # an entry of dr looks like:
            # OrderedDict([('Date', '2021-07-02_073223'), ('PAASA_Temp[C]', '-242.02'), ('2ndPAAS_Temp[C]', '-99.00'), ('Epoc', '1625229143.7965412')])
            to_db = [(pid, i['PAASA_Temp[C]'], i['2ndPAAS_Temp[C]'], int(float(i['Epoc']))) for i in dr]

            to_db = to_db[:5]

            connection.executemany("INSERT INTO panel_heat (procedure, temp_paas_a, temp_paas_b, timestamp) VALUES (?, ?, ?, ?);", to_db)

            #for i in to_db:
            #    print(i)
        #WriteTempsToDB(connection, pid, t1=888, t2=888, timestamp=1598066667)

        #to_db = [for i in dr]


"""
import csv, sqlite3

con = sqlite3.connect(":memory:") # change to 'sqlite:///your_filename.db'
cur = con.cursor()
cur.execute("CREATE TABLE t (col1, col2);") # use your column names here

with open('data.csv','r') as fin: # `with` statement available in 2.5+
        # csv.DictReader uses first line in file for column headings by default
            dr = csv.DictReader(fin) # comma is default delimiter
                to_db = [(i['col1'], i['col2']) for i in dr]

                cur.executemany("INSERT INTO t (col1, col2) VALUES (?, ?);", to_db)
                con.commit()
                con.close()

panelIDQuery = (
    # select panel ids
    sqla.select([self.panelsTable.columns.id])
    # where number = user input panel number
    .where(self.panelsTable.columns.number == self.data.humanID)
    # and where location type = MN (we don't want LPALs)
    .where(self.panelsTable.columns.location_type == "MN")
)
"""
