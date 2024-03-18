# ===============================================================================
# (1) Parse input csv, (2) load straw info, (3) load prep data table, (4)
# update straw present info
#
# loop over files and get the following:
#     cpal_list, straw_information, cpal_prefix_list
# where straw information is a dict
#     {CPAL# : [{'id': 'st20472', 'batch': '120417.B2', 'grade': 'PP.A', 'time': 1630424400}}
#
# then we update the DB:
#   1. create straws if needed
#   2. batch # and ppg in prep table
# ===============================================================================

from pathlib import Path
from guis.common.getresources import GetProjectPaths, pkg_resources
import csv
import tests.straw_present_utils as straw_utils
import datetime
import os, time, sys
import sqlalchemy as sqla
from guis.common.getresources import GetProjectPaths, GetLocalDatabasePath

# from guis.common.db_classes.straw import Straw
from guis.common.db_classes.straw_location import StrawLocation, CuttingPallet, Pallet
from guis.common.db_classes.procedure import Procedure, StrawProcedure
from guis.common.db_classes.station import Station
from guis.common.db_classes.procedures_straw import Prep
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.exc import IntegrityError


problem_files = [
    "CPAL0002.csv",
    # "CPAL0010.csv",
    "CPAL0025.csv",
    "CPAL0040.csv",
    "CPAL0056",
    "CPAL0312.csv",
    "CPAL0484.csv",
    "CPAL1008.csv",
    "CPAL1234.csv",
    "CPAL1551.csv",
    "CPAL2929.csv",
    "CPAL3945.csv",
    "CPAL6997.csv",
    "CPAL7326.csv",
    "CPAL9119.csv",
    "CPAL9999.csv",
    "prep_CPAL0591.csv",
    "prep_CPAL0615.csv",
    "prep_CPAL0659.csv",
    "prep_CPAL0666.csv",
    "prep_CPAL0668.csv",
    "prep_CPAL0669.csv",
    "prep_CPAL1229.csv",
    "prep_CPAL1231.csv",
    "prep_CPAL1232.csv",
    "prep_CPAL1233.csv",
    "prep_CPAL1234.csv",
    "prep_CPAL1234.csv",
    "prep_CPAL1235.csv",
    "prep_CPAL1236.csv",
    "prep_CPAL1237.csv",
    "prep_CPAL1238.csv",
    "prep_CPAL1239.csv",
    "prep_CPAL1240.csv",
    "prep_CPAL1241.csv",
    "prep_CPAL1242.csv",
    "prep_CPAL1243.csv",
    "prep_CPAL2081.csv",
    "prep_CPAL2082.csv",
    "prep_CPAL7474.csv",
    "prep_CPAL7653.csv",
    "prep_CPAL8476.csv",
]

pp_grades = ["A", "B", "C", "D"]

paths = GetProjectPaths()


def determine_prefix(item):
    return_val = None
    type = ""

    # determine which type of data the prefix is, and assign it accordingly

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
            # saves pallet id prefix data
            return_val = int(item[6:8])
            type = "cpalid"
    elif len(item) > 5 and item[-2] == "B":
        # saves batch data prefix
        return_val = str(item)
        type = "batch"
    elif item[0:3].lower() == "wk-":
        # saves worker prefix data
        return_val = item
        type = "worker"

    return return_val, type


# used for parsing each row in vertically oriented cpal files
def parse_vertical_straw_row(row, reached_data, prefixes):
    # checks if the data has been reached, since the first lines aren't data
    if reached_data == True:
        straw = {}
        # for each row where data has been detected, goes through assigning pertinent data to the straw dictionary
        if len(row) >= 3:
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
            # only return the straw data if there is actually data present
            # additionally, save the time in the straw dictionary, from the cpal prefixes dictionary
            if len(straw.keys()) != 0:
                straw["time"] = prefixes["time"]
                return straw

    # if the data wasn't determined to be valid, return False
    return False


# parses all rows in a horizontally oriented cpal file
def parse_horizontal_straw_rows(reader, prefixes):
    # initialize lists
    inner_straw = []
    inner_batch = []
    inner_grade = []
    cpal_straws = []

    # keeps track of whether or not the file's end has been reached
    eof = False

    # iterate through all acquired lines of the file
    for row in reader:
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

    # check that the list of straw id's matches the other data
    if len(inner_straw) == len(inner_batch) or len(inner_straw) == len(inner_grade):
        for i in range(len(inner_straw)):
            straw = {"id": inner_straw[i].lower()}

            # save the data corresponding to the straw id
            if len(inner_batch) == len(inner_straw):
                straw["batch"] = str(inner_batch[i])
            if len(inner_grade) == len(inner_straw):
                straw["grade"] = str(inner_grade[i]).upper()

            cpal_straws.append(straw)

        # use prefix batch information if appropriate
        if len(inner_batch) != len(inner_straw):
            for i in cpal_straws:
                try:
                    i["batch"] = prefixes["batch"]
                except:
                    print("batch prefix assignment failed: " + name)

        # add time to straw
        for i in cpal_straws:
            i["time"] = prefixes["time"]

        # if conditions are met, return the cpal_straws data
        return cpal_straws

    else:
        # if the data is bogus, return False
        return False


def get_cpal_prefix(file):
    prefixes = False

    if file.name not in problem_files:
        name = file.name
        with open(file, "r") as f:
            reader = csv.reader(f)

            prefixes = {"cpal": name[-8:-4]}

            print(file.name)
            for row in reader:
                # acquire cpal prefix information
                if (
                    len(str(row[0])) == 16
                    or (len(str(row[0])) == 19)
                    and 2015 < int(str(row[0][0:4])) < 2023
                ):
                    for i in row:
                        return_val, type = determine_prefix(i)
                        if type != "":
                            prefixes[type] = return_val
                    break
    return prefixes


def parse_single_file(file, cpal_list, straw_information, cpal_prefix_list):
    name = file.name

    # first determine whether the straws have a horizontal or vertical layout in the csv file
    vertical_layout = False
    with open(file, "r") as f:
        reader = csv.reader(f)

        for row in reader:
            try:
                if len(row[0]) != 0 and str(row[0]) == "straw":
                    vertical_layout = True
            except:
                pass

    prefixes = get_cpal_prefix(file)
    if prefixes != False:
        cpal_prefix_list.append(prefixes)

        # acquire constituent straw information
        with open(file, "r") as f:
            reader = csv.reader(f)
            reached_data = False
            if vertical_layout:
                cpal_straws = []
                for row in reader:
                    straw = parse_vertical_straw_row(row, reached_data, prefixes)
                    if straw is not False:
                        cpal_straws.append(straw)
                    if len(row) >= 1:
                        if str(row[0]) == "straw":
                            reached_data = True

                if len(cpal_straws) == 0:
                    print("Problem acquiring straw data on cpal " + str(name))
                else:
                    cpal_list.append(name)
                    straw_information[name[-8:-4]] = cpal_straws
            else:
                cpal_straws = parse_horizontal_straw_rows(reader, prefixes)

                if cpal_straws is False:
                    print("Problem acquiring straw data on cpal " + str(name))
                else:
                    cpal_list.append(name)
                    straw_information[name[-8:-4]] = cpal_straws

    return cpal_list, straw_information, cpal_prefix_list


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


def insert_or_compare_straw(connection, table, insert_data_list):
    print(f"Attempting to insert {len(insert_data_list)} entries.")
    insert_count = 0
    ignore_count = 0
    mismatch_count = 0
    batch_update_count = 0
    with connection.begin():
        for insert_data in insert_data_list:
            insert_stmt = table.insert().values(**insert_data)

            straw_id = insert_data["id"]
            csv_batch = insert_data.get("batch")
            csv_timestamp = insert_data.get("timestamp")

            try:
                # new straw added
                connection.execute(insert_stmt)
                print(f"{straw_id} - added")
                if csv_batch == None or csv_batch == "":
                    print(f"  {straw_id} - missing batch")
                insert_count += 1
            except IntegrityError as e:
                # this straw already has an entry in the straw table
                existing_row = connection.execute(
                    sqla.select(table).where(table.c.id == straw_id)
                ).fetchone()

                # problem with the row
                if existing_row is None:
                    print(f"{straw_id} - problem")
                    continue

                db_batch = getattr(existing_row, "batch", None)
                db_timestamp = getattr(existing_row, "timestamp", None)
                time_diff_days = (csv_timestamp - db_timestamp) / 86400.0
                earlier_timestamp = min(csv_timestamp, db_timestamp)

                if db_batch is None or db_batch.strip() == "":
                    # batch is currently missing
                    if csv_batch == None:
                        print(f"{straw_id} - missing batch")
                    else:
                        update_stmt = (
                            table.update()
                            .where(table.c.id == straw_id)
                            .values(batch=csv_batch, timestamp=earlier_timestamp)
                        )
                        result = connection.execute(update_stmt)
                        print(f"{straw_id} - added batch", result.rowcount)
                        batch_update_count += 1
                elif db_batch != csv_batch:
                    # batch mismatch
                    print(f"{straw_id} - batch mismatch")
                    while True:
                        user_input = input(
                            f"0 for db batch: {db_batch}, or 1 for csv batch: {csv_batch}"
                        )
                        if user_input in ["0", "1"]:
                            user_input = int(user_input)
                            break
                        else:
                            print("Invalid input. Please enter 0 or 1.")
                    batch = csv_batch if user_input else db_batch
                    update_stmt = (
                        table.update()
                        .where(table.c.id == straw_id)
                        .values(batch=batch, timestamp=earlier_timestamp)
                    )
                    result = connection.execute(update_stmt)
                    print(f"{straw_id} - added batch", result.rowcount)
                    batch_update_count += 1
                elif abs(int(db_timestamp) - int(csv_timestamp)) > 100:
                    # timestamp mismatch
                    print(
                        f"{straw_id} - timestamp mismatch - {db_timestamp} - {csv_timestamp} - {time_diff_days}"
                    )
                else:
                    ignore_count += 1

    print(
        "insert_count",
        insert_count,
        "batch_update_count",
        batch_update_count,
        "mismatch_count",
        mismatch_count,
        "ignore_count",
        ignore_count,
    )

    # METHOD USING SQLALCHEMY METHODS
    # check_straw = Straw.exists(straw_id)
    # if check_straw is not None:
    #    check_straw.updateBatch(batch)
    # else:
    #    straw = Straw.Straw(straw_id, batch, timestamp)


def update_straw_table(straw_table, connection, straw_information, cpal_prefix_list):
    # Prepare a list to hold all rows to be inserted
    values_to_insert = []

    # for all straws not present in straw table, add them
    for i in cpal_prefix_list:
        cpal = i["cpal"]

        for y in range(len(straw_information[cpal])):
            straw_id = int(straw_information[cpal][y]["id"][2::].lstrip("0"))
            batch = straw_information[cpal][y]["batch"].strip().replace(".", "").upper()
            timestamp = int(straw_information[cpal][y]["time"])

            # csv_batch = insert_data.get("batch", "").strip().replace(".", "").upper()

            # Append a dictionary for each row to the list
            values_to_insert.append(
                {
                    "id": straw_id,
                    "batch": batch,
                    "timestamp": timestamp,
                }
            )

    assert not find_duplicate_straw_ids(values_to_insert), "Duplicates were found."

    insert_or_compare_straw(connection, straw_table, values_to_insert)

    print("done updating straw table")


def update_measurement_prep_table(
    procedure_table,
    straw_location_table,
    connection,
    cpal_prefix_list,
    straw_information,
):
    for i in cpal_prefix_list:
        cpal = i["cpal"]
        cpalid = i["cpalid"]
        time = i["time"]
        straw_location_timestamp_updated = False

        with connection.begin():
            for y in range(len(straw_information[cpal])):
                straw_id = int(straw_information[cpal][y]["id"][2::].lstrip("0"))
                batch = straw_information[cpal][y]["batch"].replace(".", "")
                paper_pull = straw_information[cpal][y]["grade"]
                csv_timestamp = int(straw_information[cpal][y]["time"])

                # Fetch or create a procedure for this (prep,cpal) pair
                procedure = Procedure.StrawProcedure(
                    process=2, pallet_id=cpalid, pallet_number=cpal
                )

                if (not straw_location_timestamp_updated) and procedure.isNew():
                    # Correct the straw_location timestamp if we just created it.
                    # Not airtight, but also not that important.
                    update_stmt = (
                        straw_location_table.update()
                        .where(straw_location_table.c.id == procedure.straw_location)
                        .values(timestamp=csv_timestamp)
                    )
                    straw_location_timestamp_updated = True
                    result = connection.execute(update_stmt)
                else:
                    # Correct the procedure timestamp if we can find an earlier one
                    this_procedure_db_entry = connection.execute(
                        sqla.select(procedure_table).where(
                            procedure_table.c.id == procedure.id
                        )
                    ).fetchone()

                    procedure_db_timestamp = getattr(
                        this_procedure_db_entry, "timestamp", None
                    )

                    earlier_timestamp = min(csv_timestamp, procedure_db_timestamp)
                    time_diff = abs(int(csv_timestamp) - int(procedure_db_timestamp))

                    if time_diff > 100 and procedure_db_timestamp != earlier_timestamp:
                        update_stmt = (
                            procedure_table.update()
                            .where(procedure_table.c.id == procedure.id)
                            .values(timestamp=earlier_timestamp)
                        )
                        result = connection.execute(update_stmt)

                # print(procedure.id, procedure.station, procedure.straw_location)

                # prep_measurement = Prep.StrawPrepMeasurement(
                #    procedure, straw_id, paper_pull[-1], 1, timestamp
                # )
                # prep_measurement.commit()

                # print('Updated measurement prep table for cpal ' + str(cpal))


def update_straw_present_table(cpal_prefix_list, straw_information):
    for i in cpal_prefix_list:
        cpal = i["cpal"]
        cpalid = i["cpalid"]
        time = i["time"]
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


def run():
    cpal_list = []
    straw_information = {}
    cpal_prefix_list = []

    switch = False

    # accumulate all straw prep data from csv files into a few lists and dicts
    for file in Path(paths["prepdata"]).rglob("*.csv"):
        if not (
            "0010" in str(file)
            or "0941" in str(file)
            or "0799" in str(file)
            or "0396" in str(file)
        ):
            continue
        cpal_list, straw_information, cpal_prefix_list = parse_single_file(
            file, cpal_list, straw_information, cpal_prefix_list
        )
        # if switch:
        #    break
        # else:
        #    switch = True

    print(cpal_list)
    # print(straw_information)
    print(cpal_prefix_list)

    database = GetLocalDatabasePath()
    print("Using database:", database)
    engine = sqla.create_engine("sqlite:///" + database)
    metadata = MetaData()

    # reflect table structure
    straw_table = Table("straw", metadata, autoload_with=engine)
    procedure_table = Table("procedure", metadata, autoload_with=engine)
    straw_location_table = Table("straw_location", metadata, autoload_with=engine)

    """
    with engine.connect() as connection:
        existing_row = connection.execute(
            sqla.select(straw_table).where(straw_table.c.id == 1090)
        ).fetchone()
        print(existing_row)
        #batch = getattr(existing_row, "batch", None)
        #print(batch, "|", str(batch), "|", bool(batch))
    """
    with engine.connect() as connection:
        update_straw_table(straw_table, connection, straw_information, cpal_prefix_list)

    with engine.connect() as connection:
        update_measurement_prep_table(
            procedure_table,
            straw_location_table,
            connection,
            cpal_prefix_list,
            straw_information,
        )

        # update_straw_present_table(cpal_prefix_list, straw_information)


if __name__ == "__main__":
    run()
