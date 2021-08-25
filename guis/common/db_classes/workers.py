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
from datetime import datetime


class Worker(BASE, OBJECT):
    __tablename__ = "worker"

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)

    def certifiedStations(self):
        return [wc.station for wc in self._queryCertifiedStations().all()]

    # Returns boolean indicating if worker is certified to do the given station.
    def certified(self, station):
        return station.id in self.certifiedStations()

    def certify(self, station):
        if not self.certified(station):
            WorkerCertification(worker=self.id, station=station.id)

    def _queryCertifiedStations(self):
        return WorkerCertification.query().filter(WorkerCertification.worker == self.id)

    def __repr__(self):
        return "<Worker(id='%s', first_name='%s', last_name='%s')>" % (
            self.id,
            self.first_name,
            self.last_name,
        )


class WorkerCertification(BASE, OBJECT):
    __tablename__ = "worker_certification"

    id = Column(Integer, primary_key=True)
    worker = Column(CHAR(7, 13), ForeignKey("worker.id"))
    station = Column(CHAR(4), ForeignKey("station.id"))

    def __init__(self, worker, station):
        self.worker = worker
        self.station = station


class WorkerLogin(BASE, OBJECT):
    __tablename__ = "worker_login"

    id = Column(Integer, primary_key=True)
    session = Column(Integer, ForeignKey("session.id"))
    worker = Column(CHAR(7, 13), ForeignKey("worker.id"))
    present = Column(BOOLEAN)

    def __init__(self, session, worker, present=true()):
        self.id = self.IncrementID()
        self.session = session
        self.worker = worker
        self.present = present

    def logout(self):
        self.present = false()
        return self.commit()
