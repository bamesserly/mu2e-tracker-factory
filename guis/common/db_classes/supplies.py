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


class Supplies(BASE, OBJECT):
    __tablename__ = "supplies"
    id = Column(Integer, primary_key=True)
    station = Column(CHAR(4), ForeignKey("station.id"))
    type = Column(VARCHAR)
    name = Column(VARCHAR)
    needed = Column(BOOLEAN)

    def isNeeded(self):
        return self.needed

    def getName(self):
        return self.name


class SupplyChecked(BASE, OBJECT):
    __tablename__ = "supply_checked"
    id = Column(Integer, primary_key=True)
    supply = Column(Integer, ForeignKey("supplies.id"))
    session = Column(Integer, ForeignKey("session.id"))
    checked = Column(BOOLEAN)
    worker = Column(VARCHAR(7, 13), ForeignKey("worker.id"))
    timestamp = Column(Integer)

    def checkPresent(self, boolean, worker=str()):
        self.worker = worker if boolean else None
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
    id = Column(Integer, primary_key=True)
    station = Column(CHAR(4), ForeignKey("station.id"))
    name = Column(VARCHAR)
    needed = Column(BOOLEAN)

    def isNeeded(self):
        return self.needed

    def getName(self):
        return self.name


class MoldReleaseItemsChecked(BASE, OBJECT):
    __tablename__ = "mold_release_items_checked"
    id = Column(Integer, primary_key=True)
    mold_release_item = Column(Integer, ForeignKey("mold_release_items.id"))
    session = Column(Integer, ForeignKey("session.id"))
    mold_released = Column(BOOLEAN, default=false())
    worker = Column(VARCHAR(7, 13), ForeignKey("worker.id"))
    timestamp = Column(Integer)

    def setMoldReleased(self, boolean, worker=str()):
        self.id = self.ID()
        self.worker = worker if boolean else None
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
    room = Column(Integer, ForeignKey("room.id"))


class WireSpool(BASE, OBJECT):
    __tablename__ = "wire_spool"
    id = Column(Integer, primary_key=True)
    qc = Column(BOOLEAN)

    def barcode(self):
        return f"WIRE.{self.id:06}"
