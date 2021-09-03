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


class Prep(StrawProcedure):
    __mapper_args__ = {
        "polymorphic_identity": "prep"
    }  # foreign link to which station.id

    def __init__(self, station, straw_location, create_key):
        assert (
            station.id == "prep"
        ), f"Error. Tried to construct prep preocedure for a station '{station.id}' not 'prep'."
        super().__init__(station, straw_location, create_key)

    class StrawPrepMeasurement(BASE, OBJECT):
        __tablename__ = "measurement_prep"
        id = Column(Integer, primary_key=True)
        procedure = Column(Integer, ForeignKey("procedure.id"))
        straw = Column(Integer, ForeignKey("straw.id"))
        # straw = Column(Integer)
        paper_pull_grade = Column(CHAR)
        evaluation = Column(BOOLEAN)
        timestamp = Column(Integer, default=int(datetime.now().timestamp()))

        def __init__(self, procedure, straw, paper_pull_grade, evaluation):
            self.procedure = procedure.id
            self.straw = straw
            self.paper_pull_grade = paper_pull_grade
            self.evaluation = evaluation

    def recordStrawPrepMeasurement(self, straw, paper_pull_grade, evaluation):
        Prep.StrawPrepMeasurement(
            procedure=self,
            straw=straw,
            paper_pull_grade=paper_pull_grade,
            evaluation=evaluation,
        ).commit()


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

class SilvProcedure(Procedure):
    __mapper_args__ = {'polymorphic_identity': "silv"}

    @orm.reconstructor
    def init_on_load(self):
        super().init_on_load()

    def _setDetails(self):
        # Define details class
        class Details(BASE, OBJECT):
            __tablename__ = "procedure_details_silv"
            procedure = Column(Integer, ForeignKey('procedure.id'), primary_key=True)
            epoxy_batch  = Column(Integer)
            epoxy_time = Column(REAL)
        # Save to self.details
        self.details = SilvProcedure.Details(procedure = self.id)

    def setEpoxyBatch(self,batch):
        self.details.epoxy_batch = batch

    def setEpoxyTime(self,duration):
        self.details.epoxy_time = duration

"""
