from guis.common.databaseClasses import BASE, OBJECT, DM, Query
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
from sqlalchemy import orm
from datetime import datetime
from time import time


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
        assert (
            self.procedure is None
        ), "A procedure has already been defined for this session."
        p = Procedure.PanelProcedure(day=day, panel_number=panel_number)
        self._setProcedure(p)

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


class Procedure(BASE, OBJECT):
    # Create Key - Prevents public use of __init__
    __create_key = object()

    # Database Columns
    __tablename__ = "procedure"
    id = Column(Integer, primary_key=True)
    station = Column(CHAR(4), ForeignKey("station.id"))
    straw_location = Column(Integer, ForeignKey("straw_location.id"))
    elapsed_time = Column(Integer, default=0)
    __mapper_args__ = {"polymorphic_on": station}

    # Instance Variables
    new = False
    details = None

    def __repr__(self):
        return f"<{self.__class__.__name__}(station={self.station}, straw_location={self.straw_location})>"

    ## INITIALIZATION ##
    """
    __init__
        Description:
            Initialization method. This method is for internal use only.

        Input:
            station         (Station)       Station where this procedure is being conducted.
            straw_location  (StrawLocation) StrawLocation being operated on during this procedure.
            create_key      (Object)        Method only accepts the private Procedure.__create_key object,
                                            thus it is only accessible within the class.
    """

    def __init__(self, station, straw_location, create_key):
        # Enforce internal use only
        assert (
            create_key == Procedure.__create_key
        ), "You can only initialize a Procedure with PanelProcedure or StrawProcedure."

        # Save database values
        self.id = self.ID()
        self.station = station.id
        self.straw_location = straw_location.id

        # Record that this is a new Procedure (constructed, not queried)
        self.new = True

        # Commit to database, then run other load methods
        self.commit()
        self.init_on_load()

    # Capable of loading an existing procedure or making a new one.
    # Also, capable of loading/creating a specific PanelProcedure or
    # StrawProcedure (were any to ever actually be written)
    @classmethod
    def _startProcedure(cls, station, straw_location):
        # Must tell procedure that it has subclasses! Tricky error if you dont.
        import guis.common.db_classes.panel_procedures

        # This subclassing stuff is sketchy.  See __init_subclass__ and stack
        # overflow 4162456 if we ever have trouble.

        # Get furthest-derived class possible.
        for c in cls.__subclasses__():
            if c.__mapper_args__["polymorphic_identity"] == station.id:
                cls = c
                break

        procedure = (
            cls.query()
            .filter(cls.station == station.id)
            .filter(cls.straw_location == straw_location.id)
            .one_or_none()
        )

        # If one is found, return it.
        if procedure is not None:
            return procedure

        # Otherwise, construct a new one.
        else:
            return cls(
                station=station,
                straw_location=straw_location,
                create_key=cls.__create_key,
            )

    """
    PanelProcedure
    (class method)

        Description:
            Get Procedure object from panel day and panel number.

        Outline:
            - Queries
    """

    @classmethod
    def PanelProcedure(cls, day, panel_number):
        from guis.common.db_classes.straw_location import StrawLocation
        from guis.common.db_classes.station import Station

        # Get Station
        station = Station.panelStation(day=day)

        # Get panel
        panel = StrawLocation.Panel(panel_number)

        # Use Procedure._startProcedure() to return object.
        return PanelProcedure._startProcedure(station=station, straw_location=panel)

    @staticmethod
    def _queryStation(station=None, production_stage=None, production_step=None):
        from guis.common.db_classes.station import Station

        assert (station is not None) or (
            production_stage is not None and production_step is not None
        ), "Unable to query Station. You must provide a station ID or both the production_stage and production_step of the desired station."

        if station:
            qry = Station.queryWithId(station)

        if production_stage and production_step:
            qry = Station.query().filter(
                and_(
                    Station.production_stage == production_stage,
                    Station.production_step == production_step,
                )
            )

        return qry.one_or_none()

    @orm.reconstructor
    def init_on_load(self):
        self._init_details()
        self.commit()

    ## PROPERTIES ##

    # Straw Location
    def getStrawLocation(self):
        from guis.common.db_classes.straw_location import StrawLocation

        return StrawLocation.queryWithId(self.straw_location)

    # Station
    def getStation(self):
        from guis.common.db_classes.station import Station

        return Station.queryWithId(self.station)

    # Elapsed Time
    def setElapsedTime(self, seconds):
        self.elapsed_time = seconds

    def getElapsedTime(self):
        return self.elapsed_time

    def lastTimestamp(self):
        return (
            ProcedureTimestamp.query()
            .filter(ProcedureTimestamp.procedure == self.id)
            .order_by(ProcedureTimestamp.timestamp.desc())
            .first()
        )

    def start(self):
        if self.lastTimestamp() is None:
            ProcedureTimestamp.start(self).commit()

    def pause(self):
        last = self.lastTimestamp()
        if last is not None and last.event.lower() in ["start", "resume"]:
            ProcedureTimestamp.pause(self).commit()

    def resume(self):
        last = self.lastTimestamp()
        if last is not None and last.event.lower() == "pause":
            ProcedureTimestamp.resume(self).commit()

    def stop(self):
        last = self.lastTimestamp()
        if last is not None and last.event.lower() in ["start", "resume"]:
            ProcedureTimestamp.stop(self).commit()

    ## DETAILS CLASS ##

    def _init_details(self):
        try:
            dc = self._getDetailsClass()
        except Exception:
            dc = None
        if dc is None:
            return
        # Query a details class having this procedure as its procedure.
        qry = dc.query().filter(dc.procedure == self.id)
        # Check if one exists
        if Query.exists(qry):
            # If one exists, set it to be this procedure's 'self.details'
            self.details = qry.one_or_none()
        else:
            # Otherwise, construct a new one
            self.details = dc(procedure=self.id)

    def _getDetailsClass(self):
        # TODO: If additional procedure data is recorded at this station,
        # have this function define a mapper class and return it
        return None

    def isNew(self):
        return self.new

    # OVERRIDING
    def commit(self):
        # Record current status to database
        entries = []
        entries.append(self)
        # Include details if they exist
        if self.details:
            entries.append(self.details)
        # Commit to database
        DM.commitEntries(entries)

    ## COMMENTS ##

    def comment(self, text):
        from guis.common.db_classes.comment_failure import Comment

        Comment(
            procedure=self.id, text=text, timestamp=int(datetime.now().timestamp())
        ).commit()

    def getComments(self):
        from guis.common.db_classes.comment_failure import Comment

        return self._queryComments().all()

    def _queryComments(self):
        from guis.common.db_classes.comment_failure import Comment

        return (
            Comment.query()
            .filter(Comment.procedure == self.id)
            .order_by(Comment.timestamp.desc())
        )


class ProcedureTimestamp(BASE, OBJECT):
    __tablename__ = "procedure_timestamp"
    id = Column(Integer, primary_key=True)
    procedure = Column(Integer, ForeignKey("procedure.id"))
    event = Column(VARCHAR)
    timestamp = Column(Integer)

    def __init__(self, procedure, event):
        self.id = self.ID()
        self.procedure = procedure
        self.event = event
        self.timestamp = int(time())

    def getEvent(self):
        return self.event

    @classmethod
    def start(cls, procedure):
        return cls(procedure=procedure.id, event="start")

    @classmethod
    def pause(cls, procedure):
        return cls(procedure=procedure.id, event="pause")

    @classmethod
    def resume(cls, procedure):
        return cls(procedure=procedure.id, event="resume")

    @classmethod
    def stop(cls, procedure):
        return cls(procedure=procedure.id, event="stop")


class PanelProcedure(Procedure):
    ## INITIALIZATION ##
    def __init__(self, station, straw_location, create_key):
        super().__init__(station, straw_location, create_key)

    ## PANEL ##
    def getPanel(self):
        return self.getStrawLocation()

    ## FAILURE ##
    def recordFailure(self, position, failure_type, failure_mode, comment):
        from guis.common.db_classes.comment_failure import Failure

        failure = Failure(
            procedure=self.id,
            position=position,
            failure_type=failure_type.strip().lower(),
            failure_mode=failure_mode,
            comment=comment,
        )
        failure.commit()
        return failure

    ## SESSION ##
    def getSession(self):
        return (
            Session.query()
            .filter(Session.active == True)
            .filter(Session.procedure == self.id)
            .one_or_none()
        )

    """
    executeStep
        Description:
            Record that the given step has been executed for this procedure.

        Input:
            step    (PanelStep) Step that is being executed.
    """

    def executeStep(self, step):
        from guis.common.db_classes.steps import PanelStepExecution

        # Record execution
        PanelStepExecution(panel_step=step.id, procedure=self.id).commit()

    def countStepsExecuted(self):
        from guis.common.db_classes.steps import PanelStepExecution

        return len(
            PanelStepExecution.query()
            .filter(PanelStepExecution.procedure == self.id)
            .group_by(PanelStepExecution.panel_step)
            .all()
        )

    """
    recordPanelTempMeasurement
        Description:
            Record up to 2 panel temperatures. Used for processes 1, 2, and 6.
            Process 1: PAAS-A only
            Process 2: PAAS-A and PAAS-B
            Process 6: PAAS-A and PAAS-C
            The table's second temp field does double duty as either no PAAS,
            PAAS-B, OR PAAS-C. Which it is can be inferred from the procedure.

    """

    def recordPanelTempMeasurement(self, temp_paas_a, temp_paas_bc):
        from guis.common.db_classes.measurements import PanelTempMeasurement

        PanelTempMeasurement(
            procedure=self, temp_paas_a=temp_paas_a, temp_paas_bc=temp_paas_bc
        ).commit()
