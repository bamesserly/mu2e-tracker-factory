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


def parse_lpal_file(file):
    with open(file, "r") as f:
        reader = DictReader(line for line in f if line.split(",")[0])
        straws = [row for row in reader]
    return straws


# For first 75-ish panels, which LPALs were being used to load the panel was
# recorded with a timestamp in process 2. After those panels, the LPALs were
# switched to pro1 with no timestamps.
#
# So, sure, we could use the exact timestamps for the first 75 panels, but we
# still need rules for the rest.
def sort_timestamps(lpal_timestamp, pro12_start_time, pro3_start_time):
    time_counts = [0, 0, 0, 0, 0]
    # 1. straws on lpal before pro 1/2 start.
    if lpal_timestamp < pro12_start_time:
        lpal_in_time = lpal_timestamp
        panel_in_time = pro12_start_time
        time_counts[0] += 1
    # 2. Following solutions use pro3 start time as upper time limit.
    elif pro3_start_time is None:
        lpal_in_time = max(pro12_start_time, lpal_timestamp)
        panel_in_time = min(pro12_start_time, lpal_timestamp)
        time_counts[1] += 1

    # Solutions involving pro3 start time
    else:
        assert (
            pro12_start_time <= pro3_start_time
        ), f"pro12_start_time: {pro12_start_time}, pro3_start_time: {pro3_start_time}"

        # 3. straws on lpal after pro 1/2 start and before pro 3 start
        if pro12_start_time < lpal_timestamp < pro3_start_time:
            lpal_in_time = lpal_timestamp
            panel_in_time = pro3_start_time
            time_counts[2] += 1
        # 4. (sic) straws on lpal after pro 3 start
        elif pro3_start_time < lpal_timestamp:
            lpal_in_time = pro12_start_time
            panel_in_time = pro3_start_time
            time_counts[3] += 1
        # 5. punt: straws added to lpal, removed from lpal, then added to panel
        # all at the same time
        else:
            lpal_in_time = min(pro3_start_time, lpal_timestamp)
            panel_in_time = min(pro3_start_time, lpal_timestamp)
            time_counts[4] += 1

    return lpal_in_time, panel_in_time, time_counts


# ==============================================================================
# DB Functions
# ==============================================================================
class db_function:
    # jumping through hoops to avoid passing connection and tables to every
    # db function
    connection = None
    tables = None

    @classmethod
    def set_connection(cls, _connection):
        cls.connection = _connection

    @classmethod
    def set_tables(cls, _tables):
        cls.tables = _tables

    @classmethod
    def inject(cls, func):
        def wrapper(*args, **kwargs):
            if cls.connection is None:
                raise ValueError("Connection not set.")
            if cls.tables is None:
                raise ValueError("Tables not set.")
            return func(cls.connection, cls.tables, *args, **kwargs)

        return wrapper


@db_function.inject
def get_lpal_stlid(connection, tables, lpal):
    ret = connection.execute(
        sqla.select(tables["straw_location"]).where(
            sqla.and_(
                tables["straw_location"].c.number == lpal,
                tables["straw_location"].c.location_type == "LPAL",
            )
        )
    ).fetchone()
    return getattr(ret, "id", None)


# Get the procedure that uses this lpal in either top or bottom location.
@db_function.inject
def get_procedure_data(connection, tables, lpal_stlid):
    entries = []
    for pro in [tables["procedure1"], tables["procedure2"]]:
        query = (
            sqla.select(pro)
            .where(sqla.or_(pro.c.lpal_top == lpal_stlid, pro.c.lpal_bot == lpal_stlid))
            .order_by(pro.c.id)
        )
        entries.extend(connection.execute(query).fetchall())

    # Make sure there's only one such procedure
    assert entries, f"LPAL {lpal_stlid} not found in any procedure"

    # except where we transition from pro1 to pro2
    for entry in entries:
        if entry.procedure == 1605889982161047:
            return entry

    assert len(entries) == 1, f"lpal found in more than one procedure {entries}"

    return entries[0]


@db_function.inject
def get_procedure_metadata(connection, tables, procedure_id):
    return connection.execute(
        sqla.select(tables["procedure"]).where(tables["procedure"].c.id == procedure_id)
    ).fetchone()


@db_function.inject
def get_pro3_start_time(connection, tables, panel_stlid):
    pro_metadata_entries = connection.execute(
        sqla.select(tables["procedure"]).where(
            sqla.and_(
                tables["procedure"].c.straw_location == panel_stlid,
                tables["procedure"].c.station == "pan3",
            )
        )
    ).fetchall()
    # hit the breaks if extra pro 3 so I can track it down.
    if len(pro_metadata_entries) > 1:
        sys.exit(f"Multiple pro 3's for {panel_stlid}")
    assert len(pro_metadata_entries) == 1, f"missing pro 3 for {panel_stlid}."
    return getattr(pro_metadata_entries[0], "timestamp", None)


@db_function.inject
def get_panel_number(connection, tables, panel_stlid):
    panel_number = connection.execute(
        sqla.select(tables["straw_location"]).where(
            tables["straw_location"].c.id == panel_stlid
        )
    ).fetchone()
    stl_type = getattr(panel_number, "location_type", None)
    assert stl_type == "MN", "panel location not found in DB"
    panel_number = getattr(panel_number, "number", None)
    panel_number = f"{panel_number:03d}"
    return panel_number


@db_function.inject
def get_lpal_straw_position(connection, tables, lpal_position, lpal_stlid):
    lpal_straw_positions = connection.execute(
        sqla.select(tables["straw_position"]).where(
            sqla.and_(
                tables["straw_position"].c.position_number == lpal_position,
                tables["straw_position"].c.location == lpal_stlid,
            )
        )
    ).fetchall()
    assert len(lpal_straw_positions) <= 1, "more than one position found"

    # create position if missing
    if len(lpal_straw_positions) == 0:
        connection.execute(
            tables["straw_position"]
            .insert()
            .values(position_number=lpal_position, location=lpal_stlid)
            .prefix_with("OR IGNORE")
        )

        # retrieve it
        lpal_straw_positions = connection.execute(
            sqla.select(tables["straw_position"]).where(
                sqla.and_(
                    tables["straw_position"].c.position_number == lpal_position,
                    tables["straw_position"].c.location == lpal_stlid,
                )
            )
        ).fetchall()
        assert len(lpal_straw_positions) <= 1, "more than one position found"

    return lpal_straw_positions[0]


@db_function.inject
def insert_straw_present_entry(connection, tables, straw_present_entry):
    insert_stmt = (
        tables["straw_present"]
        .insert()
        .values(**straw_present_entry)
        .prefix_with("OR IGNORE")
    )
    try:
        result = connection.execute(insert_stmt)
        connection.commit()
    except IntegrityError:
        raise
    return result


@db_function.inject
def get_panel_straw_position(connection, tables, panel_position, panel_stlid):
    panel_straw_positions = connection.execute(
        sqla.select(tables["straw_position"]).where(
            sqla.and_(
                tables["straw_position"].c.position_number == panel_position,
                tables["straw_position"].c.location == panel_stlid,
            )
        )
    ).fetchall()
    assert len(panel_straw_positions) == 1
    return panel_straw_positions[0]


# count the number of panel straw present entries the present == 1
@db_function.inject
def count_panel_straw_present(connection, tables, panel_stlid):
    join_condition = tables["straw_present"].c.position == tables["straw_position"].c.id

    panel_straw_present_entries = connection.execute(
        sqla.select(tables["straw_present"])
        .select_from(
            sqla.join(tables["straw_present"], tables["straw_position"], join_condition)
        )
        .where(
            sqla.and_(
                tables["straw_position"].c.location == panel_stlid,
                tables["straw_present"].c.present == 1,
            )
        )
    ).fetchall()
    return len(panel_straw_present_entries)


# ==============================================================================
# Main
# ==============================================================================
def run():
    switch = False

    # load all straws from all LPAL files
    counter = 0
    all_straws = []
    lpal_list = []
    # print(paths["lpals"])
    for file in Path(paths["lpals"]).glob("*.csv"):
        if file.name in lpal_skip_list:
            continue
        lpal = int(str(file)[-17:-13])
        assert 0 < lpal < 600
        # print(file.name)

        # if "312" not in str(file.name):
        #   return

        straws = parse_lpal_file(file)

        cache = len(straws)

        straws = [s for s in straws if (s["Straw"] and s["Timestamp"])]

        if cache != len(straws):
            print(f"{file.name} removed {cache - len(straws)} empty straws")

        if len(straws) < 30:
            print(f"{str(file.name)} no data")
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

    print("\nProcessing first batch: all straws up to and including MN172.")
    print("This corresponds to LPALs 1-358.")
    print("additionally, skip three lpals: 26, 224, and 225 which are missing straws.")
    print("And 3, 4, and 5 have some issues.")

    bad_lpals = [26, 224, 225, 3, 4, 5, 188]
    # Process first group of straws up to LPAL0173, for which there are no
    # entries in the DB.
    all_straws = [
        s
        for s in all_straws
        if int(s["lpal"]) <= 358 and int(s["lpal"]) not in bad_lpals
    ]
    lpal_list = [l for l in lpal_list if l <= 358 and l not in bad_lpals]

    # set up DB
    database = GetLocalDatabasePath()
    print("\nUsing database:", database)
    engine = sqla.create_engine("sqlite:///" + database)
    metadata = MetaData()
    tables = {
        "straw_location": Table("straw_location", metadata, autoload_with=engine),
        "procedure1": Table("procedure_details_pan1", metadata, autoload_with=engine),
        "procedure2": Table("procedure_details_pan2", metadata, autoload_with=engine),
        "procedure": Table("procedure", metadata, autoload_with=engine),
        "straw_position": Table("straw_position", metadata, autoload_with=engine),
        "straw_present": Table("straw_present", metadata, autoload_with=engine),
    }
    db_function.set_tables(tables)

    # ==============================================================================
    # Begin DB connection, collect high-level info, then loop LPALs
    #
    # For each LPAL, loop straws and fill straw_present table with LPAL and
    # panel entries
    # ==============================================================================
    with engine.connect() as connection:
        db_function.set_connection(connection)
        count = 0
        total_time_counts = [0, 0, 0, 0, 0]
        for lpal in sorted(lpal_list):
            # ==================================================================
            # Collect high-level info about LPAL and Panel
            # ==================================================================
            # lpal straw location id
            lpal_stlid = get_lpal_stlid(lpal)
            if not lpal_stlid:
                print("straw location not found in DB", lpal_stlid, lpal)

            # procedure 1 or 2 data for this lpal
            procedure_data = get_procedure_data(lpal_stlid)
            procedure_id = getattr(procedure_data, "procedure", None)
            is_top_lpal = getattr(procedure_data, "lpal_top", None) == lpal_stlid
            procedure_metadata = get_procedure_metadata(procedure_id)
            pro12_start_time = getattr(procedure_metadata, "timestamp", None)
            panel_stlid = getattr(procedure_metadata, "straw_location", None)

            # panel number from the straw_location table "number" field
            panel_number = get_panel_number(panel_stlid)

            # use pro3 start time as upper limit on when straws went in
            try:
                pro3_start_time = get_pro3_start_time(panel_stlid)
            except AssertionError as e:
                # couldn't find pro3 start time
                pro3_start_time = None

            # ==================================================================
            # Straw Loop. Save each straw to LPAL and panel.
            # ==================================================================
            lpal_added_count = 0
            panel_added_count = 0
            print(
                f"MN{panel_number} <- LPAL{lpal:04d} {'top' if is_top_lpal else 'bot'}"
            )
            for straw in [s for s in all_straws if s["lpal"] == lpal]:
                lpal_position = int(straw["Position"])
                lpal_timestamp = int(straw["Timestamp"])
                straw_id = int(straw["Straw"][2:])

                # prepare straw_present entries
                # positions
                lpal_straw_position = get_lpal_straw_position(lpal_position, lpal_stlid)
                lpal_straw_position_id = getattr(lpal_straw_position, "id", None)
                panel_position = lpal_position + 1 if is_top_lpal else lpal_position
                panel_straw_position = get_panel_straw_position(
                    panel_position, panel_stlid
                )
                panel_straw_position_id = getattr(panel_straw_position, "id", None)

                # times - decide in and out times - lots of edge cases
                lpal_in_time, panel_in_time, time_counts = sort_timestamps(
                    lpal_timestamp, pro12_start_time, pro3_start_time
                )
                total_time_counts = [
                    x + y for x, y in zip(total_time_counts, time_counts)
                ]

                # the entries
                lpal_straw_present_entry = {
                    "straw": straw_id,
                    "position": lpal_straw_position_id,
                    "present": False,
                    "time_in": lpal_in_time,
                    "time_out": panel_in_time,
                }
                panel_straw_present_entry = {
                    "straw": straw_id,
                    "position": panel_straw_position_id,
                    "present": True,
                    "time_in": panel_in_time,
                    "time_out": None,
                }

                # insert
                lpal_result = insert_straw_present_entry(lpal_straw_present_entry)
                panel_result = insert_straw_present_entry(panel_straw_present_entry)

                lpal_txt = "NOT added" if lpal_result.rowcount == 0 else "added"
                panel_txt = "NOT added" if panel_result.rowcount == 0 else "added"
                # print(
                #    f"\tST{straw_id:05d} - {lpal_txt} to LPAL{lpal:04d} pos {lpal_position:02d} | {panel_txt} to MN{panel_number} pos {panel_position:02d}"
                # )
                lpal_added_count += lpal_result.rowcount
                panel_added_count += panel_result.rowcount
            print(f"\tlpal adds: {lpal_added_count}, panel adds: {panel_added_count}")
            print(f"\tpanel straws present: {count_panel_straw_present(panel_stlid)}")
        print(f"Done. Total lpals loaded: {count}.")
        print(f"Time counts: {total_time_counts}")


if __name__ == "__main__":
    run()
