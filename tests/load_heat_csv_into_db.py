import sqlalchemy as sqla  # for interacting with db
import sys

kPROCESSES = list(range(1, 8))

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources
import data, resources


def LoadLocalDatabasePath():
    with pkg_resources.path(data, "database.db") as p:
        return str(p.resolve())


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
    # print(query)
    result = connection.execute(query)
    result = result.fetchall()[0][0]
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

    connection = engine.connect()  # connect engine with DB

    pid = GetProcedureID(connection, panel=52, process=1)

    WriteTempsToDB(connection, pid, t1=888, t2=888, timestamp=1598066667)

    connection.close()


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
