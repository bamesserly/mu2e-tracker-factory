from abc import abstractmethod, ABC
from datetime import datetime, timedelta
from credentials import Credentials
from stepsList import Step
from pathlib import Path
import numpy as np, os, csv, shutil, sys
from csv import DictReader, DictWriter
import tkinter
from tkinter import messagebox

# Import DataProcessor for database access
sys.path.insert(
    0, str(Path(Path(__file__).resolve().parent.parent.parent.parent / "Database"))
)
from databaseClasses import (
    Comment,
    Procedure,
    Station,
    Worker,
    WireSpool,
    Panel,
    Supplies,
    PanelStep,
    SupplyChecked,
    DM,
    MoldReleaseItemsChecked,
    MoldReleaseItems,
    TensionboxMeasurement,
)

# MkI saves DB friendly CSV files
# MkII saves human friendly CSV files
# MkI can be on, but no data will be lost if it's off.
# MkII MUST BE ON for steps to be saved and loaded correctly
USE_MARK_ONE = True
USE_MARK_TWO = True

# this if statement gives a warning about the txt DP if both saving options are off
if not USE_MARK_ONE and not USE_MARK_TWO:
    root = tkinter.Tk()  # new tkinter window
    root.withdraw()  # hide tkinter main window
    # show warning (line below)
    messagebox.showwarning(
        "Warning", "The Text Processor is off.  No data will be saved in .txt format."
    )
    # raise Exception("NO TEXT PROCESSOR SELECTED")


class DataProcessor(ABC):
    def __init__(self, gui):
        self.gui = gui

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

    ## TIME EVENTS ##

    """#USED
    saveStart(self)

        Description: Record that the GUI was started (Start button was pushed).
    """

    @abstractmethod
    def saveStart(self):
        pass

    """#USED
    savePause(self)

        Description: Record that the GUI was paused.
    """

    @abstractmethod
    def savePause(self):
        pass

    """#USED
    saveResume(self)

        Description: Record that the GUI was resumed.
    """

    @abstractmethod
    def saveResume(self):
        pass

    """#USED
    saveFinish(self)

        Description: Record that the GUI was ended (closed).
    """

    @abstractmethod
    def saveFinish(self):
        pass

    """
    handleClose(self):

        Description:    Gives the Data Processor the opportunity to do any "housekeeping" before the gui closes
    """

    @abstractmethod
    def handleClose(self):
        pass

    ## WORKER PORTAL ##

    """#USED
    saveLogin(self,worker)

        Description:    Save that the given worker has been logged in.

        Input:  (str)   Worker id
    """

    @abstractmethod
    def saveLogin(self, worker):
        pass

    """#USED
    saveLogout(self,worker)

        Description:    Log out given worker.

        Input:  (str)   Worker id
    """

    @abstractmethod
    def saveLogout(self, worker):
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
        panNum - the panel being commented on
        proNum - the process being commented on
    """

    @abstractmethod
    def saveComment(self, text, panNum, proNum):
        pass

    """#USED
    getCommentText(self)

        Description:    Returns all comments for the panel consolidated into
                        one large string with timestamps and day headers.
    """

    @abstractmethod
    def getCommentText(self):
        pass

    ## OTHER SAVE METHODS (STEPS, SUPPLIES, FAILURES, ETC...) ##

    """#USED
    saveTPS(self)

        Description: Records that a Tool, Part, or Supply has been checked as (not) present.

        Input:
            - tps   (str)   must be in ['tools','parts','supplies']
            - item  (str)   name of the item being checked on/off
            - state (bool)  indicating whether item is being checked as present/not present
    """

    @abstractmethod
    def saveTPS(self, tps, item, state):
        pass

    """#USED
    saveMoldRelease(self,item,state)

        Description: Records that an item has been mold released (or not).

        Input:
            - item  (str)   name of the item being checked on/off
            - state (bool)  indicating whether item is being checked as mold released
    """

    @abstractmethod
    def saveMoldRelease(self, item, state):
        pass

    """#USED
    saveStep(self, step_name)

        Description: Record that the given step has been completed.

        Parameter: step_name (str) Name of step completed (Step.name when working with Step instance).
    """

    @abstractmethod
    def saveStep(self, step_name):
        pass

    """#USED
    saveFailure

        Description:    Saves the details of a reported failure

        Input:
            failure_type    (str)   in ['anchor','pin','straw','wire']
            failure_mode    (str)   describes nature of the failure.
            straw_position  (int)   0-95. Position on panel where failure occured.
            comment         (str)   Associated comment text to be saved as a comment.
    """

    @abstractmethod
    def saveFailure(self, failure_type, failure_mode, straw_position, comment):
        pass

    """#USED
    saveStrawTensionMeasurement

        Description:    Saves a straw tension measurement recorded with the straw tensioner device

        Input:
            position    (int)   Position of straw on panel
            tension     (float) Measured tension
            uncertainty (float) Uncertainty in measurement
    """

    @abstractmethod
    def saveStrawTensionMeasurement(self, position, tension, uncertainty):
        pass

    """#USED
    saveWireTensionMeasurement

        Description:    Saves a wire tension measurement recorded with the wire tensioner device

        Input:
            position     (int)   Position of wire on panel
            tension      (float) Measured tension
            wire_timer   (float) Recorded wire timer value
            calib_factor (float) Calibration factor used when making measurement
    """

    @abstractmethod
    def saveWireTensionMeasurement(self, position, tension, wire_timer, calib_factor):
        pass

    """#USED
    saveContinuityMeasurement

        Description:    Saves a continuity measurement of a wire.

        Input:
            position        (int)   Position of wire on panel

            continuity_str  (str)   Will be one of the following :
                ['Pass: No Continuity', 'Fail: Right Continuity', 'Fail: Left Continuity', 'Fail: Both Continuity']

            wire_position   (str)   Will be one of the following :
                ['Top 1/3', 'Middle 1/3', 'Lower 1/3']
    """

    @abstractmethod
    def saveContinuityMeasurement(self, position, continuity_str, wire_position):
        pass

    @abstractmethod
    def saveHVMeasurement(self, position, current_left, current_right, is_tripped):
        pass

    """
    saveTensionboxMeasurement(self,is_straw,position,length,frequency,pulse_width,tension)

        Description: Saves data from the Tensionbox popup in the GUI

        Input:
            panel       (str)   -   Panel ID ('MN###') of panel that this straw/wire is on.
            is_straw    (bool)  -   Indicates whether this measurement is for a straw or a wire. True => Straw, False => Wire
            position    (int)   -   Position of wire/straw on panel
            length      (float) -   Length of item being measured
            frequency   (float) -   Measured frequency
            pulse_width (float) -   Measured pulse_width
            tension     (float) -   Measured tension
    """

    @abstractmethod
    def saveTensionboxMeasurement(
        self, panel, is_straw, position, length, frequency, pulse_width, tension
    ):
        pass

    """#USED
    wireQCd(self,wire)

        Description:    Determines if the given wire has been QCd

        Input:  wire (str) wire barcode

        Return: boolean
    """

    @abstractmethod
    def wireQCd(self, wire):
        pass

    ## LOAD METHODS

    # TODO update this comment to reflect "days"-> "process"
    """#USED
    loadData

        Description:    Returns all data previously saved for this day
                            - day-specific data
                            - corresponding timestamps
                            - steps completed
                            (if day 3)
                            - continuity, wire position, resistance, and corresponding timestamps (if 6 more lists)

        Returns: List of lists
            [
            day data,
            data timestamps,
            elapsed_time, (integer, number of seconds)
            steps completed,
            continuity,
            continuity timestamp,
            wire position,
            wire position timestamp,
            resistance,
            resistance timestamp
            ]
    """

    @abstractmethod
    def loadData(self):
        pass

    """#USED
    loadTPS(self)

        Description:    Loads lists of Tools, Parts, and Supplies for this station.

        Output: 3 lists of lists (tools, parts, supplies)
            Each inner list is of length 4.
                1. (str)        item name
                2. (bool)       state - has this part been checked off or not?
                3. (str)        id of worker who checked it off (or '' if unchecked)
                4. (datetime)   datetime object corresponding to time when item when checked off
    """

    @abstractmethod
    def loadTPS(self):
        pass

    """#USED
    loadMoldRelease(self)

        Description:    Loads list of items to be mold released

        Output: list of lists (tools, parts, supplies)
            Each inner list is of length 4.
                1. (str)        item name
                2. (bool)       state - has this part been checked off or not?
                3. (str)        id of worker who checked it off (or '' if unchecked)
                4. (datetime)   datetime object corresponding to time when item when checked off
    """

    @abstractmethod
    def loadMoldRelease(self):
        pass

    """#USED
    loadSteps(self)

        Description:    Returns an ordered list of steps to be completed during this day.

        Return list(Step)
    """

    @abstractmethod
    def loadSteps(self):
        pass

    """
    loadContinuityMeasurements(self,position=None)

        Description:    Loads all or one of the continuity measurements (day 3).

        Input:  position (int)  Position of wire to load continuity for. If None, this
                                method should return all the continuity measurements for the panel.

        Returns:    Tuples of (continuity, wire_pos) for each measurement loaded.
    """

    @abstractmethod
    def loadContinuityMeasurements(self, position=None):
        pass

    """
    @abstractmethod
    def loadHVMeasurements(self,position=None):
        pass
    """

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

    def getPanel(self):
        return self.gui.getCurrentPanel()

    """
    getTimer

        Description: Gets elapsed timer of main timer in GUI.

        Returns: (timedelta)
    """

    def getTimer(self):
        return self.gui.mainTimer.getElapsedTime()


class MultipleDataProcessor(DataProcessor):
    def __init__(
        self, gui, save2txt=True, save2SQL=True, lab_version=True, sql_primary=True
    ):
        self.gui = gui
        self.processors = []
        # Instantiate Data Processors
        txtdp = None
        sqldp = None
        if save2txt:
            txtdp = TxtDataProcessor(self.gui, lab_version)
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

    def saveStart(self):
        for dp in self.processors:
            dp.saveStart()

    def savePause(self):
        for dp in self.processors:
            dp.savePause()

    def saveResume(self):
        for dp in self.processors:
            dp.saveResume()

    def saveFinish(self):
        for dp in self.processors:
            dp.saveFinish()

    def saveLogin(self, worker):
        for dp in self.processors:
            dp.saveLogin(worker)

    def saveLogout(self, worker):
        for dp in self.processors:
            dp.saveLogout(worker)

    def saveComment(self, text, panNum, proNum):
        for dp in self.processors:
            dp.saveComment(text, panNum, proNum)

    def saveStep(self, step_name):
        for dp in self.processors:
            dp.saveStep(step_name)

    def saveFailure(self, failure_type, failure_mode, straw_position, comment):
        for dp in self.processors:
            dp.saveFailure(failure_type, failure_mode, straw_position, comment)

    def saveStrawTensionMeasurement(self, position, tension, uncertainty):
        for dp in self.processors:
            dp.saveStrawTensionMeasurement(position, tension, uncertainty)

    def saveWireTensionMeasurement(self, position, tension, wire_timer, calib_factor):
        for dp in self.processors:
            dp.saveWireTensionMeasurement(position, tension, wire_timer, calib_factor)

    def saveContinuityMeasurement(self, position, continuity_str, wire_position):
        for dp in self.processors:
            dp.saveContinuityMeasurement(position, continuity_str, wire_position)

    def saveHVMeasurement(self, position, current_left, current_right, is_tripped):
        for dp in self.processors:
            dp.saveHVMeasurement(position, current_left, current_right, is_tripped)

    def saveTensionboxMeasurement(
        self, panel, is_straw, position, length, frequency, pulse_width, tension
    ):
        for dp in self.processors:
            dp.saveTensionboxMeasurement(
                panel, is_straw, position, length, frequency, pulse_width, tension
            )

    def handleClose(self):
        for dp in self.processors:
            dp.handleClose()

    ## METHODS DONE BY ALL, BUT RETURN RESULT FROM PRIMARY PROCESSOR ##

    def saveTPS(self, tps, item, state):
        for dp in self.otherDPs:
            dp.saveTPS(tps, item, state)
        return self.primaryDP.saveTPS(tps, item, state)

    def saveMoldRelease(self, item, state):
        for dp in self.otherDPs:
            dp.saveMoldRelease(item, state)
        return self.primaryDP.saveMoldRelease(item, state)

    ## METHODS DONE BY PRIMARY PROCESSOR ##

    def validateWorkerID(self, worker):
        return self.primaryDP.validateWorkerID(worker)

    def getSessionWorkers(self):
        return self.primaryDP.getSessionWorkers()

    def workerLoggedIn(self, worker):
        return self.primaryDP.workerLoggedIn(worker)

    def checkCredentials(self):
        return self.primaryDP.checkCredentials()

    def getCommentText(self):
        return self.primaryDP.getCommentText()

    def wireQCd(self, wire):
        return self.primaryDP.wireQCd(wire)

    def loadData(self):
        return self.primaryDP.loadData()

    def loadTPS(self):
        return self.primaryDP.loadTPS()

    def loadMoldRelease(self):
        return self.primaryDP.loadMoldRelease()

    def loadSteps(self):
        return self.primaryDP.loadSteps()

    def loadContinuityMeasurements(self, position=None):
        return self.primaryDP.loadContinuityMeasurements(position)

    def loadHVMeasurements(self, position=None):
        return self.primaryDP.loadHVMeasurements()


class TxtDataProcessor(DataProcessor):
    def __init__(self, gui, lab_version=True):
        super().__init__(gui)
        self._init_directories(lab_version)
        self.credentialChecker = Credentials(
            "pan" + str(self.getDay()), self.paths["credentialsChecklist"]
        )
        self.sessionWorkers = []
        self.workerInformation = []
        self.validWorkers = []

    def _init_directories(self, lab_version):

        # Get paths from file
        # TODO paths.txt is deprecated.
        path_files = {True: "paths-lab.txt", False: "paths.txt"}

        path_file = path_files[lab_version]
        path = (Path(__file__).parent / path_file).resolve()
        self.paths = dict(np.loadtxt(path, delimiter=",", dtype=str))

        current_dir = os.path.dirname(__file__)
        top_dir = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
        self.paths.update((k, top_dir + "/" + v) for k, v in self.paths.items()) # make paths absolute

        # Save directories as instance variables
        self.workerDirectory = Path(self.paths["workerDirectory"]).resolve()
        self.panelDirectory = Path(self.paths["panelDirectory"]).resolve()
        self.failDirectory = self.panelDirectory / "Failures"
        self.commentDirectory = self.panelDirectory / "Comments"
        self.listDirectory = Path(self.paths["listsDirectory"]).resolve()
        self.stepsDirectory = Path(self.paths["stepsDirectory"]).resolve()
        self.continuity_dataDirectory = Path(self.paths["continuity_data"]).resolve()
        self.wire_tensionerDirectory = Path(self.paths["wire_tensioner_data"]).resolve()
        self.strawTensionboxDirectory = Path(
            self.paths["tensionbox_data_straw"]
        ).resolve()
        self.wireTensionboxDirectory = Path(
            self.paths["tensionbox_data_wire"]
        ).resolve()
        self.straw_tensionerDirectory = Path(
            self.paths["straw_tensioner_data"]
        ).resolve()

    ### METHODS TO IMPLEMENT    ##############################################

    """
    saveData has two options for formats.  Whenever saveData is called, it'll
    make a decision on which save method to use.

    Setting the USE_MARK_ONE constant to true will make it save in the DB friendly CSV format,
    and setting it to false will make it save in the human friendly CSV format.
    """

    def saveData(self):
        if USE_MARK_TWO:
            self.saveDataMkII()  # save in user friendly CSV
        if USE_MARK_ONE:
            self.saveDataMkI()  # save in database friendly CSV

    def saveDataMkI(self):
        # what day/process?
        day = self.getDay()
        # get data from the gui to save
        data = self.getDayData()

        header = {
            1: self._day1header,
            2: self._day2header,
            3: self._day3header,
            4: self._pro4header,
            5: self._pro5header,
            6: self._day6header,
            7: self._day7header,
        }[self.getDay()]()

        # Count number of steps
        # loadRawSteps() returns a list of steps from the human
        # friendly text files.
        numSteps = 0
        for rawStep in self.loadRawSteps():
            if rawStep != "\n":
                numSteps += 1

        # if no file present, make a new one and give it a header
        # in the header, the first two items are ints
        # the first is number of variables to record, second is number of steps
        if not self.getPanelPathMkI().exists():
            with self.getPanelPathMkI().open("w") as file:
                for item in header[1:]:  # for each variable,
                    file.write(f"{item},")  # write it with a comma (no new line)
                file.write("Number of Steps completed,")
                file.write("Timestamp\n")

        # now to append data...
        # to do this we will make a new row to add to the file
        # row = var1,var2,var3,...    ...,timestamp
        row = ""
        for i in range(header[0]):  # for each piece of data
            if len(data) == 0:
                break
            if isinstance(data[i], tuple) and isinstance(
                data[i][0], timedelta
            ):  # is a timedelta tuple
                row += f"[{data[i][0]}|{data[i][1]}],"
            else:
                row += str(data[i])  # add it to the row
                row += ","  # and a comma to seperate cells in CSV

        row += str(numSteps)
        row += ","
        row += str(self.timestamp())
        row += "\n"

        if not row == "":
            with self.getPanelPathMkI().open("a") as file:
                file.write(row)

    def saveDataMkII(self):
        # what day/process?
        day = self.getDay()
        # get data to be saved
        data = self.getDayData()

        # each header function returns a list of the variables that need to be saved
        # in the same order they appear in the data list.  However, the headers begin
        # with an int that represents the number of variables that need to be saved.
        # This is more efficient than using len().  Due to the presance of the int at
        # the beginning of the header list, when writing it with data, the corresponding
        # index in header will be one higher than in data.
        header = {
            1: self._day1header,
            2: self._day2header,
            3: self._day3header,
            4: self._pro4header,
            5: self._pro5header,
            6: self._day6header,
            7: self._day7header,
        }[self.getDay()]()

        # steps are automatically saved periodically while gui is running
        # We will collect them now, and write later.
        steps = [line.strip() for line in self.loadRawSteps() if line != "\n"]

        # open file to write to
        with self.getPanelPath().open("w") as file:
            # write timestamp
            file.write("Timestamp," + self.timestamp() + "\n")

            # in f'{header[i+1]},{data[i]}\n' header[i+1] is the variable name
            # and data[i] is the value for that variable
            # The if statement checks if the data is a timedelta with a boolean
            # for timer running status.  Writing both in the tuple is a bit more
            # difficult to read.
            for i in range(
                header[0]
            ):  # header[0] is an int that equals the number of variables to be recorded
                if len(data) == 0:
                    break
                if isinstance(data[i], tuple) and isinstance(
                    data[i][0], timedelta
                ):  # is a timedelta tuple
                    file.write(
                        f"{header[i+1]},{data[i][0]},{data[i][1]},{self.timestamp()}\n"
                    )  # write '<variable name>,<time>,<running status (t/f)>,<timestamp>\n'
                else:
                    file.write(
                        f"{header[i+1]},{data[i]},{self.timestamp()}\n"
                    )  # write '<variable name>,<variable data>,<timestamp>\n'

            # write steps last
            file.write("\n\nSteps:\n")
            if any(steps):
                file.write(
                    "\n".join(steps)
                )  # go two lines down, write Steps:, then go another line down and write the list of steps

    ## TIME EVENTS ##

    def saveStart(self):
        self.saveStep(step_name=f"Day {self.getDay()} Start")

    def savePause(self):
        self.saveStep(step_name=f"Day {self.getDay()} Paused")

    def saveResume(self):
        self.saveStep(step_name=f"Day {self.getDay()} Resumed")

    def saveFinish(self):
        self.saveStep(step_name=f"Day {self.getDay()} Finished")

    def handleClose(self):
        pass

    ## WORKER PORTAL ##

    """
    saveWorkers(self)

        Description: Saves workers logging in and out to a file, so the times a person was working on the panel can
                    be reviewed later if necessary.

        Parameter: worker - String containing the worker ID of the worker who just logged in or out
        Parameter: login - Boolean value specifying if the given worker logged in (True) or logged out (False)
    """

    def saveWorkers(self, worker, login):
        path = Path(self.paths["workerDirectory"]).resolve()
        lockFile = path / "workers.lock"
        workerFile = path / "workers.csv"
        tempFile = path / "temp.csv"

        index = [worker.upper() in info for info in self.workerInformation].index(True)
        workerRow = self.workerInformation[index]
        workerRow = list(map(lambda x: x if x != None else "", workerRow))

        # Busy wait while lock file exists
        """while os.path.exists(lockFile):
            pass"""

        f = open(lockFile, "w+")

        if login:
            found = False

            with open(workerFile, "r", newline="") as csvfile:
                reader = csv.reader(csvfile)

                for row in reader:
                    if row[:3] == workerRow[:3]:
                        found = True

            if not found:
                with open(workerFile, "a", newline="") as file:
                    writer = csv.writer(file)

                    writer.writerow(workerRow)
        else:
            with open(workerFile, "r", newline="") as csvfile:
                reader = csv.reader(csvfile)

                with open(tempFile, "w+", newline="") as temp:
                    writer = csv.writer(temp)

                    for row in reader:
                        if row[:3] == workerRow[:3]:
                            writer.writerow(workerRow)
                        else:
                            writer.writerow(row)

            shutil.move(tempFile, workerFile)

            del self.workerInformation[index]

        f.close()
        os.remove(lockFile)

    def saveLogin(self, worker_id):
        worker_id = worker_id.strip().upper()
        self.sessionWorkers.append(worker_id)
        self.workerInformation.append(
            [
                worker_id,
                str(self.getDay()),
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                None,
            ]
        )
        self.saveWorkers(worker_id, login=True)

    def saveLogout(self, worker_id):
        worker_id = worker_id.strip().upper()
        self.sessionWorkers.remove(worker_id)
        try:
            index = [worker_id in info for info in self.workerInformation].index(True)
            self.workerInformation[index][-1] = datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            )
        except:
            self.saveWorkers(worker_id, login=False)

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

    ## SAVE COMMENTS ##

    def saveComment(self, text, panNum, proNum):
        comment = text.strip()  # remove whitespace around text

        if not self.getCommentFileAddress(
            proNum
        ).exists():  # if the comment file doesn't exist yet
            with (
                self.getCommentFileAddress(proNum).open("a")
            ) as comFile:  # create one
                comFile.write(
                    f"{panNum} Procedure {proNum} Comments\n\n"
                )  # write header
                comFile.close()  # close file

        with (self.getCommentFileAddress(proNum)).open(
            "a"
        ) as comFile:  # open the comment file in append mode
            comFile.write(f"\n{self.timestamp()}")  # add new line and a timestamp
            comFile.write(
                f"\n{comment}\n"
            )  # add new line, a comment, and another new line

    def getCommentText(
        self,
    ):  # read 7 files and return one big string, only called once in pangui
        allComments = ""  # string to put comments into

        for proNum in range(1, 8):  # for nubmers 1-7
            try:  # try to:
                comments = (
                    self.getCommentFileAddress(proNum).open("r").read()
                )  # get comments from procedure <proNum> comments file
            except FileNotFoundError:  # if the file doesn't exist
                comments = f"No comments for procedure {proNum}\n"  # add text that theres no comments
            allComments += comments  # add the comments we just got

        return allComments  # return all the comments!

    ## OTHER SAVE METHODS (STEPS, SUPPLIES, FAILURES, ETC...) ##

    def saveTPS(self, tps, item, state):
        worker = ""
        timestamp = ""

        # Read-in entire current list
        data = list(self.getListPath().open("r").readlines())

        # Adjust line in list corresponding to new item
        right_section = False
        for i, line in enumerate(data):
            if line.strip().lower() == tps:
                right_section = True
            if right_section:
                line = line.split(",")
                if line[0] == item:
                    worker = ""
                    timestamp = ""
                    if state:
                        worker = self.getSessionWorkers()[0]
                        timestamp = self.timestamp()
                    data[i] = ",".join([item, str(state).upper(), worker, timestamp])
                    break  # No need to continue iteration after updating this line

        # Re-write file
        with self.getListPath().open("w") as file:
            for line in data:
                line = line.strip()
                if line:
                    if line.upper() in ["SUPPLIES", "PARTS"]:
                        line = "\n" + line
                    file.write(line + "\n")

        return (
            worker,
            (datetime.strptime(timestamp, "%Y-%m-%d %H:%M") if timestamp else None),
        )

    def saveMoldRelease(self, item, state):

        # Load in current data
        data = self.loadMoldRelease()

        return_worker = ""
        return_timestamp = None

        # Look for line with this item and append it
        for i, line in enumerate(data):
            if item == line[0]:
                return_worker = self.getSessionWorkers()[0]
                return_timestamp = datetime.now()
                data[i] = [item, state, return_worker, return_timestamp]
                break

        # Overwrite current file with updated list
        with self.getMoldReleasePath().open("w") as file:
            for item, state, worker, timestamp in data:
                file.write(
                    ",".join(
                        [
                            item,
                            str(state).upper(),
                            worker,
                            timestamp.strftime("%Y-%m-%d %H:%M")
                            if timestamp is not None
                            else str(),
                        ]
                    )
                )
                file.write("\n")
        return return_worker, return_timestamp

    def saveStep(self, step_name):

        # If no file yet exists, save it before appending this step
        if not self.checkPanelFileExists():

            self.saveData()

        # Assemble step string
        step = ",".join([self.timestamp(), step_name] + self.sessionWorkers).strip()

        # Append to file
        with self.getPanelPath().open("a") as file:  # append mode

            file.write("\n" + step)

    def saveFailure(self, failure_type, failure_mode, straw_position, comment):
        ## Save Failure
        with (self.failDirectory / f"{failure_type.title()}.csv").open("a") as file:

            ## Put data in order for csv
            # Header : Timestamp, PanelID, Straw Position of Failure, Failure Mode
            data = [
                self.timestamp(),
                self.getPanel(),
                str(straw_position),
                failure_mode,
            ]

            if data[2] == None:
                data[2] = "None Given"
            if data[3] == None:
                data[3] = "None Given"

            ## Write data to file
            file.write(f"\n{','.join(data)}")

        ## Save comment:
        self.saveComment(comment, self.getPanel(), self.getDay())

    def saveStrawTensionMeasurement(self, position, tension, uncertainty):
        straw_header = "Date,Panel,StrawPosition,Tension(grams),Uncertainty(grams),Epoc"
        if not self.getStrawTensionerPath().exists():
            with (self.getStrawTensionerPath()).open("a") as straw_data:
                straw_data.write(straw_header)
                straw_data.write(
                    "\n"
                    + self.timestamp()
                    + ","
                    + self.getPanel()
                    + ","
                    + str(position)
                    + ","
                    + str(tension)
                    + ","
                    + str(uncertainty)
                    + ","
                    + str(datetime.now().timestamp())
                )

        else:
            with (self.getStrawTensionerPath()).open("a") as straw_data:
                straw_data.write(
                    "\n"
                    + self.timestamp()
                    + ","
                    + self.getPanel()
                    + ","
                    + str(position)
                    + ","
                    + str(tension)
                    + ","
                    + str(uncertainty)
                    + ","
                    + str(datetime.now().timestamp())
                )

    def saveWireTensionMeasurement(self, position, tension, wire_timer, calib_factor):
        wire_header = (
            "Date,Panel,WirePosition,Tension(grams),WireTimer(seconds),Epoc,Calibration"
        )
        if not self.getWireTensionerPath().exists():
            with (self.getWireTensionerPath()).open("a") as wire_data:
                wire_data.write(wire_header)
                wire_data.write(
                    "\n"
                    + self.timestamp()
                    + ","
                    + self.getPanel()
                    + ","
                    + str(position)
                    + ","
                    + str(tension)
                    + ","
                    + str(wire_timer)
                    + ","
                    + str(datetime.now().timestamp())
                    + ","
                    + str(calib_factor)
                )

        else:
            with (self.getWireTensionerPath()).open("a") as wire_data:
                wire_data.write(
                    "\n"
                    + self.timestamp()
                    + ","
                    + self.getPanel()
                    + ","
                    + str(position)
                    + ","
                    + str(tension)
                    + ","
                    + str(wire_timer)
                    + ","
                    + str(datetime.now().timestamp())
                    + ","
                    + str(calib_factor)
                )

    # gets passed 3 lists (straw position, continuity, wire position)
    def saveContinuityMeasurement(self, position, continuity_str, wire_position):
        # The original author didn't comment this function so:
        # REFER TO saveHVMeasurement() FOR INFO ON HOW THIS WORKS
        # They're pretty much the same thing, just different data
        con_header = "Panel,Position,Continuity,WirePosition,TimeStamp"
        if not self.getPanelLongContinuityDataPath().exists():
            with self.getPanelLongContinuityDataPath().open("w") as con_data:
                con_data.write(con_header)
        with self.getPanelLongContinuityDataPath().open("r") as con_data:
            reader = DictReader(con_data)
            rows = sorted([row for row in reader], key=lambda row: int(row["Position"]))
        with self.getPanelLongContinuityDataPath().open("w", newline="\n") as con_data:
            writer = DictWriter(con_data, fieldnames=reader.fieldnames)
            new_row = {
                "Panel": self.getPanel(),
                "Position": str(position),
                "Continuity": str(continuity_str),
                "WirePosition": str(wire_position),
                "TimeStamp": self.timestamp(),
            }
            written = False
            writer.writeheader()
            for row in rows:
                if row["Position"] == str(position):
                    row = new_row
                    written = True
                writer.writerow(row)
            if not written:
                writer.writerow(new_row)

    def saveHVMeasurement(self, position, current_left, current_right, is_tripped):
        # only works to a certain degree right now...

        # make header for file (the first line)
        header = "Position,CurrentLeft,CurrentRight,IsTripped,Timestamp"

        # make a new file if one doesn't already exist
        if not self.getPanelLongHVDataPath().exists():
            with self.getPanelLongHVDataPath().open(
                "w"
            ) as hvData:  # with path as hvData...
                hvData.write(header)  # ...write the header, and boom! new file.
        # next read from the existing file.  If we don't make sure a file already
        # exists, then python will cry when we try to read a file that isn't there
        with self.getPanelLongHVDataPath().open("r") as hvData:
            reader = DictReader(hvData)  # read the rows of the file into a dictionary
            rows = sorted([row for row in reader], key=lambda row: int(row["Position"]))

        with self.getPanelLongHVDataPath().open("w", newline="\n") as hvData:
            # fieldnames are the first row of what reader read - the header
            # or at least that's what they should be
            writer = DictWriter(
                hvData,
                fieldnames=[
                    "Position",
                    "CurrentLeft",
                    "CurrentRight",
                    "IsTripped",
                    "Timestamp",
                ],
            )
            # DictWriters treat every row as a dictionary
            newRow = {
                "Position": position,
                "CurrentLeft": current_left,
                "CurrentRight": current_right,
                "IsTripped": str(is_tripped),
                "Timestamp": datetime.now(),
            }
            written = False  # has the new row been written yet?

            # recall that rows is a sorted list of row dictionaries we got from reader
            # now we're going to re-write the whole file which is super inefficient, but
            # it's the best we have (for now... )
            hvData.write(header)
            hvData.write("\n")
            for row in rows:  # for all existing rows...
                if row["Position"] == str(
                    position
                ):  # if the row is for the straw we're updating, then update it!
                    row = newRow
                    written = True  # the new row already existed, so we updated it
                writer.writerow(row)  # write the row

            if not written:  # if the new row is actually new and not an update...
                writer.writerow(newRow)  # write it!

    def saveTensionboxMeasurement(
        self, panel, is_straw, position, length, frequency, pulse_width, tension
    ):
        # Get file path using panel and is_straw
        file = {True: self.getStrawTensionBoxPath, False: self.getWireTensionBoxPath}[
            is_straw
        ](panel)
        # If path doesn't exist, create it and write the header
        if not file.exists():
            with file.open("w+") as f:
                f.write(
                    "Timestamp,Panel,Position,Length,Frequency,PulseWidth,Tension,Epoch"
                )
        # Append measurement at the end of the file
        with file.open("a") as f:
            f.write(
                f"{self.timestamp()}, {panel}, {position:2}, {length}, {frequency}, {pulse_width}, {tension}, {datetime.now().timestamp()}"
            )

    def wireQCd(self, wire):
        qcdwires = []
        with Path(self.paths["wireQC"]).resolve().open("r") as f:
            reader = csv.reader(f, delimiter=",")
            for row in reader:
                qcdwires.append(row[0])
        qcdwires = qcdwires[1:]
        return wire in qcdwires

    ## LOAD METHODS ####

    def loadData(self):
        # Define all lists of data to return later
        data = list()
        elapsed_time = timedelta()
        steps_completed = int()
        continuity = list()
        hv = list()
        wire_position = list()
        resistance = list()
        continuity_time = list()

        # Path

        path = self.getPanelPath()
        # print("Loading data from text file:",path)

        """
        When reading data with next(reader) for day 3,
            the first use gives the header
            the second use gives the non-iterative data (panel, workers, etc.)
            the third use gives the straw numbers (a pretty useless list since it's an int thats the same as it's index in a list 0-95)
            the fourth use gives a list of continuity, 96 of 'Pass: No Continuity', 'Fail: Left Continuity', or 'Fail: Right Continuity'
            the fifth use gives a list of straw positions, 96 of  'Upper 1/3', 'Middle 1/3', or 'Lower 1/3'
            the sixth use gives a list of 96 'Finite's in a row apparently.  (maybe there's another option ?)
            the seventh use gives an empty list
            the eigth use gives ['step_number', 'time_completed', 'step_name']
            the after the eigth use it gives steps, ie: ['1', '2018-12-14_11:40', 'scan_setup'] or ['3', '2018-12-14_11:40', 'threads']

        next(reader) gives lists of strings in a space seperated format
        day 3 and pro 5 are special, but all of the rest should be in the format

            <header (a list of variables (their names) that should be present)>
            <those variables in the order they appear in in the header>
            <???>
            <empty line>
            <completed steps and stuff>

        """

        # Open file and get data only if path exists
        if path.exists():
            with path.open("r") as file:
                reader = csv.reader(file)
                print("1------------------", next(reader))  # Skip header
                # print("2-----------------------",next(reader))
                # print("3----------------------",next(reader))
                # print("4--------------------",next(reader))
                # print("5-----------------------",next(reader))
                # print("6----------------------",next(reader))
                # print("7--------------------",next(reader))
                # print("8-----------------------",next(reader))
                # print("9----------------------",next(reader))
                # print("10--------------------",next(reader))

                # Day-specific data and associated times
                day = self.getDay()
                data = self.filterDataForInput(next(reader)[1:])
                next(reader)  # Skip timestamps
                """
                # If this is day three, also extract all wire measurements
                if self.getDay() == 3:
                    print("2-----------------------",next(reader)) # Skip straw positions
                    #continuity = next(reader)
                    #wire_position = next(reader)
                    print("3-----------------------",next(reader))
                    print("4----------------------",next(reader))
                    print("5--------------------",next(reader))
                    print("6--------------------",next(reader))
                    print("7--------------------",next(reader))
                    print("8--------------------",next(reader))
                    print("9--------------------",next(reader))
                    print("10--------------------",next(reader))
                    print("11--------------------",next(reader))
                    #resistance = next(reader)
                    #continuity_time = next(reader)
                else:
                    self.filterDataForInput(next(reader)[1:0])"""

                # Elapsed time, needs to read [1] if > 1 day otherwise [0]
                elapsed_time = next(reader)
                if "day" in elapsed_time[0]:
                    elapsed_time = self.str2timedelta(
                        elapsed_time[1], elapsed_time[0][0]
                    )  # [1] passes H:MM:SS, [0][0] passes number of days
                else:
                    elapsed_time = self.str2timedelta(elapsed_time[0])

                ## STEPS

                # Collect all other entries as the steps
                l = list(reader)

                # Find the index of the "Steps:" title
                for i, el in enumerate(l):
                    if "Steps:" in el:
                        break

                # All lines after the title are the steps
                steps = [s[1] for s in l[i + 1 :]]

                # Only count as completed steps the lines that 1) contain data and 2) aren't talking about start, pause, resume, etc...
                count = lambda line: any(line) and not any(
                    s in line for s in ["Start", "Paused", "Resumed", "Finished"]
                )

                # Apply this filter to the list of steps
                steps = list(filter(count, steps))

                steps_completed = len(
                    steps
                )  # Only need to tell the GUI the number of steps that were completed

        # Return list of lists (with elapsed time)
        day = self.getDay()
        return [data, elapsed_time, steps_completed]

    def loadTPS(self):
        # TPS means tools, parts, supplies
        with self.getListPath().open("r") as file:
            reader = csv.reader(file)

            # Reads through file
            all_rows = list(reader)
            all_rows = list(filter(lambda x: x != [], all_rows))
            tools = list(
                filter(
                    lambda x: x != [],
                    all_rows[all_rows.index(["TOOLS"]) + 1 : all_rows.index(["PARTS"])],
                )
            )
            parts = list(
                filter(
                    lambda x: x != [],
                    all_rows[
                        all_rows.index(["PARTS"]) + 1 : all_rows.index(["SUPPLIES"])
                    ],
                )
            )
            supplies = list(
                filter(lambda x: x != [], all_rows[all_rows.index(["SUPPLIES"]) + 1 :])
            )
            # Output: 3 lists of lists (tools, parts, and supplies)
            #   - Format of inner lists: [(str) Tool name, (bool) checked off, (str) worker id, (str) timestamp]

        # Process list from str --> desired data type
        def convertDataTypes(lst):
            for i, data in enumerate(lst):
                item, state, worker, timestamp = data  # Parse into 4 parts

                # Convert
                state = state.upper() == "TRUE"  # Convert to boolean
                if timestamp:
                    timestamp = datetime.strptime(
                        timestamp, "%Y-%m-%d %H:%M"
                    )  # Convert to datetime
                else:
                    timestamp = None

                # Overwrite line in list
                lst[i] = [item, state, worker, timestamp]
            return lst

        tools = convertDataTypes(tools)
        parts = convertDataTypes(parts)
        supplies = convertDataTypes(supplies)

        return tools, parts, supplies

    def loadMoldRelease(self):
        # get day
        Day = self.getDay()
        items = []

        # Read file into list
        with self.getMoldReleasePath().open("r") as file:
            reader = csv.reader(file)
            all_rows = list(reader)
            all_rows = list(filter(lambda x: x != [], all_rows))

        # Process contents into predictable datatypes
        for i, line in enumerate(all_rows):
            # Example : PAAS-A,TRUE,WK-DAMBROSE01,2019-06-13 16:29
            item, boolean, worker, timestamp = line
            # Turn boolean from str --> bool
            boolean = boolean.upper() == "TRUE"
            # Turn timestamp form str --> datetime
            if timestamp:
                timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
            else:
                timestamp = None
            # Update line
            one_line = [item, boolean, worker, timestamp]
            items.append(one_line)

        # Return list
        return items

    def loadSteps(self):
        steps = []  # List that will accumulate Step objects

        if Path.exists(self.getStepsPath()):
            with self.getStepsPath().open("r") as f:
                reader = csv.reader(f, delimiter=";")
                names = []

                for index, row in enumerate(reader):
                    if len(row) == 6:
                        if row[0].isnumeric():
                            try:
                                steps.append(Step(*row))
                                names.append(row[0])
                            except Exception:
                                print("exception in loading steps")
                        else:
                            i = 1
                            s = row[0][:i]

                            while s.isnumeric():
                                i += 1
                                s = row[0][:i]

                            major = row[0][: i - 1]

                            try:
                                steps[names.index(major)].addSubstep(Step(*row))
                            except Exception:
                                print(f"Unable to find parent step for step {row[0]}")

            l = list(zip([n.getNumber().zfill(2) for n in steps], steps))
            l.sort()
            steps = [j for i, j in l]

        return steps

    def loadContinuityMeasurements(self, position=None):
        pass

    ##########################################################################

    ### PANEL INFO ###

    def getPanelPath(self):
        # ("getPanelPath:", self.getPanel())
        return (
            self.panelDirectory / f"Day {self.getDay()} data" / f"{self.getPanel()}.csv"
        )

    def getPanelPathMkI(self):
        return (
            self.panelDirectory
            / f"Day {self.getDay()} data"
            / f"{self.getPanel()}_DB.csv"
        )

    # for future day 3 saving
    def getPanelLongContinuityDataPath(self):
        return (
            self.panelDirectory
            / f"Day {self.getDay()} data"
            / f"{self.getPanel()}LongContinuityData.csv"
        )

    # for future pro 5 saving
    def getPanelLongHVDataPath(self):
        return (
            self.panelDirectory
            / f"Day {self.getDay()} data"
            / f"{self.getPanel()}LongHVData.csv"
        )

    def getListPath(self):
        return Path(f"{self.listDirectory}\Day {self.getDay()}.txt").resolve()

    def getMoldReleasePath(self):
        return Path(self.paths["moldReleasePath"]).resolve()

    def getStepsPath(self):
        return Path(self.stepsDirectory / f"Day {self.getDay()}.csv").resolve()

    def checkPanelFileExists(self):
        return self.getPanelPath().exists()

    def checkPanelFileExistsMk1(self):
        return self.getPanelPathMkI.exists()

    def getCommentFileAddress(self, proNum):
        return self.commentDirectory / f"{self.getPanel()}_pro_{proNum}.txt"

    def getWireTensionerPath(self):
        return (
            self.wire_tensionerDirectory / f"{self.getPanel()}_wire_initial_tension.csv"
        )

    def getContinuityDataPath(self):
        return self.continuity_dataDirectory / f"{self.getPanel()}.csv"

    def getStrawTensionerPath(self):
        return (
            self.straw_tensionerDirectory
            / f"{self.getPanel()}_straw_initial_tension.csv"
        )

    def getStrawTensionBoxPath(self, panel):
        return (
            self.strawTensionboxDirectory / f"{panel}_{str(datetime.now().date())}.csv"
        )

    def getWireTensionBoxPath(self, panel):
        return (
            self.wireTensionboxDirectory / f"{panel}_{str(datetime.now().date())}.csv"
        )

    ### DAY-SPECIFIC DATA ###
    # Each header function returns the info that's present in every text file of the corresponding day/pro
    # The number at the beginning is the number of variables to be saved.  That's quicker than using len().
    # All of the rest are the variables for the corresponding day/pro in the order they appear in the text file and
    # in the data list in gui main.  The number at the beginning should be the same in data_count in gui main.
    def _day1header(self):
        return [
            18,
            "Panel ID",
            "Base Plate ID",
            "BIR ID",
            "PIR Left A ID",
            "PIR Left B ID",
            "PIR Left C ID",
            "PIR RIght A ID",
            "PIR Right B ID",
            "PIR Right C ID",
            "MIR ID",
            "ALF 1 ID",
            "ALF 2 ID",
            "Left Gap [mils]",
            "Right Gap [mils]",
            "Min BP/BIR Gap [mils]",
            "Max BP/BIR Gap [mils]",
            "Epoxy Batch ID",
            "Working Time of Epoxy(H:M:S)",
        ]

    def _day2header(self):
        return [
            10,
            "Panel ID",
            "Pallet Upper",
            "Pallet Lower",
            "Epoxy Sample Lower",
            "Epoxy Time Lower",
            "Epoxy Sample Upper",
            "Epoxy Time Upper",
            "PAAS-A Max Temp [C]",
            "PAAS-B Max Temp [C]",
            "Heat Time",
        ]

    def _day3header(self):
        return [2, "Panel ID", "Sense Wire Batch"]

    # (process 4) Pin protectors and omega pieces
    def _pro4header(self):
        return [
            13,
            "Panel ID",
            "Pin Protector Epoxy Batch (Left)",
            "Pin Protector Application Time (H:M:S) (Left)",
            "Pin Protector Cure Time (H:M:S) (Left)",
            "Pin Protector Epoxy Batch (Right)",
            "Pin Protector Application Time (H:M:S) (Right)",
            "Pin Protector Cure Time (H:M:S) (Right)",
            "Omega Piece Epoxy Batch (Left)",
            "Omega Piece Application Time (H:M:S) (Left)",
            "Omega Piece Cure Time (H:M:S) (Left)",
            "Omega Piece Epoxy Batch (Right)",
            "Omega Piece Application Time (H:M:S) (Right)",
            "Omega Piece Cure Time (H:M:S) (Right)",
        ]

    # (process 5) High voltage test (most data saved in different file)
    def _pro5header(self):
        return [1, "Panel ID"]

    def _day6header(self):
        return [
            14,
            "Panel ID",
            "Frame ID",
            "Left Middle Rib ID",
            "Right Middle Rib ID",
            "Left MIR Gap",
            "Right MIR Gap",
            "Baseplate Epoxy Batch",
            "Baseplate Installation Time (H:M:S)",
            "Frame Epoxy Batch (Wetting)",
            "Frame Epoxy Batch (Bead)",
            "Frame Installation Time (H:M:S)",
            "PAAS-A Max Temp [C]",
            "PAAS-C Max Temp [C]",
            "Heating Time (H:M:S)",
        ]

    def _day7header(self):
        return [
            5,
            "Panel ID",
            "Flood Epoxy Batch (Left)",
            "Flood Epoxy Work Time (H:M:S) (Left)",
            "Flood Epoxy Batch (Right)",
            "Flood Epoxy Work Time (H:M:S) (Right)",
        ]

    ### LOAD DATA ###
    def loadRawSteps(self):
        if not self.checkPanelFileExists():
            return list()
        file = self.getPanelPath().open("r").readlines()
        for i in range(len(file)):
            line = file[i]
            if line.strip() == "Steps:":
                return file[i + 1 :]
        return list()

    def loadTimestamps(self):
        # Path
        path = self.getPanelPath()

        # Open file and get data only if path exists
        if path.exists():
            with path.open("r") as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                next(reader)  # Skip data
                current = next(reader)
                l = self.datetimeList(current)
                return l[1:]

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
            # Example: 14:42
            ret = datetime.strptime(dt_str, "%H:%M")
        except ValueError:
            pass

        try:
            # Example: 10/31/18 9:57
            ret = datetime.strptime(dt_str, "%m/%d/%y %H:%M")
        except ValueError:
            pass
        try:
            # Example: 10/31/18 9:57
            ret = datetime.strptime(dt_str, "%d day, %H:%M")
        except ValueError:
            pass
        try:
            # Example: 10/31/18 9:57
            ret = datetime.strptime(dt_str, "%d days %H:%M")
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
    def str2timedelta(dlta_str, numDays=0):
        t = [int(float(x)) for x in dlta_str.split(":")]
        return timedelta(days=(int(numDays)), hours=t[0], minutes=t[1], seconds=t[2])

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

        # Txt above


class SQLDataProcessor(DataProcessor):
    def __init__(self, gui):
        super().__init__(gui)

        # Classes to interact with the database
        self.station = Station.panelStation(
            day=self.getDay()
        )  # BUG: this is returning None
        self.session = self.station.startSession()
        self.procedure = None

    ### METHODS TO IMPLEMENT    ##############################################

    ## GUI --> DATABASE
    def saveData(self):
        # Ensure procedure - starts a procedure if doesn't exist
        if not self.ensureProcedure():
            return

        # Save Day-Specific data
        {
            1: self.saveDataProcess1,
            2: self.saveDataProcess2,
            3: self.saveDataProcess3,
            4: self.saveDataProcess4,
            5: self.saveDataProcess5,
            6: self.saveDataProcess6,
            7: self.saveDataProcess7,
        }[self.getDay()]()

    # IR
    def saveDataProcess1(self):
        # Get data from GUI
        data = self.getDayData()

        # Get panel for easy access
        panel = self.panel()

        # Call all getters to store data in sql database
        self.callMethod(panel.recordBaseplate, self.stripNumber(data[1]))  # Base Plate
        self.callMethod(panel.recordBIR, self.stripNumber(data[2]))  # BIR
        self.callMethod(
            panel.recordPIR, self.stripNumber(data[3]), "L", "A"
        )  # PIR Left A
        self.callMethod(
            panel.recordPIR, self.stripNumber(data[4]), "L", "B"
        )  # PIR Left B
        self.callMethod(
            panel.recordPIR, self.stripNumber(data[5]), "L", "C"
        )  # PIR Left C
        self.callMethod(
            panel.recordPIR, self.stripNumber(data[6]), "R", "A"
        )  # PIR Right A
        self.callMethod(
            panel.recordPIR, self.stripNumber(data[7]), "R", "B"
        )  # PIR Right B
        self.callMethod(
            panel.recordPIR, self.stripNumber(data[8]), "R", "C"
        )  # PIR Right C
        self.callMethod(panel.recordMIR, self.stripNumber(data[9]))  # MIR
        self.callMethod(panel.recordALF, self.stripNumber(data[10]), "L")  # ALF 1
        self.callMethod(panel.recordALF, self.stripNumber(data[11]), "R")  # ALF 2
        self.callMethod(self.procedure.recordLeftGap, data[12])  # Left Gap [mils]
        self.callMethod(self.procedure.recordRightGap, data[13])  # Right Gap [mils]
        self.callMethod(
            self.procedure.recordMinBPBIRGap, data[14]
        )  # Min BP/BIR Gap [mils]
        self.callMethod(
            self.procedure.recordMaxBPBIRGap, data[15]
        )  # Max BP/BIR Gap [mils]
        self.callMethod(
            self.procedure.recordEpoxyBatch, self.stripNumber(data[16])
        )  # Epoxy Batch
        self.callMethod(
            self.procedure.recordEpoxyTime, *self.parseTimeTuple(data[17])
        )  # Working Time of Epoxy(H:M:S)
        self.callMethod(
            panel.recordPAAS, self.stripNumber(data[18]), None, "A"
        )  # PAAS A
        self.callMethod(
            panel.recordPAAS, self.stripNumber(data[19]), None, "C"
        )  # PAAS C

    # Straws
    def saveDataProcess2(self):
        # Get data from GUI
        data = self.getDayData()
        # Get panel for easy access
        panel = self.panel()

        # Call all getters to store data in sql database
        self.callMethod(
            self.procedure.loadFromLPAL, self.stripNumber(data[1]), "top"
        )  # Upper LPAL
        self.callMethod(
            self.procedure.loadFromLPAL, self.stripNumber(data[2]), "bot"
        )  # Lower LPAL
        self.callMethod(
            self.procedure.recordEpoxyBatchLower, self.stripNumber(data[3])
        )  # Lower Epoxy
        self.callMethod(
            self.procedure.recordEpoxyTimeLower, *self.parseTimeTuple(data[4])
        )  # Lower Epoxy Time
        self.callMethod(
            self.procedure.recordEpoxyBatchUpper, self.stripNumber(data[5])
        )  # Upper Epoxy
        self.callMethod(
            self.procedure.recordEpoxyTimeUpper, *self.parseTimeTuple(data[6])
        )  # Upper Epoxy Time
        self.callMethod(self.procedure.recordPaasAMaxTemp, data[7])  # PAAS-A Max Temp
        self.callMethod(self.procedure.recordPaasBMaxTemp, data[8])  # PAAS-B Max Temp
        self.callMethod(
            self.procedure.recordHeatTime, *self.parseTimeTuple(data[9])
        )  # Heat Time
        self.callMethod(
            panel.recordPAAS, self.stripNumber(data[10]), None , "B"
        )  # PIR Right B

    # Wire Tensions
    def saveDataProcess3(self):
        # Get data from GUI
        data = self.getDayData()

        # Call all getters to store data in sql database
        self.callMethod(
            self.procedure.recordWireSpool, self.stripNumber(data[1])
        )  # Sense Wire Batch
        self.callMethod(
            self.procedure.recordSenseWireInsertionTime, *self.parseTimeTuple(data[2])
        )  # Sense Wire Insertion Time

    # Pin Protectors
    def saveDataProcess4(self):
        # Get data from GUI
        data = self.getDayData()

        # Call all getters to store data in sql database
        self.callMethod(
            self.procedure.recordClearEpoxyLeftBatch, self.stripNumber(data[1])
        )  # clear epoxy left - batch
        self.callMethod(
            self.procedure.recordClearEpoxyLeftApplicationDuration,
            *self.parseTimeTuple(data[2]),
        )  # clear epoxy left - application duration
        self.callMethod(
            self.procedure.recordClearEpoxyLeftCureDuration,
            *self.parseTimeTuple(data[3]),
        )  # clear epoxy left - cure duration
        self.callMethod(
            self.procedure.recordClearEpoxyRightBatch, self.stripNumber(data[4])
        )  # clear epoxy right - batch
        self.callMethod(
            self.procedure.recordClearEpoxyRightApplicationDuration,
            *self.parseTimeTuple(data[5]),
        )  # clear epoxy right - application duration
        self.callMethod(
            self.procedure.recordClearEpoxyRightCureDuration,
            *self.parseTimeTuple(data[6]),
        )  # clear epoxy right - cure duration
        self.callMethod(
            self.procedure.recordSilverEpoxyLeftBatch, self.stripNumber(data[7])
        )  # silver epoxy left - batch
        self.callMethod(
            self.procedure.recordSilverEpoxyLeftApplicationDuration,
            *self.parseTimeTuple(data[8]),
        )  # silver epoxy left - application duration
        self.callMethod(
            self.procedure.recordSilverEpoxyLeftCureDuration,
            *self.parseTimeTuple(data[9]),
        )  # silver epoxy left - cure duration
        self.callMethod(
            self.procedure.recordSilverEpoxyRightBatch, self.stripNumber(data[10])
        )  # silver epoxy right - batch
        self.callMethod(
            self.procedure.recordSilverEpoxyRightApplicationDuration,
            *self.parseTimeTuple(data[11]),
        )  # silver epoxy right - application duration
        self.callMethod(
            self.procedure.recordSilverEpoxyRightCureDuration,
            *self.parseTimeTuple(data[12]),
        )  # silver epoxy right - cure duration

    # TODO
    # HV
    def saveDataProcess5(self):
        # Get data from GUI
        data = self.getDayData()

        # If you're looking for recordHVMeasurement, it's called separately in
        # saveHVMeasurement, which is called in the GUI in the initization of
        # process 5.

    # Manifold
    def saveDataProcess6(self):
        # Get data from GUI
        data = self.getDayData()

        # Get panel for easy access
        panel = self.panel()

        # Call all getters to store data in sql database
        self.callMethod(panel.recordFrame, self.stripNumber(data[1]))  # Frame
        self.callMethod(
            panel.recordMiddleRib1, self.stripNumber(data[2])
        )  # Left Middle Rib
        self.callMethod(
            panel.recordMiddleRib2, self.stripNumber(data[3])
        )  # Right Middle Rib
        self.callMethod(
            self.procedure.recordBaseplateRibsMIRGapLeft, data[4]
        )  # Baseplate Ribs\MIR Gap (left)
        self.callMethod(
            self.procedure.recordBaseplateRibsMIRGapRight, data[5]
        )  # Baseplate Ribs\MIR Gap (right)
        self.callMethod(
            self.procedure.recordBaseplateEpoxyBatch, self.stripNumber(data[6])
        )  # Baseplate Epoxy Batch
        self.callMethod(
            self.procedure.recordBaseplateInstallationTime,
            *self.parseTimeTuple(data[7]),
        )  # Baseplate Installation Time
        self.callMethod(
            self.procedure.recordFrameEpoxyBatchWetting, self.stripNumber(data[8])
        )  # Frame Epoxy Batch (Wetting)
        self.callMethod(
            self.procedure.recordFrameEpoxyBatchBead, self.stripNumber(data[9])
        )  # Frame Epoxy Batch (Bead)
        self.callMethod(
            self.procedure.recordFrameInstallationTime, *self.parseTimeTuple(data[10])
        )  # Frame Installation Time
        self.callMethod(
            self.procedure.recordPaasAMaxTemp, data[11]
        )  # PAAS-A Max Temp [C]
        self.callMethod(
            self.procedure.recordPaasCMaxTemp, data[12]
        )  # PAAS-C Max Temp [C]
        self.callMethod(
            self.procedure.recordHeatTime, *self.parseTimeTuple(data[13])
        )  # Heating Time

    # Flooding
    def saveDataProcess7(self):
        # Get data from GUI
        data = self.getDayData()

        # Call all getters to store data in sql database
        self.callMethod(
            self.procedure.recordEpoxyBatchLeft, self.stripNumber(data[1])
        )  # Flood Epoxy Batch (Left)
        self.callMethod(
            self.procedure.recordEpoxyTimeLeft, *self.parseTimeTuple(data[2])
        )  # Flood Epoxy Work Time (Left)
        self.callMethod(
            self.procedure.recordEpoxyBatchRight, self.stripNumber(data[3])
        )  # Flood Epoxy Batch (Right)
        self.callMethod(
            self.procedure.recordEpoxyTimeRight, *self.parseTimeTuple(data[4])
        )  # Flood Epoxy Work Time (Right)

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
            self.session.terminate()
            self.saveProcedureDuration()

    def handleClose(self):
        DM.merge()
        self.session.terminate()

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

    def saveComment(self, text, panNum, proNum):
        # since the txt processor has panNum and proNum, the sql processor has them too
        if not self.ensureProcedure():
            return
        self.procedure.comment(text)

    def getCommentText(self):
        if not self.ensureProcedure():
            return

        # Query comments (ordered by timestamp)
        comments = Comment.queryByPanel(self.getPanelNumber())

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
            text += f"\n\n{self.formatDatetime(c.timestamp)}"
            # Add comment text to string
            text += f"\n{c.text}"

        # Return total string
        return text

    ## OTHER SAVE METHODS (STEPS, SUPPLIES, FAILURES, ETC...) ##

    def saveTPS(self, tps, item, state):

        # Query supply
        supply = (
            SupplyChecked.query()
            .join(Supplies, Supplies.id == SupplyChecked.supply)
            .filter(Supplies.name == item)
            .filter(Supplies.type == tps)
            .filter(SupplyChecked.session == self.session.id)
            .one_or_none()
        )

        # Check present / Remove and return worker, datetime
        supply.checkPresent(
            boolean=state, worker=(self.getSessionWorkers()[0] if state else None)
        )

        # Return worker, timestamp
        return supply.getWorker(), datetime.fromtimestamp(supply.getTimestamp())

    def saveMoldRelease(self, item, state):

        mri = (
            MoldReleaseItemsChecked.query()
            .join(
                MoldReleaseItems,
                MoldReleaseItems.id == MoldReleaseItemsChecked.mold_release_item,
            )
            .filter(MoldReleaseItems.name == item)
            .filter(MoldReleaseItemsChecked.session == self.session.id)
            .one_or_none()
        )

        mri.setMoldReleased(
            boolean=state, worker=(self.getSessionWorkers()[0] if state else None)
        )
        return mri.getWorker(), datetime.fromtimestamp(mri.getTimestamp())

        """
        for mri in self.station.queryMoldReleaseItems():    # mri = Mold Release Item
            if mri.getName() == item:
                mri.setMoldReleased(
                    boolean =   state,
                    worker  =   (self.getSessionWorkers()[0] if state else str())
                )
                return mri.getWorker(), datetime.fromtimestamp(mri.getTimestamp())"""

    def saveStep(self, step_name):
        if not self.ensureProcedure():
            return

        # Query Step
        step = (
            PanelStep.query()
            .filter(PanelStep.name == step_name)
            .filter(PanelStep.station == self.station.id)
            .one_or_none()
        )

        # Execute step
        self.procedure.executeStep(step)

    def saveFailure(self, failure_type, failure_mode, straw_position, comment):
        if not self.ensureProcedure():
            return

        self.procedure.recordFailure(
            position=straw_position,
            failure_type=failure_type,
            failure_mode=failure_mode,
            comment=comment,
        )

    def saveStrawTensionMeasurement(self, position, tension, uncertainty):
        if self.ensureProcedure():
            self.procedure.recordStrawTension(position, tension, uncertainty)

    def saveWireTensionMeasurement(self, position, tension, wire_timer, calib_factor):
        if self.ensureProcedure():
            self.procedure.recordWireTension(
                position, tension, wire_timer, calib_factor
            )

    def saveTensionboxMeasurement(
        self, panel, is_straw, position, length, frequency, pulse_width, tension
    ):
        is_straw = {True: "straw", False: "wire"}[is_straw]
        TensionboxMeasurement(
            panel=self.queryPanel(self.stripNumber(panel)),
            straw_wire=is_straw,
            position=position,
            length=length,
            frequency=frequency,
            pulse_width=pulse_width,
            tension=tension,
        ).commit()

    def saveContinuityMeasurement(self, position, continuity_str, wire_position):
        # Make sure all data is defined
        if not all(el is not None for el in [position, continuity_str, wire_position]):
            return
        # Save a continuity measurement
        self.procedure.recordContinuityMeasurement(
            position=position,
            left_continuity=(
                continuity_str in ["Pass: No Continuity", "Fail: Right Continuity"]
            ),
            right_continuity=(
                continuity_str in ["Pass: No Continuity", "Fail: Left Continuity"]
            ),
            wire_position={
                "Lower 1/3": "lower",
                "Middle 1/3": "middle",
                "Top 1/3": "top",
            }[wire_position],
        )

    # Called directly by the GUI in the initialization of Process 5
    def saveHVMeasurement(self, position, current_left, current_right, is_tripped):
        if self.ensureProcedure():
            self.procedure.recordHVMeasurement(
                position, current_left, current_right, is_tripped
            )

    def wireQCd(self, wire):
        id = self.stripNumber(wire)
        spool = WireSpool.queryWithId(id)
        return spool is not None and spool.qc

    ## LOAD METHODS ##

    # DB --> GUI
    def loadData(self):
        # Pre-set variables
        data = list()
        elapsed_time = timedelta()
        steps_completed = int()

        # TODO I've had so many details is None errors that we should consider
        # making this a try catch.
        if self.ensureProcedure():
            # Day-specific data
            data = {
                1: self.loadDataProcess1,
                2: self.loadDataProcess2,
                3: self.loadDataProcess3,
                4: self.loadDataProcess4,
                5: self.loadDataProcess5,
                6: self.loadDataProcess6,
                7: self.loadDataProcess7,
            }[self.getDay()]()

            # Elapsed Time
            elapsed_time = timedelta(seconds=self.procedure.getElapsedTime())

            # Steps Completed
            steps_completed = self.procedure.countStepsExecuted()

        # Return list of lists
        return data, elapsed_time, steps_completed

    def loadSteps(self):
        p_steps = self.station.getSteps()
        steps = []
        # Creates a Step object from Panel Object for stepsList.py to display on GUI
        for i, p in enumerate(p_steps):
            curr_substeps = p.substeps()
            steps.append(
                Step(
                    number=i + 1,
                    name=p.name,
                    checkbox=p.checkbox,
                    picture=bool(p.picture),
                    pictureName=p.picture,
                    text=p.text,
                    substeps=[],
                )
            )
            # Converts Substeps from PanelStep obj. to Step obj.
            if curr_substeps is not []:
                final = []
                for z, sub in enumerate(curr_substeps):
                    new = Step(
                        number=float(i + 1) + float(z) * 0.1,
                        name=sub.name,
                        checkbox=sub.checkbox,
                        picture=bool(sub.picture),
                        pictureName=sub.picture,
                        text=sub.text,
                        substeps=[],
                    )
                    new.setIsSubstep(True)
                    final.append(new)
            steps[i].setSubsteps(final)
        return steps

    # Load Tools, Parts, and Supplies (TPS)
    # db --> GUI
    def loadTPS(self):
        """
        Output: 3 lists of lists (tools, parts, supplies)
            Each inner list is of length 4.
                1. (str)        item name
                2. (bool)       state - has this part been checked off or not?
                3. (str)        id of worker who checked it off (or '' if unchecked)
                4. (datetime)   datetime object corresponding to time when item when checked off
        """
        # Query all Supply objects
        all = (
            DM.query(
                Supplies.type,
                Supplies.name,
                SupplyChecked.checked,
                SupplyChecked.worker,
                SupplyChecked.timestamp,
            )
            .join(SupplyChecked, SupplyChecked.supply == Supplies.id)
            .filter(SupplyChecked.session == self.session.id)
            .all()
        )

        # Sort into 3 lists
        tools = list()
        parts = list()
        supplies = list()
        append_to_list = {
            "tools": lambda ret: tools.append(ret),
            "parts": lambda ret: parts.append(ret),
            "supplies": lambda ret: supplies.append(ret),
        }
        for typ, name, state, worker, timestamp in all:
            if self.procedure is not None:
                state = True
                worker = self.getSessionWorkers()[0]
            ret = [name, state, worker, datetime.fromtimestamp(timestamp)]
            append_to_list[typ](ret)

        # Return lists
        return tools, parts, supplies

    def loadMoldRelease(self):
        """
        loadMoldRelease(self)

            Description:    Loads list of items to be mold released

            Output: list of lists (tools, parts, supplies)
                Each inner list is of length 4.
                    1. (str)        item name
                    2. (bool)       state - has this part been checked off or not?
                    3. (str)        id of worker who checked it off (or '' if unchecked)
                    4. (datetime)   datetime object corresponding to time when item when checked off
        """
        lst = (
            DM.query(
                MoldReleaseItems.name,
                MoldReleaseItemsChecked.mold_released,
                MoldReleaseItemsChecked.worker,
                MoldReleaseItemsChecked.timestamp,
            )
            .join(
                MoldReleaseItems,
                MoldReleaseItemsChecked.mold_release_item == MoldReleaseItems.id,
            )
            .filter(MoldReleaseItemsChecked.session == self.session.id)
            .all()
        )
        # Change timestamp to datetime
        for i, data in enumerate(lst):
            x, y, z, timestamp = data
            lst[i] = x, y, z, datetime.fromtimestamp(timestamp)
        # Return list
        return lst

    def loadContinuityMeasurements(self, position=None):
        # If position is None, return all in list of tuples Ex: [(cont, wire_pos,), (con, wire_pos), ...]
        if position is None:
            ret = list()
            measurements = self.procedure.getContinuityMeasurements()
            for m in measurements:
                ret.append(self.parseContinuityMeasurement(m))
        else:
            ret = self.parseContinuityMeasurement(
                self.procedure.getContinuityMeasurement(position)
            )
        return ret

    def loadHVMeasurements(self):
        # ret = [(current_left0, current_right0, is_tripped0), (current_left1, current_right1, is_tripped1), ...]
        ret = list()
        measurements = self.procedure.getHVMeasurements()
        for m in measurements:
            if m == None:
                ret.append((None, None, None))
            else:
                ret.append((m.current_left, m.current_right, m.is_tripped))
        return ret

    ##########################################################################

    def ensureProcedure(self):
        # If no procedure has been defined yet, define one.
        if self.procedure is None:
            self.session.startPanelProcedure(
                day=self.getDay(), panel_number=self.getPanelNumber()
            )
            self.procedure = self.session.getProcedure()

        # Return boolean indicating if 'self.procedure' is now defined.
        return self.procedure is not None

    def getPanelNumber(self):
        return self.stripNumber(super().getPanel())

    def saveProcedureDuration(self):
        elapsed = self.getTimer().total_seconds()
        self.procedure.setElapsedTime(elapsed)

    """
    panel

        Description:    Returns a Panel object queried using the panel barcode from the gui.
    """

    def panel(self):
        return self.queryPanel(self.getPanelNumber())

    @staticmethod
    def queryPanel(number):
        return Panel.queryByNumber(number)

    #####################
    ## DATA PROCESSING ##
    #####################

    # Saving
    @staticmethod
    def stripNumber(barcode):
        retCode = ""
        if barcode:
            # Iterate through barcode till you find a digit
            for i, b in enumerate(barcode):
                if b.isdigit():
                    retCode += b
            # Return remainder of string as integer
            return int(retCode)
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

    ## DAY-SPECIFIC DATA LOAD

    # IR
    def loadDataProcess1(self):
        panel = self.panel()
        return [
            self.getBarcode(panel),  # Panel
            self.getBarcode(panel.getBaseplate()),  # Base Plate
            self.getBarcode(panel.getBIR()),  # BIR
            self.getBarcode(panel.getPIR(L_R="L", letter="A")),  # PIR Left A
            self.getBarcode(panel.getPIR(L_R="L", letter="B")),  # PIR Left B
            self.getBarcode(panel.getPIR(L_R="L", letter="C")),  # PIR Left C
            self.getBarcode(panel.getPIR(L_R="R", letter="A")),  # PIR Right A
            self.getBarcode(panel.getPIR(L_R="R", letter="B")),  # PIR Right B
            self.getBarcode(panel.getPIR(L_R="R", letter="C")),  # PIR Right C
            self.getBarcode(panel.getMIR()),  # MIR
            self.getBarcode(panel.getALF("L")),  # ALF 1
            self.getBarcode(panel.getALF("R")),  # ALF 2
            self.procedure.getLeftGap(),  # Left Gap [mils]
            self.procedure.getRightGap(),  # Right Gap [mils]
            self.procedure.getMinBPBIRGap(),  # Min BP/BIR Gap [mils]
            self.procedure.getMaxBPBIRGap(),  # Max BP/BIR Gap [mils]
            self.epoxyBarcode(self.procedure.getEpoxyBatch()),  # Epoxy Batch
            self.timeDelta(
                self.procedure.getEpoxyTime(), self.procedure.getEpoxyTimeRunning()
            ),  # Working Time of Epoxy
            self.getBarcode(panel.getPAAS(L_R= None, letter='A')),                               # PAAS A barcode
            self.getBarcode(panel.getPAAS(L_R= None, letter='C'))                                # PAAS C barcode
        ]

    # Straws
    def loadDataProcess2(self):
        panel = self.panel()
        return [
            self.getBarcode(self.panel()),  # Panel
            self.getBarcode(self.procedure.getLPAL(top_bot="top")),  # Upper LPAL
            self.getBarcode(self.procedure.getLPAL(top_bot="bot")),  # Lower LPAL
            self.epoxyBarcode(self.procedure.getEpoxyBatchLower()),  # Lower Epoxy
            self.timeDelta(
                self.procedure.getEpoxyTimeLower(),
                self.procedure.getEpoxyTimeRunningLower(),
            ),  # Lower Epoxy Time
            self.epoxyBarcode(self.procedure.getEpoxyBatchUpper()),  # Upper Epoxy
            self.timeDelta(
                self.procedure.getEpoxyTimeUpper(),
                self.procedure.getEpoxyTimeRunningUpper(),
            ),  # Upper Epoxy Time
            self.procedure.getPaasAMaxTemp(),  # PAAS-A Max Temp
            self.procedure.getPaasBMaxTemp(),  # PAAS-B Max Temp
            self.timeDelta(
                self.procedure.getHeatTime(), self.procedure.getHeatTimeRunning()
            ),  # Heat Time
            self.getBarcode(panel.getPAAS(L_R= None, letter='B'))                                # PAAS B barcode
        ]

    # Wire Tensions
    def loadDataProcess3(self):
        return [
            self.getBarcode(self.panel()),  # Panel
            self.getBarcode(self.procedure.getWireSpool()),  # Sense Wire Batch
            self.timeDelta(
                self.procedure.getSenseWireInsertionTime(),
                self.procedure.getSenseWireInsertionTimeRunning(),
            ),  # Sense Wire Insertion Time
        ]

    # Pin Protectors
    def loadDataProcess4(self):
        return [
            self.getBarcode(self.panel()),  # Panel
            self.epoxyBarcode(
                self.procedure.getClearEpoxyLeftBatch()
            ),  # get the clear epoxy batch 1 ID
            self.timeDelta(
                self.procedure.getClearEpoxyLeftApplicationDuration(),
                self.procedure.getClearEpoxyLeftTimeIsRunning(),
            ),  # clear epoxy batch 1 application duration
            self.timeDelta(
                self.procedure.getClearEpoxyLeftCureDuration(),
                self.procedure.getClearEpoxyLeftTimeIsRunning(),
            ),  # clear epoxy batch 1 cure duration
            self.epoxyBarcode(
                self.procedure.getClearEpoxyRightBatch()
            ),  # clear epoxy batch 2 ID
            self.timeDelta(
                self.procedure.getClearEpoxyRightApplicationDuration(),
                self.procedure.getClearEpoxyRightTimeIsRunning(),
            ),  # clear epoxy batch 2 application duration
            self.timeDelta(
                self.procedure.getClearEpoxyRightCureDuration(),
                self.procedure.getClearEpoxyRightTimeIsRunning(),
            ),  # clear epoxy batch 2 cure duration
            self.epoxyBarcode(
                self.procedure.getSilverEpoxyLeftBatch()
            ),  # silver epoxy batch 1 ID
            self.timeDelta(
                self.procedure.getSilverEpoxyLeftApplicationDuration(),
                self.procedure.getSilverEpoxyLeftTimeIsRunning(),
            ),  # silver epoxy batch 1 application duration
            self.timeDelta(
                self.procedure.getSilverEpoxyLeftCureDuration(),
                self.procedure.getSilverEpoxyLeftTimeIsRunning(),
            ),  # silver epoxy batch 1 cure duration
            self.epoxyBarcode(
                self.procedure.getSilverEpoxyRightBatch()
            ),  # silver epoxy batch 2 ID
            self.timeDelta(
                self.procedure.getSilverEpoxyRightApplicationDuration(),
                self.procedure.getSilverEpoxyRightTimeIsRunning(),
            ),  # silver epoxy batch 2 application duration
            self.timeDelta(
                self.procedure.getSilverEpoxyRightCureDuration(),
                self.procedure.getSilverEpoxyRightTimeIsRunning(),
            ),  # silver epoxy batch 2 cure duration
        ]

    # TODO
    # HV
    def loadDataProcess5(self):
        return []

    # Manifold
    def loadDataProcess6(self):
        panel = self.panel()
        return [
            self.getBarcode(panel),  # Panel
            self.getBarcode(panel.getFrame()),  # Frame
            self.getBarcode(panel.getMiddleRib1()),  # Left Middle Rib
            self.getBarcode(panel.getMiddleRib1()),  # Right Middle Rib
            self.procedure.getBaseplateRibsMIRGapLeft(),  # Baseplate Ribs\MIR Gap (left)
            self.procedure.getBaseplateRibsMIRGapRight(),  # Baseplate Ribs\MIR Gap (right)
            self.epoxyBarcode(
                self.procedure.getBaseplateEpoxyBatch()
            ),  # Baseplate Epoxy Batch
            self.timeDelta(
                self.procedure.getBaseplateInstallationTime(),
                self.procedure.getBaseplateInstallationTimeRunning(),
            ),  # Baseplate Installation Time
            self.epoxyBarcode(
                self.procedure.getFrameEpoxyBatchWetting()
            ),  # Frame Epoxy Batch (Wetting)
            self.epoxyBarcode(
                self.procedure.getFrameEpoxyBatchBead()
            ),  # Frame Epoxy Batch (Bead)
            self.timeDelta(
                self.procedure.getFrameInstallationTime(),
                self.procedure.getFrameInstallationTimeRunning(),
            ),  # Frame Installation Time
            self.procedure.getPaasAMaxTemp(),  # PAAS-A Max Temp [C]
            self.procedure.getPaasCMaxTemp(),  # PAAS-C Max Temp [C]
            self.timeDelta(
                self.procedure.getHeatTime(), self.procedure.getHeatTimeRunning()
            ),  # Heating Time
        ]

    # Flooding
    def loadDataProcess7(self):
        panel = self.panel()
        return [
            self.getBarcode(panel),
            self.procedure.getEpoxyBatchLeft(),  # Flood Epoxy Batch (Left)
            self.timeDelta(
                self.procedure.getEpoxyTimeLeft(),
                self.procedure.getEpoxyTimeLeftRunning(),
            ),  # Flood Epoxy Work Time (Left)
            self.procedure.getEpoxyBatchRight(),  # Flood Epoxy Batch (Right)
            self.timeDelta(
                self.procedure.getEpoxyTimeRight(),
                self.procedure.getEpoxyTimeRightRunning(),
            ),  # Flood Epoxy Work Time (Right)
        ]


def main():
    MultipleDataProcessor(object(), save2txt=True, save2SQL=True)


if __name__ == "__main__":
    main()
