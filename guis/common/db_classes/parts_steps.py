from guis.common.databaseClasses import BASE, OBJECT, Barcode
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
