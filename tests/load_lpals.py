# ===============================================================================
# (0) Loop over all LPAL csv files in the lpals directory.
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

from guis.common.db_classes.straw_location import (
    #    StrawLocation,
    #    LoadingPallet,
    StrawPresent,
    #    StrawPosition,
)

# these lpals didn't make it to panels for whatever reason.
lpal_skip_list = [
    "LPAL0043_LPALID02.csv",  # not used
    "LPAL0048_LPALID02.csv",  # half full TODO
    "LPAL0105_LPALID02.csv",  # not used
    "LPAL0190_LPALID01.csv",  # not used
    "LPAL0350_LPALID01.csv",  # not used
    "LPAL0516_LPALID01.csv",  # not used
]


paths = GetProjectPaths()


def ParseLPALFile(file):
    with open(file, "r") as f:
        reader = DictReader(line for line in f if line.split(",")[0])
        straws = [row for row in reader]
    return straws


# ==============================================================================
# Main
# ==============================================================================
def run():
    switch = False

    # load all straws from all LPAL files
    counter = 0
    all_straws = []
    lpal_list = []
    for file in Path(paths["lpals"]).glob("*.csv"):
        if file.name in lpal_skip_list:
            continue
        lpal = int(str(file)[-17:-13])
        assert 0 < lpal < 600
        print(file.name)

        # if "312" not in str(file.name):
        #   return

        straws = ParseLPALFile(file)

        if len(straws) < 30:
            print(f"{str(file)} no data")
            continue

        # add lpal number to each straw
        straws = [{**s, "lpal": lpal} for s in straws]

        all_straws.extend(straws)
        lpal_list.append(lpal)
        counter += 1
    print(f"First straw: {all_straws[0]}")
    print(f"250th straw: {all_straws[250]}")
    print(f"Last straw: {all_straws[-1]}")
    print(f"{counter} files loaded")

    print("\nRemoving straws after MN172")
    # Process first group of straws up to LPAL0173, for which there are no
    # entries in the DB.
    all_straws = [s for s in all_straws if int(s["lpal"]) <= 358]
    lpal_list = [l for l in lpal_list if l <= 358]

    # set up DB
    database = GetLocalDatabasePath()
    print("Using database:", database)
    engine = sqla.create_engine("sqlite:///" + database)
    metadata = MetaData()
    straw_location_table = Table("straw_location", metadata, autoload_with=engine)
    procedure1_table = Table("procedure_details_pan1", metadata, autoload_with=engine)
    procedure2_table = Table("procedure_details_pan2", metadata, autoload_with=engine)
    procedure_table = Table("procedure", metadata, autoload_with=engine)
    straw_position_table = Table("straw_position", metadata, autoload_with=engine)
    straw_present_table = Table("straw_present", metadata, autoload_with=engine)

    # loop over all LPALs and straws
    # create straw_present entries for each straw in each LPAL and panel
    with engine.connect() as connection:
        for lpal in sorted(lpal_list):
            lpal_stl_entry = connection.execute(
                sqla.select(straw_location_table).where(
                    sqla.and_(
                        straw_location_table.c.number == lpal,
                        straw_location_table.c.location_type == "LPAL",
                    )
                )
            ).fetchone()
            stlid = getattr(lpal_stl_entry, "id", None)
            if not stlid:
                print("straw location not found in DB", stlid, lpal)

            # Get the procedure that uses this lpal in either top or bottom location.
            # Make sure there's only one.
            entries = []
            for p in [procedure1_table, procedure2_table]:
                query = (
                    sqla.select(p)
                    .where(sqla.or_(p.c.lpal_top == stlid, p.c.lpal_bot == stlid))
                    .order_by(p.c.id)
                )
                entries.extend(connection.execute(query).fetchall())

            assert entries, "lpal not found in any procedure"
            assert len(entries) == 1, "lpal found in more than one procedure"
            procedure_details = entries[0]
            procedure_id = getattr(procedure_details, "procedure", None)
            is_top_lpal = getattr(procedure_details, "lpal_top", None) == stlid

            # get this procedure's entry in the procedure table
            procedure_entry = connection.execute(
                sqla.select(procedure_table).where(procedure_table.c.id == procedure_id)
            ).fetchone()

            # and get this procedure entry's straw_location
            # straw_location_id = getattr(procedure_entry, "straw_location", None)

            # get this procedure's timestamp
            pro_timestamp = getattr(procedure_entry, "timestamp", None)

            # loop over all straws in this lpal
            for straw in [s for s in all_straws if s["lpal"] == lpal]:
                position = int(straw["Position"])
                timestamp = int(straw["Timestamp"])
                straw_id = int(straw["Straw"][2:])

                print(position, stlid, lpal, straw_id)

                # get the lpal position
                lpal_straw_positions = connection.execute(
                    sqla.select(straw_position_table).where(
                        sqla.and_(
                            straw_position_table.c.position_number == position,
                            straw_position_table.c.location == stlid,
                        )
                    )
                ).fetchall()
                for i in lpal_straw_positions:
                    print(i)
                assert len(lpal_straw_positions) == 1
                lpal_straw_position = lpal_straw_positions[0]
                lpal_straw_position_id = getattr(lpal_straw_position, "id", None)

                # assemble the straw_present entry and attempt to commit it
                lpal_straw_present_entry = {
                    "straw": straw_id,
                    "position": lpal_straw_position_id,
                    "present": False,
                    "time_in": timestamp,
                    "time_out": pro_timestamp,
                }
                insert_stmt = straw_present_table.insert().values(**lpal_straw_present_entry)
                print(insert_stmt)
                #with connection.begin() as transaction():
                try:
                    result = connection.execute(insert_stmt)
                    print(f"{lpal_straw_present_entry} - added")
                except IntegrityError:
                    raise

                connection.commit()

                break

            break

    # class StrawPresent(BASE, OBJECT):
    #    __tablename__ = "straw_present"
    #    id = Column(Integer, primary_key=True)
    #    straw = Column(Integer, ForeignKey("straw.id"))
    #    position = Column(Integer, ForeignKey("straw_position.id"))
    #    present = Column(BOOLEAN)

    # insert_data = {k: v for k, v in insert_data.items() if k != "cpal"}
    # insert_stmt = table.insert().values(**insert_data)

    """
    pro2_db_entry = connection.execute(
        sqla.select(procedure_table).where(procedure_table.c.id == procedure.id)
    ).fetchone()

    procedure2_db_entry = connection.execute(
        sqlalchemy.select(procedure2_table).where(...)
    ).fetchone()

    procedure2_table = Table("procedure_details_pan2", metadata, autoload_with=engine)
    procedure_table = Table("procedure", metadata, autoload_with=engine)
    """

    """
    query = (
        select(procedure2_table)
        #.join(procedure_table, procedure_table.c.id == procedure2_table.c.procedure)
        .join(straw_location_table, straw_location_table.c.id == procedure_table.c.straw_location)
        .where(straw_location_table.c.number == straw_location_number)
    )

    straw_table = Table("straw", metadata, autoload_with=engine)
    straw_present_table = Table("straw_present", metadata, autoload_with=engine)
    """

    """
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
    """

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
