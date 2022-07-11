from abc import abstractmethod, ABC
from datetime import datetime, timedelta
from guis.panel.pangui.credentials import Credentials
from guis.panel.pangui.stepsList import Step
from pathlib import Path
import numpy as np, os, csv, shutil, sys
from csv import DictReader, DictWriter
import tkinter
from tkinter import messagebox

from guis.common.db_classes.bases import DM
from guis.common.db_classes.comment_failure import Comment
from guis.common.db_classes.steps import (
    PanelStep,
    PanelStepExecution,
)
from guis.common.db_classes.procedure import Procedure
from guis.common.db_classes.station import Station
from guis.common.db_classes.straw_location import Panel
from guis.common.db_classes.supplies import (
    Supplies,
    SupplyChecked,
    MoldReleaseItemsChecked,
    MoldReleaseItems,
    WireSpool,
)
from guis.common.db_classes.workers import Worker
from guis.common.db_classes.measurements_panel import (
    TensionboxMeasurement,
    BadWire,
    LeakFinalForm,
    MethaneTestSession,
    MethaneLeakInstance,
)
import logging

logger = logging.getLogger("root")

from guis.common.getresources import GetProjectPaths

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

#   ___  _         _                  _    ______
#  / _ \| |       | |                | |   | ___ \
# / /_\ \ |__  ___| |_ _ __ __ _  ___| |_  | |_/ / __ ___   ___ ___  ___ ___  ___  _ __
# |  _  | '_ \/ __| __| '__/ _` |/ __| __| |  __/ '__/ _ \ / __/ _ \/ __/ __|/ _ \| '__|
# | | | | |_) \__ \ |_| | | (_| | (__| |_  | |  | | | (_) | (_|  __/\__ \__ \ (_) | |
# \_| |_/_.__/|___/\__|_|  \__,_|\___|\__| \_|  |_|  \___/ \___\___||___/___/\___/|_|
#
#


class DataProcessor(ABC):
    def __init__(self, gui, stage):
        self.gui = gui
        self.stage = stage

    """#USED
    saveData(self)

        Description: The generic save function that saves all data for a given pro.

        Data Saved:
            - Pro-specific data
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
                        one large string with timestamps and pro headers.
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

            wire_alignment   (str)   Will be one of the following :
                ['Top 1/3', 'Middle 1/3', 'Lower 1/3']
    """

    @abstractmethod
    def saveContinuityMeasurement(self, position, continuity_str, wire_alignment):
        pass

    @abstractmethod
    def saveHVMeasurement(self, position, side, current, voltage, is_tripped):
        pass

    @abstractmethod
    def savePanelTempMeasurement(self, temp_paas_a, temp_paas_bc):
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

    # TODO update this comment to reflect "pros"-> "process"
    """#USED
    loadData

        Description:    Returns all data previously saved for this pro
                            - pro-specific data
                            - corresponding timestamps
                            - steps completed
                            (if pro 3)
                            - continuity, wire alignment, resistance, and corresponding timestamps (if 6 more lists)

        Returns: List of lists
            [
            pro data,
            data timestamps,
            elapsed_time, (integer, number of seconds)
            steps completed,
            continuity,
            continuity timestamp,
            wire alignment,
            wire alignment timestamp,
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

        Description:    Returns an ordered list of steps to be completed during this pro.

        Return list(Step)
    """

    @abstractmethod
    def loadSteps(self):
        pass

    """
    loadContinuityMeasurements(self,position=None)

        Description:    Loads all or one of the continuity measurements (pro 3).

        Input:  position (int)  Position of wire to load continuity for. If None, this
                                method should return all the continuity measurements for the panel.

        Returns:    Tuples of (continuity, wire_align) for each measurement loaded.
    """

    @abstractmethod
    def loadContinuityMeasurements(self, position=None):
        pass

    """
    @abstractmethod
    def loadHVMeasurements(self,position=None):
        pass
    """
    
    @abstractmethod
    def saveMethaneSession(
        self, covered_areas, sep_layer, top_straw_low, top_straw_high, bot_straw_low, bot_straw_high, detector_number, user
    ):
        pass
    
    @abstractmethod
    def saveMethaneLeak(
        straw_leak, straw_number, location, straw_leak_location, description, leak_size, panel_leak_location, user
    ):
        pass
    
    
    

    ##########################################################################

    ### GETTERS ###
    # Gets variables from gui that are necessary for saving data properly

    def getPro(self):
        try:
            return self.gui.pro
        except AttributeError:
            return None

    def getProIndex(self):
        return self.gui.pro_index

    def getData(self):
        return self.gui.data

    def getProData(self):
        return self.getData()[self.getProIndex()]

    # TODO not great that we assume a DP will have these functions
    # string object
    def getPanel(self):
        return self.gui.getCurrentPanel()

    # return just the integer
    def getPalletID(self):
        pallet_id = self.gui.getPalletID()
        pallet_id = "".join(ch for ch in pallet_id if ch.isdigit())
        return pallet_id

    # return just the integer
    def getPalletNumber(self):
        pallet_number = self.gui.getPalletNumber()
        pallet_number = "".join(ch for ch in pallet_number if ch.isdigit())
        return pallet_number

    """
    getTimer

        Description: Gets elapsed timer of main timer in GUI.

        Returns: (timedelta)
    """

    def getTimer(self):
        return self.gui.mainTimer.getElapsedTime()


# ___  ___      _ _   _  ______
# |  \/  |     | | | (_) | ___ \
# | .  . |_   _| | |_ _  | |_/ / __ ___   ___ ___  ___ ___  ___  _ __
# | |\/| | | | | | __| | |  __/ '__/ _ \ / __/ _ \/ __/ __|/ _ \| '__|
# | |  | | |_| | | |_| | | |  | | | (_) | (_|  __/\__ \__ \ (_) | |
# \_|  |_/\__,_|_|\__|_| \_|  |_|  \___/ \___\___||___/___/\___/|_|
#
#


class MultipleDataProcessor(DataProcessor):
    def __init__(
        self,
        gui,
        stage,
        save2txt=True,
        save2SQL=True,
        lab_version=True,
        sql_primary=True,
    ):
        self.gui = gui
        self.stage = stage
        self.processors = []
        # Instantiate Data Processors
        txtdp = None
        sqldp = None
        if save2txt:
            txtdp = TxtDataProcessor(self.gui, self.stage, lab_version)
            self.processors.append(txtdp)
        if save2SQL:
            sqldp = SQLDataProcessor(self.gui, self.stage)
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

    def record_leak_rate(self, lr):
        for dp in self.processors:
            dp.record_leak_rate(lr)

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
        logger.debug(
            f"MULTIPROCESSOR - Attempting to save pos {position}, ten {tension}, tim {wire_timer}, cal {calib_factor}"
        )
        for dp in self.processors:
            logger.debug(f"Saving with {dp}...")
            dp.saveWireTensionMeasurement(position, tension, wire_timer, calib_factor)

    def saveContinuityMeasurement(self, position, continuity_str, wire_alignment):
        for dp in self.processors:
            dp.saveContinuityMeasurement(position, continuity_str, wire_alignment)

    def savePanelTempMeasurement(self, temp_paas_a, temp_paas_bc):
        for dp in self.processors:
            dp.savePanelTempMeasurement(temp_paas_a, temp_paas_bc)

    def saveHVMeasurement(self, position, side, current, voltage, is_tripped):
        for dp in self.processors:
            dp.saveHVMeasurement(position, side, current, voltage, is_tripped)

    def saveTensionboxMeasurement(
        self, panel, is_straw, position, length, frequency, pulse_width, tension
    ):
        for dp in self.processors:
            dp.saveTensionboxMeasurement(
                panel, is_straw, position, length, frequency, pulse_width, tension
            )
    
    def saveMethaneSession(
        self, covered_areas, sep_layer, top_straw_low, top_straw_high, bot_straw_low, bot_straw_high, detector_number, user
    ):
        for dp in self.processors:
            dp.saveMethaneSession(
                covered_areas, sep_layer, top_straw_low, top_straw_high, bot_straw_low, bot_straw_high, detector_number, user
            )
    
    def saveMethaneLeak(
        self, straw_leak, straw_number, location, straw_leak_location, description, leak_size, panel_leak_location, user
    ):
        for dp in self.processors:
            dp.saveMethaneLeak(
                straw_leak, straw_number, location, straw_leak_location, description, leak_size, panel_leak_location, user
            )

    def saveBadWire(self, position, failure, process, wire_check):
        for dp in self.processors:
            dp.saveBadWire(position, failure, process, wire_check)

    def saveLeakForm(
        self, reinstalled, inflated, location, confidence, size, resolution, next_step
    ):
        for dp in self.processors:
            dp.saveLeakForm(
                reinstalled, inflated, location, confidence, size, resolution, next_step
            )

    def saveTapForm(self, tap_id):
        for dp in self.processors:
            dp.saveTapForm(tap_id)

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

    def get_leak_rate(self):
        return self.primaryDP.get_leak_rate()

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

    def loadBadWires(self):
        return self.primaryDP.loadBadWires()
    
    def load_methane_leaks(self):
        return self.primaryDP.load_methane_leaks()


#  _____    _    ______
# |_   _|  | |   | ___ \
#   | |_  _| |_  | |_/ / __ ___   ___ ___  ___ ___  ___  _ __
#   | \ \/ / __| |  __/ '__/ _ \ / __/ _ \/ __/ __|/ _ \| '__|
#   | |>  <| |_  | |  | | | (_) | (_|  __/\__ \__ \ (_) | |
#   \_/_/\_\\__| \_|  |_|  \___/ \___\___||___/___/\___/|_|
#

# Current capabilities:
# Save panel pro data (anything entered directly into the GUI panel tab)
# Save comments and failures
# Save starts, pauses, and finishes
# Save worker logins and logouts
# Save steps
# Save continuity measurements
# Save HV measurements

# Current incapabilities:
# Load (everything)
# Save tension measurements (wire, straw, tensionbox)
# Save panel heating measurements
# Save tools, parts, supplies
# Save mold release


class TxtDataProcessor(DataProcessor):
    def __init__(self, gui, stage, lab_version=True):
        super().__init__(gui, stage)
        self.paths = GetProjectPaths()
        self._init_directories(self.paths)
        self.credentialChecker = Credentials(
            "pan" + str(self.getPro()), self.paths["credentialsChecklist"]
        )
        self.sessionWorkers = []
        self.workerInformation = []
        self.validWorkers = []
        

    def _init_directories(self, paths):
        self.workerDirectory = paths["workerDirectory"]
        self.panelDirectory = paths["panelDirectory"]
        self.failDirectory = self.panelDirectory / "Failures"
        self.commentDirectory = self.panelDirectory / "Comments"
        self.listDirectory = paths["listsDirectory"]
        self.stepsDirectory = paths["stepsDirectory"]
        self.continuity_dataDirectory = paths["continuity_data"]
        self.wire_tensionerDirectory = paths["wire_tensioner_data"]
        self.strawTensionboxDirectory = paths["tensionbox_data_straw"]
        self.wireTensionboxDirectory = paths["tensionbox_data_wire"]
        self.straw_tensionerDirectory = paths["straw_tensioner_data"]
        self.badStrawsWiresDirectory = paths["badStrawsWires"]
        self.qc8LeakFormDirectory = paths["qc_leak_resolution"]

    #  _____                  ___  ___     _   _               _
    # /  ___|                 |  \/  |    | | | |             | |
    # \ `--.  __ ___   _____  | .  . | ___| |_| |__   ___   __| |___
    #  `--. \/ _` \ \ / / _ \ | |\/| |/ _ \ __| '_ \ / _ \ / _` / __|
    # /\__/ / (_| |\ V /  __/ | |  | |  __/ |_| | | | (_) | (_| \__ \
    # \____/ \__,_| \_/ \___| \_|  |_/\___|\__|_| |_|\___/ \__,_|___/

    # Some work great, others are totally busted.
    # And their helper functions

    """
    saveData has two options for formats.  Whenever saveData is called, it'll
    make a decision on which save method to use.

    Setting the USE_MARK_ONE constant to true will make it save in the DB friendly CSV format.
    USE_MARK_TWO should ALWAYS be set to True, as it saves in the human friendly format.
    """

    def saveData(self):
        if USE_MARK_TWO:
            self.saveDataMkII()  # save in user friendly CSV
        if USE_MARK_ONE:
            self.saveDataMkI()  # save in database friendly CSV

    def saveDataMkI(self):
        # get data from the gui to save
        data = self.getProData()

        header = {
            1: self._pro1header,
            2: self._pro2header,
            3: self._pro3header,
            4: self._pro4header,
            5: self._pro5header,
            6: self._pro6header,
            7: self._pro7header,
            8: self._pro8header,
        }[self.getPro()]()

        # Count number of steps
        # loadRawSteps() returns a list of steps from the human
        # friendly text files.
        numSteps = 0
        for rawStep in self.loadRawSteps():
            if rawStep != "\n" and "Pro " not in rawStep:
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
            # TODO beyond 24 hours, the data value gets a comma e.g. "1 day,
            # and 5 hours", messing up the parsing.
            # TODO put this condition into a function and use it in both of
            # these saveData functions.
            if isinstance(data[i], tuple) and isinstance(
                data[i][0], timedelta
            ):  # is a timedelta tuple
                timedata = f"[{data[i][0]}|{data[i][1]}]"
                timedata = timedata.replace(",", "") + ","
                row += timedata
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
        # get data to be saved
        data = self.getProData()

        # each header function returns a list of the variables that need to be saved
        # in the same order they appear in the data list.  However, the headers begin
        # with an int that represents the number of variables that need to be saved.
        # This is more efficient than using len().  Due to the presance of the int at
        # the beginning of the header list, when writing it with data, the corresponding
        # index in header will be one higher than in data.
        header = {
            1: self._pro1header,
            2: self._pro2header,
            3: self._pro3header,
            4: self._pro4header,
            5: self._pro5header,
            6: self._pro6header,
            7: self._pro7header,
            8: self._pro8header,
        }[self.getPro()]()

        # steps are automatically saved periodically while gui is running
        # We will collect them now, and write later.
        steps = [line.strip() for line in self.loadRawSteps() if line != "\n"]

        # open file to write to
        with self.getPanelPathMk2().open("w") as file:
            # write timestamp
            file.write("Timestamp," + self.timestamp() + "\n")

            # in f'{header[i+1]},{data[i]}\n' header[i+1] is the variable name
            # and data[i] is the value for that variable
            # The if statement checks if the data is a timedelta with a boolean
            # for timer running status.  Writing both in the tuple is a bit more
            # difficult to read.

            # header[0] is an int that equals the number of variables to be recorded
            for i in range(header[0]):
                # if no data to record then break
                if len(data) == 0:
                    break
                # is a timedelta tuple
                # TODO beyond 24 hours, the data value gets a comma e.g. "1 day,
                # and 5 hours", messing up the parsing.
                # TODO put this condition into a function and use it in both of
                # these saveData functions.
                if isinstance(data[i], tuple) and isinstance(data[i][0], timedelta):
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

    # add a start step to panel's pro file
    def saveStart(self):
        self.saveStep(step_name=f"Pro {self.getPro()} Start")

    # add a pause step to panel's pro file
    def savePause(self):
        self.saveStep(step_name=f"Pro {self.getPro()} Paused")

    # add a resume step to panel's pro file
    def saveResume(self):
        self.saveStep(step_name=f"Pro {self.getPro()} Resumed")

    # add a finish step to panel's pro file
    def saveFinish(self):
        self.saveStep(step_name=f"Pro {self.getPro()} Finished")

    # saves worker login/out
    # worker is the worker's ID as a string
    # login = True --> logging in, login = False --> logging out
    def saveWorkers(self, worker, login):
        lockFile = self.workerDirectory / "workers.lock"
        workerFile = self.workerDirectory / "workers.csv"
        tempFile = self.workerDirectory / "temp.csv"

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

    # calls saveWorkers()
    def saveLogin(self, worker_id):
        worker_id = worker_id.strip().upper()
        self.sessionWorkers.append(worker_id)
        self.workerInformation.append(
            [
                worker_id,
                str(self.getPro()),
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                None,
            ]
        )
        self.saveWorkers(worker_id, login=True)

    # calls saveWorkers()
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

    def record_leak_rate(self, lr):
        pass

    def get_leak_rate(self):
        pass

    # add a comment to panel's comment file
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

    # add a step line to existing txt file
    def saveStep(self, step_name):

        # If no file yet exists, save it before appending this step
        if not self.checkPanelFileExistsMk2():

            self.saveData()

        # Assemble step string
        step = ",".join([self.timestamp(), step_name] + self.sessionWorkers).strip()

        # Append to file
        with self.getPanelPathMk2().open("a") as file:  # append mode

            file.write("\n" + step)

    # adds a failure comment, parameters are details about the failure
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
        self.saveComment(comment, self.getPanel(), self.getPro())
    
    def saveMethaneSession(self, covered_areas, sep_layer, top_straw_low, top_straw_high, bot_straw_low, bot_straw_high, detector_number, user):
        pass
    # update all continuity measurements for panel
    # parameters are lists of data
    def saveContinuityMeasurement(self, position, continuity_str, wire_alignment):
        con_header = "Panel,Position,Continuity,WireAlignment,TimeStamp"
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
                "WireAlignment": str(wire_alignment),
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

    # update all HV measurements for panel
    # parameters are lists of data
    def saveHVMeasurement(self, position, side, current, voltage, is_tripped):
        headers = ["Position", "Current", "Side", "Voltage", "IsTripped", "Timestamp"]

        file_exists = os.path.isfile(self.getPanelLongHVDataPath())
        logger.info(
            "Saving HV current data to {0}".format(self.getPanelLongHVDataPath())
        )
        try:
            with open(self.getPanelLongHVDataPath(), "a+") as f:
                writer = DictWriter(
                    f, delimiter=",", lineterminator="\n", fieldnames=headers
                )
                if not file_exists:
                    writer.writeheader()  # file doesn't exist yet, write a header
                writer.writerow(
                    {
                        "Position": position,
                        "Current": current,
                        "Side": side,
                        "Voltage": voltage,
                        "IsTripped": str(is_tripped),
                        "Timestamp": datetime.now().isoformat(),
                    }
                )
        except PermissionError:
            logger.warning(
                "HV data CSV file is locked. Probably open somewhere. Close and try again."
            )
            logger.warning("HV data is not being saved to CSV files.")

    # save tension measurement
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
                    "Tension Box data for "
                    + panel
                    + " process "
                    + str(self.getPro())
                    + "\n"
                )
                f.write(
                    "Timestamp,Epoch,Panel,Position,Length,Frequency,PulseWidth,Tension\n"
                )
        # Append measurement at the end of the file
        with file.open("a") as f:
            f.write(
                f"{datetime.now().isoformat()}, {datetime.now().timestamp()}, {panel}, {position:2}, {length}, {frequency}, {pulse_width}, {tension}\n"
            )
            
    # save process 8 methane testing session instance
    def saveMethaneSession(
        self, covered_areas, sep_layer, top_straw_low, top_straw_high, bot_straw_low, bot_straw_high, detector_number, user
    ):
        pass
        
    def saveMethaneLeak(
        self, straw_leak, straw_number, location, straw_leak_location, description, leak_size, panel_leak_location, user
    ):
        pass

    # save panel heating measurement (DEFUNCT)
    def savePanelTempMeasurement(self, temp_paas_a, temp_paas_bc):
        pass
    
    # save the methane session txt
    def saveMethaneSession(
        self, covered_areas, sep_layer, top_straw_low, top_straw_high, bot_straw_low, bot_straw_high, detector_number, user
    ):
        headers=["Panel","covered_areas","sep_layer","top_straw_low","top_straw_high","bot_straw_low","bot_straw_high","detector_number","user","timestamp"]

        outfile = self.getPanelLongMethaneSessionPath()
        file_exists = os.path.isfile(outfile)
        logger.info("Saving methane session data to {0}".format(outfile))
        try:
            with open(outfile, "a+") as f:
                writer = DictWriter(
                    f, delimiter=",", lineterminator="\n", fieldnames=headers
                )
                if not file_exists:
                    writer.writeheader()  # file doesn't exist yet, write a header
                writer.writerow(
                    {
                        "Panel": self.getPanel(),
                        "covered_areas": str(covered_areas),
                        "sep_layer": str(sep_layer),
                        "top_straw_low": str(top_straw_low),
                        "top_straw_high": str(top_straw_high),
                        "bot_straw_low": str(bot_straw_low),
                        "bot_straw_high": str(bot_straw_high),
                        "detector_number": str(detector_number),
                        "user": str(user),
                        "timestamp": self.timestamp(),
                    }
                )
        except PermissionError:
            logger.warning(
                "Methane session data CSV file is locked. Probably open somewhere. Close and try again."
            )
            logger.warning("Methane session data is not being saved to CSV files.")
            return
    
    # save the methane leak txt
    def saveMethaneLeak(
        self, straw_leak, straw_number, location, straw_leak_location, description, leak_size, panel_leak_location, user
    ):
        headers=["Panel","session","straw_leak","straw_number","location","straw_leak_location","description","leak_size","panel_leak_location","user","timestamp"]

        outfile = self.getPanelLongMethaneLeakPath()
        file_exists = os.path.isfile(outfile)
        logger.info("Saving methane leak data to {0}".format(outfile))
        try:
            with open(outfile, "a+") as f:
                writer = DictWriter(
                    f, delimiter=",", lineterminator="\n", fieldnames=headers
                )
                if not file_exists:
                    writer.writeheader()  # file doesn't exist yet, write a header
                writer.writerow(
                    {
                        "Panel": self.getPanel(),
                        "straw_leak": str(straw_leak),
                        "straw_number": str(straw_number),
                        "location": str(location),
                        "straw_leak_location": str(straw_leak_location),
                        "description": str(description),
                        "leak_size": str(leak_size),
                        "panel_leak_location": str(panel_leak_location),
                        "user": str(user),
                        "timestamp": self.timestamp()
                    }
                )
        except PermissionError:
            logger.warning(
                "Methane leak data CSV file is locked. Probably open somewhere. Close and try again."
            )
            logger.warning("Methane leak data is not being saved to CSV files.")
        return

    # update all wire tension measurements for panel
    # parameters are lists of data
    def saveWireTensionMeasurement(self, position, tension, wire_timer, calib_factor):
        logger.debug(
            f"TXTPROCESSOR - Attempting to save pos {position}, ten {tension}, tim {wire_timer}, cal {calib_factor}"
        )

        headers = ["Position", "Tension", "WireTimer", "CalibrationFactor", "Timestamp"]

        outfile = self.getWireTensionerPath()
        file_exists = os.path.isfile(outfile)
        logger.info("Saving wire tension data to {0}".format(outfile))
        try:
            with open(outfile, "a+") as f:
                writer = DictWriter(
                    f, delimiter=",", lineterminator="\n", fieldnames=headers
                )
                if not file_exists:
                    writer.writeheader()  # file doesn't exist yet, write a header
                writer.writerow(
                    {
                        "Position": position,
                        "Tension": tension,
                        "WireTimer": wire_timer,
                        "CalibrationFactor": calib_factor,
                        "Timestamp": datetime.now().isoformat(),
                    }
                )
        except PermissionError:
            logger.warning(
                "Wire tension data CSV file is locked. Probably open somewhere. Close and try again."
            )
            logger.warning("Wire tension data is not being saved to CSV files.")
        return

    # update all straw tension measurements for panel (DEFUNCT)
    # parameters are lists of data
    def saveStrawTensionMeasurement(self, position, tension, uncertainty):
        pass

    # save tools, supplies, parts list (DEFUNCT)
    def saveTPS(self, tps, item, state):
        return "", 0

    # save mold release (DEFUNCT)
    def saveMoldRelease(self, item, state):
        return "", 0

    def saveBadWire(self, number, failure, process, wire_check):
        panel = self.getPanel()
        # check if file exists already
        file_exists = os.path.isfile(self.getBadStrawsWiresPath(panel))

        headers = ["number", "failure", "is_wire", "timestamp"]

        # opens file (even if it doesn't exist yet) and appends data
        with open(self.getBadStrawsWiresPath(panel), "a+") as f:
            writer = DictWriter(
                f, delimiter=",", lineterminator="\n", fieldnames=headers
            )
            if not file_exists:
                writer.writeheader()  # file doesn't exist yet, write a header
            writer.writerow(
                {
                    "number": number,
                    "failure": failure,
                    "is_wire": wire_check,
                    "timestamp": datetime.now().isoformat(),
                }
            )

    def saveLeakForm(self, reinst, infl, loc, conf, size, reso, next):
        panel = self.getPanel()
        # check if file exists already
        file_exists = os.path.isfile(self.getLeakFormsPath(panel))

        headers = [
            "location",
            "size",
            "resolution",
            "next",
            "reinstalled_parts",
            "inflated",
            "timestamp",
        ]

        # opens file (even if it doesn't exist yet) and appends data
        with open(self.getLeakFormsPath(panel), "a+") as f:
            writer = DictWriter(
                f, delimiter=",", lineterminator="\n", fieldnames=headers
            )
            if not file_exists:
                writer.writeheader()  # file doesn't exist yet, write a header
            writer.writerow(
                {
                    "location": loc,
                    "size": size,
                    "resolution": reso,
                    "next": next,
                    "reinstalled_parts": reinst,
                    "inflated": infl,
                    "timestamp": datetime.now().isoformat(),
                }
            )

    #  _                     _  ___  ___     _   _               _
    # | |                   | | |  \/  |    | | | |             | |
    # | |     ___   __ _  __| | | .  . | ___| |_| |__   ___   __| |___
    # | |    / _ \ / _` |/ _` | | |\/| |/ _ \ __| '_ \ / _ \ / _` / __|
    # | |___| (_) | (_| | (_| | | |  | |  __/ |_| | | | (_) | (_| \__ \
    # \_____/\___/ \__,_|\__,_| \_|  |_/\___|\__|_| |_|\___/ \__,_|___/
    # Defunct Load methods that all just pass
    # EXCEPT THE LAST TWO

    def loadData(self):
        pass

    def loadTPS(self):
        pass

    def loadSteps(self):
        pass

    def loadContinuityMeasurements(self, position=None):
        pass

    def loadTimestamps(self):
        pass

    # Helper method for save data functions:
    def loadRawSteps(self):
        if not self.checkPanelFileExistsMk2():
            return list()
        file = self.getPanelPathMk2().open("r").readlines()
        for i in range(len(file)):
            line = file[i]
            if line.strip() == "Steps:":
                return file[i + 1 :]
        return list()

    # Helper method for save data functions:
    def loadMoldRelease(self):
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

    # ______     _   _                         ______                _   _
    # | ___ \   | | | |                        |  ___|              | | (_)
    # | |_/ /_ _| |_| |____      ____ _ _   _  | |_ _   _ _ __   ___| |_ _  ___  _ __  ___
    # |  __/ _` | __| '_ \ \ /\ / / _` | | | | |  _| | | | '_ \ / __| __| |/ _ \| '_ \/ __|
    # | | | (_| | |_| | | \ V  V / (_| | |_| | | | | |_| | | | | (__| |_| | (_) | | | \__ \
    # \_|  \__,_|\__|_| |_|\_/\_/ \__,_|\__, | \_|  \__,_|_| |_|\___|\__|_|\___/|_| |_|___/
    #                                    __/ |
    #                                   |___/
    # All of the following functions either return a file pathway in the form
    # of a string, or a boolean for weather or not a file exists.

    def getPanelPathMk2(self):
        # ("getPanelPath:", self.getPanel())
        return (
            self.panelDirectory / f"Day {self.getPro()} data" / f"{self.getPanel()}.csv"
        )

    def getPanelPathMkI(self):
        return (
            self.panelDirectory
            / f"Day {self.getPro()} data"
            / f"{self.getPanel()}_DB.csv"
        )
        
    def getPanelLongMethaneSessionPath(self):
        return (
            self.panelDirectory
            / "FinalQC"
            / "leak_resolution"
            / f"{self.getPanel()}_sess.csv"
        )
    
    def getPanelLongMethaneLeakPath(self):
        return (
            self.panelDirectory
            / "FinalQC"
            / "leak_resolution"
            / f"{self.getPanel()}_leak.csv"
        )

    def getPanelLongContinuityDataPath(self):
        return (
            self.panelDirectory
            / f"Day {self.getPro()} data"
            / f"{self.getPanel()}LongContinuityData.csv"
        )

    def getPanelLongHVDataPath(self):
        return (
            self.panelDirectory
            / f"Day {self.getPro()} data"
            / f"{self.getPanel()}LongHVData.csv"
        )

    def getListPath(self):
        return self.listDirectory / f"Day {self.getPro()}.txt"

    def getMoldReleasePath(self):
        return self.paths["moldReleasePath"]

    def getStepsPath(self):
        return self.stepsDirectory / f"Day {self.getPro()}.csv"

    def checkPanelFileExistsMk2(self):
        return self.getPanelPathMk2().exists()

    def checkPanelFileExistsMk1(self):
        return self.getPanelPathMkI.exists()

    def getCommentFileAddress(self, proNum):
        return self.commentDirectory / f"{self.getPanel()}_day_{proNum}.txt"

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
            self.strawTensionboxDirectory
            / f"TB_straws_{panel}_proc{self.getPro()}_{str(datetime.now().date())}.csv"
        )

    def getWireTensionBoxPath(self, panel):
        return (
            self.wireTensionboxDirectory
            / f"TB_wires_{panel}_proc{self.getPro()}_{str(datetime.now().date())}.csv"
        )

    def getBadStrawsWiresPath(self, panel):
        return self.badStrawsWiresDirectory / f"bad_channels_{panel}.csv"

    def getLeakFormsPath(self, panel):
        return self.qc8LeakFormDirectory / f"leak_resolution_forms_{panel}.csv"

    #  _   _                _            ______                _   _
    # | | | |              | |           |  ___|              | | (_)
    # | |_| | ___  __ _  __| | ___ _ __  | |_ _   _ _ __   ___| |_ _  ___  _ __  ___
    # |  _  |/ _ \/ _` |/ _` |/ _ \ '__| |  _| | | | '_ \ / __| __| |/ _ \| '_ \/ __|
    # | | | |  __/ (_| | (_| |  __/ |    | | | |_| | | | | (__| |_| | (_) | | | \__ \
    # \_| |_/\___|\__,_|\__,_|\___|_|    \_|  \__,_|_| |_|\___|\__|_|\___/|_| |_|___/

    # Each header function returns the info that's present in every text file of the corresponding pro/pro
    # The number at the beginning is the number of variables to be saved.  That's quicker than using len().
    # All of the rest are the variables for the corresponding pro/pro in the order they appear in the text file and
    # in the data list in gui main.  The number at the beginning should be the same in data_count in gui main.
    def _pro1header(self):
        return [
            22,
            "Panel ID",
            "Base Plate ID",
            "BIR ID",
            "PIR Left A ID",
            "PIR Left B ID",
            "PIR Left C ID",
            "PIR Right A ID",
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
            "PAASA",
            "PAASB",
            "Pallet Upper",
            "Pallet Lower",
        ]

    def _pro2header(self):
        return [
            8,
            "Panel ID",
            "Epoxy Sample Lower",
            "Epoxy Time Lower",
            "Epoxy Sample Upper",
            "Epoxy Time Upper",
            "PAAS-A Max Temp [C]",
            "PAAS-B Max Temp [C]",
            "Heat Time",
        ]

    def _pro3header(self):
        return [2, "Panel ID", "Sense Wire Batch"]

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

    def _pro5header(self):
        return [1, "Panel ID"]

    def _pro6header(self):
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

    def _pro7header(self):
        return [
            7,
            "Panel ID",
            "Flood Epoxy Batch 815 (Left)",
            "Flood Epoxy Work Time (H:M:S) (Left)",
            "Flood Epoxy Batch 815 (Right)",
            "Flood Epoxy Work Time (H:M:S) (Right)",
            "Flood Epoxy Batch 828 (Left)",
            "Flood Epoxy Batch 828 (Right)",
        ]

    def _pro8header(self):
        return [
            16,
            "Panel ID",
            "Left Cover",
            "Center Cover",
            "Right Cover",
            "Left Ring1",
            "Left Ring2Date",
            "Left Ring3Time",
            "Left Ring4",
            "Right Ring1",
            "Right Ring2Date",
            "Right Ring3Time",
            "Right Ring4",
            "Center Ring1",
            "Center Ring2Date",
            "Center Ring3Time",
            "Center Ring4",
        ]

    # ___  ____            _   _      _
    # |  \/  (_)          | | | |    | |
    # | .  . |_ ___  ___  | |_| | ___| |_ __   ___ _ __ ___
    # | |\/| | / __|/ __| |  _  |/ _ \ | '_ \ / _ \ '__/ __|
    # | |  | | \__ \ (__  | | | |  __/ | |_) |  __/ |  \__ \
    # \_|  |_/_|___/\___| \_| |_/\___|_| .__/ \___|_|  |___/
    #                                  | |
    #                                  |_|
    # Other helper functions

    # make a human readable timestamp
    @staticmethod
    def timestamp():
        return datetime.now().strftime("%Y-%m-%d %H:%M")

    # check if wire spool has been QC'd
    # returns a boolean
    def wireQCd(self, wire):
        qcdwires = []
        with Path(self.paths["wireQC"]).resolve().open("r") as f:
            reader = csv.reader(f, delimiter=",")
            for row in reader:
                qcdwires.append(row[0])
        qcdwires = qcdwires[1:]
        return wire in qcdwires

    # gets all comments for all pros and returns a big string
    def getCommentText(self,):
        # read 7 files and return one big string, only called once in pangui
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

    # check if worker has street cred
    def checkCredentials(self):
        return self.credentialChecker.checkCredentials(self.sessionWorkers)

    # another check if worker has street cred
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
                logger.warning("Unable to read worker list")

        return worker.upper() in self.validWorkers

    # returns list of current workers
    def getSessionWorkers(self):
        return self.sessionWorkers

    # TBH no idea what this does but getting
    # rid of it causes a crash
    def workerLoggedIn(self, worker):
        return any([worker.upper() in info for info in self.workerInformation])

    # does things for SQL processor, not TXT.
    # needs to exist to appease the python gods?
    def handleClose(self):
        pass


#  _____  _____ _      ______
# /  ___||  _  | |     | ___ \
# \ `--. | | | | |     | |_/ / __ ___   ___ ___  ___ ___  ___  _ __
#  `--. \| | | | |     |  __/ '__/ _ \ / __/ _ \/ __/ __|/ _ \| '__|
# /\__/ /\ \/' / |____ | |  | | | (_) | (_|  __/\__ \__ \ (_) | |
# \____/  \_/\_\_____/ \_|  |_|  \___/ \___\___||___/___/\___/|_|
#
#


class SQLDataProcessor(DataProcessor):
    def __init__(self, gui, stage):
        super().__init__(gui, stage)

        # first, set the station AKA process, e.g. straw prep or panel 3
        self.station = Station.get_station(step=self.getPro(), stage=self.stage)

        # write a new entry to the session table
        # a new session id, pointer to this station, empty procedure, and active = True
        self.session = self.station.startSession()
        self.procedure = None

    ### METHODS TO IMPLEMENT    ##############################################

    ## GUI --> DATABASE
    def saveData(self):
        # Ensure procedure - starts a procedure if doesn't exist
        if not self.ensureProcedure():
            return

        # Save Pro-Specific data
        {
            1: self.saveDataProcess1,
            2: self.saveDataProcess2,
            3: self.saveDataProcess3,
            4: self.saveDataProcess4,
            5: self.saveDataProcess5,
            6: self.saveDataProcess6,
            7: self.saveDataProcess7,
            8: self.saveDataProcess8,
        }[self.getPro()]()

    # IR
    def saveDataProcess1(self):
        # Get data from GUI
        data = self.getProData()

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
        if data[20] is not None:
            self.callMethod(
                self.procedure.loadFromLPAL, self.stripNumber(data[20]), "top"
            )  # Upper LPAL
        if data[21] is not None:
            self.callMethod(
                self.procedure.loadFromLPAL, self.stripNumber(data[21]), "bot"
            )  # Lower LPAL

    # Straws
    def saveDataProcess2(self):
        # Get data from GUI
        data = self.getProData()
        # Get panel for easy access
        panel = self.panel()

        # Call all getters to store data in sql database
        self.callMethod(
            self.procedure.recordEpoxyBatchLower, self.stripNumber(data[1])
        )  # Lower Epoxy
        self.callMethod(
            self.procedure.recordEpoxyTimeLower, *self.parseTimeTuple(data[2])
        )  # Lower Epoxy Time
        self.callMethod(
            self.procedure.recordEpoxyBatchUpper, self.stripNumber(data[3])
        )  # Upper Epoxy
        self.callMethod(
            self.procedure.recordEpoxyTimeUpper, *self.parseTimeTuple(data[4])
        )  # Upper Epoxy Time
        self.callMethod(self.procedure.recordPaasAMaxTemp, data[5])  # PAAS-A Max Temp
        self.callMethod(self.procedure.recordPaasBMaxTemp, data[6])  # PAAS-B Max Temp
        self.callMethod(
            self.procedure.recordHeatTime, *self.parseTimeTuple(data[7])
        )  # Heat Time
        self.callMethod(
            panel.recordPAAS, self.stripNumber(data[8]), None, "B"
        )  # PAAS B

    # Wire Tensions
    def saveDataProcess3(self):
        # Get data from GUI
        data = self.getProData()

        # Call all setters to store data in sql database
        # Sense Wire Batch
        self.callMethod(self.procedure.recordWireSpool, self.stripNumber(data[1]))
        # Sense Wire Insertion Time
        self.callMethod(
            self.procedure.recordSenseWireInsertionTime, *self.parseTimeTuple(data[2])
        )
        # initial_weight
        self.callMethod(self.procedure.recordInitialWireWeight, data[3])
        # final_weight
        self.callMethod(self.procedure.recordFinalWireWeight, data[4])

    # Pin Protectors
    def saveDataProcess4(self):
        # Get data from GUI
        data = self.getProData()

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

    # HV -- DEPRECATED
    def saveDataProcess5(self):
        # Get data from GUI
        data = self.getProData()

        # If you're looking for recordHVMeasurement, it's called separately in
        # saveHVMeasurement, which is called in the GUI in the initization of
        # process 5.

    # Manifold
    def saveDataProcess6(self):
        # Get data from GUI
        data = self.getProData()

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
        data = self.getProData()

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
        self.callMethod(
            self.procedure.recordEpoxyBatchLeft828, self.stripNumber(data[5])
        )  # Flood Epoxy Batch (Left)
        self.callMethod(
            self.procedure.recordEpoxyBatchRight828, self.stripNumber(data[6])
        )  # Flood Epoxy Batch (Left)

    # FinalQC
    def saveDataProcess8(self):
        data = self.getProData()

        self.callMethod(self.procedure.recordLeftCover, self.stripNumber(data[1]))
        self.callMethod(self.procedure.recordCenterCover, self.stripNumber(data[2]))
        self.callMethod(self.procedure.recordRightCover, self.stripNumber(data[3]))

        # rings consist of a line edit, then a date input, then another line edit
        # left ring example: OL 1538 25Oct19 0954 79042A
        lRing = f"{str(self.stripNumber(data[4])).zfill(4)}{data[5]}{data[6]}{data[7]}"
        if "None" in lRing:
            lRing = "000001Jan00000000000Z"
        self.callMethod(self.procedure.recordLeftRing, lRing)
        rRing = (
            f"{str(self.stripNumber(data[8])).zfill(4)}{data[9]}{data[10]}{data[11]}"
        )
        if "None" in rRing:
            rRing = "000001Jan00000000000Z"
        self.callMethod(self.procedure.recordRightRing, rRing)
        cRing = (
            f"{str(self.stripNumber(data[12])).zfill(4)}{data[13]}{data[14]}{data[15]}"
        )
        if "None" in cRing:
            cRing = "000001Jan00000000000Z"
        self.callMethod(self.procedure.recordCenterRing, cRing)

        self.callMethod(self.procedure.recordStage, data[16])

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
            self.procedure.stop()
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

    ## SAVE LEAK RATE ##

    def record_leak_rate(self, lr):
        if not self.ensureProcedure():
            return
        self.procedure.record_leak_rate(lr)

    def get_leak_rate(self):
        return self.procedure.get_leak_rate()

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
        current_pro = 0
        for c in comments:
            pro = Procedure.queryWithId(c.procedure).getStation().getDay()

            # Add pro header
            if pro > current_pro:
                current_pro = pro
                header = f"Pro {current_pro} Comments"
                if current_pro != 1:
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
        
        
        duplicate_steps = (
            PanelStepExecution.query()
            .filter(PanelStepExecution.panel_step == step.id)
            .filter(PanelStepExecution.procedure == self.procedure.id)
            .all()
        )

        if len(duplicate_steps) == 0:
            # Execute step
            self.procedure.executeStep(step)
        else:
            pass

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
        logger.debug(
            f"SQLPROCESSOR - Attempting to save pos {position}, ten {tension}, tim {wire_timer}, cal {calib_factor}"
        )
        if self.ensureProcedure():
            self.procedure.recordWireTension(
                position, tension, wire_timer, calib_factor
            )

    def saveTensionboxMeasurement(
        self, panel, is_straw, position, length, frequency, pulse_width, tension
    ):
        if self.ensureProcedure():
            is_straw = {True: "straw", False: "wire"}[is_straw]
            TensionboxMeasurement(
                procedure=self.procedure,
                panel=self.queryPanel(self.stripNumber(panel)),
                straw_wire=is_straw,
                position=position,
                length=length,
                frequency=frequency,
                pulse_width=pulse_width,
                tension=tension,
            ).commit()
            
    def saveMethaneSession(
        self, covered_areas, sep_layer, top_straw_low, top_straw_high, bot_straw_low, bot_straw_high, detector_number, user
    ):
        if self.ensureProcedure():
            MethaneTestSession(
                covered_areas=covered_areas,
                sep_layer=sep_layer,
                top_straw_low=top_straw_low,
                top_straw_high=top_straw_high,
                bot_straw_low=bot_straw_low,
                bot_straw_high=bot_straw_high,
                detector_number=detector_number,
                straw_location=self.procedure.straw_location,
                user=user,
            ).commit()
        
    def saveMethaneLeak(
        self, straw_leak, straw_number, location, straw_leak_location, description, leak_size, panel_leak_location, user
    ):
        if self.ensureProcedure():
            MethaneLeakInstance(
                straw_leak=straw_leak,
                straw_number=straw_number,
                location=location,
                straw_leak_location=straw_leak_location,
                description=description,
                leak_size=leak_size,
                panel_leak_location=panel_leak_location,
                straw_location=self.procedure.straw_location,
                user=user,
            ).commit()
        

    def saveContinuityMeasurement(self, position, continuity_str, wire_alignment):
        # Make sure all data is defined
        if not all(el is not None for el in [position, continuity_str, wire_alignment]):
            return
        if wire_alignment == "":
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
            wire_alignment={
                "Lower 1/3": "lower",
                "Middle 1/3": "middle",
                "Top 1/3": "top",
                "Short, Top": "short top",
                "Short, Middle": "short middle",
                "Short, Bottom": "short lower",
                "Middle, Top": "middle top",
                "True Middle": "middle middle",
                "Middle, Bottom": "middle lower",
                "Long, Top": "long top",
                "Long, Middle": "long middle",
                "Long, Bottom": "long lower",
            }[wire_alignment],
        )

    def savePanelTempMeasurement(self, temp_paas_a, temp_paas_bc):
        if self.ensureProcedure():
            self.procedure.recordPanelTempMeasurement(temp_paas_a, temp_paas_bc)

    # Called directly by the GUI in the initialization of Process 5
    def saveHVMeasurement(self, position, side, current, voltage, is_tripped):
        if self.ensureProcedure():
            # convert string to float (cut the "V" off the end) if not a none type
            if voltage is not None:
                voltage = float(voltage[:4])
                # don't save if no data to save
                if current == "":
                    return

                self.procedure.recordHVMeasurement(
                    position, side, current, voltage, is_tripped
                )
            else:
                # if voltage is none, skip string chopping

                # don't save if no data to save
                if current == "":
                    return

                self.procedure.recordHVMeasurement(
                    position, side, current, voltage, is_tripped
                )

    def saveTapForm(self, tap_value):
        if self.ensureProcedure():
            self.procedure.recordBrokenTaps(tap_value)

    def saveBadWire(self, position, failure, process, wire_check):
        if self.ensureProcedure():
            BadWire(
                position=position,
                failure=failure,
                process=process,
                procedure=self.procedure.id,
                wire_check=wire_check,
            )

    def saveLeakForm(
        self, reinstalled, inflated, location, confidence, size, resolution, next_step
    ):
        if self.ensureProcedure():
            LeakFinalForm(
                procedure=self.procedure.id,
                cover_reinstalled=reinstalled,
                inflated=inflated,
                leak_location=location,
                confidence=confidence,
                leak_size=size,
                resolution=resolution,
                next_step=next_step,
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
            # Pro-specific data
            data = {
                1: self.loadDataProcess1,
                2: self.loadDataProcess2,
                3: self.loadDataProcess3,
                4: self.loadDataProcess4,
                5: self.loadDataProcess5,
                6: self.loadDataProcess6,
                7: self.loadDataProcess7,
                8: self.loadDataProcess8,
            }[self.getPro()]()

            # Elapsed Time
            elapsed_time = timedelta(seconds=self.procedure.getElapsedTime())

            # Steps Completed
            steps_completed = self.procedure.steps_executed()

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
        # If position is None, return all in list of tuples Ex: [(cont, wire_align,), (con, wire_align), ...]
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
        # ret = [(current_left0, current_right0, voltage0, is_tripped0), (current_left1, current_right1, voltage1, is_tripped1), ...]
        ret = list()
        measurements = self.procedure.getHVMeasurements()
        for m in measurements:
            if m == None:
                ret.append((None, None, None, None, None, None))
            else:
                ret.append(
                    (
                        m.current_left,
                        m.current_right,
                        m.voltage,
                        m.is_tripped,
                        m.position,
                        m.timestamp,
                    )
                )
        return ret

    def loadBadWires(self):
        ret = []
        wires = self.procedure.getBadWires()
        for wire in wires:
            ret.append((wire.position, wire.failure, wire.wire))

        return ret
    
    def load_methane_leaks(self):
        straw_location=int(self.procedure.straw_location)
        
        sessions = (
            DM.query(MethaneTestSession)
            .filter(MethaneTestSession.straw_location == straw_location)
            .all()
        )
        output = ''
        covered_list_reference=['Top Covers','Top Flooding','Bottom Covers','Bottom Flooding','Electronics Slot','Side Seams','Stay Bolts','PFN Holes']
        for session in sessions:
            if session.covered_areas is not None:
                output += str(session.user) + ' ' + str(datetime.fromtimestamp(session.timestamp)) + '\n'
                output += 'Covered Areas: '
                for bool,reference in zip(session.covered_areas, covered_list_reference):
                    if bool == 'Y':
                        output += reference + '\n'
                
                if session.covered_areas[8] == 'Y':
                    output += 'Top Straws ' + str(session.top_straw_low) + '-' + str(session.top_straw_high) + '\n'
                if session.covered_areas[9] == 'Y':
                    output += 'Bottom Straws ' + str(session.bot_straw_low) + '-' + str(session.bot_straw_high) + '\n'
                if session.sep_layer is True:
                    output += 'A plastic separator was used.'
                else:
                    output += 'A plastic separator was not used.'
                    
                output += '\nDetector number ' + str(session.detector_number) + ' was used.'
                
                output += '\n\n'   

        leak_list_reference=['Covers','Stay Bolts','Flooding','PFN Holes','Electronics Slot','Side Seams']
        leaks = (
            DM.query(MethaneLeakInstance)
            .filter(MethaneLeakInstance.straw_location == straw_location)
            .all()
        )
        
        for leak in leaks:
            if leak.straw_leak == 0:
                output += str(leak.user) + ' ' + str(datetime.fromtimestamp(leak.timestamp)) + '\n'
                output += 'Panel Leak: \n'
                        
                output += 'Covered Areas: '
                for bool,reference in zip(leak.panel_leak_location, leak_list_reference):
                    if bool == 'Y':
                        output += reference + '\n'
                output += 'Leak Size: ' + str(leak.leak_size) + ' ppm\n\n'
            else:
                output += str(leak.user) + ' ' + str(datetime.fromtimestamp(leak.timestamp)) + '\n'
                output += 'Straw Leak: \n'
                output += 'Straw Number ' + str(leak.straw_number)
                if leak.straw_leak_location == 'top':
                    output += ' on top side, ' + str(leak.location) + ' inches from left.\n'
                elif leak.straw_leak_location == 'bottom':
                    output += ' on bottom side, ' + str(leak.location) + ' inches from left.\n'
                elif leak.straw_leak_location == 'long':
                    output += ' on long straw side, ' + str(leak.location) + ' inches from left.\n'
                else:
                    output += ' on short straw side, ' + str(leak.location) + ' inches from left.\n'
                        
                output += 'Leak Size: ' + str(leak.leak_size) + ' ppm\n\n'
                        
            output += str(leak.description) + '\n\n\n'
            output += '\n\n'
        

        return output
    ##########################################################################

    # Create a procedure
    # Record it in the DB, create/get a straw location
    def ensureProcedure(self):
        # If no procedure has been defined yet, define one.
        if self.procedure is None:
            if self.stage == "panel":
                self.session.startPanelProcedure(
                    process=self.getPro(), panel_number=self.getPanelNumber()
                )
            elif self.stage == "straws":
                self.session.startStrawProcedure(
                    process=self.getPro(),
                    pallet_id=self.getPalletID(),
                    pallet_number=self.getPalletNumber(),
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
        wire_align = None

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
            wire_align = {
                None: None,
                # old panels
                "lower": "Lower 1/3",
                "middle": "Middle 1/3",
                "top": "Top 1/3",
                # new panels
                "short top": "Short, Top",
                "short middle": "Short, Middle",
                "short lower": "Short, Bottom",
                "middle top": "Middle, Top",
                "middle middle": "True Middle",
                "middle lower": "Middle, Bottom",
                "long top": "Long, Top",
                "long middle": "Long, Middle",
                "long lower": "Long, Bottom",
            }[meas.wire_alignment]

        # Return data as list
        return continuity, wire_align

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

    ## PRO-SPECIFIC DATA LOAD

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
            self.getBarcode(panel.getPAAS(L_R=None, letter="A")),  # PAAS A barcode
            self.getBarcode(panel.getPAAS(L_R=None, letter="C")),  # PAAS C barcode
            self.getBarcode(self.procedure.getLPAL(top_bot="top")),  # Upper LPAL
            self.getBarcode(self.procedure.getLPAL(top_bot="bot")),  # Lower LPAL
        ]

    # Straws
    def loadDataProcess2(self):
        panel = self.panel()
        return [
            self.getBarcode(self.panel()),  # Panel
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
            self.getBarcode(panel.getPAAS(L_R=None, letter="B")),  # PAAS B barcode
            self.procedure.getElapsedTime(),  # get elapsed time for main timer
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
            self.procedure.getInitialWireWeight(),  # initial wire spool weight
            self.procedure.getFinalWireWeight(),  # final wire spool weight
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
            self.procedure.getElapsedTime(),  # get elapsed time for main timer
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
            self.getBarcode(panel.getMiddleRib2()),  # Right Middle Rib
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
            self.procedure.getElapsedTime(),  # get elapsed time for main timer
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
            self.procedure.getEpoxyBatchLeft828(),
            self.procedure.getEpoxyBatchRight828(),
            self.procedure.getElapsedTime(),  # get elapsed time for main timer
        ]

    # Final QC
    def loadDataProcess8(self):
        panel = self.panel()
        # print(
        #    str(self.procedure.getLeftRing())[:4],
        #    "hi",
        #    str(self.procedure.getLeftRing())[4:15],
        #    "hi",
        #    str(self.procedure.getLeftRing())[15:],
        #    "hi",
        #    str(self.procedure.getRightRing())[:4],
        #    "hi",
        #    str(self.procedure.getRightRing())[4:15],
        #    "hi",
        #    str(self.procedure.getRightRing())[15:],
        #    "hi",
        #    str(self.procedure.getCenterRing())[:4],
        #    "hi",
        #    str(self.procedure.getCenterRing())[4:15],
        #    "hi",
        #    str(self.procedure.getCenterRing())[15:]
        # )
        return [
            self.getBarcode(panel),
            self.procedure.getLeftCover(),
            self.procedure.getRightCover(),
            self.procedure.getCenterCover(),
            # 8888 01Jan07 0000 66666A
            str(self.procedure.getLeftRing())[:4]
            if self.procedure.getLeftRing() is not None
            else None,
            str(self.procedure.getLeftRing())[4:11]
            if self.procedure.getLeftRing() is not None
            else None,
            str(self.procedure.getLeftRing())[11:15]
            if self.procedure.getLeftRing() is not None
            else None,
            str(self.procedure.getLeftRing())[15:]
            if self.procedure.getLeftRing() is not None
            else None,
            str(self.procedure.getRightRing())[:4]
            if self.procedure.getRightRing() is not None
            else None,
            str(self.procedure.getRightRing())[4:11]
            if self.procedure.getRightRing() is not None
            else None,
            str(self.procedure.getRightRing())[11:15]
            if self.procedure.getRightRing() is not None
            else None,
            str(self.procedure.getRightRing())[15:]
            if self.procedure.getRightRing() is not None
            else None,
            str(self.procedure.getCenterRing())[:4]
            if self.procedure.getCenterRing() is not None
            else None,
            str(self.procedure.getCenterRing())[4:11]
            if self.procedure.getCenterRing() is not None
            else None,
            str(self.procedure.getCenterRing())[11:15]
            if self.procedure.getCenterRing() is not None
            else None,
            str(self.procedure.getCenterRing())[15:]
            if self.procedure.getCenterRing() is not None
            else None,
            self.procedure.getStage(),
        ]


# ___  ___      _
# |  \/  |     (_)
# | .  . | __ _ _ _ __
# | |\/| |/ _` | | '_ \
# | |  | | (_| | | | | |
# \_|  |_/\__,_|_|_| |_|
#
#


def main():
    MultipleDataProcessor(object(), save2txt=True, save2SQL=True)


if __name__ == "__main__":
    main()
