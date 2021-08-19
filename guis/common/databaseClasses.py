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
from datetime import datetime
from sys import modules, exit
from inspect import isclass, getmembers
from datetime import datetime
from time import time

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


class Comment(BASE, OBJECT):
    __tablename__ = "comment"
    id = Column(Integer, primary_key=True)
    procedure = Column(Integer, ForeignKey("procedure.id"))
    text = Column(TEXT)
    timestamp = Column(Integer, default=int(datetime.now().timestamp()))

    def __repr__(self):
        return f"Comment: procedure = {self.procedure}, text = {self.text}"

    def __init__(self, procedure, text, timestamp=int(datetime.now().timestamp())):
        self.id = self.ID()
        self.procedure = procedure
        self.text = text
        self.timestamp = timestamp

    @classmethod
    def queryByPanel(cls, panel_number):
        from guis.common.db_classes.straw_location import StrawLocation
        from guis.common.db_classes.session_procedure import Procedure

        # panel = Panel.query().filter(Panel.number == panel_number).one_or_none()

        # when was this code written? looks like a solution to MP
        panel = StrawLocation.Panel(panel_number)

        return (
            cls.query()
            .join(Procedure, cls.procedure == Procedure.id)
            .join(StrawLocation, Procedure.straw_location == StrawLocation.id)
            .filter(StrawLocation.id == panel.id)
            .order_by(Comment.timestamp.asc())
            .all()
        )


class Failure(BASE, OBJECT):
    # Table Columns
    __tablename__ = "failure"
    id = Column(Integer, primary_key=True)
    procedure = Column(Integer, ForeignKey("procedure.id"))
    position = Column(Integer)
    failure_type = Column(VARCHAR)
    failure_mode = Column(TEXT)
    comment = Column(TEXT, ForeignKey("comment.id"))

    # Failure Types
    pin = "pin"
    straw = "straw"
    anchor = "anchor"
    wire = "wire"

    def __init__(self, procedure, position, failure_type, failure_mode, comment):
        self.procedure = procedure
        self.position = position
        self.failure_type = failure_type
        self.failure_mode = failure_mode
        self.comment = self._recordComment(comment).id

    def _recordComment(self, text):
        comment = Comment(
            procedure=self.procedure,
            text=text,
            timestamp=int(datetime.now().timestamp()),
        )
        comment.commit()
        return comment


class PanelPart(BASE, OBJECT):
    __tablename__ = "panel_part"
    id = Column(Integer, primary_key=True)
    type = Column(Integer, ForeignKey("panel_part_type.id"))
    number = Column(Integer)
    left_right = Column(CHAR)
    letter = Column(CHAR)

    def __init__(self, type, number, left_right=None, letter=None):
        self.id = self.ID()
        self.type = type
        self.number = number
        self.left_right = left_right
        self.letter = letter

    def getPartType(self):
        return PanelPartType.queryWithId(id=self.type)

    def barcode(self):
        return self.getPartType().barcode(self.number)

    # Expands Query.query to filter by attributes rather than id.
    @classmethod
    def queryPart(cls, type, number=None, L_R=None, letter=None):
        qry = cls.query().filter(cls.type == type)
        if number:
            qry = qry.filter(cls.number == number)
        if L_R:
            qry = qry.filter(cls.left_right == L_R)
        if letter:
            qry = qry.filter(cls.letter == letter)
        return qry


class PanelPartType(BASE, OBJECT):
    __tablename__ = "panel_part_type"
    id = Column(VARCHAR, primary_key=True)
    barcode_prefix = Column(VARCHAR)
    barcode_digits = Column(Integer)

    def barcode(self, n):
        return Barcode.barcode(
            prefix=self.barcode_prefix, digits=self.barcode_digits, n=n
        )


class PanelPartUse(BASE, OBJECT):
    __tablename__ = "panel_part_use"
    id = Column(Integer, primary_key=True)
    panel_part = Column(Integer, ForeignKey("panel_part.id"))
    panel = Column(Integer, ForeignKey("straw_location.id"))
    left_right = Column(CHAR)

    def __init__(self, panel_part, panel, left_right):
        self.panel_part = panel_part
        self.panel = panel
        self.left_right = left_right


class PanelStep(BASE, OBJECT):
    __tablename__ = "panel_step"
    id = Column(Integer, primary_key=True)
    station = Column(Integer, ForeignKey("station.id"))
    name = Column(VARCHAR)
    text = Column(TEXT)
    checkbox = Column(BOOLEAN)
    picture = Column(VARCHAR)
    next = Column(Integer, ForeignKey("panel_step.id"))
    previous = Column(Integer, ForeignKey("panel_step.id"))
    parent_step = Column(Integer, ForeignKey("panel_step.id"))
    current = Column(BOOLEAN)

    def __repr__(self):
        return f"<PanelStep(station={self.station},name={self.name})>"

    def substeps(self):
        # Query first substep

        first_sub_step = (
            self.querySubSteps()
            .filter(PanelStep.parent_step == self.id)
            .filter(PanelStep.previous == None)
            .one_or_none()
        )
        # Append steps to list in order until there are no more.
        sub_steps = self.stepsList(first_sub_step)
        return sub_steps

    def nextStep(self):
        # Query the step who's id is 'self.next'
        return PanelStep.queryWithId(self.next)

    def previousStep(self):
        # Query the step who's id is 'self.previous'
        return PanelStep.queryWithId(self.previous)

    """
    querySubSteps
    (classmethod)

        Queries steps that are sub steps (have a parent PanelStep)

        Output: (Query) query of substeps that can be manipulated further.
    """

    @classmethod
    def querySubSteps(cls):
        return cls.query().filter(cls.parent_step != None)

    @staticmethod
    def stepsList(root_step):
        steps = []
        step = root_step
        # Append steps to list in order until there are no more.
        while step is not None:
            steps.append(step)
            step = step.nextStep()
        # Return list
        return steps


class PanelStepExecution(BASE, OBJECT):
    __tablename__ = "panel_step_execution"
    id = Column(Integer, primary_key=True)
    panel_step = Column(Integer, ForeignKey("panel_step.id"))
    procedure = Column(Integer, ForeignKey("procedure.id"))

    def __init__(self, panel_step, procedure):
        self.id = self.IncrementID()
        self.panel_step = panel_step
        self.procedure = procedure


class Room(BASE, OBJECT):
    __tablename__ = "room"
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR)


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

###################################


def main():
    pass


if __name__ == "__main__":
    # main()
    MeasurementPan5pass
