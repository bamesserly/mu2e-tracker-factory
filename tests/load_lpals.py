# ===============================================================================
# (1) Parse input csv,
# (2) Loop straws
#   * insert or update: straw_present entry for this LPAL with in and out times.
#   * insert or update: straw_present entry for its panel with in time.
# ===============================================================================

from pathlib import Path
from guis.common.getresources import GetProjectPaths, pkg_resources
from csv import DictReader, DictWriter
import datetime
import os, time, sys
import sqlalchemy as sqla
from guis.common.getresources import GetProjectPaths, GetLocalDatabasePath
import re
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.exc import IntegrityError
#from guis.common.db_classes.straw_location import (
#    StrawLocation,
#    LoadingPallet,
#    StrawPresent,
#    StrawPosition,
#)


paths = GetProjectPaths()


# ==============================================================================
# Main
# ==============================================================================
def run():
    straws = []
    lpal_list = []
    switch = False
    counter = 0
    for file in Path(paths["lpals"]).glob("*.csv"):
        counter += 1
        print(file.name)
        lpal = int(str(file)[-17:-13])
        assert 0 < lpal < 600
        lpal_list.append(lpal)
        with open(file, "r") as f:
            reader = DictReader(line for line in f if line.split(",")[0])
            rows = [row for row in reader]
            rows = [{**d, "lpal": lpal} for d in rows]
            straws.extend(rows)
        #break
    print(straws[0])
    print(straws[250])
    print(straws[-1])
    print(f"{counter} files loaded")

    # set up DB
    database = GetLocalDatabasePath()
    print("Using database:", database)
    engine = sqla.create_engine("sqlite:///" + database)
    metadata = MetaData()

    straw_location_table = Table("straw_location", metadata, autoload_with=engine)

    # get lpals straw location number
    with engine.connect() as connection:
        for lpal in sorted(lpal_list):
            lpal_stl_entry = connection.execute(
                sqla.select(straw_location_table).where(
                    sqla.and_(
                        straw_location_table.c.number == lpal,
                        straw_location_table.c.location_type == "LPAL"
                    )
                )
            ).fetchone()
            stlid = getattr(lpal_stl_entry, "id", None)
            if not stlid:
                print(stlid, lpal)

    '''
    pro2_db_entry = connection.execute(
        sqla.select(procedure_table).where(procedure_table.c.id == procedure.id)
    ).fetchone()

    procedure2_db_entry = connection.execute(
        sqlalchemy.select(procedure2_table).where(...)
    ).fetchone()

    procedure2_table = Table("procedure_details_pan2", metadata, autoload_with=engine)
    procedure_table = Table("procedure", metadata, autoload_with=engine)
    '''



    '''
    query = (
        select(procedure2_table)
        #.join(procedure_table, procedure_table.c.id == procedure2_table.c.procedure)
        .join(straw_location_table, straw_location_table.c.id == procedure_table.c.straw_location)
        .where(straw_location_table.c.number == straw_location_number)
    )

    straw_table = Table("straw", metadata, autoload_with=engine)
    straw_present_table = Table("straw_present", metadata, autoload_with=engine)
    '''

    '''
    with engine.connect() as connection:
        existing_row = connection.execute(
            sqla.select(straw_table).where(straw_table.c.id == 1090)
        ).fetchone()
        print(existing_row)
        #batch = getattr(existing_row, "batch", None)
        #print(batch, "|", str(batch), "|", bool(batch))

    lpalLoc = (
        StrawLocation.query()
        .filter(StrawLocation.location_type == "LPAL")
        .filter(StrawLocation.number == int(lpalNum))
        .one_or_none()
    )
    '''


    """
    #  DB query example for tests
    with engine.connect() as connection:
        existing_row = connection.execute(
            sqla.select(straw_table).where(straw_table.c.id == 1090)
        ).fetchone()
        print(existing_row)
        #batch = getattr(existing_row, "batch", None)
        #print(batch, "|", str(batch), "|", bool(batch))
    """

    """
    # insert new straws and add missing batches in straw table
    with engine.connect() as connection:
        insert_or_compare_straw(connection, straw_table, straw_data)
    """


if __name__ == "__main__":
    run()
