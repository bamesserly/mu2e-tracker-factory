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
#   update_straw_table(straw_information, cpal_prefix_list)
#   update_measurement_prep_table(cpal_prefix_list, straw_information)
#   update_straw_present_table(cpal_prefix_list, straw_information)
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
    "CPAL0040.csv",
    "CPAL0025.csv",
    "prep_CPAL7653.csv",
    "CPAL1234.csv",
    "prep_CPAL1234.csv",
    "CPAL0010.csv",
    "CPAL0056",
    "CPAL3945.csv",
    "CPAL6997.csv",
    "CPAL0484.csv",
    "CPAL9119.csv",
    "CPAL0312.csv",
    "CPAL9999.csv",
    "CPAL1551.csv",
    "prep_CPAL0591.csv",
    "prep_CPAL7474.csv",
    "prep_CPAL8476.csv",
    "CPAL1008.csv",
    "prep_CPAL0615.csv",
    "CPAL2929.csv",
    "prep_CPAL0659.csv",
    "CPAL7326.csv",
    "prep_CPAL0666.csv",
    "prep_CPAL0668.csv",
    "prep_CPAL0669.csv",
    "prep_CPAL2081.csv",
    "prep_CPAL2082.csv",
    "prep_CPAL1231.csv",
    "prep_CPAL1232.csv",
    "prep_CPAL1233.csv",
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
    "prep_CPAL1229.csv",
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


def insert_or_compare_batch(connection, table, insert_data_list):
    print(f"Attempting to insert {len(insert_data_list)} entries.")
    insert_count = 0
    ignore_count = 0
    mismatch_count = 0
    batch_update_count = 0
    for insert_data in insert_data_list:
        insert_stmt = table.insert().values(**insert_data)

        try:
            # new straw added
            connection.execute(insert_stmt)
            print("Insert successful for:", insert_data)
            insert_count += 1
        except IntegrityError as e:
            # this straw already has an entry in the straw table
            existing_row = connection.execute(
                sqla.select(table).where(table.c.id == insert_data["id"])
            ).fetchone()

            # problem with the row
            if existing_row is None:
                print("No existing row found with the conflicting id.")
                continue

            ignore_count += 1

            # compare new and existing entry
            for key in insert_data.keys():
                new_value = insert_data[key]
                old_value = getattr(existing_row, key, None)

                if key == "batch" and old_value is None and new_value is not None:
                    # add missing batch
                    entry_id = insert_data.get("id")
                    # use the smaller of the two timestamps as the date that the straw was originally added to the DB.
                    new_timestamp = min(insert_data.get("timestamp"), getattr(existing_row, 'timestamp',None))
                    update_stmt = (
                        table.update()
                        .where(table.c.id == entry_id)
                        .values(batch=new_value, timestamp=new_timestamp)
                    )
                    connection.execute(update_stmt)
                    time_diff_days = (new_timestamp - getattr(existing_row, 'timestamp',None))/86400.
                    print(
                        f"Updated batch and timestamp for entry with id {entry_id}: "
                        f"new batch is {new_value}, new timestamp is {new_timestamp}, "
                        f"old timestamp was {getattr(existing_row, 'timestamp',None)}."
                    )
                    batch_update_count += 1
                    ignore_count -= 1
                    break  # Break out of the loop after handling the update to avoid redundant checks
                elif key == "timestamp" and abs(int(old_value) - int(new_value)) <= 100:
                    # ignore small timestamp differences
                    continue
                elif old_value != new_value:
                    mismatch_count += 1
                    ignore_count -= 1
                    # For all other mismatches not handled above
                    entry_id = insert_data.get("id", None) or getattr(
                        existing_row, "id", None
                    )
                    print(
                        f"Mismatch for {key} in entry with id {entry_id}: "
                        f"existing value is {old_value}, attempted insert value is {new_value}"
                    )

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


def update_straw_table(straw_table, connection, straw_information, cpal_prefix_list):
    # Prepare a list to hold all rows to be inserted
    values_to_insert = []

    # for all straws not present in straw table, add them
    for i in cpal_prefix_list:
        cpal = i["cpal"]

        for y in range(len(straw_information[cpal])):
            straw_id = int(straw_information[cpal][y]["id"][2::].lstrip("0"))
            batch = straw_information[cpal][y]["batch"].replace(".", "")
            timestamp = int(straw_information[cpal][y]["time"])

            # Append a dictionary for each row to the list
            values_to_insert.append(
                {
                    "id": straw_id,
                    "batch": batch,
                    "timestamp": timestamp,
                }
            )

    # print(values_to_insert)

    assert not find_duplicate_straw_ids(values_to_insert), "Duplicates were found."

    insert_or_compare_batch(connection, straw_table, values_to_insert)

    ## SQL query using named placeholders with 'INSERT OR IGNORE INTO'
    # query = """
    # INSERT OR IGNORE INTO straw(id, batch, timestamp)
    # VALUES (:straw_id, :batch, :timestamp);
    # """

    ## Execute all inserts in a batch
    # for values in values_to_insert:
    #    connection.execute(query, values)

    # try:
    #    sendIt = connection.execute(query)
    # except sqla.exc.OperationalError as e:
    #    return e
    # except sqla.exc.IntegrityError as e:
    #    return e

    # METHOD USING SQLALCHEMY METHODS
    # check_straw = Straw.exists(straw_id)
    # if check_straw is not None:
    #    check_straw.updateBatch(batch)
    # else:
    #    straw = Straw.Straw(straw_id, batch, timestamp)

    # except:
    #    print("Error updating straw table for cpal " + str(cpal))

    print("done updating straw table")


def update_measurement_prep_table(cpal_prefix_list, straw_information):
    for i in cpal_prefix_list:
        cpal = i["cpal"]
        cpalid = i["cpalid"]
        time = i["time"]

        try:
            for y in range(len(straw_information[cpal])):
                straw_id = straw_information[cpal][y]["id"][2::].lstrip("0")
                batch = straw_information[cpal][y]["batch"].replace(".", "")
                paper_pull = straw_information[cpal][y]["grade"]
                timestamp = int(straw_information[cpal][y]["time"])

                procedure = Procedure.StrawProcedure(2, cpalid, cpal, timestamp, True)

                prep_measurement = Prep.StrawPrepMeasurement(
                    procedure, straw_id, paper_pull[-1], 1, timestamp
                )
                prep_measurement.commit()

                # print('Updated measurement prep table for cpal ' + str(cpal))
        except:
            print("Error updating measurement_prep data for cpal " + str(cpal))


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


def save_db():
    cpal_list = []
    straw_information = {}
    cpal_prefix_list = []

    switch = False

    # accumulate all straw prep data from csv files into a few lists and dicts
    for file in Path(paths["prepdata"]).rglob("*.csv"):
        cpal_list, straw_information, cpal_prefix_list = parse_single_file(
            file, cpal_list, straw_information, cpal_prefix_list
        )
        if switch:
            break
        else:
            switch = True

    # print(cpal_list)
    # print(straw_information)
    # print(cpal_prefix_list)

    database = GetLocalDatabasePath()
    print("Using database:", database)
    engine = sqla.create_engine("sqlite:///" + database)
    metadata = MetaData()

    # reflect table structure
    straw_table = Table("straw", metadata, autoload_with=engine)

    with engine.connect() as connection:
        update_straw_table(straw_table, connection, straw_information, cpal_prefix_list)

        # update_measurement_prep_table(cpal_prefix_list, straw_information)

        # update_straw_present_table(cpal_prefix_list, straw_information)


def run():
    save_db()


if __name__ == "__main__":
    run()
