from guis.common.databaseClasses import BASE, OBJECT, DM
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


class Station(BASE, OBJECT):
    __tablename__ = "station"
    id = Column(CHAR(4), primary_key=True)
    name = Column(VARCHAR(30))
    room = Column(Integer, ForeignKey("room.id"))
    # room = Column(Integer)
    production_stage = Column(Integer, ForeignKey("production_stage.id"))
    # production_stage = Column(Integer)
    production_step = Column(Integer)
    __mapper_args__ = {"polymorphic_on": production_stage}

    # solution to MP?
    # TODO instead of one_or_none, call one() and try catch if None
    # As-is: crash when none
    @staticmethod
    def panelStation(day):
        # print(PanelStation.query().first()) # None!
        # print(PanelStation.query().filter(PanelStation.production_step == day))
        try:
            return (
                PanelStation.query()
                .filter(PanelStation.production_step == day)
                .one_or_none()
            )
        except sqlalchemy.exc.OperationalError:
            logger.error("DB Locked. Panel station query failed.")

    def startSession(self):
        from guis.common.db_classes.session_procedure import Session

        # Start new session and return
        return Session(self)

    def activeSessions(self):
        from guis.common.db_classes.session_procedure import Session

        return Session.query().filter(Session.active == True).all()

    def queryMoldReleaseItems(self):
        return (
            MoldReleaseItems.query().filter(MoldReleaseItems.station == self.id).all()
        )


class PanelStation(Station):
    __mapper_args__ = {"polymorphic_identity": "panel"}

    def getSteps(self):
        from guis.common.db_classes.steps import PanelStep

        # Get step 1
        s1 = (
            DM.query(PanelStep)
            .filter(PanelStep.current == True)
            .filter(PanelStep.station == self.id)
            .filter(PanelStep.previous == None)
            .filter(PanelStep.parent_step == None)
            .one_or_none()
        )
        # Generate steps list from step 1
        return PanelStep.stepsList(root_step=s1)

    def getDay(self):
        return self.production_step


class Room(BASE, OBJECT):
    __tablename__ = "room"
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR)
