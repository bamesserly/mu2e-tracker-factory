from guis.common.db_classes.bases import BASE, OBJECT, Barcode
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


class PanelPart(BASE, OBJECT):
    __tablename__ = "panel_part"
    id = Column(Integer, primary_key=True)
    type = Column(Integer, ForeignKey("panel_part_type.id"))
    number = Column(Integer)
    left_right = Column(CHAR)
    letter = Column(CHAR)

    def __init__(self, type, number, left_right=None, letter=None):
        self.id = self.ID()
        self.type = type
        self.number = number
        self.left_right = left_right
        self.letter = letter

    def getPartType(self):
        return PanelPartType.queryWithId(id=self.type)

    def barcode(self):
        return self.getPartType().barcode(self.number)

    # Expands Query.query to filter by attributes rather than id.
    @classmethod
    def queryPart(cls, type, number=None, L_R=None, letter=None):
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

    def barcode(self, n):
        return Barcode.barcode(
            prefix=self.barcode_prefix, digits=self.barcode_digits, n=n
        )


class PanelPartUse(BASE, OBJECT):
    __tablename__ = "panel_part_use"
    id = Column(Integer, primary_key=True)
    panel_part = Column(Integer, ForeignKey("panel_part.id"))
    panel = Column(Integer, ForeignKey("straw_location.id"))
    left_right = Column(CHAR)

    def __init__(self, panel_part, panel, left_right):
        self.panel_part = panel_part
        self.panel = panel
        self.left_right = left_right
