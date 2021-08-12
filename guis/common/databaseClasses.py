"""
    databaseClasses.py

    'declarative_base' classes mirroring the sqlite database. These classes have additional data-handling functionality.

    Author: Joe Dill

    In this update: (5-29-19)
        -   Procedure-Procedure Schema implemented
            Explanation:
                -   A "procedure" is when a panel/pallet goes through a station. This is one-to-one. Every pallet gets opperated on
                    at each station. This table records that.
                -   A "session" is when a group of workers login to a gui and do something. One gets created/ended every time a gui is opened/closed.
                -   Procedures are linked to procedures in a separate to distinguish between procedures happening on panels and those happening on
                    CPAL rotations.
"""

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
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
)
from sqlalchemy.types import DateTime
from sqlalchemy.sql.functions import now, localtime
from sqlalchemy.sql.expression import true, false
from sqlalchemy import orm
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from guis.common.databaseManager import DatabaseManager
from sys import modules, exit
from inspect import isclass, getmembers
from datetime import datetime

import logging

logger = logging.getLogger("root")

# GLOBAL VARIABLES #
DM = DatabaseManager()
BASE = declarative_base()


class AutoCommit:
    def commit(self):
        return DM.commitEntry(self)


class Barcode:
    @staticmethod
    def barcode(prefix, digits, n):
        try:
            return f"{prefix}{format(n,f'0{digits}')}"
        except:
            return f"{prefix}0{digits}"


class Query:
    @classmethod
    def query(cls):
        return DM.query(cls)

    """
    __queryWithId
    (class method)

        Runs an query on its class and filters by id.

        Input:  id  (int)   PK of object to be queried
        Return: (Query) object to be manipulated further.
    """

    @classmethod
    def __queryWithId(cls, id):
        return cls.query().filter(cls.id == id)

    """
    queryWithId
    (class method)

        Returns result of query by id.

        Input:  id  (int)   PK of object to be queried
        Return: (instance of cls)/(None) if a database entry is (found)/(not found) in this table having the given id.
    """

    @classmethod
    def queryWithId(cls, id):
        return cls.__queryWithId(id).one_or_none()

    """
    existsWithId
    (class method)

        Runs an "exists" query on its class.

        Input:  id  (int)   PK of object to be queried
        Return: (bool) indicating whether a class object having the given id exists in the database.
    """

    @classmethod
    def existsWithId(cls, id):
        return cls.exists(qry=cls.__queryWithId(id))

    """
    exists
    (static method)

        Runs the result of an "exists" query of the given query.

        Input:  qry (Query)   Query object.
        Return: (bool) indicating whether the given query found anything.
    """

    @staticmethod
    def exists(qry):
        return DM.query(qry.exists()).scalar()

    """
    queryCount
    (class method)

        Runs a query on this class that returns a count of the number of entries that match the
        specifications, but not the mapped objects themselves
    """

    @classmethod
    def queryCount(cls):
        return DM.query(func.count(cls.id))


ID_INCREMENT = 100


class ID:
    @staticmethod
    def ID(*args):
        return int(datetime.now().timestamp() * 1e6)

    # Use this type of id for objects that will be created in fast-succession
    @staticmethod
    def IncrementID():
        global ID_INCREMENT
        ID_INCREMENT += 1
        return int(f"{int(datetime.now().timestamp()*1e4)}{'%03d' % ID_INCREMENT}")


class Cast:
    def cast(self, new_class):
        self.__class__ = new_class


# OBJECT class pulls all other classes and methods together
class OBJECT(AutoCommit, Barcode, Query, ID, Cast):
    pass


### TABLES ###


"""
    Bad Wire Form
        Table used to record broken taps in the database
        This form is part of process 8
"""


class BadWire(BASE, OBJECT):
    __tablename__ = "bad_wire_straw"

    id = Column(Integer, primary_key=True)
    position = Column(Integer)
    failure = Column(String)
    process = Column(Integer)
    procedure = Column(Integer)
    wire = Column(BOOLEAN)

    def __init__(self, position, failure, process, procedure, wire_check):
        self.position = position
        self.failure = failure
        self.process = process
        self.procedure = procedure
        self.wire = wire_check

        self.commit()


class LeakFinalForm(BASE, OBJECT):
    __tablename__ = "leak_final_form"

    id = Column(Integer, primary_key=True)
    procedure = Column(Integer)
    cover_reinstalled = Column(String)
    inflated = Column(BOOLEAN)
    leak_location = Column(String)
    confidence = Column(String)
    leak_size = Column(Integer)
    resolution = Column(TEXT)
    next_step = Column(String)

    def __init__(
        self,
        procedure,
        cover_reinstalled,
        inflated,
        leak_location,
        confidence,
        leak_size,
        resolution,
        next_step,
    ):
        self.procedure = procedure
        self.cover_reinstalled = cover_reinstalled
        self.inflated = inflated
        self.leak_location = leak_location
        self.confidence = confidence
        self.leak_size = leak_size
        self.resolution = resolution
        self.next_step = next_step

        self.commit()


###################################


### STATION #######################


###################################


class Straw(BASE, OBJECT):
    # Create Key - Prevents direct use of __init__
    __create_key = object()

    __tablename__ = "straw"
    id = Column(Integer, primary_key=True)
    batch = Column(VARCHAR)

    def __init__(self, id, batch=None, create_key=None):

        # Check for authorization with 'create_key'
        assert (
            create_key == Straw.__create_key
        ), "You can only obtain a StrawLocation with one of the following methods: panel(), cpal(), lpal()."

        self.id = id
        self.batch = batch
        self.commit()

    @classmethod
    def Straw(cls, id, batch=None):

        # Try to query the straw
        s = cls.queryWithId(id)

        # If None is found, construct straw
        if s is None:
            s = Straw(id, batch, cls.__create_key)

        # Return straw
        return s

    """
    strpBarcode(cls,barcode)

        Description:    Class method that returns a straw object when given a straw barcode

        Input:          (str)   Straw barcode

        Return:         Straw object corresponding to given barcode

        Ex: 'ST12345' ==> Straw(id=12345)
    """

    @classmethod
    def strpBarcode(cls, barcode):
        n = int(barcode[2:])
        return cls.Straw(n)

    def __repr__(self):
        return "<Straw(id='%s')>" % (self.id)

    def barcode(self):
        return Barcode.barcode("ST", 5, self.id)

    ## VERIFICATION METHODS ##
    def passed(self, station):
        return self._queryVerification()[station]

    # Verify that straw has passed all previous stations
    def readyFor(self, station):
        stations = [s.name for s in self._queryStations().all()]
        previous_stations = stations[: stations.index(station)]
        return all([self.passed(s) for s in previous_stations])

    ## QUERY METHODS ##
    def _queryStations(self):
        DM.query(Station).filter(Station.production_stage == "straws").order_by(
            Station.production_step.asc()
        )

    # Determines what station this straw is coming from. Returns str() 'station.id'.
    def _queryLastStation(self):
        return
        """station = DM.query(Station).\
            join(Procedure, Procedure.station == Station.label).\
            join(Measurement, Measurement.session == Procedure.id).\
            filter(Measurement.straw == self.id).\
            order_by(Procedure.end_time.desc()).\
            first()
        if station:
            return station.id
        else:
            return None"""

    # Internal class that references a "view" table in the SQL database that evaluates each straw at every station.
    class _Verification(BASE, OBJECT):
        __tablename__ = "straw_verification"

        straw = Column(Integer, primary_key=True)
        prep = Column(Integer)
        ohms = Column(Integer)
        co2 = Column(Integer)
        leak = Column(Integer)
        lasr = Column(Integer)
        silv = Column(Integer)
        leng = Column(Integer)

    # Returns a dictionary: key- station : value- (bool) indicating if straw passed that station
    def _queryVerification(self):
        data = (
            DM.query(self._Verification)
            .filter(self._Verification.straw == self.id)
            .one_or_none()
        )
        if not data:
            return None
        d = data.__dict__
        for k, v in d.items():
            d[k] = bool(v)  # Convert 1,0 to True,False
        return d


### BEGIN STRAW LOCATION CLASSES ###


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
        self.pallet_id = pallet_id = None

        # Record that this StrawLocation was recently made
        self.new = True

        # Commit to database
        self.commit()

        # Make new positions for this StrawLocation
        self._makeNewPositions()

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

    @classmethod
    def _construct(cls, number=int(), pallet_id=None):

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

    @staticmethod
    def CPAL(number=int(), pallet_id=None):
        return CuttingPallet._construct(number=number, pallet_id=pallet_id)

    @staticmethod
    def LPAL(number=int(), pallet_id=None):
        return LoadingPallet._construct(number=number, pallet_id=pallet_id)

    ## PROPERTIES ##

    def getStraws(self):
        # Query Tuples of Straw Position ids and Straw objects
        qry = (
            DM.query(StrawPosition.id, Straw)
            .join(StrawPresent, StrawPresent.straw == Straw.id)
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

    ## INSTANCE METHODS ##

    def getStrawAtPosition(self, position):
        return (
            DM.query(Straw)
            .join(StrawPresent, StrawPresent.straw == Straw.id)
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

    def removeStraw(self, straw=None, position=int(), commit=True):
        # Query StrawPresent
        qry = self._queryStrawPresents()
        if straw:
            qry = qry.filter(StrawPresent.straw == straw.id)
        if position:
            qry = qry.filter(StrawPosition.position_number == position)
        straw_present = qry.one_or_none()
        # If there's not a straw there, return early
        if straw_present is None:
            return
        # Record remove. Commit if requested
        straw_present.remove(commit)
        return straw_present

    def addStraw(self, straw, position, commit=True):

        # Make sure there's not already a straw there
        straw_present = (
            self._queryStrawPresents()
            .filter(StrawPresent.straw == straw.id)
            .one_or_none()
        )
        if straw_present is not None:
            return

        # Query StrawPosition key
        position = (
            self._queryStrawPositions()
            .filter(StrawPosition.position_number == position)
            .one_or_none()
        )

        # Add new StrawPresent to database
        straw_present = StrawPresent(
            straw=straw.id, position=position.id, present=true()
        )

        if commit:
            straw_present.commit()

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
        from guis.common.db_classes.parts_steps import PanelPart, PanelPartUse

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
        from guis.common.db_classes.parts_steps import PanelPart, PanelPartUse

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
        assert self._palletIsEmpty(pallet_id), "Unable to start new pallet "
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
        return "<StrawPosition(id='%s',location'%s',position_number='%s')>" % (
            self.id,
            self.location,
            self.position_number,
        )


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

    def remove(self, commit=True):
        self.present = false()
        if commit:
            self.commit()


### END STRAW LOCATION CLASSES ###


### WORKERS ###


### MEASUREMENTS ###


class PanelTempMeasurement(BASE, OBJECT):
    __tablename__ = "panel_heat"
    id = Column(Integer, primary_key=True)
    procedure = Column(Integer, ForeignKey("procedure.id"))
    temp_paas_a = Column(REAL)
    temp_paas_bc = Column(REAL)

    def __init__(self, procedure, temp_paas_a, temp_paas_bc):
        self.procedure = procedure.id
        self.temp_paas_a = temp_paas_a
        self.temp_paas_bc = temp_paas_bc


class StrawTensionMeasurement(BASE, OBJECT):
    __tablename__ = "measurement_straw_tension"
    id = Column(Integer, primary_key=True)
    procedure = Column(Integer, ForeignKey("procedure.id"))
    position = Column(Integer)
    tension = Column(REAL)
    uncertainty = Column(REAL)

    def __init__(self, procedure, position, tension, uncertainty):
        self.procedure = procedure.id
        self.position = position
        self.tension = tension
        self.uncertainty = uncertainty


class WireTensionMeasurement(BASE, OBJECT):
    __tablename__ = "measurement_wire_tension"
    id = Column(Integer, primary_key=True)
    procedure = Column(Integer, ForeignKey("procedure.id"))
    position = Column(Integer)
    tension = Column(REAL)
    wire_timer = Column(REAL)
    calibration_factor = Column(REAL)

    def __init__(self, procedure, position, tension, wire_timer, calibration_factor):
        self.procedure = procedure.id
        self.position = position
        self.tension = tension
        self.wire_timer = wire_timer
        self.calibration_factor = calibration_factor


class TensionboxMeasurement(BASE, OBJECT):
    __tablename__ = "measurement_tensionbox"
    id = Column(Integer, primary_key=True)
    procedure = Column(Integer, ForeignKey("procedure.id"))
    panel = Column(Integer, ForeignKey("straw_location.id"))
    straw_wire = Column(VARCHAR)
    position = Column(Integer)
    length = Column(REAL)
    frequency = Column(REAL)
    pulse_width = Column(REAL)
    tension = Column(REAL)

    def __init__(
        self,
        procedure,
        panel,
        straw_wire,
        position,
        length,
        frequency,
        pulse_width,
        tension,
    ):
        self.id = self.ID()
        self.procedure = procedure.id
        self.panel = panel.id
        self.straw_wire = straw_wire
        self.position = position
        self.length = length
        self.frequency = frequency
        self.pulse_width = pulse_width
        self.tension = tension


class MeasurementPan5(BASE, OBJECT):
    __tablename__ = "measurement_pan5"
    id = Column(Integer, primary_key=True)
    procedure = Column(Integer, ForeignKey("procedure.id"))
    position = Column(Integer)
    current_left = Column(REAL)
    current_right = Column(REAL)
    voltage = Column(REAL)
    is_tripped = Column(BOOLEAN)
    timestamp = Column(Integer)

    def __init__(
        self, procedure, position, current_left, current_right, voltage, is_tripped
    ):
        self.id = self.ID()
        self.procedure = procedure
        self.position = position
        self.current_left = current_left
        self.current_right = current_right
        self.voltage = voltage
        self.is_tripped = is_tripped
        self.timestamp = int(datetime.now().timestamp())


def main():
    pass


if __name__ == "__main__":
    # main()
    pass
