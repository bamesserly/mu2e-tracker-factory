
# Class to organize panel data in order to 
#   make storing/accesing data easier and
#   more consistent





class panelData():

    def __init__(self):
        
        # FIRST, init space for data!
        # Data we need:
        #   Panel human id
        #   Panel database id
        #   Procedure ids
        #   Procedure timing
        #   Comments
        #   HV measurements
        #   Heat measurements
        #   Straw and wire tension data
        #   Parts - Base plate, MIR, BIR,
        #           PIR L/R A/B/C, ALF 1/2,
        #           PAAS A/B/C
        
        # Human ID always an int between 1 and 999, inclusive
        self.humanID = -1

        # Database ID is a (up to) 16 digit int
        #   This is the straw_location id for the panel
        self.databaseID = -1

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
        self.comLists = {
            "pan1": [],
            "pan2": [],
            "pan3": [],
            "pan4": [],
            "pan5": [],
            "pan6": [],
            "pan7": [],
        }

        # HV data: list of hv data where list index = straw
        # List of tuples of the form: (<TODO>)
        self.hvData = []

        # Heat data: list of heat measurements by procedure
        # List of tuples of the form: (<TODO>)
        self.p1HeatData = []
        self.p2HeatData = []
        self.p6HeatData = []

        # Straw tension data: list of straw data where
        #   index = straw
        # List of tuples of the form: (<TODO>)
        self.strawData = []

        # Wire tension data: list of wire data where
        #   index = wire
        # List of tuples of the form: (<TODO>)
        self.wireData = []
        
        # Part IDs
        # Baseplate id
        self.partBP = -1
        # MIR id
        self.partMIR = -1
        # BIR id
        self.partBIR = -1
        # PIR ids --> PLA = PIR LA
        self.partPLA = -1
        self.partPLB = -1
        self.partPLC = -1
        self.partPRA = -1
        self.partPRB = -1
        self.partPRC = -1
        # ALF ids
        self.partALF1 = -1
        self.partALF2 = -1
        # PAAS ids
        self.partPaasA = -1
        self.partPaasB = -1
        self.partPaasC = -1

    # Clear all panel data (calls everyting in init)
    def clearPanel(self):
        self.humanID = -1
        self.databaseID = -1

        for key in self.proIDs:
            self.proIDs[key] = -1

        for key in self.timingLists:
            self.timingLists[key] = []
        
        for key in self.comLists:
            self.comLists[key] = []

        self.hvData = []

        self.p1HeatData = []
        self.p2HeatData = []
        self.p6HeatData = []

        self.strawData = []

        self.wireData = []

        self.partBP = -1
        self.partMIR = -1
        self.partBIR = -1
        self.partPLA = -1
        self.partPLB = -1
        self.partPLC = -1
        self.partPRA = -1
        self.partPRB = -1
        self.partPRC = -1
        self.partALF1 = -1
        self.partALF2 = -1
        self.partPaasA = -1
        self.partPaasB = -1
        self.partPaasC = -1

    
    # print ALL the data (for debugging)
    def __str__(self):
        return f'''PANEL: {self.humanID}
        '''