################################################################################
# STRAW LOCATION (STRAW POSITION)
#
# An entry in the straw_location table points to a specific location that a
# straw can be located at any point during the straw and panel process.
#
# The straw_location_type table tells us that a straw location can be a CPAL,
# LPAL, Panel, storage, or trash. Currently, only the LPAL and Panel location
# types are used, and the location field (along with the type) alone identify
# the location.
#
# If/when we start storing CPAL info, we'll also need to use the pallet ID.
#
# __tablename__ = "straw_location"
#    id = Column(Integer, primary_key=True)
#    location_type = Column(Integer, ForeignKey("straw_location_type.id"))
#    number = Column(Integer)
#    pallet_id = Column(Integer)
#
# Currently, pangui merely saves the LPAL associated with a panel, and blinldy
# populates the straw_position table with 96 straw ids, 48 corresponding to two
# LPAL straw location IDs. Nothing is done with the straw_position table,
# currently.
#
# Initializing any straw location commits it to the DB
#
################################################################################
import logging

logger = logging.getLogger("root")

from guis.common.db_classes.bases import BASE, OBJECT, DM, Barcode
from sqlalchemy import (
    Column,
    Integer,
    String,
    REAL,
    VARCHAR,
    ForeignKey,
    CHAR,
    BOOLEAN,
    and_,
    DATETIME,
    Table,
    TEXT,
    func,
    or_,
)
from sqlalchemy.sql.expression import true, false
import guis.common.db_classes.straw as st
from time import sleep


class StrawLocation(BASE, OBJECT):
    # Create Key - Prevents direct use of __init__
    __create_key = object()

    # Database Columns
    __tablename__ = "straw_location"
    id = Column(Integer, primary_key=True)
    location_type = Column(Integer, ForeignKey("straw_location_type.id"))
    number = Column(Integer)
    pallet_id = Column(Integer)
    __mapper_args__ = {"polymorphic_on": location_type}

    # StrawLocation Information
    new = False

    ## INITIALIZATION ##

    def __init__(
        self, location_type=None, number=int(), pallet_id=None, create_key=None
    ):
        # Check for authorization with 'create_key'
        assert (
            create_key == StrawLocation.__create_key
        ), "You can only obtain a StrawLocation with one of the following methods: panel(), cpal(), lpal()."

        # Database information
        self.id = self.ID()
        self.location_type = location_type
        self.number = number if number else self.nextNumber()
        self.pallet_id = pallet_id

        # Record that this StrawLocation was recently made
        self.new = True

        # Commit to database
        self.commit()

        # Make new positions for this StrawLocation
        self._makeNewPositions()

    def __repr__(self):
        rep = (
            f"{self.id} straw location {self.location_type}{str(self.number).zfill(4)}"
        )

        if self.pallet_id:
            rep += f" at {self.location_type}ID{str(self.pallet_id).zfill(2)}"

        return rep

    """
    _construct
    (class method)

        Description:
            This is the ultimate constructor for any StrawLocation class. Returns a queried
            StrawLocation (or derivative) if a number is provided.
            Otherwise, creates a new one (using the create_key).

        Input:
            number      (int)                       StrawLocation's number in the database (provide to query)
            new         (bool)                      Set to True if this is a new StrawLocation
            pallet_id   (int)                       Applicable to pallets (CuttingPallet and Loading Pallet) only.
                                                    This is the number on the pallets 'CPALID##' barcode.

        Output:
            An instance of 'cls' that is linked to an entry in the database.
    """

    # problem with this function for pallets (not panels): if multiple pallets
    # exist with the same number but different id. Well I'm not sure what would
    # happen, but it's not good. Likewise, if you can call this function with
    # an existing number but new id, then you'll just get returned the existing
    # pallet when instead you should get an error.
    @classmethod
    def _construct(cls, number=int(), pallet_id=None):
        assert int(
            number
        ), "Error: attempting to retrieve or create a straw location with a non-integer number."
        sl = None

        # Try to query the desired straw_location
        sl = cls._queryStrawLocation(number)

        # If None was found, make a new one.
        if sl is None:
            sl = cls(
                number=number,
                pallet_id=pallet_id,
                create_key=cls.__create_key,
            )

        return sl

    ## CONSTRUCTORS ##

    @staticmethod
    def Panel(number):
        return Panel._construct(number)

    # TODO check here (not in construct) for existing pallets with this number
    # but a different id.
    @staticmethod
    def CPAL(number=int(), pallet_id=None):
        return CuttingPallet._construct(number=number, pallet_id=pallet_id)

    # TODO check here (not in construct) for existing pallets with this number
    # but a different id.
    @staticmethod
    def LPAL(number=int(), pallet_id=None):
        return LoadingPallet._construct(number=number, pallet_id=pallet_id)

    ## PROPERTIES ##
    def getStraws(self):

        # Query Tuples of Straw Position ids and Straw objects
        qry = (
            DM.query(StrawPosition.id, st.Straw)
            .join(StrawPresent, StrawPresent.straw == st.Straw.id)
            .outerjoin(StrawPosition, StrawPosition.id == StrawPresent.position)
            .filter(StrawPosition.location == self.id)
            .filter(StrawPresent.present == True)
            .order_by(StrawPosition.position_number.asc())
            .all()
        )

        # Create a dictionary of this query {<position id> : <Straw>, ...}
        straw_position_dict = dict(qry)

        # Query straw position ids on this straw location ordered by position number
        positions = (
            DM.query(StrawPosition.id)
            .filter(StrawPosition.location == self.id)
            .order_by(StrawPosition.position_number.asc())
            .all()
        )

        # Create a list of straws of equal length to the list of positions
        straws = [None] * len(positions)

        # Iterate through the list of positions and use the dictionary to populate the list of straws, leaving None objects wherever there is no Straw.
        for i, pos in enumerate([p[0] for p in positions]):
            try:
                straws[i] = straw_position_dict[pos]
            except KeyError:
                pass
        return straws

    def isEmpty(self):
        return not any(self.getStraws())

    def getLocationType(self):
        return StrawLocationType.queryWithId(self.location_type)

    def barcode(self):
        return self.getLocationType().barcode(self.number)

    def isNew(self):
        return self.new

    # return [0, 6, 8, 14, 22, ...]
    def getUnfilledPositions(self):
        all_positions = [i for i in range(0, 95) if i % 2 == 0]  # [0,2,4,...,94]
        filled_positions = self.getFilledPositions()
        return [i for i in all_positions if i not in filled_positions]
        """
        # This one fails to capture the fact that a straw may have been removed
        # from a position and then another straw or the same one re-added to the
        # same position. Need to search get positions which do not have a 1.
        # Keeping it here because notes on how to make sql queries helpful.
        unfilled_positions = (
            DM.query(StrawPosition.position_number)  # get all straw position numbers
            .outerjoin(
                StrawPresent, StrawPresent.position == StrawPosition.id
            )  # and all the matching StrawPresent positions
            .filter(
                or_(StrawPresent.position == None, StrawPresent.present == 0)
            )  # such that the StrawPresent positions don't actually have an entry
            # or such that the present field is false
            .filter(StrawPosition.location == self.id)  # for this straw location
            .order_by(StrawPosition.position_number.asc())
            .all()
        )

        return [pos for pos, *remainder in unfilled_positions]
        """

    # return [0, 6, 8, 14, 22, ...]
    def getFilledPositions(self):
        filled_positions = (
            DM.query(StrawPosition.position_number)  # get all straw position numbers
            .join(
                StrawPresent, StrawPresent.position == StrawPosition.id
            )  # where the straw positions have an entry in the StrawPresent table
            .filter(StrawPresent.present == 1)
            .filter(StrawPosition.location == self.id)  # for this straw location
            .order_by(StrawPosition.position_number.asc())
            .all()
        )
        return [pos for pos, *remainder in filled_positions]

    ## INSTANCE METHODS ##

    def getStrawAtPosition(self, position):
        return (
            DM.query(st.Straw)
            .join(StrawPresent, StrawPresent.straw == st.Straw.id)
            .join(StrawPosition, StrawPresent.position == StrawPosition.id)
            .filter(StrawPosition.location == self.id)
            .filter(StrawPosition.position_number == position)
            .one_or_none()
        )

    def getLikeLocations(self):
        return self.queryStrawLocations(self.__class__)

    #  Used when constructing new StrawLocations...

    # This method should eventually be re-created in SQL.
    def _makeNewPositions(self):
        # Make list of StrawPosition objects
        positions = []
        for i in self.getLocationType().positionRange():
            sp = StrawPosition(location=self.id, position_number=i)
            sp.id += i
            positions.append(sp)
        # Commit to database
        return DM.commitEntries(positions)

    # ADD/REMOVE STRAWS
    # straw argument here is a Straw object
    def removeStraw(self, straw=None, position=None, commit=True):
        logger.debug(f"removing straw in position {position}")
        qry = (
            DM.query(StrawPresent)  # get entries from straw present table
            .filter(StrawPresent.present == True)  # such that straws are present
            .filter(StrawPosition.location == self.id)  # for this straw location
        )
        if straw:
            qry = qry.filter(
                StrawPresent.straw == straw.id
            )  # and with straw id matching the argument
        if position is not None:
            qry = qry.join(
                StrawPosition, StrawPosition.id == StrawPresent.position
            ).filter(  # w/ position matching an entry in straw position table
                StrawPosition.position_number == position
            )  # with Straw Position matching the argument
        logger.debug(f"removeStraw: straws matching query: {qry.all()}")
        straw_present = qry.one_or_none()
        if straw_present is None:
            return
        straw_present.remove(commit)
        return straw_present

    def removeAllStraws(self, commit=True):
        for position in self.getFilledPositions():
            self.removeStraw(position=position, commit=commit)

    # Cautiously add straws to this straw location
    #
    # WARNING ­ function might not do what you want. In short: it adopts a very
    # cautious approach. Only in perfect conditions will the straw actually get
    # added to this location. Otherwise it will do nothing, silently.
    #
    # The conditions that must be satisfied to add the straw are:
    # (1) the straw is not already located somewhere else
    # AND
    # (2) the target location is not currently occupied.
    #
    # I'm not messing with this function until I can understand all its
    # consequences, specifically, in its (only) application when transfering
    # straws from LPALs to panels in procedure_panel. Instead, for new use in
    # straw guis, I'm creating forceAddStraw(), below. -BAM
    def addStraw(self, straw, position, commit=True):
        # If this straw is currently located /anywhere/ quit and do nothing
        straw_present = (
            self._queryStrawPresents()
            .filter(StrawPresent.straw == straw.id)
            .one_or_none()
        )
        if straw_present is not None:
            return

        # Get the target position object
        position = (
            self._queryStrawPositions()
            .filter(StrawPosition.position_number == position)
            .one_or_none()
        )

        # Create a new entry in the straw_present table corresponding to this
        # position, this straw, and with present = true
        straw_present = StrawPresent(
            straw=straw.id, position=position.id, present=true()
        )

        if commit:
            straw_present.commit()

        return straw_present

    # Safely transfer a straw from previous location(s) to target location.
    #
    # 1. Remove given straw from all current locations (unless one of them is
    # the target location).
    # 2. Remove any straws from target location.
    # 3. Finally, add the straw.
    def forceAddStraw(self, straw, position, commit=True):
        # Get or create target position
        target_position = (
            self._queryStrawPositions()
            .filter(StrawPosition.position_number == position)
            .one_or_none()
        )
        if not target_position:
            logger.warning(
                f"Adding straw {straw} to position {self.location_type}{self.number} - {position}, which doesn't exist in the DB. This is weird, and you should let Ben know."
            )
            logger.warning(
                "Anways, I'm creating the position and adding the straw to it."
            )
            target_position = StrawPosition(location=self.id, position=position)
            target_position.commit()

        # Get positions where straw is currently located.
        # Nothing stopping from a straw existing in two places at once, so get
        # all possible. This is a list of StrawPresent objects.
        straw_presents = (
            self._queryStrawPresents().filter(StrawPresent.straw == straw).all()
        )
        if len(straw_presents) > 1:
            logger.debug(f"Straw ST{straw} located in > 1 position :(.")

        # Remove straw from all current positions, unless one of them is the
        # target position, in which case quit when done.
        done = False
        for straw_present in straw_presents:
            if straw_present.getStrawPosition() == target_position:
                logger.debug(
                    f"Straw ST{straw} already in target location {target_position}."
                )
                done = True
            else:
                straw_present.remove()
        if done:
            return

        # Clear the target position of all straws
        target_position.unloadPresentStraws()

        # Add the straw to the target position (add entry to straw_position
        # table).
        straw_present = StrawPresent(
            straw=straw, position=target_position.id, present=true()
        )

        if commit:
            sleep(0.4)  # so the order of events in the DB is clear
            straw_present.commit()
            logger.debug(f"Straw ST{straw_present.straw} added to {target_position}.")

        return straw_present

    ### QUERY METHODS ###

    ## Instance Queries ##
    # These are queries that pertain only to a specific instance of StrawLocation.
    # However, they make use of public static methods.

    def _queryStrawPositions(self):
        return self.queryStrawPositions(self.id)

    def _queryStrawPresents(self):
        return self.queryStrawPresents(self.id)

    ## Straw Locations

    # Private

    @classmethod
    def _queryStrawLocation(cls, number):
        # Query a StrawLocation of the specified type with the given number.
        # In two recent lab occurances of the MP error, this line was the culprit
        sl = cls.query().filter(cls.number == number).one_or_none()
        return sl

    ## Straw Positions

    @staticmethod
    def queryStrawPositions(straw_location):
        return (
            DM.query(StrawPosition)
            .filter(StrawPosition.location == straw_location)
            .order_by(StrawPosition.position_number)
        )

    ## Straw Presents

    """queryStrawPresents
    (public static method)

        Description:
            General Query of StrawPresent objects at the specified location.

        Input:
            straw_location (int) Database PK of desired StrawLocation.

        Output:
            (list) List of StrawPresent Objects
    """

    @classmethod
    def queryStrawPresents(cls, straw_location):
        return (
            StrawPresent.query()
            .join(cls.queryStrawPositions(straw_location).subquery())
            .filter(StrawPresent.present == True)
        )

    ## Other
    @classmethod
    def nextNumber(cls):
        n = DM.query(func.max(cls.number)).one()[0]
        if n is None:
            return 1
        else:
            return int(n[2:]) + 1


class Panel(StrawLocation):
    __mapper_args__ = {"polymorphic_identity": "MN"}

    def __init__(self, number=int(), pallet_id=None, create_key=None):
        super().__init__(
            location_type="MN",
            number=number,
            pallet_id=None,  # This is always None, no matter the input.
            create_key=create_key,
        )
        # Note, this method will only pass super().__init__() if called from StrawLocation.panel
        # because otherwise it won't have the create key.

    def _recordPart(self, type, number, L_R=None, letter=None, on_L_R=None):
        from guis.common.db_classes.panel_parts import PanelPart, PanelPartUse

        # Query/Construct Part
        part = PanelPart.queryPart(type, number, L_R, letter).one_or_none()
        if not part:
            # If part doesn't exist, construct and commit it
            part = PanelPart(type, number, L_R, letter)
            part.commit()
        # Check if part has already been used on this panel
        use = (
            PanelPartUse.query()
            .filter(PanelPartUse.panel_part == part.id)
            .filter(PanelPartUse.panel == self.id)
            .filter(PanelPartUse.left_right == on_L_R)
            .one_or_none()
        )
        if use is None:
            # Record use in database
            PanelPartUse(panel_part=part.id, panel=self.id, left_right=on_L_R).commit()

    def getBIR(self):
        return self._queryPartOnPanel("BIR").one_or_none()

    def recordBIR(self, number):
        self._recordPart("BIR", number)

    def getMIR(self):
        return self._queryPartOnPanel("MIR").one_or_none()

    def recordMIR(self, number):
        self._recordPart("MIR", number)

    def getPIR(self, L_R, letter):
        return self._queryPartOnPanel("PIR", L_R, letter).one_or_none()

    def recordPIR(self, number, L_R, letter):
        self._recordPart("PIR", number, L_R, letter)

    def getALF(self, L_R):
        return self._queryPartOnPanel("ALF", on_L_R=L_R).one_or_none()

    def recordALF(self, number, L_R):
        self._recordPart("ALF", number, on_L_R=L_R)

    def getBaseplate(self):
        return self._queryPartOnPanel("BASEPLATE").one_or_none()

    def recordBaseplate(self, number):
        self._recordPart("BASEPLATE", number)

    def getFrame(self):
        return self._queryPartOnPanel("FRAME").one_or_none()

    def recordFrame(self, number):
        self._recordPart("FRAME", number)

    # gets LEFT rib
    def getMiddleRib1(self):
        return self._queryPartOnPanel("MIDDLERIB_1").one_or_none()

    # records LEFT rib
    def recordMiddleRib1(self, number):
        self._recordPart("MIDDLERIB_1", number)

    # gets RIGHT rib
    def getMiddleRib2(self):
        return self._queryPartOnPanel("MIDDLERIB_2").one_or_none()

    # records RIGHT rib
    def recordMiddleRib2(self, number):
        self._recordPart("MIDDLERIB_2", number)

    def getPAAS(self, L_R, letter):
        return self._queryPartOnPanel("PAAS", None, letter).one_or_none()

    def recordPAAS(self, number, L_R, letter):
        if number is not None:
            self._recordPart("PAAS", number, None, letter)

    ## QUERY METHODS ##

    def _queryPartOnPanel(self, type, L_R=None, letter=None, on_L_R=None):
        from guis.common.db_classes.panel_parts import PanelPart, PanelPartUse

        return (
            PanelPart.queryPart(type=type, L_R=L_R, letter=letter)
            .join(PanelPartUse, PanelPartUse.panel_part == PanelPart.id)
            .filter(PanelPartUse.left_right == on_L_R)
            .filter(PanelPartUse.panel == self.id)
        )

    @classmethod
    def queryByNumber(cls, number):
        # MP error or something also here!
        sl = cls.query().filter(cls.number == number).one_or_none()
        return sl


class Pallet(StrawLocation):
    def __init__(
        self, location_type=None, number=int(), pallet_id=None, create_key=None
    ):
        assert self._palletIsEmpty(
            pallet_id
        ), f"Unable to create pallet {number}: pallet {pallet_id} is not empty."
        super().__init__(
            location_type=location_type,
            number=number,
            pallet_id=pallet_id,
            create_key=create_key,
        )

    @property
    def palletBarcode(self):
        return self.getLocationType().palletBarcode(self.pallet_id)

    @classmethod
    def _palletIsEmpty(cls, pallet_id):
        pallets = cls._queryPalletsByID(pallet_id).all()
        return all(p.isEmpty() for p in pallets)

    @classmethod
    def _queryPalletsByID(cls, pallet_id):
        return cls.query().filter(cls.pallet_id == pallet_id)

    @classmethod
    def remove_straws_from_pallet_by_id(cls, pallet_id):
        old_pals = cls._queryPalletsByID(pallet_id).all()
        logger.debug(f"clearing straws from old pallets\n{old_pals}")
        for pal in old_pals:
            filled_positions = pal.getFilledPositions()
            if len(filled_positions):
                logger.debug(
                    f"Clearing {len(filled_positions)} straws from this {pal}."
                )
                pal.removeAllStraws()
            assert pal.isEmpty()


class LoadingPallet(Pallet):
    __mapper_args__ = {"polymorphic_identity": "LPAL"}

    def __init__(
        self, location_type=None, number=int(), pallet_id=None, create_key=None
    ):
        super().__init__(
            location_type="LPAL",
            number=number,
            pallet_id=pallet_id,
            create_key=create_key,
        )


class CuttingPallet(Pallet):
    __mapper_args__ = {"polymorphic_identity": "CPAL"}

    def __init__(
        self, location_type=None, number=int(), pallet_id=None, create_key=None
    ):
        super().__init__(
            location_type="CPAL",
            number=number,
            pallet_id=pallet_id,
            create_key=create_key,
        )
    
    @classmethod
    def save_to_db(self, straws_passed_list, pallet_id, pallet_number):
        logger = logging.getLogger("root")
        #assert len(straws_passed_list) == 24
        
        # Get a cpal in the DB
        try:
            cpal = self.CPAL(pallet_id=pallet_id, number=pallet_number)
        # can't make new pallet bc this id still has straws on it.
        except AssertionError as e:
            logger.debug(e)
            self.remove_straws_from_pallet_by_id(pallet_id)
            cpal = self.CPAL(pallet_id=pallet_id, number=pallet_number)
    
        for position, straw_id in enumerate(straws_passed_list):
            straw_number = int(straw_id[2:])
            if not st.Straw.exists(straw_number):
                logger.info(f"Straw ST{straw_number} doesn't exist! Creating it.")
                logger.info("If you see lots of these messages, stop and inform Ben.")
    
            # safely remove this straw from its current location(s), clear the
            # target position, and then add the straw
            cpal.forceAddStraw(st.Straw.Straw(id=straw_number).id, position)


class StrawLocationType(BASE, OBJECT):
    __tablename__ = "straw_location_type"
    id = Column(VARCHAR(4, 7), primary_key=True)
    name = Column(VARCHAR(25))
    barcode_digits = Column(Integer)
    position_min = Column(Integer)
    position_max = Column(Integer)
    position_increment = Column(Integer)
    pallet_barcode_prefix = Column(VARCHAR)
    pallet_barcode_digits = Column(Integer)

    def __repr__(self):
        return "<StrawLocationType('%s')>" % (self.id)

    def barcode(self, n):
        if self.barcode_digits is not None:
            return Barcode.barcode(self.id, self.barcode_digits, n)
        else:
            return None

    def palletBarcode(self, n):
        if (
            self.pallet_barcode_prefix is not None
            and self.pallet_barcode_digits is not None
        ):
            return Barcode.barcode(
                self.pallet_barcode_prefix, self.pallet_barcode_digits, n
            )
        else:
            return None

    def positionRange(self):
        return range(
            self.position_min,
            self.position_max + self.position_increment,
            self.position_increment,
        )


# A straw position is a slot on a straw location
class StrawPosition(BASE, OBJECT):
    __tablename__ = "straw_position"
    id = Column(Integer, primary_key=True)
    location = Column(Integer, ForeignKey("straw_location.id"))
    position_number = Column(Integer)

    def __init__(self, location, position_number):
        self.id = self.IncrementID()
        self.location = location
        self.position_number = position_number

    def __repr__(self):
        return f"<{self.id} straw position {self.position_number} on {repr(self.getStrawLocation())}>"

    def getStrawLocation(self):
        return (
            DM.query(StrawLocation)
            .filter(StrawLocation.id == self.location)
            .one_or_none()
        )

    def getStrawLocationType(self):
        return self.getStrawLocation().location_type

    # Get (a query of) the StrawPresent objects associated with this position
    def queryStrawPresents(self):
        return (
            StrawPresent.query()
            .join(StrawPosition, StrawPosition.id == StrawPresent.position)
            .filter(StrawPosition.id == self.id)
        )

    # unload all straws from this position
    def unloadPresentStraws(self, straw_number=None):
        present_straws = (
            self.queryStrawPresents().filter(StrawPresent.present == True).all()
        )  # list of StrawPresent objects
        for present_straw in present_straws:
            if straw_number is not None and straw_number != present_straw.straw:
                continue
            present_straw.remove()


# Each straw's past (present == false) and current (present == true) straw
# locations. More specifically, the position points to the straw_position
# table, which is a space for a straw on a straw location.
#
# "remove" means set present to false.
class StrawPresent(BASE, OBJECT):
    __tablename__ = "straw_present"
    id = Column(Integer, primary_key=True)
    straw = Column(Integer, ForeignKey("straw.id"))
    position = Column(Integer, ForeignKey("straw_position.id"))
    present = Column(BOOLEAN)

    def __init__(self, straw, position, present=true()):
        self.id = self.IncrementID()
        self.straw = straw
        self.position = position
        self.present = present

    def __repr__(self):
        return "<StrawPresent(id='%s',straw'%s',position='%s')>" % (
            self.id,
            self.straw,
            self.position,
        )

    def getStrawPosition(self):
        return (
            StrawPosition.query()
            .join(StrawPresent, StrawPresent.position == StrawPosition.id)
            .filter(StrawPresent.position == self.position)
            .one_or_none()
        )

    def remove(self, commit=True):
        self.present = false()
        if commit:
            self.commit()
            logger.debug(f"Straw ST{self.straw} removed from {self.getStrawPosition()}")
