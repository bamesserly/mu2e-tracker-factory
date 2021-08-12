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
from sqlalchemy.sql.expression import true, false


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
        # Start new session and return
        return Session(self)

    def activeSessions(self):
        return Session.query().filter(Session.active == True).all()

    def queryMoldReleaseItems(self):
        from guis.common.db_classes.supplies import MoldReleaseItems

        return (
            MoldReleaseItems.query().filter(MoldReleaseItems.station == self.id).all()
        )


class PanelStation(Station):
    __mapper_args__ = {"polymorphic_identity": "panel"}

    def getSteps(self):
        from guis.common.db_classes.parts_steps import PanelStep

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


class Session(BASE, OBJECT):
    __tablename__ = "session"
    id = Column(Integer, primary_key=True)
    station = Column(VARCHAR, ForeignKey("station.id"))
    procedure = Column(Integer, ForeignKey("procedure.id"))
    active = Column(BOOLEAN, default=true())

    ## SESSION VARIABLES ##
    _procedure = None  # Defines with _setProcedure

    def __init__(self, station):
        self.id = self.ID()
        # Need to define id here so this object doesn't lose track of it's
        # row when the database auto-generates an id.
        self.station = station.id
        self._station = station  # Pointer to the Station object
        self.commit()

    def terminate(self):
        self.logoutAll()
        if self._procedure is not None:
            self._procedure.stop()
        self.active = false()
        self.commit()

    ## PROCEDURE ##

    def getProcedure(self):
        return self._procedure

    def _setProcedure(self, procedure):
        # Save object to private member variable
        self._procedure = procedure
        # Save ID to database column
        self.procedure = procedure.id
        # Commit change to database
        self.commit()

    def startPanelProcedure(self, day, panel_number):
        from guis.common.db_classes.procedure import Procedure

        assert (
            self.procedure is None
        ), "A procedure has already been defined for this session."
        self._setProcedure(Procedure.PanelProcedure(day=day, panel_number=panel_number))

    def startStrawProcedure(self, station, cpal_number):
        """self._setProcedure(
            Procedure.StrawProcedure(
            )
        )"""
        pass

    ## WORKER PORTAL ##

    def login(self, worker_id):
        from guis.common.db_classes.workers import WorkerLogin

        WorkerLogin(session=self.id, worker=worker_id).commit()

    def logout(self, worker_id):
        for wl in self._queryWorkerLogins().all():
            if wl.worker == worker_id:
                wl.logout()
                break

    def logoutAll(self):
        for wl in self._queryWorkerLogins().all():
            wl.logout()

    def checkCredentials(self):
        certifications = [w.certified(self._station) for w in self._sessionWorkers()]
        return any(certifications) and all(certifications)

    def getWorkers(self):
        return [w.id for w in self._sessionWorkers()]

    def _sessionWorkers(self):
        return self._queryWorkers().all()

    def _queryWorkers(self):
        from guis.common.db_classes.workers import Worker

        return Worker.query().join(self._queryWorkerLogins().subquery())

    def _queryWorkerLogins(self):
        from guis.common.db_classes.workers import WorkerLogin

        return (
            WorkerLogin.query()
            .filter(WorkerLogin.session == self.id)
            .filter(WorkerLogin.present == true())
        )
