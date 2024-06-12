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

    print("\nDon't add straws after MN172")
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
            lpal_stlid = getattr(lpal_stl_entry, "id", None)
            if not lpal_stlid:
                print("straw location not found in DB", lpal_stlid, lpal)

            # Get the procedure that uses this lpal in either top or bottom location.
            entries = []
            for p in [procedure1_table, procedure2_table]:
                query = (
                    sqla.select(p)
                    .where(
                        sqla.or_(p.c.lpal_top == lpal_stlid, p.c.lpal_bot == lpal_stlid)
                    )
                    .order_by(p.c.id)
                )
                entries.extend(connection.execute(query).fetchall())

            # Make sure there's only one such procedure
            assert entries, "lpal not found in any procedure"
            assert len(entries) == 1, "lpal found in more than one procedure"
            procedure_details = entries[0]
            procedure_id = getattr(procedure_details, "procedure", None)
            is_top_lpal = getattr(procedure_details, "lpal_top", None) == lpal_stlid

            # get this procedure's entry in the procedure table
            procedure_entry = connection.execute(
                sqla.select(procedure_table).where(procedure_table.c.id == procedure_id)
            ).fetchone()
            pro_timestamp = getattr(procedure_entry, "timestamp", None)

            # and get this procedure entry's straw_location
            panel_stlid = getattr(procedure_entry, "straw_location", None)

            # get the panel number from the straw_location table "number" field
            panel_number = connection.execute(
                sqla.select(straw_location_table).where(
                    straw_location_table.c.id == panel_stlid
                )
            ).fetchone()
            stl_type = getattr(panel_number, "location_type", None)
            assert stl_type == "MN", "panel location not found in DB"
            panel_number = getattr(panel_number, "number", None)
            panel_number = f"{panel_number:03d}"

            # Save straws to LPALs and panels
            count = 0
            print(f"LPAL {lpal}")
            for straw in [s for s in all_straws if s["lpal"] == lpal]:
                lpal_position = int(straw["Position"])
                timestamp = int(straw["Timestamp"])
                straw_id = int(straw["Straw"][2:])

                # get the lpal position id where this straw will go
                lpal_straw_positions = connection.execute(
                    sqla.select(straw_position_table).where(
                        sqla.and_(
                            straw_position_table.c.position_number == lpal_position,
                            straw_position_table.c.location == lpal_stlid,
                        )
                    )
                ).fetchall()
                assert len(lpal_straw_positions) == 1
                lpal_straw_position_id = getattr(lpal_straw_positions[0], "id", None)

                # assemble the LPAL straw_present entry and attempt to commit it
                lpal_straw_present_entry = {
                    "straw": straw_id,
                    "position": lpal_straw_position_id,
                    "present": False,
                    "time_in": timestamp,
                    "time_out": pro_timestamp,
                }
                insert_stmt = (
                    straw_present_table.insert()
                    .values(**lpal_straw_present_entry)
                    .prefix_with("OR IGNORE")
                )
                try:
                    lpal_result = connection.execute(insert_stmt)
                    connection.commit()
                except IntegrityError:
                    raise

                # top and bot lpal -> panel position mapping
                panel_position = lpal_position + 1 if is_top_lpal else lpal_position

                # get the panel position id where this straw will go
                panel_straw_positions = connection.execute(
                    sqla.select(straw_position_table).where(
                        sqla.and_(
                            straw_position_table.c.position_number == panel_position,
                            straw_position_table.c.location == panel_stlid,
                        )
                    )
                ).fetchall()
                assert len(panel_straw_positions) == 1
                panel_straw_position_id = getattr(panel_straw_positions[0], "id", None)

                # assemble the panel straw_present entry and attempt to commit it
                panel_straw_present_entry = {
                    "straw": straw_id,
                    "position": panel_straw_position_id,
                    "present": True,
                    "time_in": pro_timestamp,
                    "time_out": None,
                }
                insert_stmt = (
                    straw_present_table.insert()
                    .values(**panel_straw_present_entry)
                    .prefix_with("OR IGNORE")
                )
                try:
                    panel_result = connection.execute(insert_stmt)
                    connection.commit()
                except Exception as e:
                    print(e)
                    raise

                lpal_txt = "NOT added" if lpal_result.rowcount == 0 else "added"
                panel_txt = "NOT added" if panel_result.rowcount == 0 else "added"
                print(
                    f"\tST{straw_id:05d} - {lpal_txt} to LPAL{lpal:04d} pos {lpal_position} | {panel_txt} to MN{panel_number} pos {panel_position}"
                )

                count += 1
                if count > 5:
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
