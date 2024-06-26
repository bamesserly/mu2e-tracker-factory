################################################################################
# SESSION
#
# __tablename__ = "session"
#    id = Column(Integer, primary_key=True)
#    station = Column(VARCHAR, ForeignKey("station.id"))
#    procedure = Column(Integer, ForeignKey("procedure.id"))
#    active = Column(BOOLEAN, default=true())
#
# A Session is started by a SQLDataProcessor's Station. Stations know about
# active sessions.
#
# New entry every time pangui is opened and a process is selected.
#
# Critically, a Session starts Procedures, whether loading a pre-existing
# procedure or creating a new one. Within a session is the only place where
# Procedures are created.
################################################################################
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
from sqlalchemy.sql.expression import true, false
from guis.common.db_classes.procedure import Procedure


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
        return self._procedure  # Procedure object

    def _setProcedure(self, procedure):
        # Save object to private member variable
        self._procedure = procedure
        # Save ID to database column
        self.procedure = procedure.id
        # Commit change to database
        self.commit()

    # The /only/ place where a PanelProcedure is created
    def startPanelProcedure(self, process, panel_number):
        assert (
            self.procedure is None
        ), "A procedure has already been defined for this session."
        p = Procedure.PanelProcedure(process=process, panel_number=panel_number)
        self._setProcedure(p)

    # The /only/ place where a StrawProcedure is created
    def startStrawProcedure(self, process, pallet_id, pallet_number):

        assert (
            self.procedure is None
        ), "A procedure has already been defined for this session."
        p = Procedure.StrawProcedure(
            process=process, pallet_id=pallet_id, pallet_number=pallet_number
        )
        self._setProcedure(p)

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
        return any(certifications)

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
