# Class to organize panel data in order to
#   make storing/accesing data easier and
#   more consistent


class PanelData:
    def __init__(self):

        # FIRST, init space for data!
        # Data we need:
        #   Panel human id
        #   Panel database id
        #   Procedure ids
        #   Procedure timing
        #   Comments
        #   HV measurements
        #       pro 3 @ 1100V
        #       pro 3 @ 1500V
        #       pro 6 @ 1500V
        #   Heat measurements
        #   Straw and wire tension data
        #   Parts - Base plate, MIR, BIR,
        #           PIR L/R A/B/C, ALF 1/2,
        #           PAAS A/B/C

        # Human ID always an int between 1 and 999, inclusive
        self.humanID = -1

        # Database ID is a (up to) 16 digit int
        #   This is the straw_location id for the panel
        self.dbID = -1

        # Procedure IDs are ints up to 16 digits that all
        #   correspond to a certain procedure (1, 2, 3, etc)
        self.proIDs = {
            "pan1": -1,
            "pan2": -1,
            "pan3": -1,
            "pan4": -1,
            "pan5": -1,
            "pan6": -1,
            "pan7": -1,
        }

        # Pro timing lists: lists of start/stops for each procedure
        self.timingLists = {
            "pan1": [],
            "pan2": [],
            "pan3": [],
            "pan4": [],
            "pan5": [],
            "pan6": [],
            "pan7": [],
        }

        # Comment lists: lists of comments for each procedure
        # each comment is a tuple: (<text>, <timestamp in epoch time>)
        self.comLists = {
            "pan1": [],
            "pan2": [],
            "pan3": [],
            "pan4": [],
            "pan5": [],
            "pan6": [],
            "pan7": [],
        }

        # Parts list: dict of part ids
        self.parts = {
            # Baseplate id
            "BASEPLATE": -1,
            # MIR id
            "MIR": -1,
            # BIR id
            "BIR": -1,
            # PIR ids
            "PIRLA": -1,
            "PIRLB": -1,
            "PIRLC": -1,
            "PIRRA": -1,
            "PIRRB": -1,
            "PIRRC": -1,
            # ALF ids
            "ALFL": -1,  # 1 = Left
            "ALFR": -1,  # 2 = Right  ...?
            # PAAS ids
            "PAASA": -1,
            "PAASB": -1,
            "PAASC": -1,
            # frame id
            "FRAME": -1,
            # rib ids
            "MIDDLERIB_1": -1,
            "MIDDLERIB_2": -1,
            # loading pallet ids
            # lowercse because that's how it is in the database
            "lpal_bot_": -1,
            "lpal_top_": -1,
        }

        # HV data: list of hv data where list index = straw
        # List of tuples of the form:
        # (<position>, <current>, <trip status>, <side>, <timestamp>)
        self.hv1100P3 = []
        self.hv1500P3 = []
        self.hvXXXXP5 = []
        self.hv1500P6 = []

        # Heat data: list of heat measurements by procedure
        # List of tuples of the form:
        # (<human timestamp>, <epoch timestamp>, <PAAS A temp>, <PAAS B/C temp>)
        self.p1HeatData = []
        self.p2HeatData = []
        self.p6HeatData = []

        # Straw tension data: list of straw data where index = straw
        # List of tuples of the form:
        # (<position>, <tension>, <epoch timestamp>, <uncertainty>)
        self.strawData = []

        # Wire tension data: list of wire data where index = wire
        # List of tuples of the form:
        # (<position>, <tension>, <epoch timestamp>)
        self.wireData = []

    # Clear all panel data (calls everyting in init)
    # if dbOnly is true, then the human id will be preserved
    def clearPanel(self, dbOnly=False):
        if not dbOnly:
            self.humanID = -1
        
        self.databaseID = -1

        for key in self.proIDs:
            self.proIDs[key] = -1

        for key in self.timingLists:
            self.timingLists[key] = []

        for key in self.comLists:
            self.comLists[key] = []

        for key in self.parts:
            self.parts[key] = []

        self.hv1100P3 = []
        self.hv1500P3 = []
        self.hvXXXXP5 = []
        self.hv1500P6 = []

        self.p1HeatData = []
        self.p2HeatData = []
        self.p6HeatData = []

        self.strawData = []

        self.wireData = []

    # print ALL the data (for debugging)
    # indentation is gone due to multi-line string
    def __str__(self):
        return f"""
PANEL: {self.humanID}

    DB ID: {self.dbID}

    Pro IDs: {self.proIDs}

    Timing: {self.timingLists}

    Comments: {self.comLists}

    Parts: {self.parts}

    Straws: {self.strawData}

    Wires: {self.wireData}

    HV P3 1.1kV: {self.hv1100P3}

    HV P3 1.5kV: {self.hv1500P3}

    HV P5 ???kV: {self.hvXXXXP5}

    HV P6 1.5kV: {self.hv1500P6}

    Heat P1: {self.p1HeatData}

    Heat P2: {self.p2HeatData}

    Heat P6: {self.p6HeatData}
"""

