# Manually enter bad channels

from guis.common.panguilogger import SetupPANGUILogger

import logging

logger = SetupPANGUILogger("root", "dead_channel_entry")

from guis.common.db_classes.measurements_panel import BadWire
from guis.common.db_classes.procedure import PanelProcedure
from guis.common.gui_utils import except_hook
import sys

kPROCESSNUMBER = 8
sys.excepthook = except_hook  # crash, don't hang when an exception is raised

if __name__ == "__main__":

    """
    data fields collected:
        * panel_number
        * position
        * is_wire
        * process_number (in which failure occurred)
        * description
    """

    # keep inputting data until you ctrl-C
    while True:
        # panel number from user input
        while True:
            panel_number = input("Enter panel number XXX: ")
            # panel_number = 147
            try:
                assert 0 < int(panel_number) < 1000
                break
            except KeyboardInterrupt:
                sys.exit()
            except:
                print("Invalid panel number {panel_number}")
                continue

        # look up procedure id
        pid = -1
        try:
            pid = PanelProcedure.GetPanelProcedure(kPROCESSNUMBER, panel_number).id
            assert pid != -1
        except AttributeError as e:
            logger.error(
                f"panel MN{panel_number} either doesn't exist or it doesn't have a process 8 in the DB."
            )
            continue

        # position of dead channel from user input
        while True:
            position = input("Position of dead wire/straw? ")
            try:
                assert 0 <= int(position) <= 95
                break
            except KeyboardInterrupt:
                sys.exit()
            except:
                logger.debug("Invalid position {position}")

        # wire or straw from user input
        response = input("Is it a wire [a] or straw [b] that failed? ").lower()
        is_wire = 1 if response == "a" else 0

        # process number in which failure occurred (if other than 8)
        while True:
            try:
                process_number = input(
                    "In which process was the failure detected? [Default: 8]) >"
                )
                process_number = 8 if process_number == "" else int(process_number)
                assert process_number in list(range(1, 9))
                break
            except KeyboardInterrupt:
                sys.exit()
            except:
                logger.debug("Invalid process number {process_number}")

        # description of failure from user input
        while True:
            try:
                description = input(
                    "Describe in (< 80 characters) how/why the wire/straw failed: "
                )
                description.replace("\n", " ")
                assert len(description) < 80
                break
            except KeyboardInterrupt:
                sys.exit()
            except:
                logger.error("Invalid desciption {description}")

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
