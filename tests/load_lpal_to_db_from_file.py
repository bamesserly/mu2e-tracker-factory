# ===============================================================================
#
# ===============================================================================
from csv import DictReader, DictWriter
from pathlib import Path
from guis.common.db_classes.straw_location import LoadingPallet
from guis.common.db_classes.straw import Straw


def read_file(lpal_file):
    with lpal_file.open("r") as f:
        reader = DictReader(line for line in f if line.split(",")[0])
        rows = [row for row in reader]
    return rows, reader.fieldnames


def get_or_create_straw(straw_id):
    straw = Straw.exists(straw_id=straw_id)
    if not straw:
        print("Straw not found in DB, creating straw.")
        straw = Straw.Straw(id=straw_id)
    assert straw
    return straw


def removeStrawFromCurrentLocation(straw, straw_position):
    straw_location = straw_position.getStrawLocation()
    position_on_straw_location = straw_position.position_number
    straw_location.removeStraw(straw, position_on_straw_location)
    logger.info(
        f"Straw ST{straw.id} removed from {repr(straw_location)}, position {position_on_straw_location}."
    )
    return straw_location


def remove_straw_from_current_locations(straw):
    # list of StrawPositions where the DB thinks this straw is currently
    # located.
    # Hopefully, it's just present in one place: the cpal from which we're
    # transferring it.
    straw_positions = straw.locate()

    # straw not found anywhere. possible that we just created this straw
    if len(straw_positions) == 0:
        print("Straw not found anywhere. You probably just created it.")
    # straw found on exactly 1 CPAL -- GOOD
    elif (
        len(straw_positions) == 1
        and straw_positions[0].getStrawLocationType() == "CPAL"
    ):
        print("Straw found on exactly 1 CPAL. Removing.")
        cpal = removeStrawFromCurrentLocation(straw, straw_positions[0])
    # straw found in more than one location
    else:
        print("Straw found in more than one location:")
        for p in straw_positions:
            straw_location = removeStrawFromCurrentLocation(straw, p)
            cpals.add(straw_location)  # record this straw location
        logger.warning(
            f"Straw ST{straw.id} found present somewhere other than a single CPAL!"
        )
        logger.warning("\n".join([repr(i) for i in straw_positions]))
        if not getYN(f"Do you want to remove the straw from all of these locations?"):
            return False
    return True


if __name__ == "__main__":
    # 1. submit new/update existing info about LPAL (LPAL ID)
    # "lpal" or "lpal number" == LPAL1234
    # "lpalid" == LPALID01
    # I'm pretty sure that when you do this: associated entries in the
    # straw_position table will be created.

    # 2. add straw info to the LPAL
    # (in most old cases) add new entries to straw_present table
    # This means: collect 24 entries -- get the field info for each entry.
    #     straw should be a Straw object (see class in guis/common/db_classes/)
    #     position should be a StrawPosition object
    #     time_in and time_out -- no current way to record this info
    #     timestamp = timestamp of LPAL file OR same as time_in
    # The addition of a new StrawPresent entry should just amount to /instantiating/ a StrawPresent object.
    # loop straws in an lpal file
    #   straw_number, straw_position_integer, time_in = parse_file()
    #   straw = GetStraw(straw_number) # Straw(straw_number)
    #   straw_position = GetStrawPosition(straw_position_integer, LPAL)
    #   sp = StrawPresent(straw, straw_position, current = False, time_in=1234, time_out = 2345, timestamp = 12345)
    lpal = LoadingPallet._queryStrawLocation(468)
    print(lpal)
    unfilled_db = lpal.getUnfilledPositions()
    print(len(unfilled_db), "unfilled positions in the DB.")

    lpal_file = Path(r"C:\Users\mu2e\Desktop\LPAL0468_LPALID01COPY.csv")
    straws, fieldnames = read_file(lpal_file)
    print(48 - len(straws), "unfilled positions in the text file.")

    for row in straws:
        straw = get_or_create_straw(int(row["straw"][2:]))
        removeStrawFromCurrentLocations(straw, cpals)


# 2. Remove straw from current CPAL (and any other pallets)
if not removeStrawFromCurrentLocations(straw, cpals):
    return "scanning"

# 3. Remove straw currently in this position
lpal.removeStraw(straw=None, position=position, commit=True)

# 3. Add straw to LPAL in the DB
lpal.addStraw(straw, position)
logger.info(f"Straw ST{straw_id} added to LPAL{lpal.number} at position {position}.")


# print(fieldnames)

"""
# first draft:
# pass input file
# 
# lpal = get straw location/lpal from id and/or number
# loop lines in file:
#   straw_present_entry = lpal.addStraw(straw, position)
#   update the "time_in" timestamp of straw_present_entry

unfilled = getUnfilledPositions(outfile)  # from text file
unfilled_db = lpal.getUnfilledPositions()  # from the DB

outfile = getLPALFile(lpal.pallet_id, lpal.number)
status = addStrawToLPAL(lpal, outfile, cpals)


# Txt file and DB agree.
# When totally filled, unfilled = [], unfilled_db = None, which is why we
# need both checks.
if (not unfilled and not unfilled_db) or unfilled == unfilled_db:
    logger.debug("db and text file agree on which positions are filled.")
    logger.debug(f"{unfilled} {unfilled_db}")
    logger.debug(f"filled (DB) {lpal.getFilledPositions()}")
# Txt file and DB do not agree
else:
    logger.warning(
        f"Text file {outfile} and database disagree on which LPAL positions are unfilled."
    )
    logger.info(f"unfilled (txt file)\n{getUnfilledPositions(outfile)}")
    logger.info(f"filled (DB)\n{lpal.getFilledPositions()}")
    logger.info(f"unfilled (DB)\n{lpal.getUnfilledPositions()}")
    logger.info(
        "You can proceed to scan any and all straws to set the "
        "record straight in the DB AND text file."
    )

if len(unfilled) == 0:
    logger.info(
        f"According to {outfile} all positions on this pallet have been filled."
    )
    if not getYN("Continue scanning straws?"):
        if getYN("Finish?"):
            return "finish"
else:
    logger.info(f"Unfilled Positions:\n{unfilled}")
    if not getYN("Continue scanning straws?"):
        return "pause"

# 1. Get Straw object
straw = getOrCreateStraw(int(straw_id[2:]))
if not straw:
    return "scanning"

# 2. Remove straw from current CPAL (and any other pallets)
if not removeStrawFromCurrentLocations(straw, cpals):
    return "scanning"

# 3. Remove straw currently in this position
lpal.removeStraw(straw=None, position=position, commit=True)

# 3. Add straw to LPAL in the DB
lpal.addStraw(straw, position)
logger.info(
    f"Straw ST{straw_id} added to LPAL{lpal.number} at position {position}."
)
"""
