################################################################################
# What: Quick tool to create a procedure in the db given a panel and process.
#
# Why: Wrote this to load CSV data into the DB for panels that were too old to
# have a pid.
#
# How: If procedure already exists, retrieve its pid number. If it doesn't not
# already exist, create it and retrieve its pid number. When creating a
# procedure, also create its entry in its corresponding procedure_details tails
# (when applicable).
#
# TODO: currently only works for panels, not straws
#
# N.B.
# - you're editing the database! careful!
# - you're editing the local database. You changes won't be propagated until
# you run an automerge, which this script does not automatically do.
################################################################################
from guis.common.db_classes.procedure import Procedure, PanelProcedure
import sys


def main(panel_number, process_number):
    print(f"MN{panel_number} pro{process_number}")
    pid = -1
    try:
        pid = PanelProcedure.GetPanelProcedure(process_number, panel_number).id
        print("PID exists")
    except AttributeError as e:
        print(f"PID does NOT exist.")
        if (
            "y"
            in input(
                "Are you sure you want to create it? Type 'y' to confirm> "
            ).lower()
        ):
            procedure = Procedure.PanelProcedure(process=process_number, panel_number=panel_number)
            pid = procedure.id
    print(f"PID: {pid}")


if __name__ == "__main__":
    main(panel_number=sys.argv[1], process_number=sys.argv[2])
