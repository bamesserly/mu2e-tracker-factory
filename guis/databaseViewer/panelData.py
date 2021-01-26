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
            "FRAME": -1,
            "MIDDLERIB_1": -1,
            "MIDDLERIB_2": -1,
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
        return f"""PANEL: {self.humanID}
        """


"""
    # called upon hitting submit (does a lot of stuff)
    def findPanel(self):
        # What it does:
        # gets rid of data on the gui
        # changes the panel ID on the top of the gui
        # checks if the requested panel exists, if not gives error popup
        # finally calls all the functions that read data from the database
        #   which in turn call all the display functions (should a seperate
        #   thing call those maybe?)

        # first get rid of any existing data
        self.panelDatabaseID = -1  # reset panel database ID
        self.disableButtons() # disable buttons
        for widget in self.comListWidgetList:  # clear comments from list widgets
            widget.clear()
        for widget in self.partSetupWidgetList:  # erase all part IDs
            widget.setText("")
        for key in self.panelProcedureIDs:  # "rip up" the dictionary (keep keys of course)
            self.panelProcedureIDs[key] = -1
        # clear lists
        self.ui.hvListWidget.clear()  # clear text in widget
        self.hvData = []  # clear saved data
        self.ui.strawListWidget.clear()
        self.strawTensionData = []
        self.ui.wireListWidget.clear()
        self.wireTensionData = []

        # get new data and do stuff with it!
        self.panelNumber = self.ui.panelLE.text()  # get panel number from user input
        self.ui.label_2.setText(
            f"MN{str(self.panelNumber).zfill(3)}"
        )  # set label on top of gui (zfill because all panels have 3 numeric digits)
        self.findPanelDatabaseID()  # get the panels id in the straw_location table in the db
        if self.panelDatabaseID == -1:  # if the panel is not in the db
            tkinter.messagebox.showerror(  # show error message
                title="Error",  # name it 'Error'
                message=f"No data for MN{str(self.panelNumber).zfill(3)} was found.",  # give it this string for a message
            )       
            return  # return to avoid errors (if self.panelDatabaseID == -1)
        self.findProcedures()  # get procedure IDs (get data for self.panelProcedureIDs)
        self.findComments()  # get comments, put them into list widgets
        self.findPanelParts()  # get part IDs, put them into disabled line edit widgets
        self.findMeasurements()  # get measurements, put them into class member lists and display them
        self.findHeat() # get heat measurements
"""
