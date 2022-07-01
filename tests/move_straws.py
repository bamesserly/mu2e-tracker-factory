from guis.common.db_classes.straw_location import (
    StrawLocation,
    StrawPosition,
    StrawPresent,
)
from guis.common.db_classes.straw import Straw
from sqlalchemy.sql.expression import true, false
from guis.common.panguilogger import SetupPANGUILogger
from guis.common.getresources import pkg_resources
import resources

logger = SetupPANGUILogger("root", tag="move_straws", be_verbose=True)

try:
    assert "Production" not in pkg_resources.read_text(resources, "rootDirectory.txt")
except AssertionError:
    logger.error("You can't run this test from a production folder.")

cpal = StrawLocation.CPAL(pallet_id=22, number=1091)
# straw = Straw.Straw(id=27444)
# cpal.addStraw(straw=straw,position=1)
if Straw.exists(73670):
    logger.info("Straw 73670 already exists!")
else:
    logger.info("Straw 73670 does not exist!")
cpal.forceAddStraw(straw=Straw.Straw(id=73670).id, position=10)


"""
# Get the target position object
position = (
    cpal._queryStrawPositions()
    .filter(StrawPosition.position_number == 1)
    .one_or_none()
)

straws_in_this_position = position.queryStrawPresents().filter(StrawPresent.present == True).all()
print("Straws already in this position:", straws_in_this_position)

# Create a new entry in the straw_present table corresponding to this
# position, this straw, and with present = true
straw_present = StrawPresent(
    straw=straw.id, position=position.id, present=true()
)

print("straws_present entry we're trying to submit", straw_present)

straw_present.commit()
"""


"""
def addStraw(self, straw, position, commit=True):
    # Check if this straw is already in any position
    straw_present = (
        self._queryStrawPresents()
        .filter(StrawPresent.straw == straw.id)
        .one_or_none()
    )
    print(straw_present)
    # if so, then we're done
    if straw_present is not None:
        return

    # Remove straw from all locations 
    straw.removeFromAllLocations()

    # clear the target position of other straws
    position = (
        self._queryStrawPositions()
        .filter(StrawPosition.position_number == position)
        .one_or_none()
    )
    print(position)
    position.unloadPresentStraws()

    # Add new StrawPresent to database
    straw_present = StrawPresent(
        straw=straw.id, position=position.id, present=true()
    )
    print(straw_present)

    if commit:
        straw_present.commit()

    return straw_present

    ## 4. Remove straw currently in this CPAL position
    #straw_position.unloadPresentStraws()

    ## 5. Add straw to CPAL in the DB
    #cpal.addStraw(straw, position)
    #logger.debug(
    #    f"Straw ST{straw_id} added to CPAL{lpal.number} at position {position}."
    #)
"""
