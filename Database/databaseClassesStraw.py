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
from sqlalchemy import Column, Integer, String, REAL, VARCHAR, ForeignKey, CHAR, BOOLEAN, and_, DATETIME, Table, TEXT, func
from sqlalchemy.types import DateTime
from sqlalchemy.sql.functions import now, localtime
from sqlalchemy.sql.expression import true, false
from sqlalchemy import orm
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from databaseManager import DatabaseManager
from datetime import datetime
from sys import modules
from inspect import isclass, getmembers
from datetime import datetime
from time import time

# GLOBAL VARIABLES #
DM = DatabaseManager()
BASE = declarative_base()

class AutoCommit:
    def commit(self):
        return DM.commitEntry(self)

class Barcode:
    @staticmethod
    def barcode(prefix,digits,n):
        return f"{prefix}{format(n,f'0{digits}')}"

class Query:
    @classmethod
    def query(cls):
        return DM.query(cls)

    '''
    __queryWithId
    (class method)

        Runs an query on its class and filters by id.

        Input:  id  (int)   PK of object to be queried
        Return: (Query) object to be manipulated further.
    '''
    @classmethod
    def __queryWithId(cls,id):
        return cls.query().filter(cls.id == id)

    '''
    queryWithId
    (class method)

        Returns result of query by id.

        Input:  id  (int)   PK of object to be queried
        Return: (instance of cls)/(None) if a database entry is (found)/(not found) in this table having the given id.
    '''
    @classmethod
    def queryWithId(cls,id):
        return cls.__queryWithId(id).one_or_none()

    '''
    existsWithId
    (class method)

        Runs an "exists" query on its class.

        Input:  id  (int)   PK of object to be queried
        Return: (bool) indicating whether a class object having the given id exists in the database.
    '''
    @classmethod
    def existsWithId(cls,id):
        return cls.exists(
            qry = cls.__queryWithId(id)
        )

    '''
    exists
    (static method)

        Runs the result of an "exists" query of the given query.

        Input:  qry (Query)   Query object.
        Return: (bool) indicating whether the given query found anything.
    '''
    @staticmethod
    def exists(qry):
        return DM.query(qry.exists()).scalar()

    '''
    queryCount
    (class method)

        Runs a query on this class that returns a count of the number of entries that match the 
        specifications, but not the mapped objects themselves
    '''
    @classmethod
    def queryCount(cls):
        return DM.query(func.count(cls.id))

ID_INCREMENT = 100

class ID:
    @staticmethod
    def ID(*args):
        return int(datetime.now().timestamp()*1e6)

    # Use this type of id for objects that will be created in fast-succession
    @staticmethod
    def IncrementID():
        global ID_INCREMENT
        ID_INCREMENT += 1
        return int(
            f"{int(datetime.now().timestamp()*1e4)}{'%03d' % ID_INCREMENT}"
        )

class Cast:
    def cast(self,new_class):
        self.__class__ = new_class

# OBJECT class pulls all other classes and methods together
class OBJECT(AutoCommit, Barcode, Query, ID, Cast):
    pass


### TABLES ###

class Comment(BASE, OBJECT):
    __tablename__ = "comment"
    id = Column(Integer, primary_key=True)
    procedure = Column(Integer, ForeignKey('procedure.id'))
    text = Column(TEXT)
    timestamp = Column(Integer, default=int(datetime.now().timestamp()))

    def __repr__(self):
        return f'Comment: procedure = {self.procedure}, text = {self.text}'

    def __init__(self,procedure,text):
        self.id = self.ID()
        self.procedure = procedure
        self.text = text

    @classmethod
    def queryByPanel(cls,panel_number):
        panel = Panel.query().filter(Panel.number == panel_number).one_or_none()

        return cls.query().\
            join(Procedure, cls.procedure == Procedure.id).\
            join(StrawLocation, Procedure.straw_location == StrawLocation.id).\
            filter(StrawLocation.id == panel.id).\
            order_by(Comment.timestamp.asc()).\
            all()
    
    @classmethod
    def queryByPallet(cls,pallet_number):
        pallet = Pallet.query().filter(Pallet.number==pallet_number).one_or_none()

        return cls.query().\
            join(Procedure, cls.procedure == Procedure.id).\
            join(StrawLocation, Procedure.straw_location == StrawLocation.id).\
            filter(StrawLocation.id == pallet.id).\
            order_by(Comment.timestamp.asc()).\
            all()

class Failure(BASE, OBJECT):
    # Table Columns
    __tablename__ = "failure"
    id = Column(Integer, primary_key=True)
    procedure = Column(Integer, ForeignKey('procedure.id'))
    position = Column(Integer)
    failure_type = Column(VARCHAR)
    failure_mode = Column(TEXT)
    comment = Column(TEXT, ForeignKey('comment.id'))

    # Failure Types
    pin     = 'pin'
    straw   = 'straw'
    anchor  = 'anchor'
    wire    = 'wire'

    def __init__(self,procedure,position,failure_type,failure_mode,comment):
        self.procedure = procedure
        self.position = position
        self.failure_type = failure_type
        self.failure_mode = failure_mode
        self.comment = self._recordComment(comment).id

    def _recordComment(self,text):
        comment = Comment(procedure=self.procedure,text=text)
        comment.commit()
        return comment

class PanelPart(BASE, OBJECT):
    __tablename__ = "panel_part"
    id = Column(Integer, primary_key=True)
    type = Column(Integer, ForeignKey('panel_part_type.id'))
    number = Column(Integer)
    left_right = Column(CHAR)
    letter = Column(CHAR)

    def __init__(self,type,number,left_right=None,letter=None):
        self.id = self.ID()
        self.type = type
        self.number = number
        self.left_right = left_right
        self.letter = letter

    def getPartType(self):
        return PanelPartType.queryWithId(id = self.type)
        
    def barcode(self):
        return self.getPartType().barcode(self.number)

    # Expands Query.query to filter by attributes rather than id.
    @classmethod
    def queryPart(cls,type,number=None,L_R=None,letter=None):
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

    def barcode(self,n):
        return Barcode.barcode(
            prefix  = self.barcode_prefix,
            digits  = self.barcode_digits,
            n       = n
        )

class PanelPartUse(BASE, OBJECT):
    __tablename__ = "panel_part_use"
    id = Column(Integer, primary_key=True)
    panel_part = Column(Integer, ForeignKey('panel_part.id'))
    panel = Column(Integer, ForeignKey('straw_location.id'))
    left_right = Column(CHAR)

    def __init__(self, panel_part, panel, left_right):
        self.panel_part = panel_part
        self.panel      = panel
        self.left_right = left_right

class PanelStep(BASE, OBJECT):
    __tablename__ = "panel_step"
    id = Column(Integer, primary_key=True)
    station = Column(Integer, ForeignKey('station.id'))
    name = Column(VARCHAR)
    text = Column(TEXT)
    checkbox = Column(BOOLEAN)
    picture = Column(VARCHAR)
    next = Column(Integer, ForeignKey('panel_step.id'))
    previous = Column(Integer, ForeignKey('panel_step.id'))
    parent_step = Column(Integer, ForeignKey('panel_step.id'))
    current = Column(BOOLEAN)

    def __repr__(self):
        return f"<PanelStep(station={self.station},name={self.name})>"

    def substeps(self):
        # Query first substep
        
        first_sub_step = self.querySubSteps().\
            filter(PanelStep.parent_step == self.id).\
            filter(PanelStep.previous == None).\
            one_or_none()
        # Append steps to list in order until there are no more.
        sub_steps = self.stepsList(first_sub_step)
        return sub_steps

    def nextStep(self):
        # Query the step who's id is 'self.next'
        return PanelStep.queryWithId(self.next)

    def previousStep(self):
        # Query the step who's id is 'self.previous'
        return PanelStep.queryWithId(self.previous)

    '''
    querySubSteps
    (classmethod)

        Queries steps that are sub steps (have a parent PanelStep)

        Output: (Query) query of substeps that can be manipulated further.
    '''
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
    panel_step = Column(Integer, ForeignKey('panel_step.id'))
    procedure = Column(Integer, ForeignKey('procedure.id'))

    def __init__(self,panel_step,procedure):
        self.id = self.IncrementID()
        self.panel_step = panel_step
        self.procedure = procedure

class Room(BASE, OBJECT):
    __tablename__ = "room"
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR)


### SESSION / PROCEDURE CLASSES ###

class Session(BASE, OBJECT):
    
    ## DATABASE INFORMATION ##
    __tablename__ = "session"
    id          =   Column(Integer, primary_key=True)
    station     =   Column(VARCHAR, ForeignKey('station.id'))
    procedure   =   Column(Integer, ForeignKey('procedure.id'))
    active      =   Column(BOOLEAN, default=true())

    ## SESSION VARIABLES ##
    _procedure = None # Defines with _setProcedure

    def __init__(self,station):
        self.id = self.ID()
            # Need to define id here so this object doesn't lose track of it's 
            # row when the database auto-generates an id.
        self.station = station.id
        self._station = station # Pointer to the Station object
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

    def _setProcedure(self,procedure):

        # Save object to private member variable
        self._procedure = procedure

        # Save ID to database column
        #### The line below failed
        self.procedure = procedure.id

        self.commit()
        # Commit change to database


    def startPanelProcedure(self,day,panel_number):
        assert(self.procedure is None), \
            "A procedure has already been defined for this session."
        self._setProcedure(
            Procedure.PanelProcedure(
                day             =   day,
                panel_number    =   panel_number
            )
        )

    def startStrawProcedure(self,stationID,palletID,pallet_number):
        assert(self.procedure is None), \
            "A procedure has already been defined for this session."

        self._setProcedure(
            Procedure.StrawProcedure(
                stationID      =   stationID,
                palletID       =   palletID,
                pallet_number  =   pallet_number
            )
        )
        

    ## WORKER PORTAL ##

    def login(self,worker_id):
        WorkerLogin(session = self.id,worker = worker_id).commit()

    def logout(self,worker_id):
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
        return Worker.query().\
            join(
                self._queryWorkerLogins().subquery()
            )

    def _queryWorkerLogins(self):
        return WorkerLogin.query().\
            filter(WorkerLogin.session == self.id).\
            filter(WorkerLogin.present == true())

class Procedure(BASE, OBJECT):
    # Create Key - Prevents public use of __init__
    __create_key = object()

    # Database Columns
    __tablename__   = "procedure"
    id              =   Column(Integer, primary_key=True)
    station         =   Column(CHAR(4), ForeignKey('station.id'))
    straw_location  =   Column(Integer, ForeignKey('straw_location.id'))
    elapsed_time    =   Column(Integer, default=0)
    timestamp       = Column(Integer, default=int(datetime.now().timestamp()))
    __mapper_args__ = {'polymorphic_on': station}

    # Instance Variables
    new             =   False
    details         =   None

    def __repr__(self):
        return f"<{self.__class__.__name__}(station={self.station}, straw_location={self.straw_location})>"


    ## INITIALIZATION ##
    '''
    __init__
        Description:
            Initialization method. This method is for internal use only. 

        Input: 
            station         (Station)       Station where this procedure is being conducted.
            straw_location  (StrawLocation) StrawLocation being operated on during this procedure.
            create_key      (Object)        Method only accepts the private Procedure.__create_key object, 
                                            thus it is only accessible within the class.
    '''
    def __init__(self,station,straw_location,create_key):

        # Enforce internal use only
        assert(create_key == Procedure.__create_key), \
            "You can only initialize a Procedure with PanelProcedure or StrawProcedure."

        # Save database values
        self.id = self.ID()
        self.station = station.id
        self.straw_location = straw_location.id


        # Record that this is a new Procedure (constructed, not queried)
        self.new = True
        # Commit to database, then run other load methods
        self.commit()
        self.init_on_load()

    @classmethod
    def _startProcedure(cls,station,straw_location):

        # Get furthest-derived class possible:
    
        # for c in cls.__subclasses__():
        #     if c.__mapper_args__['polymorphic_identity'] == station.id:
        #         cls = c
        #         break
        #  #Try to query a procedure that matches the given station and straw_location
        procedure = cls.query().\
            filter(cls.station==station.id).\
            filter(cls.straw_location==straw_location.id).\
            one_or_none()
        
        # If one is found, return it.
        if procedure is not None:
            return procedure
        
        # Otherwise, construct a new one.
        else:
            if station.id == "silv":
                return SilvProcedure(
                station         =   station,
                straw_location  =   straw_location,
                create_key      =   cls.__create_key            
            )
            elif station.id == "co2":
                return Co2Procedure(
                station         =   station,
                straw_location  =   straw_location,
                create_key      =   cls.__create_key            
            )
            else:
                print("normal cls") 
                return cls(
                station         =   station,
                straw_location  =   straw_location,
                create_key      =   cls.__create_key
            )

    '''
    PanelProcedure
    (class method)

        Description:
            Get Procedure object from panel day and panel number.

        Outline:
            - Queries
    '''
    @classmethod
    def PanelProcedure(cls,day,panel_number):
        # Get Station
        station = Station.panelStation(day=day)
        assert(station is not None), \
            f"Unable to find a panel station for day {day}."
        
        # Get panel
        panel = StrawLocation.Panel(panel_number)

        # Use Procedure._startProcedure() to return object.
        return PanelProcedure._startProcedure(
            station         =   station,
            straw_location  =   panel
        )
      
      ##### EDITS REQ
  
    @classmethod
    def StrawProcedure(cls,stationID,palletID,pallet_number):
        # Get Station
        station = Station.strawStation(stationID)
        assert(station is not None), \
            f"Unable to find a station for Straw GUI."
        
        # Get strawLocation
        pallet = StrawLocation.CPAL(pallet_number, palletID)

        return cls._startProcedure(
            station         =   station,
            straw_location  =   pallet
        )


    @staticmethod
    def _queryStation(station=None,production_stage=None,production_step=None):
        assert((station is not None) or (production_stage is not None and production_step is not None)), \
            "Unable to query Station. You must provide a station ID or both the production_stage and production_step of the desired station."
        
        if station:
            qry = Station.queryWithId(station)

        if production_stage and production_step:
            qry = Station.query().filter(
                and_(
                    Station.production_stage == production_stage,
                    Station.production_step  == production_step
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
        return StrawLocation.queryWithId(self.straw_location)

    # Station
    def getStation(self):
        return Station.queryWithId(self.station)

    # Elapsed Time
    def setElapsedTime(self,seconds):
        self.elapsed_time = seconds

    def getElapsedTime(self):
        return self.elapsed_time
    
    def lastTimestamp(self):
        return ProcedureTimestamp.query().\
            filter(ProcedureTimestamp.procedure == self.id).\
            order_by(ProcedureTimestamp.timestamp.desc()).\
            first()

    def start(self):
        if self.lastTimestamp() is None:
            ProcedureTimestamp.start(self).commit()
        
    def pause(self):
        last = self.lastTimestamp()
        if last is not None and last.event.lower() in ['start','resume']:
            ProcedureTimestamp.pause(self).commit()
        
    def resume(self):
        last = self.lastTimestamp()
        if last is not None and last.event.lower() == 'pause':
            ProcedureTimestamp.resume(self).commit()
        
    def stop(self):
        last = self.lastTimestamp()
        if last is not None and last.event.lower() in ['start','resume']:
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
            self.details = dc(procedure = self.id)
        print(self.details)

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
    
    def comment(self,text):
        Comment(procedure=self.id,text=text).commit()

    def getComments(self):
        return self._queryComments().all()
    
    def _queryComments(self):
        return Comment.query().\
            filter(Comment.procedure == self.id).\
            order_by(Comment.timestamp.desc())

class ProcedureTimestamp(BASE, OBJECT):
    __tablename__   =   "procedure_timestamp"
    id              =   Column(Integer, primary_key=True)
    procedure       =   Column(Integer, ForeignKey('procedure.id'))
    event           =   Column(VARCHAR)
    timestamp       =   Column(Integer)

    def __init__(self,procedure,event):
        self.id = self.ID()
        self.procedure = procedure
        self.event = event
        self.timestamp = int(time())

    def getEvent(self):
        return self.event

    @classmethod
    def start(cls,procedure):
        return cls(procedure=procedure.id,event='start')

    @classmethod
    def pause(cls,procedure):
        return cls(procedure=procedure.id,event='pause')

    @classmethod
    def resume(cls,procedure):
        return cls(procedure=procedure.id,event='resume')

    @classmethod
    def stop(cls,procedure):
        return cls(procedure=procedure.id,event='stop')

class PanelProcedure(Procedure):

    ## INITIALIZATION ##

    def __init__(self, station, straw_location, create_key):
        super().__init__(station, straw_location, create_key)

    ## PANEL ##

    def getPanel(self):
        return self.getStrawLocation()

    ## FAILURE ##

    def recordFailure(self,position,failure_type,failure_mode,comment):
        failure = Failure(
            procedure       =   self.id,
            position        =   position,
            failure_type    =   failure_type.strip().lower(),
            failure_mode    =   failure_mode,
            comment         =   comment
            )
        failure.commit()
        return failure

    ## SESSION ##
    def getSession(self):
        return Session.query().\
            filter(Session.active == True).\
            filter(Session.procedure == self.id).\
            one_or_none()

    '''
    executeStep
        Description:
            Record that the given step has been executed for this procedure.

        Input: 
            step    (PanelStep) Step that is being executed.
    '''
    def executeStep(self,step):
        # Record execution
        PanelStepExecution(panel_step=step.id,procedure=self.id).commit()

    def countStepsExecuted(self):
        return len(
            PanelStepExecution.query().\
            filter(PanelStepExecution.procedure == self.id).\
            group_by(PanelStepExecution.panel_step).\
            all()
        )

class StrawProcedure(Procedure):
  
    ## INITIALIZATION ##
    def __init__(self, station, straw_location, create_key):
        __mapper_args__ = {'polymorphic_identity': station.id}
        super().__init__(station, straw_location, create_key)
        

    ## PALLET ##
    def getStationID(self):
        return self.getStrawLocation()

    ## SESSION ##
    def getSession(self):
        return Session.query().\
            filter(Session.active == True).\
            filter(Session.procedure == self.id).\
            one_or_none()        

class Pan1Procedure(PanelProcedure):
    __mapper_args__ = {'polymorphic_identity': "pan1"}

    def __init__(self, station, straw_location, create_key):
        assert(station.id == 'pan1'), \
            f"Error. Tried to construct Pan1Procedure for a station '{station.id}' not 'pan1'."
        super().__init__(station, straw_location, create_key)

    def _getDetailsClass(self):
        class Details(BASE, OBJECT):
            __tablename__ = "procedure_details_pan1"
            id = Column(Integer, primary_key=True)
            procedure = Column(Integer, ForeignKey('procedure.id'))
            left_gap  = Column(Integer)
            right_gap = Column(Integer)
            min_BP_BIR_gap  = Column(Integer)
            max_BP_BIR_gap = Column(Integer)
            epoxy_batch  = Column(Integer)
            epoxy_time = Column(Integer)
            epoxy_time_running = Column(BOOLEAN)

        return Details
    
    def getLeftGap(self):
        return self.details.left_gap

    def recordLeftGap(self,gap):
        self.details.left_gap = gap
        self.commit()

    def getRightGap(self):
        return self.details.right_gap

    def recordRightGap(self,gap):
        self.details.right_gap = gap
        self.commit()
    
    def getMinBPBIRGap(self):
        return self.details.min_BP_BIR_gap

    def recordMinBPBIRGap(self,gap):
        self.details.min_BP_BIR_gap = gap
        self.commit()

    def getMaxBPBIRGap(self):
        return self.details.max_BP_BIR_gap

    def recordMaxBPBIRGap(self,gap):
        self.details.max_BP_BIR_gap = gap
        self.commit()

    def getEpoxyBatch(self):
        return self.details.epoxy_batch

    def recordEpoxyBatch(self,batch):
        self.details.epoxy_batch = batch
        self.commit()
    
    def getEpoxyTime(self):
        return self.details.epoxy_time

    def getEpoxyTimeRunning(self):
        return self.details.epoxy_time_running
    
    def recordEpoxyTime(self,duration,running):
        self.details.epoxy_time = duration
        self.details.epoxy_time_running = running
        self.commit()
    
class Pan2Procedure(PanelProcedure):
    __mapper_args__ = {'polymorphic_identity': "pan2"}

    def __init__(self, station, straw_location, create_key):
        assert(station.id == 'pan2'), \
            f"Error. Tried to construct Pan1Procedure for a station '{station.id}' not 'pan2'."
        super().__init__(station,straw_location,create_key)
    
    def _getDetailsClass(self):
        class Details(BASE, OBJECT):
            __tablename__ = "procedure_details_pan2"
            id                          = Column(Integer, primary_key =True)
            procedure                   = Column(Integer, ForeignKey('procedure.id'))
            lpal_top                    = Column(Integer, ForeignKey('straw_location.id'))
            lpal_bot                    = Column(Integer, ForeignKey('straw_location.id'))
            epoxy_batch_lower           = Column(Integer)
            epoxy_time_lower            = Column(Integer)
            epoxy_time_running_lower    = Column(BOOLEAN)
            epoxy_batch_upper           = Column(Integer)
            epoxy_time_upper            = Column(Integer)
            epoxy_time_running_upper    = Column(BOOLEAN)
            PAAS_A_max_temp             = Column(Integer)
            PAAS_B_max_temp             = Column(Integer)
            heat_time                   = Column(Integer)
            heat_time_running           = Column(BOOLEAN)
        
        return Details

    def _setLPAL(self,lpal,top_bot):
        if top_bot in ['top','bot']:
            if top_bot == 'top':
                self.details.lpal_top = lpal.id
            if top_bot == 'bot':
                self.details.lpal_bot = lpal.id
            self.commit()

    def loadFromLPAL(self,lpal_num,top_bot):
        # Query Objects
        lpal = StrawLocation.LPAL(lpal_num)
        straws = lpal.getStraws()
        panel = self.getPanel()
        # Equation mapping lpal straw list index to panel position
        position = lambda pos : 2*pos + {'top':1,'bot':0}[top_bot]
        # Execute all removes from lpal and moves to panel.
        entries = []
        for i in range(len(straws)):
            s = straws[i]
            if s is None:
                continue
            entries.append(lpal.removeStraw(s,commit=False))
            entries.append(
                panel.addStraw(
                    straw = s,
                    position = position(i),
                    commit = False
                )
            )
        DM.commitEntries(entries)
        # Record LPAL in details table aswell
        self._setLPAL(lpal,top_bot)

    def getLPAL(self,top_bot):
        # Get id from details class
        lpal_id = {
            'top'   :   self.details.lpal_top,
            'bot'   :   self.details.lpal_bot
        }[top_bot]
        # Return result of Query for Loading Pallet
        # Note, this will return None if no lpal
        # has been recorded yet.
        return LoadingPallet.queryWithId(lpal_id)

    def getEpoxyBatchLower(self):
        return self.details.epoxy_batch_lower
    
    def recordEpoxyBatchLower(self,batch):
        self.details.epoxy_batch_lower = batch
        self.commit()
    
    def getEpoxyTimeLower(self):
        return self.details.epoxy_time_lower

    def getEpoxyTimeRunningLower(self):
        return self.details.epoxy_time_running_lower

    def recordEpoxyTimeLower(self,duration,running):
        self.details.epoxy_time_lower = duration
        self.details.epoxy_time_running_lower = running
        self.commit()

    def getEpoxyBatchUpper(self):
        return self.details.epoxy_batch_upper
    
    def recordEpoxyBatchUpper(self,batch):
        self.details.epoxy_batch_upper = batch
        self.commit()
    
    def getEpoxyTimeUpper(self):
        return self.details.epoxy_time_upper

    def getEpoxyTimeRunningUpper(self):
        return self.details.epoxy_time_running_upper

    def recordEpoxyTimeUpper(self,duration,running):
        self.details.epoxy_time_upper = duration
        self.details.epoxy_time_running_upper = running
        self.commit()

    def getPaasAMaxTemp(self):
        return self.details.PAAS_A_max_temp

    def recordPaasAMaxTemp(self,temp):
        self.details.PAAS_A_max_temp = temp
        self.commit()

    def getPaasBMaxTemp(self):
        return self.details.PAAS_B_max_temp

    def recordPaasBMaxTemp(self,temp):
        self.details.PAAS_B_max_temp = temp
        self.commit()

    def getHeatTime(self):
        return self.details.heat_time

    def getHeatTimeRunning(self):
        return self.details.heat_time_running

    def recordHeatTime(self,time,running):
        self.details.heat_time = time
        self.details.heat_time_running = running
        self.commit()

    def recordStrawTension(self,position,tension,uncertainty):
        StrawTensionMeasurement(
            procedure   =   self,
            position    =   position,
            tension     =   tension,
            uncertainty =   uncertainty
        ).commit()

class Pan3Procedure(PanelProcedure):
    __mapper_args__ = {'polymorphic_identity': "pan3"}

    def __init__(self, station, straw_location, create_key):
        assert(station.id == 'pan3'), \
            f"Error. Tried to construct Pan1Procedure for a station '{station.id}' not 'pan3'."
        super().__init__(station, straw_location, create_key)
    
    def _getDetailsClass(self):
        class Details(BASE, OBJECT):
            __tablename__ = "procedure_details_pan3"
            procedure = Column(Integer, ForeignKey('procedure.id'), primary_key=True)
            sense_wire_insertion_time  = Column(REAL)
            sense_wire_insertion_time_running = Column(BOOLEAN)
            wire_spool = Column(Integer, ForeignKey('wire_spool.id'))
        
        return Details

    def getSenseWireInsertionTime(self):
        return self.details.sense_wire_insertion_time
    
    def getSenseWireInsertionTimeRunning(self):
        return self.details.sense_wire_insertion_time_running

    def recordSenseWireInsertionTime(self,duration,running):
        self.details.sense_wire_insertion_time = duration
        self.details.sense_wire_insertion_time_running = running
        self.commit()

    def getWireSpool(self):
        return WireSpool.queryWithId(self.details.wire_spool)

    def recordWireSpool(self,number):
        spool = DM.query(WireSpool).filter(WireSpool.id == number).one_or_none()
        if not spool:
            return False # Return false if wire spool can't be found in database
        self.details.wire_spool = spool.id
        return True

    # Continuity Measurements
    class MeasurementPan3(BASE, OBJECT):
        __tablename__ = "measurement_pan3"
        id = Column(Integer, primary_key=True)
        procedure = Column(Integer, ForeignKey('procedure.id'))
        position = Column(Integer)
        left_continuity = Column(BOOLEAN)
        right_continuity = Column(BOOLEAN)
        wire_position = Column(VARCHAR)

        def __init__(self,procedure, position, left_continuity, right_continuity, wire_position):
            self.id                 =   self.ID()
            self.procedure          =   procedure
            self.position           =   position
            self.left_continuity    =   left_continuity
            self.right_continuity   =   right_continuity
            self.wire_position      =   wire_position

        def __repr__(self):
            return "<MeasurementPan3(id='%s', procedure='%s', position='%s', left_continuity='%s', right_continuity='%s', wire_position='%s')>" % (
                self.id, self.procedure, self.position, self.left_continuity, self.right_continuity, self.wire_position)

        def isCompletelyDefined(self):
            data =  [self.procedure, self.position, self.left_continuity, self.right_continuity, self.wire_position]
            return all([x is not None for x in data])

        def recordLeftContinuity(self,boolean):
            self.left_continuity = boolean
        
        def recordRightContinuity(self,boolean):
            self.right_continuity = boolean

        def recordContinuity(self,left_continuity,right_continuity):
            self.recordLeftContinuity(left_continuity)
            self.recordRightContinuity(right_continuity)

        def recordWirePosition(self,position):
            self.wire_position = position

        def getPosition(self):
            return self.position

        def getLeftContinuity(self):
            return self.left_continuity
        
        def getRightContinuity(self):
            return self.right_continuity

        def getWirePosition(self):
            return self.wire_position

    def recordContinuityMeasurement(self,position,left_continuity,right_continuity,wire_position):
        
        # Check if a measurement has alread been made at this position
        meas = self._queryMeasurement(position).one_or_none()
        
        # If so, update continuity and resistance
        if meas:
            meas.recordContinuity(left_continuity,right_continuity)
            meas.recordWirePosition(wire_position)
        
        # If not, construct a new one with all data defined
        else:
            meas = Pan3Procedure.MeasurementPan3(
                procedure           =   self.id,
                position            =   position,
                left_continuity     =   left_continuity,
                right_continuity    =   right_continuity,
                wire_position       =   wire_position
            )
        
        # If all data is defined, commit (updated) measurement
        if meas.isCompletelyDefined():
            return meas.commit()
    
    def getContinuityMeasurements(self):
        measurements = self._queryMeasurements().all()
        lst = [None for _ in range(96)]
        for m in measurements:
            lst[m.position] = m
        return lst

    def getContinuityMeasurement(self,position):
        return self._queryMeasurement(position).one_or_none()

    def _queryMeasurement(self,position):
        return self._queryMeasurements().\
            filter(Pan3Procedure.MeasurementPan3.position == position)
    
    def _queryMeasurements(self):
        return Pan3Procedure.MeasurementPan3.query().\
            filter(Pan3Procedure.MeasurementPan3.procedure == self.id).\
            order_by(Pan3Procedure.MeasurementPan3.position.asc())

    # Wire Tensioner Measurements
    def recordWireTension(self,position,tension,wire_timer,calibration_factor):
        WireTensionMeasurement(
            procedure           =   self,
            position            =   position,
            tension             =   tension,
            wire_timer          =   wire_timer,
            calibration_factor  =   calibration_factor
        ).commit()

class Pan4Procedure(PanelProcedure):
    __mapper_args__ = {'polymorphic_identity': "pan4"}

    def __init__(self, station, straw_location, create_key):
        assert(station.id == 'pan4'), \
            f"Error. Tried to construct Pan1Procedure for a station '{station.id}' not 'pan4'."
        super().__init__(station, straw_location, create_key)
    
    def _getDetailsClass(self):
        class Details(BASE, OBJECT):
            __tablename__ = "procedure_details_pan4"
            procedure                       = Column(Integer, ForeignKey('procedure.id'), primary_key=True)
            baseplate_ribs_MIR_gap_left     = Column(Integer)
            baseplate_ribs_MIR_gap_right    = Column(Integer)
            base_plate_epoxy_batch          = Column(Integer)
            baseplate_installation_time     = Column(REAL)
            baseplate_installation_time_running = Column(BOOLEAN)
            frame_epoxy_batch_wetting       = Column(Integer)
            frame_epoxy_batch_bead          = Column(Integer)
            frame_installation_time         = Column(REAL)
            frame_installation_time_running = Column(BOOLEAN)
            PAAS_A_max_temp                 = Column(REAL)
            PAAS_C_max_temp                 = Column(REAL)
            heat_time                       = Column(Integer)
            heat_time_running               = Column(BOOLEAN)

        return Details

    def getBaseplateRibsMIRGapLeft(self):
        return self.details.baseplate_ribs_MIR_gap_left

    def recordBaseplateRibsMIRGapLeft(self,gap):
        self.details.baseplate_ribs_MIR_gap_left = gap
        self.commit()

    def getBaseplateRibsMIRGapRight(self):
        return self.details.baseplate_ribs_MIR_gap_right

    def recordBaseplateRibsMIRGapRight(self,gap):
        self.details.baseplate_ribs_MIR_gap_right = gap
        self.commit()

    def getBaseplateEpoxyBatch(self):
        return self.details.base_plate_epoxy_batch

    def recordBaseplateEpoxyBatch(self,batch):
        self.details.base_plate_epoxy_batch = batch
        self.commit()

    def getBaseplateInstallationTime(self):
        return self.details.baseplate_installation_time

    def getBaseplateInstallationTimeRunning(self):
        return self.details.baseplate_installation_time_running   

    def recordBaseplateInstallationTime(self,time,running):
        self.details.baseplate_installation_time = time
        self.details.baseplate_installation_time_running = running
        self.commit()

    def getFrameEpoxyBatchWetting(self):
        return self.details.frame_epoxy_batch_wetting
        
    def recordFrameEpoxyBatchWetting(self,batch):
        self.details.frame_epoxy_batch_wetting = batch
        self.commit()
        
    def getFrameEpoxyBatchBead(self):
        return self.details.frame_epoxy_batch_bead

    def recordFrameEpoxyBatchBead(self,batch):
        self.details.frame_epoxy_batch_bead = batch
        self.commit()

    def getFrameInstallationTime(self):
        return self.details.frame_installation_time

    def getFrameInstallationTimeRunning(self):
        return self.details.frame_installation_time_running           

    def recordFrameInstallationTime(self,time,running):
        self.details.frame_installation_time = time
        self.details.frame_installation_time_running = running
        self.commit()

    def getPaasAMaxTemp(self):
        return self.details.PAAS_A_max_temp

    def recordPaasAMaxTemp(self,temp):
        self.details.PAAS_A_max_temp = temp
        self.commit()

    def getPaasCMaxTemp(self):
        return self.details.PAAS_C_max_temp

    def recordPaasCMaxTemp(self,temp):
        self.details.PAAS_C_max_temp = temp
        self.commit()

    def getHeatTime(self):
        return self.details.heat_time

    def getHeatTimeRunning(self):
        return self.details.heat_time_running

    def recordHeatTime(self,time,running):
        self.details.heat_time = time
        self.details.heat_time_running =running
        self.commit()

class Pan5Procedure(PanelProcedure):
    __mapper_args__ = {'polymorphic_identity': "pan5"}

    def __init__(self, station, straw_location, create_key):
        assert(station.id == 'pan5'), \
            f"Error. Tried to construct Pan1Procedure for a station '{station.id}' not 'pan5'."
        super().__init__(station, straw_location, create_key)
    
    def _getDetailsClass(self):
        class Details(BASE, OBJECT):
            __tablename__ = "procedure_details_pan5"
            id                  = Column(Integer, primary_key=True)
            procedure           = Column(Integer, ForeignKey('procedure.id'))
            epoxy_batch_left    = Column(Integer)
            epoxy_time_left     = Column(Integer)
            epoxy_time_left_running = Column(BOOLEAN)
            epoxy_batch_right   = Column(Integer)
            epoxy_time_right    = Column(Integer)
            epoxy_time_right_running = Column(BOOLEAN)

        return Details

    def getEpoxyBatchLeft(self):
        return self.details.epoxy_batch_left

    def recordEpoxyBatchLeft(self,batch):
        self.details.epoxy_batch_left = batch
        self.commit()

    def getEpoxyTimeLeft(self):
        return self.details.epoxy_time_left

    def getEpoxyTimeLeftRunning(self):
        return self.details.epoxy_time_left_running

    def recordEpoxyTimeLeft(self,time,running):
        self.details.epoxy_time_left = time
        self.details.epoxy_time_left_running = running
        self.commit()

    def getEpoxyBatchRight(self):
        return self.details.epoxy_batch_right

    def recordEpoxyBatchRight(self,batch):
        self.details.epoxy_batch_right = batch
        self.commit()

    def getEpoxyTimeRight(self):
        return self.details.epoxy_time_right

    def getEpoxyTimeRightRunning(self):
        return self.details.epoxy_time_right_running

    def recordEpoxyTimeRight(self,time,running):
        self.details.epoxy_time_right = time
        self.details.epoxy_time_right_running = running
        self.commit()

class Co2Procedure(StrawProcedure):
    __mapper_args__ = {'polymorphic_identity': "co2"}

    def __init__(self, station, straw_location, create_key):
        assert(station.id == 'co2'), \
            f"Error. Tried to construct straw station for a station '{station.id}' not 'co2'."
        super().__init__(station, straw_location, create_key)

    def _getDetailsClass(self):
        class Details(BASE, OBJECT):
            __tablename__ = "procedure_details_co2"
            procedure = Column(Integer, ForeignKey('procedure.id'), primary_key=True)
            epoxy_batch  = Column(VARCHAR)
            epoxy_time = Column(REAL)
            dp190 = Column(VARCHAR)
        return Details
   
    def setEpoxyBatch(self,batch):
        self.details.epoxy_batch = batch
    
    def setEpoxyTime(self,duration):
        self.details.epoxy_time = duration
    
    def setDp190(self,dp190):
        self.details.dp190 = dp190
        self.commit()

class LasrProcedure(StrawProcedure):
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

class SilvProcedure(StrawProcedure):
    __mapper_args__ = {'polymorphic_identity': "silv"}
    
    def __init__(self, station, straw_location, create_key):
        assert(station.id == 'silv'), \
            f"Error. Tried to construct straw station for a station '{station.id}' not 'silv'."
        super().__init__(station, straw_location, create_key)
    
    def _getDetails(self):
        # Define details class
        class Details(BASE, OBJECT):
            __tablename__ = "procedure_details_silv"
            procedure = Column(Integer, ForeignKey('procedure.id'), primary_key=True)
            epoxy_batch  = Column(VARCHAR)
            epoxy_time = Column(REAL)
        return Details
        
    def setEpoxyBatch(self,batch):
        self.details.epoxy_batch = batch
    
    def setEpoxyTime(self,duration):
        self.details.epoxy_time = duration

###################################


### STATION #######################

class Station(BASE, OBJECT):
    __tablename__ = "station"
    id = Column(CHAR(4), primary_key = True)
    name = Column(VARCHAR(30))
    room = Column(Integer, ForeignKey('room.id'))
    production_stage = Column(Integer, ForeignKey('production_stage.id'))
    production_step  = Column(Integer)
    timestamp = Column(Integer)
    __mapper_args__ = {'polymorphic_on': production_stage}

    @staticmethod
    def panelStation(day):
        return PanelStation.query().\
            filter(PanelStation.production_step == day).\
            one_or_none()

    @staticmethod
    def strawStation(stationID):
        return StrawStation.query().\
            filter(StrawStation.id == stationID).\
            one_or_none()

    def startSession(self):
        # Start new session and return
        return Session(self)

    def activeSessions(self):
        return Session.query().filter(Session.active == True).all()

    def queryMoldReleaseItems(self):
        return MoldReleaseItems.query().\
            filter(MoldReleaseItems.station == self.id).\
            all()

class PanelStation(Station):
    __mapper_args__ = {'polymorphic_identity': 'panel'}

    def getSteps(self):
        # Get step 1
        s1 = DM.query(PanelStep).\
            filter(PanelStep.current == True).\
            filter(PanelStep.station == self.id).\
            filter(PanelStep.previous == None).\
            filter(PanelStep.parent_step == None).\
            one_or_none()
        # Generate steps list from step 1
        return PanelStep.stepsList(root_step=s1)

    def getDay(self):
        return self.production_step

class StrawStation(Station):
    __mapper_args__ = {'polymorphic_identity': 'straws'}

    def getStationID(self):
        return self.production_step

###################################


class Straw(BASE, OBJECT):

    __tablename__ = "straw"
    id = Column(Integer, primary_key=True)
    batch = Column(VARCHAR)
    parent = Column(Integer, ForeignKey('straw.id'))
    location = Column(Integer, ForeignKey('straw_location.id'))
    timestamp = Column(Integer, default=int(datetime.now().timestamp()))

    def __init__(self,id,batch,location,parent=None):
            
        self.id = id
        self.batch = batch
        self.location = location
        self.parent = parent
        self.commit()
    

        

    @classmethod
    # Master Straw Method
    def Straw(cls, id, batch, location, parent = None, position = None):

        # 1. Prep straws
        if parent is None:

            # Try to query the straw
            s = cls.queryWithId(id)

            # If None is found, construct straw
            if s is None:
                s = Straw(id,batch,location)
                sPosition = StrawPosition(s.id, location, position)
                StrawPresent(s.id, sPosition.id)
            else:
                print("This is an existing goood straw!")

        # 'recycle straws' and 'make a straw from another good straw'
        else:
            # get the position number of this straw
            pos = StrawPosition.queryWithId(id).position_number

            # know the parent straw is a recycled straw or a good straw
            parentPresent = StrawPresent.queryWithStraw(parent).present
            parentPosition = StrawPosition.queryWithID(parent).position_number
            
            # 2. Top position 
            # can be recycled by 'recycling straws' 
            # and 'make the top straw by cutting the second good straw' 
            if pos == 0:

                # Try to query the straw
                s = cls.queryWithId(id)
                
                # top straw is missed
                if s is None:
                    # strat to recycle a straw/make a straw
                    if ((parentPresent == True) and (parentPosition == 1)) or ((parentPresent == False) and (parentPosition == 99)):

                        # update old straw object(will represent a half straw or a recycled straw)
                        s.location = location
                        s.batch = batch
                        s.parent = parent
                        s.commit()
            
                        # update straw position object
                        positionObj = StrawPosition.queryWithId(s.id)
                        positionObj.position_number = position
                        positionObj.location = location
                        positionObj.commit()

                        # update straw present object
                        pallet = StrawLocation.queryWithId(location)
                        pallet.addStraw(s, position)

                    else:
                        print("Your parent straw is neither the second straw nor a recycled straw")

                
                else:
                    # top straw existed but failed
                    present = StrawPresent.queryWithStraw(s.id).present
                    if present == False:

                        # transfer the failed straw info
                        s.transfer()

                        if ((parentPresent == True) and (parentPosition == 1)) or ((parentPresent == False) and (parentPosition == 99)):

                            # update old straw object(will represent a half straw or a recycled straw)
                            s.location = location
                            s.batch = batch
                            s.parent = parent
                            s.commit()
            
                            # update straw position object
                            positionObj = StrawPosition.queryWithId(s.id)
                            positionObj.position_number = position
                            positionObj.location = location
                            positionObj.commit()

                            # update straw present object
                            pallet = StrawLocation.queryWithId(location)
                            pallet.addStraw(s, position)

                        else:
                            print("Your parent straw is neither the second straw nor a recycled straw")


                    else:
                        print("This is an existing goood straw!")

            
            # 3. Other positions
            # can only be recycled by 'recycling straws'
            else:

                # Try to query the straw
                s = cls.queryWithId(id)
                
                # This position is empty before
                if s is None:
                    # strat to recycle a straw
                    if ((parentPresent == False) and (parentPosition == 99)):

                        # update old straw object(will represent a half straw or a recycled straw)
                        s.location = location
                        s.batch = batch
                        s.parent = parent
                        s.commit()
            
                        # update straw position object
                        positionObj = StrawPosition.queryWithId(s.id)
                        positionObj.position_number = position
                        positionObj.location = location
                        positionObj.commit()

                        # update straw present object
                        pallet = StrawLocation.queryWithId(location)
                        pallet.addStraw(s, position)

                    else:
                        print("Your parent straw is not a recycled straw")
                 
                else:
                    # The earlier straw at this position was failed
                    present = StrawPresent.queryWithStraw(s.id).present
                    if present == False:

                        # transfer the old straw
                        s.transfer()

                        if (parentPresent == False) and (parentPosition == 99):
                            # update old straw object(will represent a half straw or a recycled straw)
                            s.location = location
                            s.batch = batch
                            s.parent = parent
                            s.commit()
            
                            # update straw position object
                            positionObj = StrawPosition.queryWithId(s.id)
                            positionObj.position_number = position
                            positionObj.location = location
                            positionObj.commit()

                            # update straw present object
                            pallet = StrawLocation.queryWithId(location)
                            pallet.addStraw(s, position)

                        else:
                            print("Your parent straw is neither the second straw nor a recycled straw")
 
                    else:
                        print("This is an existing goood straw!")

        # Return straw
        return s
    
    '''
    strpBarcode(cls,barcode)

        Description:    Class method that returns a straw object when given a straw barcode

        Input:          (str)   Straw barcode
        
        Return:         Straw object corresponding to given barcode
        
        Ex: 'ST12345' ==> Straw(id=12345)
    '''
    @classmethod
    def strpBarcode(cls,barcode):
        n = int(barcode[2:])
        return cls.Straw(n)

    def __repr__(self):
        return "<Straw(id='%s')>" % (self.id)

    def barcode(self):
        return Barcode.barcode("ST",5,self.id)

    ## VERIFICATION METHODS ##
    def passed(self,station):
        return self._queryVerification()[station]

    # Verify that straw has passed all previous stations
    def readyFor(self,station):
        stations = [s.name for s in self._queryStations().all()]
        previous_stations = stations[:stations.index(station)]
        return all([self.passed(s) for s in previous_stations])

    ## QUERY METHODS ##
    def _queryStations(self):
        DM.query(Station).\
        filter(Station.production_stage=="straws").\
        order_by(Station.production_step.asc())

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

        straw   =   Column(Integer, primary_key=True)
        prep    =   Column(Integer)
        ohms    =   Column(Integer)
        co2     =   Column(Integer)
        leak    =   Column(Integer)
        lasr    =   Column(Integer)
        silv    =   Column(Integer)
        leng    =   Column(Integer)

    # Returns a dictionary: key- station : value- (bool) indicating if straw passed that station
    def _queryVerification(self):
        data = DM.query(self._Verification).filter(self._Verification.straw == self.id).one_or_none()
        if not data:
            return None
        d = data.__dict__
        for k,v in d.items():
            d[k] = bool(v) # Convert 1,0 to True,False
        return d

    # Change straw.location & straw_position.location to trash.id;
    # Change straw_position.position_number to 99
    # Change straw_present.present to False
    def trashStraw(self):
        # Get the trash strawLocation
        #trash = StrawLocation._queryStrawLocation(0)

        # 1. Change the straw.location to trashID
        locationID = self.location # This is for step 3
        self.location = 1565033884299813
        self.commit()

        # 2. Change StrawPresent:: present: False;
        position = StrawPosition.queryWithId(self.id)
        pos = position.position_number
        pallet = StrawLocation.queryWithId(locationID) # Obtain a StrawLocation Object
        pallet.removeStraw(pos, strawID = self.id) # Remove straw_present
        
        ## Change strawPosition after setting strawPresent to false because
        ## the pallet query the strawPresent by strawLocation and position number
        # 3. Change StrawPosition:: location: trash.id; position number: 99
        position.location = 1565033884299813
        position.position_number = 99
        position.commit()
    
    # Transfer the info of an earlier failed straw to a fake straw
    def transfer(self):
        TstrawID = self.id + 35000
        Tbatch = self.batch
        Tlocation = self.location
        Tparent = self.id
        Tstraw = Straw(TstrawID, Tbatch, Tlocation, Tparent)
        Tposition= StrawPosition(Tstraw.id, Tlocation, 99)
        StrawPresent(Tstraw.id, Tposition.id, present=False)
        

### BEGIN STRAW LOCATION CLASSES ###

class StrawLocation(BASE, OBJECT):

    # Create Key - Prevents direct use of __init__
    __create_key = object()

    # Database Columns
    __tablename__ = "straw_location"
    id = Column(Integer, primary_key=True)
    location_type = Column(VARCHAR, ForeignKey('straw_location_type.id'))
    number = Column(Integer)
    pallet_id = Column(Integer)
    __mapper_args__ = {'polymorphic_on': location_type}

    # StrawLocation Information
    new = False


    ## INITIALIZATION ##

    def __init__(self,location_type=None,number=int(),pallet_id=None,create_key=None):

        # Check for authorization with 'create_key'
        assert(create_key == StrawLocation.__create_key), \
            "You can only obtain a StrawLocation with one of the following methods: panel(), cpal(), lpal()."

        # Database information
        self.id = self.ID()
        self.location_type = location_type
        self.number = (number if number else self.nextNumber())
        self.pallet_id = pallet_id
        # Record that this StrawLocation was recently made
        self.new = True

        # Commit to database
        self.commit()

        # Make new positions for this StrawLocation
        #self._makeNewPositions()

    '''
    _construct
    (class method)

        Description:
            This is the ultimate constructor for any StrawLocation class. Returns a queried 
            StrawLocation (or derivative) if a number is provided. 
            Otherwise, creates a new one (using the create_key).

        Input:
            number      (int)                       StrawLocation's number in the database (provide to query)
            new         (bool)                      Set to True if this is a new StrawLocation
            pallet_id   (int)                       Applicable to pallets (CuttingPallet and Loading Pallet) only.
                                                    This is the number on the pallets 'CPALID##' barcode.
        
        Output:
            An instance of 'cls' that is linked to an entry in the database.
    '''
    @classmethod
    def _construct(cls,type,number=int(),pallet_id=None):

        sl = None

        # Try to query the desired straw_location
        sl = cls._queryStrawLocation(number)

        # If None was found, make a new one.
        if sl is None:
            sl = cls(
                location_type =   type,
                number        =   number,
                pallet_id     =   pallet_id,
                create_key    =   cls.__create_key,
            )

        return sl


    ## CONSTRUCTORS ##
     
    @staticmethod
    def Panel(number):
        return Panel._construct(number)

    @staticmethod
    def CPAL(number=int(), pallet_id=None):
        return CuttingPallet._construct(
            type = 'CPAL',
            number        =   number,
            pallet_id     =   pallet_id
        )

    @staticmethod
    def LPAL(number=int(), pallet_id=None):
        return LoadingPallet._construct(
            number      =   number,
            pallet_id   =   pallet_id
        )


    ## PROPERTIES ##

    def getStraws(self):
        # Query Tuples of Straw Position ids and Straw objects
        qry  = DM.query(StrawPosition.id, Straw).\
            join(StrawPresent, StrawPresent.straw == Straw.id).\
            outerjoin(StrawPosition, StrawPosition.id == StrawPresent.position).\
            filter(StrawPosition.location == self.id).\
            filter(StrawPresent.present == True).\
            order_by(StrawPosition.position_number.asc()).\
            all()

        # Create a dictionary of this query {<position id> : <Straw>, ...}
        straw_position_dict = dict(qry)

        # Query straw position ids on this straw location ordered by position number            
        positions = DM.query(StrawPosition.id).filter(StrawPosition.location == self.id).order_by(StrawPosition.position_number.asc()).all()
        
        # Create a list of straws of equal length to the list of positions
        straws = [None]*len(positions)

        # Iterate through the list of positions and use the dictionary to populate the list of straws, leaving None objects wherever there is no Straw.
        for i, pos in enumerate([p[0] for p in positions]):
            try:
                straws[i] = straw_position_dict[pos]
            except KeyError:
                pass

        return straws
    
    def isEmpty(self):
        return not any(self.getStraws())

    def getLocationType(self):
        return StrawLocationType.queryWithId(self.location_type)

    def barcode(self):
        return self.getLocationType().barcode(self.number)

    def isNew(self):
        return self.new

    ## INSTANCE METHODS ##

    def getStrawAtPosition(self,position):
        return DM.query(Straw).\
            join(StrawPresent, StrawPresent.straw == Straw.id).\
            join(StrawPosition, StrawPresent.position == StrawPosition.id).\
            filter(StrawPosition.location == self.id).\
            filter(StrawPosition.position_number == position).\
            one_or_none()

    def getLikeLocations(self):
        return self.queryStrawLocations(self.__class__)
    
    #  Used when constructing new StrawLocations...
    
    # This method should eventually be re-created in SQL.
    def _makeNewPositions(self):
        # Make list of StrawPosition objects
        positions = []
        for i in self.getLocationType().positionRange():
            sp = StrawPosition(
                    location        =   self.id,
                    position_number =   i
                )
            sp.id += i
            positions.append(sp)
        # Commit to database
        return DM.commitEntries(positions)
    
    # ADD/REMOVE STRAWS

    def removeStraw(self,position,strawID=None,commit=True):
        # Query StrawPresent
        #print('position number is', position)
        #print('straw number is', strawID)
        qry = self._queryStrawPresents()

        # if strawID:
        #     qry = qry.filter(StrawPresent.straw == strawID)
        # elif position:
        #     qry = qry.filter(StrawPosition.position_number == position)
        #print(qry)
        obj = None 
        for instance in qry:
            #print(instance.straw)
            #print(instance.position)
            if instance.straw ==strawID:
                obj = instance
            elif instance.position == position:
                obj = instance    
        # straw_present = qry.one_or_none()
        # If there's not a straw there, return early
        #print(straw_present)
        # if straw_present is None:
        #     return
        # Record remove. Commit if requested
        obj.remove(commit)
        return obj 

    def addStraw(self,straw,position,commit=True):
        
        # Make sure there's not already a straw there
        straw_present = self._queryStrawPresents().\
            filter(StrawPresent.straw == straw.id).\
            one_or_none()
        if (straw_present is not None) and (straw_present.present == 1) :
            print("There's already a straw here")
            return
        

        # Query StrawPosition key
        position = self._queryStrawPositions().\
            filter(StrawPosition.position_number == position).\
            one_or_none()
        
        # There is no straw here
        qry = Straw.queryWithId(straw.id)
        if qry is None:
            straw_present = StrawPresent(
                straw    = straw.id,
                position = position.id, # straw_present.position = position.id
                present  = true()
            )
            
        # The straw is trashed
        else:
            straw_present = StrawPresent.query().\
                filter(StrawPresent.straw == straw.id).\
                one_or_none()
            straw_present.present = True
        
        if commit:
            straw_present.commit()
        
        return straw_present
    
    ### QUERY METHODS ###

    ## Instance Queries ##
    # These are queries that pertain only to a specific instance of StrawLocation.
    # However, they make use of public static methods.

    def _queryStrawPositions(self):
        return self.queryStrawPositions(self.id)

    def _queryStrawPresents(self):
        return self.queryStrawPresents(self.id)

    ## Straw Locations

    # Private

    @classmethod
    def _queryStrawLocation(cls,number):
        # Query a StrawLocation of the specified type with the given number.
        return cls.query().\
            filter(cls.number==number).\
            one_or_none()

    ## Straw Positions
    
    @staticmethod
    def queryStrawPositions(straw_location):
        return DM.query(StrawPosition).\
            filter(StrawPosition.location == straw_location).\
            order_by(StrawPosition.position_number)

    ## Straw Presents
    
    '''queryStrawPresents
    (public static method)

        Description:
            General Query of StrawPresent objects at the specified location.

        Input:
            straw_location (int) Database PK of desired StrawLocation.

        Output:
            (list) List of StrawPresent Objects
    '''
    @classmethod
    def queryStrawPresents(cls,straw_location):
        return StrawPresent.query().\
            join(cls.queryStrawPositions(straw_location).subquery()).\
            filter(StrawPresent.present == True)

    ## Other
    @classmethod
    def nextNumber(cls):
        n = DM.query(func.max(cls.number)).one()[0]
        if n is None:
            return 1
        else:
            return n + 1

class Panel(StrawLocation):
    __mapper_args__ = {'polymorphic_identity': 'MN'}

    def __init__(self, number = int(), pallet_id=None, create_key=None):
        super().__init__(
            location_type   =   'MN',
            number          =   number,
            pallet_id       =   None,    # This is always None, no matter the input.
            create_key      =   create_key
        )
        # Note, this method will only pass super().__init__() if called from StrawLocation.panel 
        # because otherwise it won't have the create key.

    def _recordPart(self,type,number,L_R=None,letter=None,on_L_R=None):
        # Query/Construct Part
        part = PanelPart.queryPart(type,number,L_R,letter).one_or_none()
        if not part:
            # If part doesn't exist, construct and commit it
            part = PanelPart(type,number,L_R,letter)
            part.commit()
        # Check if part has already been used on this panel
        use = PanelPartUse.query().\
            filter(PanelPartUse.panel_part == part.id).\
            filter(PanelPartUse.panel == self.id).\
            filter(PanelPartUse.left_right == on_L_R).\
            one_or_none()
        if use is None:
            # Record use in database
            PanelPartUse(
                    panel_part  = part.id,
                    panel       = self.id,
                    left_right  = on_L_R
                ).commit()

    def getBIR(self):
        return self._queryPartOnPanel('BIR').one_or_none()

    def recordBIR(self,number):
        self._recordPart("BIR",number)

    def getMIR(self):
        return self._queryPartOnPanel('MIR').one_or_none()

    def recordMIR(self,number):
        self._recordPart("MIR",number)

    def getPIR(self,L_R,letter):
        return self._queryPartOnPanel('PIR',L_R,letter).one_or_none()

    def recordPIR(self,number,L_R,letter):
        self._recordPart("PIR",number,L_R,letter)
    
    def getALF(self,L_R):
        return self._queryPartOnPanel('ALF',on_L_R=L_R).one_or_none()

    def recordALF(self,number,L_R):
        self._recordPart("ALF",number,on_L_R=L_R)

    def getBaseplate(self):
        return self._queryPartOnPanel('BASEPLATE').one_or_none()

    def recordBaseplate(self,number):
        self._recordPart("BASEPLATE",number)
    
    def getFrame(self):
        return self._queryPartOnPanel('FRAME').one_or_none()

    def recordFrame(self,number):
        self._recordPart("FRAME",number)

    def getMiddleRib1(self):
        return self._queryPartOnPanel('MIDDLERIB_1').one_or_none()

    def recordMiddleRib1(self,number):
        self._recordPart("MIDDLERIB_1",number)

    def getMiddleRib2(self):
        return self._queryPartOnPanel('MIDDLERIB_2').one_or_none()

    def recordMiddleRib2(self,number):
        self._recordPart("MIDDLERIB_2",number)

    ## QUERY METHODS ##

    def _queryPartOnPanel(self,type,L_R=None,letter=None,on_L_R=None):
        return PanelPart.queryPart(type=type,L_R=L_R,letter=letter).\
            join(PanelPartUse, PanelPartUse.panel_part == PanelPart.id).\
            filter(PanelPartUse.left_right == on_L_R).\
            filter(PanelPartUse.panel == self.id)

    @classmethod
    def queryByNumber(cls,number):
        return cls.query().filter(cls.number == number).one_or_none()
        
class Pallet(StrawLocation):
    def __init__(self,location_type=None,number=int(),pallet_id=None,create_key=None):
        #assert(self._palletIsEmpty(pallet_id)),\
        #    "Unable to start new pallet "
        super().__init__(location_type=location_type,number=number,pallet_id=pallet_id,create_key=create_key)

    @property
    def palletBarcode(self):
        return self.getLocationType().palletBarcode(self.pallet_id)

    @classmethod
    def _palletIsEmpty(cls,pallet_id):
        pallets = cls._queryPalletsByID(pallet_id).all()
        return all(p.isEmpty() for p in pallets)
    
    @classmethod
    def _queryPalletsByID(cls,pallet_id):
        return cls.query().filter(cls.pallet_id==pallet_id)

class LoadingPallet(Pallet):
    __mapper_args__ = {'polymorphic_identity': "LPAL"}
    
    def __init__(self,location_type=None,number=int(),pallet_id=None,create_key=None):
        super().__init__(location_type='LPAL',number=number,pallet_id=pallet_id,create_key=create_key)

class CuttingPallet(Pallet):
    __mapper_args__ = {'polymorphic_identity': "CPAL"}
    
    def __init__(self,location_type=None,number=int(),pallet_id=None,create_key=None):
        super().__init__(location_type='CPAL',number=number,pallet_id=pallet_id,create_key=create_key)

class StrawLocationType(BASE, OBJECT):
    __tablename__ = "straw_location_type"
    id                      = Column(VARCHAR(4,7), primary_key=True)
    name                    = Column(VARCHAR(25))
    barcode_digits          = Column(Integer)
    position_min            = Column(Integer)
    position_max            = Column(Integer)
    position_increment      = Column(Integer)
    pallet_barcode_prefix   = Column(VARCHAR)
    pallet_barcode_digits   = Column(Integer)
    timestamp               = Column(Integer)

    def __repr__(self):
        return "<StrawLocationType('%s')>" % (self.id)  

    def barcode(self,n):
        if self.barcode_digits is not None:
            return Barcode.barcode(self.id,self.barcode_digits,n)
        else:
            return None

    def palletBarcode(self,n):
        if self.pallet_barcode_prefix is not None and self.pallet_barcode_digits is not None:
            return Barcode.barcode(self.pallet_barcode_prefix,self.pallet_barcode_digits,n)
        else:
            return None

    def positionRange(self):
        return range(
            self.position_min,
            self.position_max + self.position_increment,
            self.position_increment
        )

class StrawPosition(BASE, OBJECT):
    __tablename__   = "straw_position"
    id              = Column(Integer,   ForeignKey('straw.id'), primary_key=True,)
    location        = Column(Integer, ForeignKey('straw_location.id'))
    position_number = Column(Integer)
    timestamp       = Column(Integer, default=int(datetime.now().timestamp()))

    # may need a check if the straw position is new
    def __init__(self,id,location,position_number):
        self.id = id
        self.location = location
        self.position_number = position_number

        # Commit to database
        self.commit()

    def __repr__(self):
        return "<StrawPosition(id='%s',location'%s',position_number='%s')>" % (self.id,self.location,self.position_number)  

class StrawPresent(BASE, OBJECT):
    __tablename__ = "straw_present"
    id = Column(Integer, primary_key=True)
    straw = Column(Integer, ForeignKey('straw.id'))
    position = Column(Integer, ForeignKey('straw_position.id'))
    present = Column(BOOLEAN)
    timestamp= Column(Integer, default=int(datetime.now().timestamp()))

    def __init__(self,straw,position,present=True):
        self.id = self.IncrementID()
        self.straw = straw
        self.position = position
        self.present = present
        self.commit()

    def __repr__(self):
        return "<StrawPresent(id='%s',straw'%s',position='%s')>" % (self.id,self.straw,self.position)  

    def remove(self,commit=True):
        self.present = false()
        if commit:
            self.commit()
    
    @classmethod
    def queryWithStraw(cls,straw):
        straw_present = StrawPresent.query().\
                filter(StrawPresent.straw == straw.id).\
                one_or_none()
        return straw_present

### END STRAW LOCATION CLASSES ###


### SUPPLIES, ITEMS, AND MOLD RELEASE ###

class Supplies(BASE, OBJECT):
    __tablename__ = "supplies"
    id          = Column(Integer, primary_key=True)
    station     = Column(CHAR(4), ForeignKey('station.id'))
    type        = Column(VARCHAR)
    name        = Column(VARCHAR)
    needed      = Column(BOOLEAN)

    def isNeeded(self):
        return self.needed

    def getName(self):
        return self.name

class SupplyChecked(BASE, OBJECT):
    __tablename__ = "supply_checked"
    id          = Column(Integer, primary_key=True)
    supply      = Column(Integer, ForeignKey('supplies.id'))
    session     = Column(Integer, ForeignKey('session.id'))
    checked     = Column(BOOLEAN)
    worker      = Column(VARCHAR(7,13), ForeignKey('worker.id'))
    timestamp   = Column(Integer)

    def checkPresent(self,boolean,worker=str()):
        self.worker = (worker if boolean else None)
        self.checked = boolean
        self.commit()

    def isPresent(self):
        return self.checked
    
    def getName(self):
        return self.getSupply().getName()

    ## returns supply object
    def getSupply(self):
        return Supplies.queryWithId(self.supply)


    def getWorker(self):
        return self.worker

    def getTimestamp(self):
        return self.timestamp

class MoldReleaseItems(BASE, OBJECT):
    __tablename__ = "mold_release_items"
    id              = Column(Integer, primary_key=True)
    station         = Column(CHAR(4), ForeignKey('station.id'))
    name            = Column(VARCHAR)
    needed          = Column(BOOLEAN)

    def isNeeded(self):
        return self.needed

    def getName(self):
        return self.name

class MoldReleaseItemsChecked(BASE, OBJECT):
    __tablename__ = "mold_release_items_checked"
    id          = Column(Integer, primary_key=True)
    mold_release_item = Column(Integer, ForeignKey('mold_release_items.id'))
    session     = Column(Integer, ForeignKey('session.id'))
    mold_released     = Column(BOOLEAN, default = false())
    worker      = Column(VARCHAR(7,13), ForeignKey('worker.id'))
    timestamp   = Column(Integer)

    def setMoldReleased(self,boolean,worker=str()):
        self.worker = (worker if boolean else None)
        self.mold_released = boolean
        self.commit()

    def getMoldRelease(self):
        return MoldReleaseItems.queryWithId(self.mold_release_item)

    def isMoldReleased(self):
        return self.mold_released

    def getName(self):
        return self.getMoldRelease().getName()

    def getWorker(self):
        return self.worker

    def getTimestamp(self):
        return self.timestamp

class TemperatureAndHumidity(BASE, OBJECT):
    __tablename__ = "temperatureand__humidity"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DATETIME)
    temperature = Column(REAL)
    humidity = Column(REAL)
    room = Column(Integer, ForeignKey('room.id'))

class WireSpool(BASE, OBJECT):
    __tablename__ = "wire_spool"
    id = Column(Integer, primary_key=True)
    qc = Column(BOOLEAN)

    def barcode(self):
        return f'WIRE.{self.id:06}'

### WORKERS ###

class Worker(BASE, OBJECT):
    __tablename__ = 'worker'
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)

    def certifiedStations(self):
        return [wc.station for wc in self._queryCertifiedStations().all()]

    # Returns boolean indicating if worker is certified to do the given station.
    def certified(self,station):
        return station.id in self.certifiedStations()

    def certify(self,station):
        if not self.certified(station):
            WorkerCertification(worker=self.id,station=station.id)
        
    def _queryCertifiedStations(self):
        return WorkerCertification.query().\
            filter(WorkerCertification.worker == self.id)
    
    def __repr__(self):
        return "<Worker(id='%s', first_name='%s', last_name='%s')>" % (
            self.id, self.first_name, self.last_name)

class WorkerCertification(BASE, OBJECT):
    __tablename__ = 'worker_certification'
    
    id = Column(Integer, primary_key=True)
    worker = Column(CHAR(7,13), ForeignKey('worker.id'))
    station = Column(CHAR(4), ForeignKey('station.id'))

    def __init__(self,worker,station):
        self.worker  = worker
        self.station = station

class WorkerLogin(BASE, OBJECT):
    __tablename__ = 'worker_login'
    
    id = Column(Integer, primary_key=True)
    session = Column(Integer, ForeignKey('session.id'))
    worker = Column(CHAR(7,13), ForeignKey('worker.id'))
    present = Column(BOOLEAN)

    def __init__(self,session,worker,present=true()):
        self.id = self.IncrementID()
        self.session = session
        self.worker = worker
        self.present = present

    def logout(self):
        self.present = false()
        return self.commit()


### MEASUREMENTS ################

'''PANEL MEASUREMENTS'''

class StrawTensionMeasurement(BASE, OBJECT):
    __tablename__ = 'measurement_straw_tension'
    id = Column(Integer, primary_key=True)
    procedure = Column(Integer, ForeignKey('procedure.id'))
    position = Column(Integer)
    tension = Column(REAL)
    uncertainty = Column(REAL)
    timestamp = Column(Integer, default=func.current_timestamp)

    def __init__(self,procedure,position,tension,uncertainty):
        self.procedure = procedure.id
        self.position = position
        self.tension = tension
        self.uncertainty = uncertainty

class WireTensionMeasurement(BASE, OBJECT):
    __tablename__ = 'measurement_wire_tension'
    id = Column(Integer, primary_key=True)
    procedure = Column(Integer, ForeignKey('procedure.id'))
    position = Column(Integer)
    tension = Column(REAL)
    wire_timer = Column(REAL)
    calibration_factor = Column(REAL)

    def __init__(self,procedure,position,tension,wire_timer,calibration_factor):
        self.procedure = procedure.id
        self.position = position
        self.tension = tension
        self.wire_timer = wire_timer
        self.calibration_factor = calibration_factor

class TensionboxMeasurement(BASE, OBJECT):
    __tablename__ = 'measurement_tensionbox'
    id = Column(Integer, primary_key=True)
    panel = Column(Integer, ForeignKey('straw_location.id'))
    straw_wire = Column(VARCHAR)
    position = Column(Integer)
    length = Column(REAL)
    frequency = Column(REAL)
    pulse_width = Column(REAL)
    tension = Column(REAL)

    def __init__(self,panel,straw_wire,position,length,frequency,pulse_width,tension):
        self.id             = self.ID()
        self.panel          = panel.id
        self.straw_wire     = straw_wire
        self.position       = position
        self.length         = length
        self.frequency      = frequency
        self.pulse_width    = pulse_width
        self.tension        = tension

'''STRAW LAB MEASUREMENTS'''

class StrawPrep(BASE, OBJECT):
    __tablename__ = 'measurement_prep'
    id = Column(Integer, primary_key=True)
    session = Column(Integer, ForeignKey('procedure.id'))
    straw = Column(Integer, ForeignKey('straw.id'))
    paper_pull_grade = Column(CHAR)
    evaluation = Column(BOOLEAN)
    timestamp= Column(Integer, default=int(datetime.now().timestamp()))
    
    def __init__(self, session, straw, paper_pull_grade, evaluation):
        self.session = session
        self.straw  = straw
        self.paper_pull_grade = paper_pull_grade
        self.evaluation = evaluation
        self.commit()
        
class Resistance(BASE, OBJECT):
    __tablename__ = 'measurement_ohms'
    id = Column(Integer, primary_key=True)
    procedure = Column(Integer, ForeignKey('procedure.id'))
    straw = Column(Integer, ForeignKey('straw.id'))
    inside_inside_resistance = Column(REAL)
    inside_inside_method = Column(String)
    inside_outside_resistance = Column(REAL)
    inside_outside_method = Column(String)
    outside_inside_resistance = Column(REAL)
    outside_inside_method = Column(String)
    outside_outside_resistance = Column(REAL)
    outside_outside_method = Column(String)
    evaluation = Column(BOOLEAN)
    timestamp= Column(Integer, default=int(datetime.now().timestamp()))

    def __init__(self, procedure, straw, inside_inside_resistance,inside_inside_method,inside_outside_resistance,inside_outside_method,outside_inside_resistance,\
         outside_inside_method, outside_outside_resistance, outside_outside_method, evaluation):
        self.procedure = procedure
        self.straw = straw
        self.inside_inside_resistance = inside_inside_resistance
        self.inside_inside_method = inside_inside_method
        self.inside_outside_resistance = inside_outside_resistance
        self.inside_outside_method = inside_outside_method
        self.outside_inside_resistance = outside_inside_resistance
        self.outside_inside_method = outside_inside_method
        self.outside_outside_resistance = outside_outside_resistance
        self.outside_outside_method = outside_outside_method
        self.evaluation = evaluation
        self.commit()
        
class CO2(BASE, OBJECT):
    __tablename__ = 'measurement_co2'
    id = Column(Integer, primary_key=True)
    session = Column(Integer, ForeignKey('session.id'))
    straw = Column(Integer, ForeignKey('straw.id'))
    co2_endpieces_installed = Column(BOOLEAN)
    timestamp= Column(Integer, default=int(datetime.now().timestamp()))

    def __init__(self, session, straw, co2_endpieces_installed):
        self.session = session
        self.straw = straw
        self.co2_endpieces_installed = co2_endpieces_installed
        self.commit()

class LeakTest(BASE, OBJECT):
    __tablename__ = 'measurement_leak'
    id = Column(Integer, primary_key=True)
    procedure = Column(Integer, ForeignKey('procedure.id'))
    straw = Column(Integer, ForeignKey('straw.id'))
    leak_rate = Column(REAL)
    uncertainty = Column(REAL)
    evaluation = Column(BOOLEAN)
    timestamp= Column(Integer, default=int(datetime.now().timestamp()))

    def _init_(self, procedure, straw, leak_rate, uncertainty, evaluation):
        self.procedure = procedure
        self.straw = straw
        self.leak_rate = leak_rate
        self.uncertainty = uncertainty
        self.evaluation = evaluation
        self.commit()

class LaserCut(BASE, OBJECT):
    __tablename__ = 'measurement_lasr'
    id = Column(Integer, primary_key=True)
    procedure = Column(Integer, ForeignKey('procedure.id'))
    straw = Column(Integer, ForeignKey('straw.id'))
    position = Column(Integer)
    timestamp= Column(Integer, default=int(datetime.now().timestamp()))

    def _init_(self, procedure, straw, position):
        self.procedure = procedure
        self.straw = straw
        self.position = position
        self.commit()

class SilverEpoxy(BASE, OBJECT):
    __tablename__ = 'measurement_silv'
    id = Column(Integer, primary_key=True)
    procedure = Column(Integer, ForeignKey('procedure.id'))
    straw = Column(Integer, ForeignKey('straw.id'))
    silv_endpieces_installed = Column(BOOLEAN)
    timestamp = Column(Integer)

    def _init_(self, procedure, straw, silv_endpieces_installed):
        self.procedure = procedure
        self.straw = straw
        self.silv_endpieces_installed = silv_endpieces_installed


def main():
    pass



if __name__ == "__main__":
    #main()
    pass