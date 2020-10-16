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
        self.palletID = gui.palletID
        self.palletNum = gui.palletNum
        self.straws = gui.straws
        # Save directories as instance variables
        ## copied from the second constructor
        self.palletDirectory = os.path.dirname(__file__) + "/../../../Data/Pallets/"
        self.boardPath = os.path.dirname(__file__) + "/../../../Data/Status Board 464/"
        self.workerDirectory = (
            os.path.dirname(__file__)
            + "/../../../Data/workers/straw workers/CO2 endpiece insertion/"
        )
        self.epoxyDirectory = (
            os.path.dirname(__file__) + "/../../../Data/CO2 endpiece data/"
        )

    ### METHODS TO IMPLEMENT    ##############################################

    def saveData(self):
        if os.path.exists(
            self.palletDirectory + self.palletID + "\\" + self.palletNum + ".csv"
        ):
            with open(
                self.palletDirectory + self.palletID + "\\" + self.palletNum + ".csv",
                "a",
            ) as palletWrite:
                palletWrite.write("\n")
                palletWrite.write(datetime.now().strftime("%Y-%m-%d_%H:%M") + ",")
                palletWrite.write(self.gui.stationID + ",")

                for straw in self.gui.straws:
                    palletWrite.write(straw)
                    palletWrite.write(",")
                    if straw != "":
                        palletWrite.write("P")
                    palletWrite.write(",")
                i = 0
                for worker in self.sessionWorkers:
                    palletWrite.write(worker.lower())
                    if i != len(self.sessionWorkers) - 1:
                        palletWrite.write(",")
                    i = i + 1
        with open(self.epoxyDirectory + self.palletNum + ".csv", "w+") as file:
            header = "Timestamp, Pallet ID, Epoxy Batch #, DP190 Batch #, CO2 endpiece insertion time (H:M:S), workers ***NEWLINE: Comments (optional)***\n"
            file.write(header)
            file.write(datetime.now().strftime("%Y-%m-%d_%H:%M") + ",")
            file.write(
                self.palletID
                + ","
                + self.gui.epoxyBatch
                + ","
                + self.gui.DP190Batch
                + ","
            )
            file.write(
                str(self.gui.ui.hour_disp.intValue())
                + ":"
                + str(self.gui.ui.min_disp.intValue())
                + ":"
                + str(self.gui.ui.sec_disp.intValue())
                + ","
            )
            i = 0
            for worker in self.sessionWorkers:
                file.write(worker)
                if i != len(self.sessionWorkers) - 1:
                    file.write(",")
                i = i + 1
            if self.gui.ui.commentBox.document().toPlainText() != "":
                file.write("\n" + self.gui.ui.commentBox.document().toPlainText())

    ## WORKER PORTAL #####

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
        self.gui.stationID = "co2"
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
        self.callMethod(
            self.procedure.setEpoxyBatch, self.gui.epoxyBatch
        )  # Right Gap [mils]
        self.callMethod(
            self.procedure.setEpoxyTime, self.gui.getElapsedTime()
        )  # Min BP/BIR Gap [mils]
        self.callMethod(self.procedure.setDp190, self.gui.DP190Batch)
        # for i in range(len(self.gui.straws)):
        #     # print("starting now")
        #     if self.gui.straws[i] != "":
        #         straw = self.stripNumber(self.gui.straw[i])
        #         print(straw)
        #         CO2(self.procedure.id, straw, True)

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
            Number = self.gui.palletNum
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
