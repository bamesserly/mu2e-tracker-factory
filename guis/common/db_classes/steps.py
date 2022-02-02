from guis.common.db_classes.bases import BASE, OBJECT
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
    
    def id_to_step(id):
        # Query the step whose id is inputted
        return PanelStep.queryWithId(id)
    
    def getName(self):
        # return the step's name
        return self.name

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
        
    def get_id(self):
        # return id from pertinent step
        return self.panel_step
