import sqlite3
from guis.common.databaseManager import DatabaseManager as DM

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
from datetime import datetime

from guis.common.db_classes.straw_location import StrawLocation
from guis.common.db_classes.measurements_panel import TensionboxMeasurement

def get_straw_tb(panel):
    panel_id=DM.query(StrawLocation).filter(StrawLocation.location_type == 'MN').filter(StrawLocation.number == str(panel[2:]))
    panel_id=panel_id[0].id

    straw_tb=DM.query(TensionboxMeasurement).filter(TensionboxMeasurement.panel == str(panel_id)).filter(TensionboxMeasurement.straw_wire == 'straw')
    straw_tb=straw_tb.all()
    for i in range(len(straw_tb)):
        straw_tb[i]=straw_tb[i].get_tensionbox_data()
    
    return straw_tb
    
    
def get_wire_tb(panel):
    panel_id=DM.query(StrawLocation).filter(StrawLocation.location_type == 'MN').filter(StrawLocation.number == str(panel[2:]))
    panel_id=panel_id[0].id

    wire_tb=DM.query(TensionboxMeasurement).filter(TensionboxMeasurement.panel == str(panel_id)).filter(TensionboxMeasurement.straw_wire == 'wire')
    wire_tb=wire_tb.all()
    for i in range(len(wire_tb)):
        wire_tb[i]=wire_tb[i].get_tensionbox_data()

    return wire_tb