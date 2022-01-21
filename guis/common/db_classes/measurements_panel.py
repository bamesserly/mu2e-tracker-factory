################################################################################
# CHANNEL-BY-CHANNEL INFO/MEASUREMENTS, INFO/MEASUREMENTS THAT DON'T FIT IN
# PROCEDURE DETAILS
#
# Channel-by-channel measurements/info: wire and straw tensions, tensionbox
# measurements, bad channels.
#
# Measurements/info that don't fit in procedure details: panel temperature
# tracking during heating (many measurements as a function of time) and leak
# check forms (many forms submitted per process).
#
# Each table has a procedure id, linking it to a panel and process, though a
# procedure id shouldn't strictly be required.
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


class PanelTempMeasurement(BASE, OBJECT):
    __tablename__ = "panel_heat"
    id = Column(Integer, primary_key=True)
    procedure = Column(Integer, ForeignKey("procedure.id"))
    temp_paas_a = Column(REAL)
    temp_paas_bc = Column(REAL)

    def __init__(self, procedure, temp_paas_a, temp_paas_bc):
        self.id = self.ID()
        self.procedure = procedure.id
        self.temp_paas_a = temp_paas_a
        self.temp_paas_bc = temp_paas_bc


class StrawTensionMeasurement(BASE, OBJECT):
    __tablename__ = "measurement_straw_tension"
    id = Column(Integer, primary_key=True)
    procedure = Column(Integer, ForeignKey("procedure.id"))
    position = Column(Integer)
    tension = Column(REAL)
    uncertainty = Column(REAL)

    def __init__(self, procedure, position, tension, uncertainty):
        self.id = self.ID()
        self.procedure = procedure.id
        self.position = position
        self.tension = tension
        self.uncertainty = uncertainty


class WireTensionMeasurement(BASE, OBJECT):
    __tablename__ = "measurement_wire_tension"
    id = Column(Integer, primary_key=True)
    procedure = Column(Integer, ForeignKey("procedure.id"))
    position = Column(Integer)
    tension = Column(REAL)
    wire_timer = Column(REAL)
    calibration_factor = Column(REAL)

    def __init__(self, procedure, position, tension, wire_timer, calibration_factor):
        self.id = self.ID()
        self.procedure = procedure.id
        self.position = position
        self.tension = tension
        self.wire_timer = wire_timer
        self.calibration_factor = calibration_factor


class TensionboxMeasurement(BASE, OBJECT):
    __tablename__ = "measurement_tensionbox"
    id = Column(Integer, primary_key=True)
    procedure = Column(Integer, ForeignKey("procedure.id"))
    panel = Column(Integer, ForeignKey("straw_location.id"))
    straw_wire = Column(VARCHAR)
    position = Column(Integer)
    length = Column(REAL)
    frequency = Column(REAL)
    pulse_width = Column(REAL)
    tension = Column(REAL)

    def __init__(
        self,
        procedure,
        panel,
        straw_wire,
        position,
        length,
        frequency,
        pulse_width,
        tension,
    ):
        self.id = self.ID()
        self.procedure = procedure.id
        self.panel = panel.id
        self.straw_wire = straw_wire
        self.position = position
        self.length = length
        self.frequency = frequency
        self.pulse_width = pulse_width
        self.tension = tension


# High voltage current measurement.
# (originally associated specifically with the (deprecated) process 5, hence
# the unfortunately nonspecific name).
class MeasurementPan5(BASE, OBJECT):
    __tablename__ = "measurement_pan5"
    id = Column(Integer, primary_key=True)
    procedure = Column(Integer, ForeignKey("procedure.id"))
    position = Column(Integer)
    current_left = Column(REAL)
    current_right = Column(REAL)
    voltage = Column(REAL)
    is_tripped = Column(BOOLEAN)
    timestamp = Column(Integer)

    def __init__(
        self, procedure, position, current_left, current_right, voltage, is_tripped
    ):
        self.id = self.ID()
        self.procedure = procedure
        self.position = position
        self.current_left = current_left
        self.current_right = current_right
        self.voltage = voltage
        self.is_tripped = is_tripped
        self.timestamp = int(datetime.now().timestamp())


class BadWire(BASE, OBJECT):
    __tablename__ = "bad_wire_straw"

    id = Column(Integer, primary_key=True)
    position = Column(Integer)
    failure = Column(String)
    process = Column(Integer)
    procedure = Column(Integer)
    wire = Column(BOOLEAN)

    def __init__(self, position, failure, process, procedure, wire_check):
        self.id = self.ID()
        self.position = position
        self.failure = failure
        self.process = process
        self.procedure = procedure
        self.wire = wire_check

        self.commit()


class LeakFinalForm(BASE, OBJECT):
    __tablename__ = "leak_final_form"

    id = Column(Integer, primary_key=True)
    procedure = Column(Integer)
    cover_reinstalled = Column(String)
    inflated = Column(BOOLEAN)
    leak_location = Column(String)
    confidence = Column(String)
    leak_size = Column(Integer)
    resolution = Column(TEXT)
    next_step = Column(String)

    def __init__(
        self,
        procedure,
        cover_reinstalled,
        inflated,
        leak_location,
        confidence,
        leak_size,
        resolution,
        next_step,
    ):
        self.id = self.ID()
        self.procedure = procedure
        self.cover_reinstalled = cover_reinstalled
        self.inflated = inflated
        self.leak_location = leak_location
        self.confidence = confidence
        self.leak_size = leak_size
        self.resolution = resolution
        self.next_step = next_step

        self.commit()
