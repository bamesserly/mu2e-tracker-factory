# Form to submit dead channels to the DB

from guis.common.panguilogger import SetupPANGUILogger

import logging

logger = SetupPANGUILogger("root", "dead_channel_entry")

from guis.common.db_classes.measurements_panel import BadWire
from guis.common.db_classes.procedure import PanelProcedure
from guis.common.gui_utils import except_hook
import sys
from dataclasses import dataclass
from pathlib import Path
import pandas as pd
from datetime import datetime
import time


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
    data = pd.read_csv(infile, sep=",", skipinitialspace=True).to_dict("records")
    bad_channels = []
    for i in data:
        # timestamp
        dt = datetime.strptime(i["date"], "%m/%d/%Y")
        timestamp = time.mktime(dt.timetuple())

        # procedure ID
        pid = -1
        pid = PanelProcedure.GetPanelProcedure(kPROCESSNUMBER, i["panel"]).id
        assert pid != -1

        # wire/straw
        assert i["wire_straw"] == "S" or i["wire_straw"] == "W"
        is_wire = 1 if i["wire_straw"].upper() == "W" else 0

        assert len(i.explanation) <= 80

        bad_channels.append(
            BadChannel(
                pid=int(pid),
                position=int(i["position"]),
                is_wire=is_wire,
                description=i["explanation"],
                timestamp=timestamp,
            )
        )


def bulk_load():
    # list of bad channel objects
    bad_channel_data = load_data_from_csv("tests/dead_channels.csv")
    for i in bad_channel_data:
        print(i)
    #    straw_wire_str = "wire" if i.is_wire else "straw"
    #    logger.debug(f"Submitting entry to DB:")
    #    logger.debug(
    #        f"panel:{i.panel_number}, position:{i.position}, "
    #        "wire-straw:{i.straw_wire_str}, process:{i.process_number}, "
    #        "timestamp:{i.timestamp}\n"
    #    )
    #    logger.debug(f"description:{description}")
    #    BadWire(
    #        procedure=i.pid,
    #        position=i.position,
    #        wire_check=i.is_wire,
    #        failure=i.description,
    #        process=i.process_number,
    #        timestamp=i.timestamp,
    #    )


if __name__ == "__main__":
    bulk_load()
    # interactive_load()
