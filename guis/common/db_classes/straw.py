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
)


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
