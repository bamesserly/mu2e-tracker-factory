"""
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
"""
