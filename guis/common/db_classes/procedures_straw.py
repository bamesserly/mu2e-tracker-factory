################################################################################
# Panel Process Metadata Classes/Tables
#
# Most straw processes don't collect enough metainfo to warrant their own
# procedure_details_X data tables. Thus, these classes are dummy classes that
# only exist so that a Procedure created with these child classes just have
# "prep" or whatever as their station in the procedure database table.
#
# Actually, they /would/ be dummy classes except that I've also packed their
# specific straw-by-straw measurements into them. For example: prep has paper
# pull grades, resistance has its resistance measurements. These measurement
# classes/tables need not live within their procedure classes -- they often
# don't for panel processes/measurements.
################################################################################
from guis.common.db_classes.bases import BASE, OBJECT, DM, logger
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
from datetime import datetime
from guis.common.db_classes.procedure import StrawProcedure
from guis.common.db_classes.straw import Straw


class Prep(StrawProcedure):
    __mapper_args__ = {
        "polymorphic_identity": "prep"
    }  # foreign link to which station.id

    def __init__(self, station, straw_location, create_key):
        assert (
            station.id == "prep"
        ), f"Error. Tried to construct prep procedure for a station '{station.id}' not 'prep'."
        super().__init__(station, straw_location, create_key)

    class StrawPrepMeasurement(BASE, OBJECT):
        __tablename__ = "measurement_prep"
        id = Column(Integer, primary_key=True)
        procedure = Column(Integer, ForeignKey("procedure.id"))
        straw = Column(Integer, ForeignKey("straw.id"))
        paper_pull_grade = Column(CHAR)
        evaluation = Column(BOOLEAN)
        timestamp = Column(Integer, default=int(datetime.now().timestamp()))

        def __init__(self, procedure, straw_id, paper_pull_grade, evaluation):
            self.procedure = procedure.id
            self.straw = straw_id
            self.paper_pull_grade = paper_pull_grade
            self.evaluation = evaluation


class Resistance(StrawProcedure):
    __mapper_args__ = {
        "polymorphic_identity": "ohms"
    }  # foreign link to which station.id

    def __init__(self, station, straw_location, create_key):
        assert (
            station.id == "ohms"
        ), f"Error. Tried to construct ohms procedure for a station '{station.id}' not 'ohms'."
        super().__init__(station, straw_location, create_key)

    # measurement_ohms table
    class StrawResistanceMeasurement(BASE, OBJECT):
        __tablename__ = "measurement_ohms"
        id = Column(Integer, primary_key=True)
        procedure = Column(Integer, ForeignKey("procedure.id"))
        straw = Column(Integer, ForeignKey("straw.id"))
        inside_inside_resistance = Column(REAL)
        inside_inside_method = Column(String)
        inside_outside_resistance = Column(REAL)
        inside_outside_method = Column(String)
        outside_inside_resistance = Column(REAL)
        outside_inside_method = Column(String)
        outside_outside_resistance = Column(REAL)
        outside_outside_method = Column(String)
        evaluation = Column(BOOLEAN)
        timestamp = Column(Integer, default=int(datetime.now().timestamp()))

        def __init__(
            self,
            id,
            procedure,
            straw,
            ii_resistance=None,
            ii_method=None,
            io_resistance=None,
            io_method=None,
            oi_resistance=None,
            oi_method=None,
            oo_resistance=None,
            oo_method=None,
            evaluation=None,
        ):
            self.id = self.ID()
            self.procedure = procedure.id
            self.straw = straw
            self.inside_inside_resistance = ii_resistance
            self.inside_inside_method = ii_method
            self.inside_outside_resistance = io_resistance
            self.inside_outside_method = io_method
            self.outside_inside_resistance = oi_resistance
            self.outside_inside_method = oi_method
            self.outside_outside_resistance = oo_resistance
            self.outside_outside_method = oo_method
            self.evaluation = evaluation
            self.commit()

        def __repr__(self):
            return (
                f"""{"procedure":<17}| {"straw":<8}| {"ii":<10}| {"io":<10}| {"oi":<10}| {"oo":<10}\n"""
                f"""{self.procedure:<17}| ST{self.straw:<6}| {self.inside_inside_resistance:<10}| """
                f"""{self.inside_outside_resistance:<10}| {self.outside_inside_resistance:<10}| """
                f"""{self.outside_outside_resistance:<10}"""
            )

        def setMeasurement(self, measurement, measurement_type):
            which_member = {
                "ii": "inside_inside_resistance",
                "io": "inside_outside_resistance",
                "oi": "outside_inside_resistance",
                "oo": "outside_outside_resistance",
            }[measurement_type]
            setattr(self, which_member, "%9.5f" % measurement)


class FillLPAL(StrawProcedure):
    __mapper_args__ = {
        "polymorphic_identity": "load"
    }  # foreign link to which station.id

    def __init__(self, station, straw_location, create_key):
        assert (
            station.id == "load"
        ), f"Error. Tried to construct load procedure for a station '{station.id}' not 'load'."
        super().__init__(station, straw_location, create_key)


class SilvProcedure(StrawProcedure):
    __mapper_args__ = {"polymorphic_identity": "silv"}

    def __init__(self, station, straw_location, create_key):
        assert (
            station.id == "silv"
        ), f"Error. Tried to construct SilverEpoxy for a station '{station.id}' not 'silv'."
        super().__init__(station, straw_location, create_key)

    def _getDetailsClass(self):
        class Details(BASE, OBJECT):
            __tablename__ = "procedure_details_silv"
            procedure = Column(Integer, ForeignKey("procedure.id"), primary_key=True)
            epoxy_batch = Column(Integer)
            epoxy_time = Column(REAL)

        return Details

    # We no longer save this info
    def setEpoxyBatch(self, batch):
        self.details.epoxy_batch = batch
        self.commit()

    def setEpoxyTime(self, duration):
        self.details.epoxy_time = duration
        self.commit()

    # We no longer save this info
    def getEpoxyBatch(self):
        return self.details.epoxy_batch

    def getEpoxyTime(self):
        return self.details.epoxy_time


"""
class Co2Procedure(Procedure):
    __mapper_args__ = {'polymorphic_identity': "co2"}

    def _setDetails(self):
        class Details(BASE, OBJECT):
            __tablename__ = "procedure_details_co2"
            procedure = Column(Integer, ForeignKey('procedure.id'), primary_key=True)
            epoxy_batch  = Column(Integer)
            epoxy_time = Column(REAL)
            dp190 = Column(Integer)
        self.details = Co2Procedure.Details(procedure = self.id)

    def setEpoxyBatch(self,batch):
        self.details.epoxy_batch = batch

    def setEpoxyTime(self,duration):
        self.details.epoxy_time = duration

    def setDp190(self,dp190):
        self.details.dp190 = dp190

class LasrProcedure(Procedure):
    __mapper_args__ = {'polymorphic_identity': "lasr"}

    @orm.reconstructor
    def init_on_load(self):
        super().init_on_load()

    def _setDetails(self):
        class _FirstPosition(BASE, OBJECT):
            __tablename__ = "laser_cut_first_position"
            position = Column(Integer, primary_key=True)
            cut_type  = Column(VARCHAR)

        class _ApproximateHumidity(BASE, OBJECT):
            __tablename__ = "laser_cut_approximate_humidity"
            humidity = Column(Integer, primary_key=True)

        # Define details class
        class Details(BASE, OBJECT):
            __tablename__ = "procedure_details_lasr"
            procedure = Column(Integer, ForeignKey('procedure.id'), primary_key=True)
            first_position  = Column(Integer, ForeignKey('laser_cut_first_position.position'))
            approximate_humidity = Column(REAL, ForeignKey('laser_cut_approximate_humidity.humidity'))
        # Save to self.details
        self.details = LasrProcedure.Details(procedure = self.id)

    def setFirstPosition(self,position):
        # Make sure input is valid first position
        position_entry = DM.query(LasrProcedure._FirstPosition).\
            filter(LasrProcedure._FirstPosition.position == position).\
            one_or_none()
        # Record position if valid
        if position_entry:
            self.details.first_position = position

    def setApproximateHumidity(self,humidity):
        # Make sure input is valid humidity
        position_entry = DM.query(LasrProcedure._ApproximateHumidity).\
            filter(LasrProcedure._ApproximateHumidity.humidity == humidity).\
            one_or_none()
        # Record humidity if valid
        if position_entry:
            self.details.approximate_humidity = humidity


"""
