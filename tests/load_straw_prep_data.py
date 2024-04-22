# ===============================================================================
# (1) Parse input csv, (2) load straw info into db, (3) load prep data into db
#
# This does NOT currently update straw prep data.
# I considered creating straw present entries recording when straws were added
# to their CPALs, but it's not a priority, and it can be done later.
#
# loop over files and get the following:
#     cpal_list, straw_information, metainfo_list
# where straw information is a dict
#     {CPAL# : [{'id': 'st20472', 'batch': '120417.B2', 'grade': 'PP.A', 'time': 1630424400}}
#
# Then we update the DB:
#   1. create straws if needed
#   2. update the batch numbers
#   3. create CPAL straw location if needed, straw_position entries created
#   automatically. If CPAL is created, also create a procedure entry.
#   4. create measurement_prep entries for straws-ppgs
# ===============================================================================

from pathlib import Path
from guis.common.getresources import GetProjectPaths, pkg_resources
import csv
import tests.straw_present_utils as straw_utils
import datetime
import os, time, sys
import sqlalchemy as sqla
from guis.common.getresources import GetProjectPaths, GetLocalDatabasePath
import re

# from guis.common.db_classes.straw import Straw
from guis.common.db_classes.straw_location import StrawLocation, CuttingPallet, Pallet
from guis.common.db_classes.procedure import Procedure, StrawProcedure
from guis.common.db_classes.station import Station
from guis.common.db_classes.procedures_straw import Prep
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.exc import IntegrityError


problem_files = [
    "CPAL0002.csv",  # oddly formatted, no batch numbers
    "CPAL0010.csv",
    "CPAL0023.csv",
    "CPAL0025.csv",  # no ppgs, none on panels
    "CPAL0056.csv",
    "CPAL0111.csv",
    "CPAL0112.csv",
    "CPAL0113.csv",
    "CPAL0114.csv",
    "CPAL0120.csv",
    "CPAL0121.csv",
    "CPAL0122.csv",
    "CPAL0125.csv",
    "CPAL0130.csv",
    "CPAL0150.csv",
    "CPAL0155.csv",
    "CPAL0160.csv",
    "CPAL0165.csv",
    "CPAL0170.csv",
    "CPAL0175.csv",
    "CPAL0180.csv",
    "CPAL0185.csv",
    "CPAL0190.csv",
    "CPAL0195.csv",
    "CPAL0200.csv",
    "CPAL0250.csv",
    "CPAL0260.csv",
    "CPAL0270.csv",
    "CPAL1008.csv",
    "CPAL1094.csv",
    "CPAL1191.csv",
    "CPAL1207.csv",
    "CPAL1209.csv",
    "CPAL1234.csv",
    "CPAL1235.csv",
    "CPAL1287.csv",
    "CPAL1362.csv",
    "CPAL1551.csv",
    "CPAL1654.csv",
    "CPAL2044.csv",
    "CPAL2456.csv",
    "CPAL2929.csv",
    "CPAL3467.csv",
    "CPAL3945.csv",
    "CPAL4657.csv",
    "CPAL4747.csv",
    "CPAL5462.csv",
    "CPAL6154.csv",
    "CPAL6439.csv",
    "CPAL6489.csv",
    "CPAL6767.csv",
    "CPAL6997.csv",
    "CPAL7164.csv",
    "CPAL7315.csv",
    "CPAL7326.csv",
    "CPAL7615.csv",
    "CPAL7954.csv",
    "CPAL8181.csv",
    "CPAL9825.csv",
    "prep_CPAL1234.csv",
    "prep_CPAL2081.csv",
    "prep_CPAL2082.csv",
    "prep_CPAL2345.csv",
    "prep_CPAL2501.csv",
    "prep_CPAL5028.csv",
    "prep_CPAL7474.csv",
    "prep_CPAL7652.csv",
    "prep_CPAL7653.csv",
    "prep_CPAL7654.csv",
    "prep_CPAL8372.csv",
    "prep_CPAL8472.csv",
    "prep_CPAL8476.csv",  # most likely bogus. batch 010101.B1
    "prep_CPAL8763.csv",
    "prep_CPAL9834.csv",
]

pp_grades = ["A", "B", "C", "D"]

paths = GetProjectPaths()

desired_batch_format = r"^\d{6}B\d$"


# ===============================================================================
# CSV Parsing Functions
# ===============================================================================
# Input: chunk of comma-separated first line of the prep file
# Extract metainfo from this chunk.
# Looks for one of datetime, cpalid, batch, and worker.
# Intended to be called in succession on each comma-separated element of the
# first line.
def get_metainfo_item(item):
    return_val = None
    type = ""

    # determine which type of data the metainfo is, and assign it accordingly
    item = item.strip()
    if len(item) == 16 and 2015 < int(item[0:4]) < 2023:
        time = datetime.datetime.strptime(item, "%Y-%m-%d_%H:%M")
        time = datetime.datetime.timestamp(time)
        type = "time"
        return_val = int(time)
    elif len(item) == 19 and 2015 < int(item[0:4]) < 2023 and item[10] == " ":
        time = datetime.datetime.strptime(item, "%Y-%m-%d %H:%M:%S")
        time = datetime.datetime.timestamp(time)
        return_val = int(time)
        type = "time"
    elif len(item) == 19 and 2015 < int(item[0:4]) < 2023 and item[10] == "_":
        time = datetime.datetime.strptime(item, "%Y-%m-%d_%H:%M:%S")
        time = datetime.datetime.timestamp(time)
        return_val = int(time)
        type = "time"
    elif len(item) == 8:
        if item[0:6].upper() == "CPALID":
            return_val = int(item[6:8])
            type = "cpalid"
    elif len(item) > 5 and item[-2] == "B":
        return_val = str(item)
        type = "batch"
    elif item[0:3].lower() == "wk-":
        return_val = item
        type = "worker"

    return return_val, type


# Get metainfo from single header row. Header row found based on date.
# May not find all of these fields:
# {'cpal': '0799', 'time': 1630424400, 'cpalid': 5, 'worker': 'WK-MHALPERN01',
# 'batch' : '110817.B3'}
#
# "process" refers to this prep procedure defined by a prep file. Not a synonym
# for "get".
def get_metainfo(file):
    if file in problem_files:
        return {}

    metainfo = {"cpal": str(file)[-8:-4]}
    with open(file, "r") as f:
        for row in csv.reader(f):
            if (len(str(row[0])) == 16 or (len(str(row[0])) == 19)) and 2015 < int(
                str(row[0][0:4])
            ) < 2023:
                for item in row:
                    return_val, type = get_metainfo_item(item)
                    if type != "":
                        metainfo[type] = return_val
                break

    return metainfo


# Parse file caller for dependency injection
def parse_prep_file(file, metainfo, parser):
    return parser(file, metainfo)


# parse each row in vertically-oriented (later-gen) cpal files
# output: list of dicts, each dict containing info about one straw.
def parse_vertical_prep_file(file, metainfo):
    cpal_straws = []
    is_header = True

    with open(file, "r") as f:
        for row in csv.reader(f):
            # Are we done with the header and onto the straw data?
            if is_header and row and str(row[0]) == "straw":
                is_header = False
                continue

            if is_header or len(row) < 3:
                continue

            straw = {}
            # for each row where data has been detected, goes through assigning
            # pertinent data to the straw dictionary
            for i in range(3):
                if len(row[i]) == 7:
                    # acquires straw_id
                    if str(row[i])[0:2].lower() == "st" and str(row[i][2].isnumeric()):
                        straw["id"] = str(row[i]).lower()
                elif len(row[i]) > 3 and str(row[i][-2]) == "B":
                    # acquires straw batch
                    straw["batch"] = str(row[i])
                elif len(str(row[i])) == 4 or len(str(row[i])) == 3:
                    # acquires straw grade (paper pull)
                    if str(row[i][0:2]).upper() == "PP" and str(row[i]) != "DNE":
                        straw["grade"] = str(row[i]).upper()
                    elif str(row[i]).upper() == "DNE":
                        straw["grade"] = ""

            if straw:
                straw["time"] = metainfo["time"]
                cpal_straws.append(straw)

    return cpal_straws


# parse each row in vertically-oriented (earlier-gen) cpal files
# output: list of dicts, each dict containing info about one straw.
def parse_horizontal_prep_file(file, metainfo):
    # initialize lists
    inner_straw = []
    inner_batch = []
    inner_grade = []
    cpal_straws = []

    # keeps track of whether or not the file's end has been reached
    eof = False

    # iterate through all acquired lines of the file
    with open(file, "r") as f:
        for row in csv.reader(f):
            # go through each row, checking to see if desired data is present
            # if it is, append it to the pertinent list
            for i in row:
                if len(i) == 7:
                    # check for straw id
                    if str(i)[0:2].lower() == "st" and str(i[2].isnumeric()):
                        inner_straw.append(str(i))
                elif len(i) > 3 and str(i[-2]) == "B":
                    # check for straw batch
                    inner_batch.append(str(i))
                elif len(i) == 4 or len(i) == 3:
                    # check for grade (paper pull)
                    if str(i[0:3]).upper() == "PP." and str(i).upper() != "DNE":
                        inner_grade.append(str(i).upper())
                    elif str(i).upper() == "DNE":
                        inner_grade.append("")

    # check that the list of straw id's matches the other data
    if len(inner_straw) != len(inner_batch) and len(inner_straw) != len(inner_grade):
        return cpal_straws

    # add straws to list
    for i in range(len(inner_straw)):
        straw = {"id": inner_straw[i].lower()}

        # save the data corresponding to the straw id
        if len(inner_batch) == len(inner_straw):
            straw["batch"] = str(inner_batch[i])
        if len(inner_grade) == len(inner_straw):
            straw["grade"] = str(inner_grade[i]).upper()

        cpal_straws.append(straw)

    # use metainfo batch information if appropriate
    if len(inner_batch) != len(inner_straw):
        for i in cpal_straws:
            try:
                i["batch"] = metainfo["batch"]
            except KeyError:
                print("batch metainfo assignment failed: ")
                print(i.items())

    # add time to straw
    for i in cpal_straws:
        i["time"] = metainfo["time"]

    return cpal_straws


# Is this file in the newer vertical layout or the older horizontal layout?
def is_vert_layout(file):
    with open(file, "r") as f:
        for row in csv.reader(f):
            try:
                if len(row[0]) != 0 and str(row[0]) == "straw":
                    return True
            except:
                pass

    return False


# put batch in desired format XXXXXXBX or else return None
def clean_batch(batch):
    if batch is None:
        return None
    batch = batch.strip()
    batch = re.sub(r"[^\d\w]", "", batch)  # Remove non-alphanumeric characters
    batch = batch.upper()
    if re.match(desired_batch_format, batch):
        return batch
    return None


def organize_straw_data(straw_information, metainfo_list):
    # Prepare a list to hold all rows to be inserted
    values_to_insert = []

    # for all straws not present in straw table, add them
    for prep_procedure in metainfo_list:
        cpal = prep_procedure["cpal"]

        for y in range(len(straw_information[cpal])):
            try:
                straw_id = int(straw_information[cpal][y]["id"][2::].lstrip("0"))
                batch = (
                    straw_information[cpal][y]["batch"].strip().replace(".", "").upper()
                )
                timestamp = int(straw_information[cpal][y]["time"])
            except KeyError:
                print(straw_information[cpal][y])
                raise

            formatted_batch = batch
            if batch is None or re.match(desired_batch_format, batch):
                # batch is either None or in the correct format
                pass
            else:
                # attempt to format it
                formatted_batch = clean_batch(batch)
                if batch is not None and formatted_batch is None:
                    print(f"Batch reformat failed for {straw_id}-{batch}-{cpal}")
                # either way, formatted_batch is either correct or None. Either
                # way, proceed.

            # Append a dictionary for each row to the list
            values_to_insert.append(
                {
                    "id": straw_id,
                    "batch": formatted_batch,
                    "timestamp": timestamp,
                    "cpal": cpal,
                }
            )

    return values_to_insert


# ==============================================================================
# Data cleaning/organization and individual straw db insert/update methods
# ==============================================================================
def find_duplicate_straw_ids(entries):
    """
    Finds duplicate straw_id values in a list of dictionaries.

    :param entries: List of dictionaries, each containing a 'straw_id' key.
    :return: A set of duplicate 'straw_id' values. Returns an empty set if no duplicates are found.
    """
    seen_straw_ids = set()
    duplicates = set()

    for entry in entries:
        straw_id = entry["id"]
        if straw_id in seen_straw_ids:
            duplicates.add(straw_id)
        else:
            seen_straw_ids.add(straw_id)

    return duplicates


def insert_new_straw(connection, table, insert_data):
    insert_stmt = table.insert().values(**insert_data)

    batch = insert_data.get("batch")
    assert (
        re.match(desired_batch_format, batch) or batch is None
    ), "formatted batch is neither correct format nor None."

    try:
        connection.execute(insert_stmt)
        print(f"{insert_data['id']} - added")
        if not batch:
            print(f"  {insert_data['id']} - missing batch")
        return True
    except IntegrityError:
        return False


def update_batch(connection, table, insert_data):
    straw_id = insert_data["id"]
    csv_batch = insert_data.get("batch")
    csv_timestamp = insert_data.get("timestamp")

    assert re.match(
        desired_batch_format, csv_batch
    ), "Formatted batch is not in correct format."

    existing_row = connection.execute(
        sqla.select(table).where(table.c.id == straw_id)
    ).fetchone()

    if existing_row is None:
        print(f"{straw_id} - db problem")
        return False

    db_batch = getattr(existing_row, "batch", None)
    db_timestamp = getattr(existing_row, "timestamp", None)
    earlier_timestamp = min(csv_timestamp, db_timestamp)

    if db_batch is None or not db_batch.strip():
        # add missing batch to db
        update_stmt = (
            table.update()
            .where(table.c.id == straw_id)
            .values(batch=csv_batch, timestamp=earlier_timestamp)
        )
        result = connection.execute(update_stmt)
        print(f"{straw_id} - added batch", result.rowcount)
        return True
    elif db_batch != csv_batch:
        # csv and db disagree
        print(f"{straw_id}")
        batch = handle_batch_mismatch(db_batch, csv_batch)
        update_stmt = (
            table.update()
            .where(table.c.id == straw_id)
            .values(batch=batch, timestamp=earlier_timestamp)
        )
        result = connection.execute(update_stmt)
        print(f"{straw_id} - added batch", result.rowcount)
        return True
    else:
        # csv and db agree
        return False

    # I don't care about timestamp mismatches
    # if abs(int(db_timestamp) - int(csv_timestamp)) > 100:
    #    time_diff_days = (csv_timestamp - db_timestamp) / 86400.0
    #    print(
    #        f"{straw_id} - timestamp mismatch - {db_timestamp} - {csv_timestamp} - {time_diff_days}"
    #    )

    return False


def handle_batch_mismatch(db_batch, csv_batch):
    while True:
        user_input = input(
            f"  0 for db batch: {db_batch}, or 1 for csv batch: {csv_batch}> "
        )
        if user_input in ["0", "1"]:
            user_input = int(user_input)
            break
        else:
            print("Invalid input. Please enter 0 or 1.")
    return csv_batch if user_input else db_batch


def insert_or_compare_straw(connection, table, insert_data_list):
    print(f"Attempting to insert {len(insert_data_list)} entries.")
    insert_count = 0
    batch_update_count = 0
    ignore_count = 0
    empty_csv_batch_count = 0

    with connection.begin():
        for insert_data in insert_data_list:
            insert_data = {k: v for k, v in insert_data.items() if k != "cpal"}
            batch = insert_data.get("batch")
            if not batch:
                empty_csv_batch_count += 1
            if insert_new_straw(connection, table, insert_data):
                insert_count += 1
            else:
                if batch and update_batch(connection, table, insert_data):
                    batch_update_count += 1
                else:
                    ignore_count += 1  # csv batch is None OR csv and DB agree

    print("done updating straw table")

    print(
        "insert_count",
        insert_count,
        "batch_update_count",
        batch_update_count,
        "ignore_count",
        ignore_count,
        "empty_csv_batch_count",
        empty_csv_batch_count,
    )


# ==============================================================================
# Loop all straws and insert into/update db
# ==============================================================================
def update_measurement_prep_table(
    procedure_table,
    straw_location_table,
    connection,
    metainfo_list,
    straw_information,
):
    for prep_procedure in metainfo_list:
        cpal = prep_procedure["cpal"]
        cpalid = prep_procedure["cpalid"]
        time = prep_procedure["time"]
        straw_location_timestamp_updated = False

        with connection.begin():
            # FETCH OR CREATE A PROCEDURE FOR THIS (PREP,CPAL) PAIR
            try:
                procedure = Procedure.StrawProcedure(
                    process=2, pallet_id=cpalid, pallet_number=cpal
                )
            except Exception as e:
                print("CPAL/PROCEDURE CREATION ERROR", cpalid, cpal)
                raise

            # IF STRAW_LOCATION JUST CREATED, FIX TIMESTAMP
            csv_timestamp = int(straw_information[cpal][0]["time"])
            if (not straw_location_timestamp_updated) and procedure.isNew():
                # update straw_location timestamp
                # Correct the straw_location timestamp if we just created it.
                # Not airtight, but also not that important.
                update_stmt = (
                    straw_location_table.update()
                    .where(straw_location_table.c.id == procedure.straw_location)
                    .values(timestamp=csv_timestamp)
                )
                result = connection.execute(update_stmt)

                straw_location_timestamp_updated = True

            # CORRECT THE PROCEDURE TIMESTAMP IF THE CSV TIMESTAMP IS MUCH EARLIER
            # (A bunch of preps got uploaded at once and this was not fixed)
            this_procedure_db_entry = connection.execute(
                sqla.select(procedure_table).where(procedure_table.c.id == procedure.id)
            ).fetchone()

            procedure_db_timestamp = getattr(this_procedure_db_entry, "timestamp", None)

            earlier_timestamp = min(csv_timestamp, procedure_db_timestamp)
            time_diff = abs(int(csv_timestamp) - int(procedure_db_timestamp))

            if time_diff > 36000 and procedure_db_timestamp != earlier_timestamp:
                # print("procedure DB timestamp later than csv", procedure_db_timestamp, csv_timestamp)
                update_stmt = (
                    procedure_table.update()
                    .where(procedure_table.c.id == procedure.id)
                    .values(timestamp=earlier_timestamp)
                )
                result = connection.execute(update_stmt)

            # LOOP STRAWS AND INSERT PPG MEASUREMENTS
            for y in range(len(straw_information[cpal])):
                # collect info from straw_information list of dicts
                # one straw at a time
                try:
                    straw_id = int(straw_information[cpal][y]["id"][2::].lstrip("0"))
                    batch = straw_information[cpal][y]["batch"].replace(".", "")
                    paper_pull = straw_information[cpal][y]["grade"]
                    csv_timestamp = int(straw_information[cpal][y]["time"])
                except KeyError:
                    print("ERROR", cpal, straw_information[cpal])

                # print(procedure.id, procedure.station, procedure.straw_location)

                if not paper_pull:
                    continue

                prep_measurement = Prep.StrawPrepMeasurement(
                    procedure=procedure,
                    straw_id=straw_id,
                    paper_pull_grade=paper_pull[-1],
                    evaluation=1,
                )
                prep_measurement.timestamp = csv_timestamp
                # print(prep_measurement.procedure, prep_measurement.straw, prep_measurement.paper_pull_grade, prep_measurement.timestamp)
                prep_measurement.commit()

                # print('Updated measurement prep table for cpal ' + str(cpal))


def update_straw_present_table(metainfo_list, straw_information):
    for prep_procedure in metainfo_list:
        cpal = prep_procedure["cpal"]
        cpalid = prep_procedure["cpalid"]
        time = prep_procedure["time"]
        try:
            straw_location = (
                StrawLocation.query()
                .filter(StrawLocation.location_type == "CPAL")
                .filter(StrawLocation.number == cpal)
                .one_or_none()
            )
        except:
            print("Problem with CPAL: " + str(cpal))

        if straw_location is not None:
            try:
                for position in range(len(straw_information[cpal])):
                    # straw_id is the straw_id
                    # cpal is the cpal, used as a key
                    # straw is the key to the dictionary containing assorted straw information

                    # all but the last two chars in the recovered id are taken
                    # then all leading zeros are stripped
                    straw_id = straw_information[cpal][position]["id"][2::].lstrip("0")
                    timestamp = int(straw_information[cpal][position]["time"])

                    straw_location.add_historical_straw(straw_id, position, True, time)
                # print('Updated straw present table for cpal ' + str(cpal))

            except:
                print("Error saving positions on cpal " + str(cpal))
        else:
            print("Straw location not found for cpal " + str(cpal))


# ==============================================================================
# Main
# ==============================================================================
def run():
    # accumulate all straw prep data from csv files into a few lists and dicts
    cpal_list = []
    straw_information = {}
    metainfo_list = []
    switch = False
    counter = 0
    for file in Path(paths["prepdata"]).glob("*.csv"):
        if file.name in problem_files:
            continue
        counter += 1
        # if counter > 200:
        #    break
        # if not ( "0396" in str(file) ):
        #    continue

        name = file.name

        metainfo = get_metainfo(file)

        if not metainfo:
            print("Couldn't get any metainfo from", name)
            continue

        # print(metainfo)

        # Choose the appropriate parser function based on the file layout
        parser = (
            parse_vertical_prep_file
            if is_vert_layout(file)
            else parse_horizontal_prep_file
        )

        # Get straws from file in a list of dicts:
        # cpal_straws = [{'id': 'st02942', 'grade': '', 'batch': '110717.B2',
        #                 'time': 1538516460, 'cpal': 'CPAL0067.csv'}, ... ]
        straws = parse_prep_file(file, metainfo, parser)
        straws = [{**d, "cpal": name} for d in straws]

        if len(straws) == 0:
            print("Didn't get any straws from", metainfo.items())
            continue

        metainfo_list.append(metainfo)
        cpal_list.append(name)
        straw_information[name[-8:-4]] = straws

        # if switch:
        #    break
        # else:
        #    switch = True

    straw_data = organize_straw_data(straw_information, metainfo_list)

    # duplicate straws found in the csv files? (There shouldn't be.)
    duplicates = find_duplicate_straw_ids(straw_data)
    try:
        assert not duplicates, "Duplicates were found."
    except AssertionError:
        print(
            "Trying to insert duplicate straws.\n", len(duplicates), sorted(duplicates)
        )
        sys.exit()

    """
        # print info about duplicates (cleaning)
        dupe_batches = []
        # print(len(duplicates))
        # print out the duplicate entries in order, with their info.
        for straw in sorted(duplicates):
            dupe_straw_info = [d for d in straw_data if d["id"] == straw]
            for entry in dupe_straw_info:
                if entry["batch"] not in dupe_batches:
                    dupe_batches.append(entry["batch"])
                print(entry)
        print(sorted(dupe_batches))
        sys.exit()
    """

    # set up DB
    database = GetLocalDatabasePath()
    print("Using database:", database)
    engine = sqla.create_engine("sqlite:///" + database)
    metadata = MetaData()

    straw_table = Table("straw", metadata, autoload_with=engine)
    procedure_table = Table("procedure", metadata, autoload_with=engine)
    straw_location_table = Table("straw_location", metadata, autoload_with=engine)

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

    # insert new straws and add missing batches in straw table
    with engine.connect() as connection:
        insert_or_compare_straw(connection, straw_table, straw_data)

    # update prep table (paper pull grades, ppg)
    with engine.connect() as connection:
        update_measurement_prep_table(
            procedure_table,
            straw_location_table,
            connection,
            metainfo_list,
            straw_information,
        )

        # update_straw_present_table(metainfo_list, straw_information)


if __name__ == "__main__":
    run()
