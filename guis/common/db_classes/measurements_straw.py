################################################################################
#
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
from datetime import datetime


"""
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
"""
