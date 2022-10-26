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
        #  some pro 8 data

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
            "pan8": -1
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
            "pan8": []
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
            "pan8": []
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
            # wire spool ids, and pro 3 before/after weight
            "wire_spool": -1,
            "wire_weight_initial": -1,
            "wire_weight_final": -1
        }

        # list of parts entered in pro 8
        self.qcParts = {
            "left_cover": -1,
            "right_cover": -1,
            "center_cover": -1,
            "left_ring": "",
            "right_ring": "",
            "center_ring": "",
            "stage": "",
            "leak_rate": ""
        }

        # list of leak rate submissions
        self.leaks = []

        # List of leak tests
        # List of tuples of the form:
        # (<tag name>, <elapsed time in days>, <timestamp>)
        self.leakTests = []

        # list of methane leak form submissions
        self.methane = []

        # list of bad wires/straws
        self.badWires = []
        self.badStraws = []

        # HV data: list of hv data where list index = straw
        # List of tuples of the form:
        # (<position>, <current>, <trip status>, <side>, <timestamp>)
        self.hv1100P3 = []
        self.hv1500P3 = []
        self.hv1500P4 = []
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

        self.p1HeatData = []
        self.p2HeatData = []
        self.p6HeatData = []

        self.hv1100P3 = []
        self.hv1500P3 = []
        self.hvXXXXP5 = []
        self.hv1500P6 = []

        self.p3tbData = []
        self.p6tbData = []

        self.strawData = []

        self.wireData = []

        self.leaks = []

        self.leakTests = []

        self.methane = []

        self.badWires = []
        self.badStraws = []

    # print ALL the data (for debugging)
    # indentation is gone due to multi-line string
    # add pro 8 stuff eventually
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

    Heat P1: {self.p1HeatData}

    Heat P2: {self.p2HeatData}

    Heat P6: {self.p6HeatData}
    
    HV P3 1.1kV: {self.hv1100P3}

    HV P3 1.5kV: {self.hv1500P3}

    HV P5 ???kV: {self.hvXXXXP5}

    HV P6 1.5kV: {self.hv1500P6}   

    TB P3: {self.p3tbData}

    TB P6: {self.p6tbData}
"""

