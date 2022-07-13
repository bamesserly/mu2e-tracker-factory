################################################################################
# This script is able to submit a csv of bad channels to the DB, and it can
# interactively submit a dead channel to the DB.
#
# Specifically, we're talking about adding entries to the bad_wire_straw table.
#
# Currently runs the batch/csv submission by default.
#
# TODO accept an infile argument and the ability to run interactive instead.
#
# Also TODO: Haven't decided yet whether you should be allowed to update
# entries, or whether submitting an entry with an existing (procedure_id,
# channel position) pair should ignore or fail.
#
################################################################################

from guis.common.panguilogger import SetupPANGUILogger

import logging

logger = SetupPANGUILogger("root", "dead_channel_entry")

import sqlalchemy as sqla  # for interacting with db
from guis.common.db_classes.measurements_panel import BadWire
from guis.common.db_classes.procedure import Procedure, PanelProcedure
from guis.common.gui_utils import except_hook
import sys
from dataclasses import dataclass
from pathlib import Path
import pandas as pd
from datetime import datetime
import time
from guis.common.db_classes.bases import DM


kPROCESSNUMBER = 8
sys.excepthook = except_hook  # crash, don't hang when an exception is raised


@dataclass
class BadChannel:
    pid: int
    position: int
    is_wire: bool
    description: str
    timestamp: int
    process_number: int = 8


def get_from_user(prompt, manipulation, condition):
    while True:
        info = input(prompt)
        try:
            info = manipulation(info)
            assert condition(info)
            return info
        except KeyboardInterrupt:
            sys.exit()
        except:
            print(f"Invalid input {info}")
            continue


def interactive_load():
    """
    data fields collected:
        * panel_number
        * position
        * is_wire
        * process_number (in which failure occurred)
        * description
    """

    # keep inputting dead channels until you ctrl-C
    while True:

        panel_number = get_from_user(
            prompt="Panel number XXX: ",
            manipulation=lambda x: x,
            condition=lambda x: 0 <= int(x) < 1000,
        )

        pid = -1
        try:
            pid = PanelProcedure.GetPanelProcedure(kPROCESSNUMBER, panel_number).id
            assert pid != -1
        except AttributeError as e:
            logger.error(
                f"panel MN{panel_number} either doesn't exist or it doesn't have a process 8 in the DB."
            )
            continue

        position = get_from_user(
            prompt="Position of dead wire/straw: ",
            manipulation=lambda x: x,
            condition=lambda x: 0 <= int(x) <= 95,
        )

        # wire/straw
        response = input("Is it a wire [a] or straw [b] that failed? ").lower()
        is_wire = 1 if response == "a" else 0

        process_number = get_from_user(
            prompt="Process when failure was detected [Default 8]: ",
            manipulation=lambda x: 8 if x == "" else int(x),
            condition=lambda x: x in list(range(1, 9)),
        )

        description = get_from_user(
            prompt="Describe (< 80 characters) how/why wire/straw failed: ",
            manipulation=lambda x: x.replace("\n", " "),
            condition=lambda x: len(x) < 80,
        )

        # ship it
        straw_wire_str = "wire" if is_wire else "straw"
        logger.info(
            f"Submitting entry to DB:\npanel:{panel_number}, position:{position}, wire-straw:{straw_wire_str}, process:{process_number}, description:{description}\n"
        )
        BadWire(
            procedure=pid,
            position=position,
            wire_check=is_wire,
            failure=description,
            process=process_number,
        )


def load_data_from_csv(infile):
    assert Path(infile).is_file()
    # header = ('panel', 'date', 'position', 'explanation', 'wire_straw', 'shipping_confirmed', 'box', 'dbv_notes', 'nsources', 'notes')
    df = pd.read_csv(infile, sep=",", skipinitialspace=True, index_col=False)
    df = df.where(pd.notnull(df), None)
    data = df.to_dict("records")
    bad_channels = []
    for i in data:
        # make sure all the important fields are not null
        notnull_fields = ["date", "panel", "wire_straw", "position", "explanation"]
        try:
            assert all(
                value is not None for key, value in i.items() if key in notnull_fields
            )
        except AssertionError:
            logger.error(
                f"Entry is missing one or more fields. Skipping this one:\n{i}"
            )
            continue

        # validate timestamp
        try:
            dt = datetime.strptime(i["date"], "%m/%d/%Y")
        except ValueError:
            dt = datetime.strptime(i["date"], "%m/%d/%y")

        timestamp = int(time.mktime(dt.timetuple()))

        # validate procedure ID
        procedure = PanelProcedure.GetPanelProcedure(kPROCESSNUMBER, i["panel"])
        try:
            assert procedure
        except AssertionError:
            # print(i)
            logger.info(f"Process 8 doesn't exist for MN{i['panel']}. Creating it.")
            procedure = Procedure.PanelProcedure(
                process=kPROCESSNUMBER, panel_number=int(i["panel"])
            )
            assert procedure

        pid = procedure.id

        # validate is_wire vs is_straw
        assert i["wire_straw"] == "S" or i["wire_straw"] == "W"
        is_wire = 1 if i["wire_straw"].upper() == "W" else 0

        # validate explanation of failure
        assert len(i["explanation"]) <= 80

        # add BadChannel object to list of bad channels
        bad_channels.append(
            BadChannel(
                pid=int(pid),
                position=int(i["position"]),
                is_wire=is_wire,
                description=i["explanation"],
                process_number=i["process"] if i["process"] else kPROCESSNUMBER,
                timestamp=timestamp,
            )
        )
    return bad_channels


def bulk_load(infile):
    # list of bad channel objects from csv
    bad_channel_data = load_data_from_csv(infile)
    logger.info(f"Loading {len(bad_channel_data)} bad channels into DB.")
    print("\n\n")
    submitted = 0
    failed = 0
    # loop bad channels and submit each to DB
    for i in bad_channel_data:
        print("\n")
        logger.info(f"Submitting entry to DB:")
        print(i)

        # ship it
        try:
            BadWire(
                procedure=i.pid,
                position=i.position,
                wire_check=i.is_wire,
                failure=i.description,
                process=i.process_number,
                timestamp=i.timestamp,
            )
            submitted += 1

        # uniqueness constraint (procedure, position, wire-straw) failed
        # in other words: this bad channel already exists
        # If you want to update a channel, you gotta do something different
        except sqla.exc.IntegrityError:
            failed += 1
            logger.warning(
                "Bad channel entry already exists. NOT adding duplicate to the DB."
            )
            logger.warning(
                "If you want to update an entry tell Ben or put it in the comments."
            )
            DM._connection.rollback()  # after the conflict, need to rollback
    print("\n\n")
    logger.info(f"Of {len(bad_channel_data)} bad channels from the csv file...")
    logger.info(
        f"{submitted} entries added to DB. {failed} duplicate entries not added."
    )


if __name__ == "__main__":
    bulk_load("tests/2022-07-13_dead_channels.csv")
    # interactive_load()
