from guis.common.databaseClasses import BASE, OBJECT
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


class Comment(BASE, OBJECT):
    __tablename__ = "comment"
    id = Column(Integer, primary_key=True)
    procedure = Column(Integer, ForeignKey("procedure.id"))
    text = Column(TEXT)
    timestamp = Column(Integer, default=int(datetime.now().timestamp()))

    def __repr__(self):
        return f"Comment: procedure = {self.procedure}, text = {self.text}"

    def __init__(self, procedure, text, timestamp=int(datetime.now().timestamp())):
        self.id = self.ID()
        self.procedure = procedure
        self.text = text
        self.timestamp = timestamp

    @classmethod
    def queryByPanel(cls, panel_number):
        from guis.common.databaseClasses import StrawLocation
        from guis.common.db_classes.procedure import Procedure

        # panel = Panel.query().filter(Panel.number == panel_number).one_or_none()

        # when was this code written? looks like a solution to MP
        panel = StrawLocation.Panel(panel_number)

        return (
            cls.query()
            .join(Procedure, cls.procedure == Procedure.id)
            .join(StrawLocation, Procedure.straw_location == StrawLocation.id)
            .filter(StrawLocation.id == panel.id)
            .order_by(Comment.timestamp.asc())
            .all()
        )


class Failure(BASE, OBJECT):
    # Table Columns
    __tablename__ = "failure"
    id = Column(Integer, primary_key=True)
    procedure = Column(Integer, ForeignKey("procedure.id"))
    position = Column(Integer)
    failure_type = Column(VARCHAR)
    failure_mode = Column(TEXT)
    comment = Column(TEXT, ForeignKey("comment.id"))

    # Failure Types
    pin = "pin"
    straw = "straw"
    anchor = "anchor"
    wire = "wire"

    def __init__(self, procedure, position, failure_type, failure_mode, comment):
        self.procedure = procedure
        self.position = position
        self.failure_type = failure_type
        self.failure_mode = failure_mode
        self.comment = self._recordComment(comment).id

    def _recordComment(self, text):
        comment = Comment(
            procedure=self.procedure,
            text=text,
            timestamp=int(datetime.now().timestamp()),
        )
        comment.commit()
        return comment
