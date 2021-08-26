################################################################################
# STATION (AKA "PROCESS")
#
# Terminology/Concept Note:
#   Terminology and lab procedures have evolved such that this table no longer
#   represents a single concept. It conflates what we now call a "process" and
#   what we now call a "station" (a spot on the floor in a room), though the
#   latter usage is no longer very useful or common. The original idea must
#   have been that the same processes would always be performed in the same
#   spot in each room, so it was OK to combine them. But this no longer
#   reflects how the lab works; in large part due to covid where any given
#   process is performed is flexible across rooms and within a room.
#
# __tablename__ = "station"
#   id = Column(CHAR(4), primary_key=True) -- e.g. "pan3"
#   name = Column(VARCHAR(30)) -- e.g. "Panel Day 3"
#   room = Column(Integer, ForeignKey("room.id")) -- e.g. 3 --> "450_panel"
#   production_stage = Column(Integer, ForeignKey("production_stage.id")) -- e.g. "panel" (vs "straw" vs "qc")
#   production_step = Column(Integer) -- e.g. 3 (arbitrary number)
#
# The station table has 19 hard entries; 8 panel entries and 10 straw entries.
#
# A station is set as a part of an SQLDataProcessor. And (mixing up the station
# = process and the station = spot in a room terminologies) a Station instance
# can start Sessions and knows about active Sessions.
################################################################################
from guis.common.db_classes.bases import BASE, OBJECT, DM, logger
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
    id = Column(CHAR(4), primary_key=True)  # "pan3", "prep"
    name = Column(VARCHAR(30))  # "Panel Day 3", "Paper Pull"
    room = Column(Integer, ForeignKey("room.id"))
    production_stage = Column(
        Integer, ForeignKey("production_stage.id")
    )  # "panel", "straws"
    production_step = Column(
        Integer
    )  # integer based on the order that the steps AKA processes occur

    # classes that inherit from this one will only read/write rows in this
    # table that have the production stage equal to the "polymorphic_identity"
    # set by the class.
    __mapper_args__ = {"polymorphic_on": production_stage}

    # station = (stage + step)
    # In modern lingo: process = (panels/straws + process)
    # e.g. station pan3 or straw prep
    #
    # Make sure that the stage and step given are valid and return a
    # PanelStation or StrawStation object respectively.
    @staticmethod
    def get_station(stage, step):
        query = None
        try:
            query = {"panel": PanelStation.query(), "straws": StrawStation.query()}[
                stage
            ]
            return query.filter(Station.production_step == step).one_or_none()
        except KeyError:
            logger.error(
                "Invalid stage in Station query. Valid stages are 'panel' and 'straws'."
            )
        except sqlalchemy.exc.OperationalError:
            logger.error("DB Locked. Panel station query failed.")

    def startSession(self):
        from guis.common.db_classes.session import Session

        # Start new session and return
        return Session(self)

    def activeSessions(self):
        from guis.common.db_classes.session import Session

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


class StrawStation(Station):
    __mapper_args__ = {"polymorphic_identity": "straws"}


class Room(BASE, OBJECT):
    __tablename__ = "room"
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR)
