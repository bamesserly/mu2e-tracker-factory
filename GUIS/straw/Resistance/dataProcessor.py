from abc import abstractmethod, ABC
from datetime import datetime, timedelta
import sys
from pathlib import Path
import numpy as np, os, csv, shutil, sys
from csv import DictReader, DictWriter

# from PrepGUI import sameBatch
sys.path.insert(
    0, str(Path(Path(__file__).resolve().parent.parent.parent.parent / "Data"))
)
from workers.credentials.credentials import Credentials

# Import DataProcessor for database access
sys.path.insert(
    0, str(Path(Path(__file__).resolve().parent.parent.parent.parent / "Database"))
)
from databaseClassesStraw import (
    Comment,
    Procedure,
    Station,
    Worker,
    DM,
    StrawPrep,
    Resistance,
    CO2,
    LeakTest,
    LaserCut,
    SilverEpoxy,
    StrawPresent,
    StrawPosition,
    StrawLocationType,
    CuttingPallet,
    LoadingPallet,
    Pallet,
    StrawLocation,
    Straw,
)


class DataProcessor(ABC):
    def __init__(self, gui):
        self.gui = gui

    ### METHODS TO IMPLEMENT    ##############################################

    """#USED
    saveData(self)

        Description: The generic save function that saves all data for a given day.

        Data Saved:
            - Day-specific data
            - Steps completed
            - Comments
    """

    @abstractmethod
    def saveData(self):
        pass

    """#USED
    validateWorkerID

        Description:    Determines whtether the given worker id is one that exists

        Input:  worker (str) A worker ID corresponding to someone who works for Mu2e.
    """

    @abstractmethod
    def validateWorkerID(self, worker):
        pass

    """#USED
    getSessionWorkers

        Description:    Returns a list of worker id's corresponding 
                        to the workers currently logged in.
    """

    @abstractmethod
    def getSessionWorkers(self):
        pass

    """#USED
    workerLoggedIn

        Description:    Determines if the given worker is logged in.

        Returns: (bool) is worker logged in?
    """

    @abstractmethod
    def workerLoggedIn(self, worker):
        pass

    """#USED
    checkCredentials(self)

        Description:    Determines if the workers currently logged in are certified to work at this station

        Return: boolean
    """

    @abstractmethod
    def checkCredentials(self):
        pass

    ## SAVE COMMENTS ##

    """#USED
    saveComment(self, text)

        Description: Record the given text as a comment.

        Parameter: text - The content of the comment.
    """
    # @abstractmethod
    # def saveComment(self,text):
    #     pass

    """#USED
    getCommentText(self)

        Description:    Returns all comments for the panel consolidated into 
                        one large string with timestamps and day headers.
    """
    # @abstractmethod
    # def getCommentText(self):
    #     pass

    ##########################################################################

    ### GETTERS ###
    # Gets variables from gui that are necessary for saving data properly

    def getDay(self):
        try:
            return self.gui.day
        except AttributeError:
            return None

    def getDayIndex(self):
        return self.gui.day_index

    def getData(self):
        return self.gui.data

    def getDayData(self):
        return self.getData()[self.getDayIndex()]

    def getStationID(self):
        return self.gui.stationID

    """
    getTimer

        Description: Gets elapsed timer of main timer in GUI.

        Returns: (timedelta)
    """

    def getTimer(self):
        return timedelta(seconds=self.gui.getElapsedTime())


class MultipleDataProcessor(DataProcessor):
    def __init__(self, gui, save2txt=True, save2SQL=True, sql_primary=True):
        self.gui = gui
        self.processors = []
        # Instantiate Data Processors
        txtdp = None
        sqldp = None
        if save2txt:
            txtdp = TxtDataProcessor(self.gui)
            self.processors.append(txtdp)
        if save2SQL:
            sqldp = SQLDataProcessor(self.gui)
            self.processors.append(sqldp)
        # Set primary
        if sql_primary:
            self.primaryDP = sqldp
        else:
            self.primaryDP = txtdp
        # Put all others in list
        self.otherDPs = [dp for dp in self.processors if dp != self.primaryDP]

    ## METHODS DONE BY ALL PROCESSORS ##

    def saveData(self):
        for dp in self.processors:
            dp.saveData()

    def saveWorkers(self):
        for dp in self.processors:
            dp.saveWorkers()

    ## METHODS DONE BY PRIMARY PROCESSOR ##

    def saveStart(self):
        self.primaryDP.saveStart()

    def savePause(self):
        self.primaryDP.savePause()

    def saveResume(self):
        self.primaryDP.saveResume()

    def saveFinish(self):
        self.primaryDP.saveFinish()

    def saveComment(self, text):
        self.primaryDP.saveComment(text)

    def handleClose(self):
        self.primaryDP.handleClose()

    def validateWorkerID(self, worker):
        return self.primaryDP.validateWorkerID(worker)

    def getSessionWorkers(self):
        return self.primaryDP.getSessionWorkers()

    def workerLoggedIn(self, worker):
        return self.primaryDP.workerLoggedIn(worker)

    def saveLogin(self, worker):
        self.primaryDP.saveLogin(worker)

    def saveLogout(self, worker):
        self.primaryDP.saveLogout(worker)

    def checkCredentials(self):
        return self.primaryDP.checkCredentials()

    def getCommentText(self):
        return self.primaryDP.getCommentText()

    def loadData(self):
        return self.primaryDP.loadData()


class TxtDataProcessor(DataProcessor):
    def __init__(self, gui):
        super().__init__(gui)
        self.credentialChecker = Credentials(self.gui.stationID)
        # self.sessionWorkers = []
        self.sessionWorkers = gui.sessionWorkers
        self.workerInformation = []
        self.validWorkers = []

        self.Current_workers = gui.Current_workers
        self.justLogOut = gui.justLogOut

        # Save directories as instance variables
        ## copied from the second constructor
        self.workerDirectory = (
            os.path.dirname(__file__)
            + "/../../../Data/workers/straw workers/resistance/"
        )
        self.palletDirectory = os.path.dirname(__file__) + "/../../../Data/Pallets/"
        self.boardPath = os.path.dirname(__file__) + "/../../../Data/Status Board 464/"

    ### METHODS TO IMPLEMENT    ##############################################

    def saveData(self):

        day = datetime.now().strftime("%Y-%m-%d_%H%M%S_")
        filename = (
            os.path.dirname(__file__)
            + "/../../../Data/Resistance Testing/Straw_Resistance_"
            + day
            + "_"
            + self.gui.first_strawID
            + "-"
            + self.gui.last_strawID
            + ".csv"
        )
        # Create new file on computer
        saveF = open(fileName, "a+")
        # Write self.saveFile to new file
        saveF.write(self.gui.saveFile)
        # Close new file. Save is complete.
        saveF.close()

        ## SAVE TO PALLET FILE ##
        ## This is a .txt file logging the history of each CPAL that all GUIs write to.
        for palletid in os.listdir(self.palletDirectory):
            for pallet in os.listdir(self.palletDirectory + palletid + "\\"):
                if self.gui.palletNumber + ".csv" == pallet:
                    self.gui.palletID = palletid
                    with open(
                        self.palletDirectory + palletid + "\\" + pallet, "a"
                    ) as file:
                        # Record Session Data
                        file.write(
                            "\n" + datetime.now().strftime("%Y-%m-%d_%H:%M") + ","
                        )  # Date
                        file.write(self.gui.stationID + ",")  # Test ID

                        # Record each straw and whether it passes/fails
                        for i in range(24):

                            straw = self.gui.strawIDs[i]
                            pass_fail = ""

                            # If straw doesn't exist
                            if straw == None:
                                straw = "_______"  # _ x7
                                pass_fail = "_"

                            # If straw exists, summarize all four booleans (1 fail --> straw fails)
                            else:
                                boolean = True
                                for j in range(4):
                                    if self.gui.bools[i][j] == False:
                                        boolean = False

                                if boolean:
                                    pass_fail = "P"
                                else:
                                    pass_fail = "F"

                            file.write(straw + "," + pass_fail + ",")

                        i = 0
                        for worker in self.sessionWorkers:
                            file.write(worker)
                            if i != len(self.sessionWorkers) - 1:
                                file.write(",")
                            i += 1
                    file.close()

    ## WORKER PORTAL ##

    """
    saveWorkers(self)
    
        Description: Saves workers logging in and out to a file, so the times a person was working on the panel can
                    be reviewed later if necessary.

        Parameter: worker - String containing the worker ID of the worker who just logged in or out
        Parameter: login - Boolean value specifying if the given worker logged in (True) or logged out (False)
    """

    def saveWorkers(self):
        previousWorkers = []
        activeWorkers = []
        exists = os.path.exists(
            self.workerDirectory + datetime.now().strftime("%Y-%m-%d") + ".csv"
        )
        if exists:
            with open(
                self.workerDirectory + datetime.now().strftime("%Y-%m-%d") + ".csv", "r"
            ) as previous:
                today = csv.reader(previous)
                for row in today:
                    previousWorkers = []
                    for worker in row:
                        previousWorkers.append(worker)
        for i in range(len(self.Current_workers)):
            if self.Current_workers[i].text() != "":
                activeWorkers.append(self.Current_workers[i].text())
        for prev in previousWorkers:
            already = False
            for act in activeWorkers:
                if prev == act:
                    already = True
            if not already:
                if prev != self.justLogOut:
                    activeWorkers.append(prev)
        with open(
            self.workerDirectory + datetime.now().strftime("%Y-%m-%d") + ".csv", "a+"
        ) as workers:
            if exists:
                workers.write("\n")
            if len(activeWorkers) == 0:
                workers.write(",")
            for i in range(len(activeWorkers)):
                workers.write(activeWorkers[i])
                if i != len(activeWorkers) - 1:
                    workers.write(",")

    def validateWorkerID(self, worker):
        if self.validWorkers == []:
            path = Path(self.paths["credentialsChecklist"])
            if path.exists():
                with path.open("r") as file:
                    reader = csv.reader(file)
                    next(reader)

                    for row in reader:
                        self.validWorkers.append(row[0].upper())
            else:
                print("Unable to read worker list")

        return worker.upper() in self.validWorkers

    def getSessionWorkers(self):
        return self.sessionWorkers

    def workerLoggedIn(self, worker):
        return any([worker.upper() in info for info in self.workerInformation])

    def checkCredentials(self):
        return self.credentialChecker.checkCredentials(self.sessionWorkers)

    ##########################################################################

    ### HELPER METHODS ###
    """
    filterDataForOutput(self, data)

        Description: Used to handle output of data. In order to prevent "None" from being written for data values
                    that have not been set yet, all "None" entries are filtered to empty strings. This is to provide
                    a cleaner output file, as well as to make input parsing easier.

        Parameter: data - The data list for the day that is being run

        Return: The same data list, with "None" entries replaced by empty strings
    """

    @staticmethod
    def filterDataForOutput(data):
        return ["" if x is None else x for x in data]

    """
    filterDataForInput(self, data)

        Description: Used to handle loading data from the data file. Takes all empty string entries and sets "None" in
                    their place.

        Parameter: data - The data list created from parsing the data file

        Return: The data list with empty string entries replaced by "None"
    """

    @staticmethod
    def filterDataForInput(data):
        return [None if x == "" else x for x in data]

    @staticmethod
    def str2Datetime(dt_str):
        ret = None

        # Try different potential formats...
        try:
            # Example: 2018-10-31_14:42
            ret = datetime.strptime(dt_str, "%Y-%m-%d_%H:%M")
        except ValueError:
            pass

        try:
            # Example: 2018-10-31 14:42
            ret = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        except ValueError:
            pass

        try:
            # Example: 10/31/18 9:57
            ret = datetime.strptime(dt_str, "%m/%d/%y %H:%M")
        except ValueError:
            pass

        # If none work, return None
        return ret

    @classmethod
    def datetimeList(cls, lst):
        return [cls.str2Datetime(dt) for dt in lst]

    @staticmethod
    def datetime2StrList(dt_list):
        return [
            (dt.strftime("%Y-%m-%d %H:%M") if dt is not None else str())
            for dt in dt_list
        ]

    @staticmethod
    def str2timedelta(dlta_str):
        t = [int(float(x)) for x in dlta_str.split(":")]
        return timedelta(hours=t[0], minutes=t[1], seconds=t[2])

    @staticmethod
    def timestamp():
        return datetime.now().strftime("%Y-%m-%d %H:%M")

    @staticmethod
    def timeTuple2str(td, isRunning):
        return ("*" if isRunning else "") + str(td)

    @classmethod
    def filterData(cls, input):
        if input == None:
            return ""
        elif type(input) is tuple:
            return cls.timeTuple2str(*input)
        else:
            return str(input)


class SQLDataProcessor(DataProcessor):
    def __init__(self, gui):
        super().__init__(gui)

        # Classes to interact with the database
        self.station = Station.strawStation(stationID=self.getStationID())
        self.session = self.station.startSession()
        self.procedure = None

    ### METHODS TO IMPLEMENT    ##############################################

    ## New GUI --> DATABASE
    """
    saveData(self)

        Description: Makes sure that the procedure exists, and calls saveStraw().
                     Creates a Straw Location(Pallet).
    """

    def saveData(self):
        # Ensure procedure - starts a procedure if doesn't exist
        if not self.ensureProcedure():
            return
        self.saveResistance()

    """
    saveResistance(self)

        Description: Save resistance test data for 23/24 instaces of straw
                     and logs data into ohms table
    """

    def saveResistance(self):
        for pos in range(24):
            strawID = self.gui.strawIDs[pos]
            if strawID:
                eval = True
                for pf in range(4):
                    if self.gui.saveData[pos][pf][1] == "fail":
                        eval = False

                Resistance(
                    procedure=self.procedure.id,
                    straw=self.stripNumber(strawID),
                    inside_inside_resistance=self.gui.saveData[pos][0][0],
                    inside_inside_method=self.gui.method[pos][0],
                    inside_outside_resistance=self.gui.saveData[pos][1][0],
                    inside_outside_method=self.gui.method[pos][1],
                    outside_inside_resistance=self.gui.saveData[pos][2][0],
                    outside_inside_method=self.gui.method[pos][2],
                    outside_outside_resistance=self.gui.saveData[pos][3][0],
                    outside_outside_method=self.gui.method[pos][3],
                    evaluation=eval,
                )

    def saveWorkers(self):
        pass

    ## TIME EVENTS ##

    def saveStart(self):
        if self.ensureProcedure():
            self.procedure.start()

    def savePause(self):
        if self.ensureProcedure():
            self.procedure.pause()
            self.saveProcedureDuration()
        # Stop working on procedure, but don't terminate session.
        # Allow the workers to remain logged in.

    def saveResume(self):
        if self.ensureProcedure():
            self.procedure.resume()

    def saveFinish(self):
        if self.ensureProcedure():
            self.saveProcedureDuration()

    def handleClose(self):
        self.session.terminate()
        DM.merge()

    ## WORKER PORTAL ##

    def saveLogin(self, worker):
        self.session.login(worker)

    def saveLogout(self, worker):
        self.session.logout(worker)

    def validateWorkerID(self, worker):
        return Worker.existsWithId(worker)

    def getSessionWorkers(self):
        return self.session.getWorkers()

    def workerLoggedIn(self, worker):
        return worker in self.getSessionWorkers()

    def checkCredentials(self):
        return self.session.checkCredentials()

    ## SAVE COMMENTS ##

    def saveComment(self, text):
        if not self.ensureProcedure():
            return
            # Comments
        if text != "":
            self.procedure.comment(text)

    def getCommentText(self):
        if not self.ensureProcedure():
            return

        # Query comments (ordered by timestamp)
        comments = Comment.queryByPallet(self.stripNumber(self.gui.palletNumber))

        # Assemble text
        text = ""
        current_day = 0
        for c in comments:
            day = Procedure.queryWithId(c.procedure).getStation().getDay()

            # Add day header
            if day > current_day:
                current_day = day
                header = f"Day {current_day} Comments"
                if current_day != 1:
                    header = "\n\n" + header
                text += header

            # Add timestamp header
            if not self.formatDatetime(c.timestamp) in text:
                text += f"\n\n{self.formatDatetime(c.timestamp)}"

            # Add comment text to string
            text += f"\n{c.text}"

        # Return total string
        return text

    ##########################################################################

    def ensureProcedure(self):

        # If no procedure has been defined yet, define one.
        if self.procedure is None:

            Number = self.gui.palletNumber
            Number = self.stripNumber(Number)
            ID = self.gui.palletID
            ID = self.stripNumber(ID)
            self.session.startStrawProcedure(
                stationID=self.getStationID(), palletID=ID, pallet_number=Number
            )
            self.procedure = self.session.getProcedure()
        # Return boolean indicating if 'self.procedure' is now defined.
        return self.procedure is not None

    def saveProcedureDuration(self):
        elapsed = self.getTimer().total_seconds()
        self.procedure.setElapsedTime(elapsed)

    @staticmethod
    def queryPanel(number):
        return Panel.queryByNumber(number)

    ## DATA PROCESSING ##

    # Saving
    @staticmethod
    def stripNumber(barcode):
        if barcode == "_______":
            return None

        elif barcode:
            # Iterate through barcode till you find a digit
            for i, b in enumerate(barcode):
                if b.isdigit():
                    break
            # Return remainder of string as integer
            return int(barcode[i:])
        else:
            return None

    # Loading

    @staticmethod
    def formatDatetime(dt):
        if isinstance(dt, int):
            dt = datetime.fromtimestamp(dt)
        return dt.strftime("%Y-%m-%d %H:%M")

    @staticmethod
    def epoxyBarcode(number):
        if number is not None:
            return f"EP{number:04}"
        else:
            return None

    # DB --> GUI
    @staticmethod
    def parseContinuityMeasurement(meas):

        continuity = None
        wire_pos = None

        if meas is not None:

            # Continuity
            continuity = {
                (None, None): None,
                (True, True): "Pass: No Continuity",
                (True, False): "Fail: Right Continuity",
                (False, True): "Fail: Left Continuity",
                (False, False): "Fail: Both Continuity",
            }[meas.left_continuity, meas.right_continuity]

            # Wire Position
            wire_pos = {
                None: None,
                "lower": "Lower 1/3",
                "middle": "Middle 1/3",
                "top": "Top 1/3",
            }[meas.wire_position]

        # Return data as list
        return continuity, wire_pos

    @staticmethod
    def getBarcode(obj):
        if obj is not None:
            return obj.barcode()
        else:
            return None

    @staticmethod
    def timeDelta(time, boolean):
        if time is not None and boolean is not None and (bool(time) or boolean):
            return timedelta(seconds=time), boolean
        else:
            return None

    @staticmethod
    def callMethod(method, *args):
        if any(a is not None for a in args):
            return method(*args)

    @staticmethod
    def parseTimeTuple(tpl):
        if tpl is not None and any(el for el in tpl):
            return (int(tpl[0].total_seconds()), tpl[1])
        else:
            return (None,)


def main():
    MultipleDataProcessor(object(), save2txt=True, save2SQL=True)


if __name__ == "__main__":
    main()
