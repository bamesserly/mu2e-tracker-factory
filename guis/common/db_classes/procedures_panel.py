################################################################################
# Panel Process Metadata Classes/Tables
#
# These classes define the procedure_details_panX tables. These tables hold
# info specific to each process. Epoxy batch numbers and timers, process-wide
# measurements, select part numbers. There is one entry in each table for each
# procedure (panel, process AKA straw_location, station) pair. So the use of
# "procedure" is correct in that each entry represents a procedure, however
# each /table/ more generally represents a process. Read these tables to learn
# about which measurements are performed/saved in each process.
#
# For example, process 1:
#
# __tablename__ = "procedure_details_pan1"
#   id = Column(Integer, primary_key=True)
#   procedure = Column(Integer, ForeignKey("procedure.id"))
#   left_gap = Column(Integer)
#   right_gap = Column(Integer)
#   min_BP_BIR_gap = Column(Integer)
#   max_BP_BIR_gap = Column(Integer)
#   epoxy_batch = Column(Integer)
#   epoxy_time = Column(Integer)
#   epoxy_time_running = Column(BOOLEAN)
#   epoxy_time_timestamp = Column(Integer)
#   lpal_top = Column(Integer, ForeignKey("straw_location.id"))
#   lpal_bot = Column(Integer, ForeignKey("straw_location.id"))
#
################################################################################
from guis.common.db_classes.bases import BASE, OBJECT, DM, logger
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
from guis.common.db_classes.procedure import PanelProcedure


# IR
class Pan1Procedure(PanelProcedure):
    __mapper_args__ = {"polymorphic_identity": "pan1"}

    def __init__(self, station, straw_location, create_key):
        assert (
            station.id == "pan1"
        ), f"Error. Tried to construct Pan1Procedure for a station '{station.id}' not 'pan1'."
        super().__init__(station, straw_location, create_key)

    def _getDetailsClass(self):
        class Details(BASE, OBJECT):
            __tablename__ = "procedure_details_pan1"
            id = Column(Integer, primary_key=True)
            procedure = Column(Integer, ForeignKey("procedure.id"))
            left_gap = Column(Integer)
            right_gap = Column(Integer)
            min_BP_BIR_gap = Column(Integer)
            max_BP_BIR_gap = Column(Integer)
            epoxy_batch = Column(Integer)
            epoxy_time = Column(Integer)
            epoxy_time_running = Column(BOOLEAN)
            epoxy_time_timestamp = Column(Integer)
            lpal_top = Column(Integer, ForeignKey("straw_location.id"))
            lpal_bot = Column(Integer, ForeignKey("straw_location.id"))

        return Details

    # Getters/Setters

    def _setLPAL(self, lpal, top_bot):
        if top_bot in ["top", "bot"]:
            if top_bot == "top":
                self.details.lpal_top = lpal.id
            if top_bot == "bot":
                self.details.lpal_bot = lpal.id
            self.commit()

    # Change straw's present location from an LPAL to a panel
    def loadFromLPAL(self, lpal_num, top_bot):
        from guis.common.db_classes.straw_location import StrawLocation

        # Query Objects

        # If this LPAL number is new, commit a new LPAL entry to the straw
        # location table. Else, get the existing entry from the db. Either way,
        # return the corresponding LoadingPallet object.
        lpal = StrawLocation.LPAL(lpal_num)
        straws = lpal.getStraws()
        panel = self.getPanel()
        # Equation mapping lpal straw list index to panel position
        position = lambda pos: 2 * pos + {"top": 1, "bot": 0}[top_bot]
        # Execute all removes from lpal and moves to panel.
        entries = []
        for i in range(len(straws)):
            s = straws[i]
            if s is None:
                continue
            entries.append(lpal.removeStraw(s, commit=False))
            entries.append(panel.addStraw(straw=s, position=position(i), commit=False))
        DM.commitEntries(entries)
        # Record LPAL in details table aswell
        self._setLPAL(lpal, top_bot)

    def getLPAL(self, top_bot):
        from guis.common.db_classes.straw_location import LoadingPallet

        # Get id from details class
        lpal_id = {"top": self.details.lpal_top, "bot": self.details.lpal_bot}[top_bot]
        # Return result of Query for Loading Pallet
        # Note, this will return None if no lpal
        # has been recorded yet.
        return LoadingPallet.queryWithId(lpal_id)

    def getLeftGap(self):
        return self.details.left_gap

    def recordLeftGap(self, gap):
        self.details.left_gap = gap
        self.commit()

    def getRightGap(self):
        return self.details.right_gap

    def recordRightGap(self, gap):
        self.details.right_gap = gap
        self.commit()

    def getMinBPBIRGap(self):
        return self.details.min_BP_BIR_gap

    def recordMinBPBIRGap(self, gap):
        self.details.min_BP_BIR_gap = gap
        self.commit()

    def getMaxBPBIRGap(self):
        return self.details.max_BP_BIR_gap

    def recordMaxBPBIRGap(self, gap):
        self.details.max_BP_BIR_gap = gap
        self.commit()

    def getEpoxyBatch(self):
        return self.details.epoxy_batch

    def recordEpoxyBatch(self, batch):
        self.details.epoxy_batch = batch
        self.commit()

    def getEpoxyTime(self):
        if self.details.epoxy_time_running == 0:
            return self.details.epoxy_time
        if self.details.epoxy_time_running == 1:
            return (
                int(datetime.now().timestamp())
                - self.details.epoxy_time_timestamp
                + self.details.epoxy_time
            )

    def getEpoxyTimeRunning(self):
        return self.details.epoxy_time_running

    def recordEpoxyTime(self, duration, running):
        self.details.epoxy_time = duration
        self.details.epoxy_time_running = running
        self.commit()


# Straws
class Pan2Procedure(PanelProcedure):
    __mapper_args__ = {"polymorphic_identity": "pan2"}

    def __init__(self, station, straw_location, create_key):
        assert (
            station.id == "pan2"
        ), f"Error. Tried to construct Pan2Procedure for a station '{station.id}' not 'pan2'."
        super().__init__(station, straw_location, create_key)

    def _getDetailsClass(self):
        class Details(BASE, OBJECT):
            __tablename__ = "procedure_details_pan2"
            id = Column(Integer, primary_key=True)
            procedure = Column(Integer, ForeignKey("procedure.id"))
            lpal_top = Column(Integer, ForeignKey("straw_location.id"))
            lpal_bot = Column(Integer, ForeignKey("straw_location.id"))
            epoxy_batch_lower = Column(Integer)
            epoxy_time_lower = Column(Integer)
            epoxy_time_running_lower = Column(BOOLEAN)
            epoxy_batch_upper = Column(Integer)
            epoxy_time_upper = Column(Integer)
            epoxy_time_running_upper = Column(BOOLEAN)
            PAAS_A_max_temp = Column(Integer)
            PAAS_B_max_temp = Column(Integer)
            heat_time = Column(Integer)
            heat_time_running = Column(BOOLEAN)
            epoxy_time_upper_timestamp = Column(Integer)
            epoxy_time_lower_timestamp = Column(Integer)

        return Details

    # Getters/Setters

    def getEpoxyBatchLower(self):
        return self.details.epoxy_batch_lower

    def recordEpoxyBatchLower(self, batch):
        self.details.epoxy_batch_lower = batch
        self.commit()

    def getEpoxyTimeLower(self):
        if self.details.epoxy_time_running_lower == 0:
            return self.details.epoxy_time_lower
        if self.details.epoxy_time_running_lower == 1:
            return (
                int(datetime.now().timestamp())
                - self.details.epoxy_time_lower_timestamp
                + self.details.epoxy_time_lower
            )

    def getEpoxyTimeRunningLower(self):
        return self.details.epoxy_time_running_lower

    def recordEpoxyTimeLower(self, duration, running):
        self.details.epoxy_time_lower = duration
        self.details.epoxy_time_running_lower = running
        self.commit()

    def getEpoxyBatchUpper(self):
        return self.details.epoxy_batch_upper

    def recordEpoxyBatchUpper(self, batch):
        self.details.epoxy_batch_upper = batch
        self.commit()

    def getEpoxyTimeUpper(self):
        if self.details.epoxy_time_running_upper == 0:
            return self.details.epoxy_time_upper
        if self.details.epoxy_time_running_upper == 1:
            return (
                int(datetime.now().timestamp())
                - self.details.epoxy_time_upper_timestamp
                + self.details.epoxy_time_upper
            )

    def getEpoxyTimeRunningUpper(self):
        return self.details.epoxy_time_running_upper

    def recordEpoxyTimeUpper(self, duration, running):
        self.details.epoxy_time_upper = duration
        self.details.epoxy_time_running_upper = running
        self.commit()

    def getPaasAMaxTemp(self):
        return self.details.PAAS_A_max_temp

    def recordPaasAMaxTemp(self, temp):
        self.details.PAAS_A_max_temp = temp
        self.commit()

    def getPaasBMaxTemp(self):
        return self.details.PAAS_B_max_temp

    def recordPaasBMaxTemp(self, temp):
        self.details.PAAS_B_max_temp = temp
        self.commit()

    def getHeatTime(self):
        return self.details.heat_time

    def getHeatTimeRunning(self):
        return self.details.heat_time_running

    def recordHeatTime(self, time, running):
        self.details.heat_time = time
        self.details.heat_time_running = running
        self.commit()

    def recordStrawTension(self, position, tension, uncertainty):
        from guis.common.db_classes.measurements_panel import StrawTensionMeasurement

        StrawTensionMeasurement(
            procedure=self, position=position, tension=tension, uncertainty=uncertainty
        ).commit()


# Wire Tensions
class Pan3Procedure(PanelProcedure):
    __mapper_args__ = {"polymorphic_identity": "pan3"}

    def __init__(self, station, straw_location, create_key):
        assert (
            station.id == "pan3"
        ), f"Error. Tried to construct Pan3Procedure for a station '{station.id}' not 'pan3'."
        super().__init__(station, straw_location, create_key)

    def _getDetailsClass(self):
        class Details(BASE, OBJECT):
            __tablename__ = "procedure_details_pan3"
            id = Column(Integer, primary_key=True)
            procedure = Column(Integer, ForeignKey("procedure.id"), primary_key=True)
            sense_wire_insertion_time = Column(REAL)
            sense_wire_insertion_time_running = Column(BOOLEAN)
            wire_spool = Column(Integer, ForeignKey("wire_spool.id"))
            wire_weight_initial = Column(REAL)
            wire_weight_final = Column(REAL)

        return Details

    def getSenseWireInsertionTime(self):
        return self.details.sense_wire_insertion_time

    def getSenseWireInsertionTimeRunning(self):
        return self.details.sense_wire_insertion_time_running

    def recordSenseWireInsertionTime(self, duration, running):
        self.details.sense_wire_insertion_time = duration
        self.details.sense_wire_insertion_time_running = running
        self.commit()

    def getWireSpool(self):
        from guis.common.db_classes.supplies import WireSpool

        return WireSpool.queryWithId(self.details.wire_spool)

    def recordWireSpool(self, number):
        from guis.common.db_classes.supplies import WireSpool

        spool = DM.query(WireSpool).filter(WireSpool.id == number).one_or_none()
        if not spool:
            return False  # Return false if wire spool can't be found in database
        self.details.wire_spool = spool.id
        return True

    def getInitialWireWeight(self):
        return self.details.wire_weight_initial

    def recordInitialWireWeight(self, weight):
        self.details.wire_weight_initial = weight

    def getFinalWireWeight(self):
        return self.details.wire_weight_final

    def recordFinalWireWeight(self, weight):
        self.details.wire_weight_final = weight

    # Continuity Measurements
    class MeasurementPan3(BASE, OBJECT):
        __tablename__ = "measurement_pan3"
        id = Column(Integer, primary_key=True)
        procedure = Column(Integer, ForeignKey("procedure.id"))
        position = Column(Integer)
        left_continuity = Column(BOOLEAN)
        right_continuity = Column(BOOLEAN)
        wire_alignment = Column("wire_position", VARCHAR)

        def __init__(
            self, procedure, position, left_continuity, right_continuity, wire_alignment
        ):
            self.id = self.ID()
            self.procedure = procedure
            self.position = position
            self.left_continuity = left_continuity
            self.right_continuity = right_continuity
            self.wire_alignment = wire_alignment

        def __repr__(self):
            return (
                "<MeasurementPan3(id='%s', procedure='%s', position='%s', left_continuity='%s', right_continuity='%s', wire_alignment='%s')>"
                % (
                    self.id,
                    self.procedure,
                    self.position,
                    self.left_continuity,
                    self.right_continuity,
                    self.wire_alignment,
                )
            )

        def isCompletelyDefined(self):
            data = [
                self.procedure,
                self.position,
                self.left_continuity,
                self.right_continuity,
                self.wire_alignment,
            ]
            return all([x is not None for x in data])

        def recordLeftContinuity(self, boolean):
            self.left_continuity = boolean

        def recordRightContinuity(self, boolean):
            self.right_continuity = boolean

        def recordContinuity(self, left_continuity, right_continuity):
            self.recordLeftContinuity(left_continuity)
            self.recordRightContinuity(right_continuity)

        def recordWireAlignment(self, alignment):
            self.wire_alignment = alignment

        def getPosition(self):
            return self.position

        def getLeftContinuity(self):
            return self.left_continuity

        def getRightContinuity(self):
            return self.right_continuity

        def getWireAlignment(self):
            return self.wire_alignment

    def recordContinuityMeasurement(
        self, position, left_continuity, right_continuity, wire_alignment
    ):
        # Check if a measurement has alread been made at this position
        meas = self._queryMeasurement(position).one_or_none()

        # If so, update continuity and resistance
        if meas:
            meas.recordContinuity(left_continuity, right_continuity)
            meas.recordWireAlignment(wire_alignment)

        # If not, construct a new one with all data defined
        else:
            meas = Pan3Procedure.MeasurementPan3(
                procedure=self.id,
                position=position,
                left_continuity=left_continuity,
                right_continuity=right_continuity,
                wire_alignment=wire_alignment,
            )

        # If all data is defined, commit (updated) measurement
        if meas.isCompletelyDefined():
            # attr = vars(meas)
            # print("=====",', '.join("%s: %s" % item for item in attr.items()))
            return meas.commit()

    def getContinuityMeasurements(self):
        measurements = self._queryMeasurements().all()
        lst = [None for _ in range(96)]
        for m in measurements:
            lst[m.position] = m
        return lst

    def getContinuityMeasurement(self, position):
        return self._queryMeasurement(position).one_or_none()

    def _queryMeasurement(self, position):
        return self._queryMeasurements().filter(
            Pan3Procedure.MeasurementPan3.position == position
        )

    def _queryMeasurements(self):
        return (
            Pan3Procedure.MeasurementPan3.query()
            .filter(Pan3Procedure.MeasurementPan3.procedure == self.id)
            .order_by(Pan3Procedure.MeasurementPan3.position.asc())
        )

    # Wire Tensioner Measurements
    def recordWireTension(self, position, tension, wire_timer, calibration_factor):
        from guis.common.db_classes.measurements_panel import WireTensionMeasurement

        WireTensionMeasurement(
            procedure=self,
            position=position,
            tension=tension,
            wire_timer=wire_timer,
            calibration_factor=calibration_factor,
        ).commit()

    # hv measurements
    def getHVMeasurements(self):
        measurements = self._queryMeasurementsHV().all()
        lst = []
        for m in measurements:
            lst += [m]
        return lst

    def _queryMeasurementHV(self, position):
        from guis.common.db_classes.measurements_panel import MeasurementPan5

        return self._queryMeasurementsHV().filter(MeasurementPan5.position == position)

    def _queryMeasurementsHV(self):
        from guis.common.db_classes.measurements_panel import MeasurementPan5

        return (
            MeasurementPan5.query()
            .filter(MeasurementPan5.procedure == self.id)
            .order_by(MeasurementPan5.position.asc())
        )

    def recordHVMeasurement(self, position, side, current, voltage, is_tripped):
        from guis.common.db_classes.measurements_panel import MeasurementPan5

        MeasurementPan5(
            procedure=self.id,
            position=position,
            current_left=current if side == "Left" else None,
            current_right=current if side == "Right" else None,
            voltage=voltage,
            is_tripped=is_tripped,
        ).commit()


# Pin Protectors
class Pan4Procedure(PanelProcedure):
    __mapper_args__ = {"polymorphic_identity": "pan4"}

    def __init__(self, station, straw_location, create_key):
        assert (
            station.id == "pan4"
        ), f"Error. Tried to construct Pan4Procedure for a station '{station.id}' not 'pan4'."
        super().__init__(station, straw_location, create_key)

    # All but the timestamp columns are collected here
    def _getDetailsClass(self):
        class Details(BASE, OBJECT):
            __tablename__ = "procedure_details_pan4"
            id = Column(Integer, primary_key=True)
            procedure = Column(Integer, ForeignKey("procedure.id"))
            clear_epoxy_left_batch = Column(Integer)
            clear_epoxy_left_application_duration = Column(Integer)
            clear_epoxy_left_cure_duration = Column(Integer)
            clear_epoxy_left_time_is_running = Column(BOOLEAN)
            clear_epoxy_right_batch = Column(Integer)
            clear_epoxy_right_application_duration = Column(Integer)
            clear_epoxy_right_cure_duration = Column(Integer)
            clear_epoxy_right_time_is_running = Column(BOOLEAN)
            silver_epoxy_left_batch = Column(Integer)
            silver_epoxy_left_application_duration = Column(Integer)
            silver_epoxy_left_cure_duration = Column(Integer)
            silver_epoxy_left_time_is_running = Column(BOOLEAN)
            silver_epoxy_right_batch = Column(Integer)
            silver_epoxy_right_application_duration = Column(Integer)
            silver_epoxy_right_cure_duration = Column(Integer)
            silver_epoxy_right_time_is_running = Column(BOOLEAN)

        # attr = vars(Details)
        # print("=====",', '.join("%s: %s" % item for item in attr.items()))

        return Details

    #####################
    ## Getters/Setters ##
    #####################

    #####################
    ## Epoxy Batch IDs ##
    #####################
    # Clear left
    def getClearEpoxyLeftBatch(self):
        return self.details.clear_epoxy_left_batch

    def recordClearEpoxyLeftBatch(self, batch):
        self.details.clear_epoxy_left_batch = batch
        self.commit()

    # Clear right
    def getClearEpoxyRightBatch(self):
        return self.details.clear_epoxy_right_batch

    def recordClearEpoxyRightBatch(self, batch):
        self.details.clear_epoxy_right_batch = batch
        self.commit()

    # Silver left
    def getSilverEpoxyLeftBatch(self):
        return self.details.silver_epoxy_left_batch

    def recordSilverEpoxyLeftBatch(self, batch):
        self.details.silver_epoxy_left_batch = batch
        self.commit()

    # Silver right
    def getSilverEpoxyRightBatch(self):
        return self.details.silver_epoxy_right_batch

    def recordSilverEpoxyRightBatch(self, batch):
        self.details.silver_epoxy_right_batch = batch
        self.commit()

    ##############################
    ## Epoxy application timing ##
    ##############################
    # Clear left
    def getClearEpoxyLeftApplicationDuration(self):
        return self.details.clear_epoxy_left_application_duration

    def recordClearEpoxyLeftApplicationDuration(self, duration, running):
        self.details.clear_epoxy_left_application_duration = duration
        self.details.clear_epoxy_left_time_is_running = running
        self.commit()

    # Clear right
    def getClearEpoxyRightApplicationDuration(self):
        return self.details.clear_epoxy_right_application_duration

    def recordClearEpoxyRightApplicationDuration(self, duration, running):
        self.details.clear_epoxy_right_application_duration = duration
        self.details.clear_epoxy_right_time_is_running = running
        self.commit()

    # Silver left
    def getSilverEpoxyLeftApplicationDuration(self):
        return self.details.silver_epoxy_left_application_duration

    def recordSilverEpoxyLeftApplicationDuration(self, duration, running):
        self.details.silver_epoxy_left_application_duration = duration
        self.details.silver_epoxy_left_time_is_running = running
        self.commit()

    # Silver right
    def getSilverEpoxyRightApplicationDuration(self):
        return self.details.silver_epoxy_right_application_duration

    def recordSilverEpoxyRightApplicationDuration(self, duration, running):
        self.details.silver_epoxy_right_application_duration = duration
        self.details.silver_epoxy_right_time_is_running = running
        self.commit()

    #######################
    ## Epoxy cure timing ##
    #######################
    # Clear left
    def getClearEpoxyLeftCureDuration(self):
        return self.details.clear_epoxy_left_cure_duration

    def recordClearEpoxyLeftCureDuration(self, duration, running):
        self.details.clear_epoxy_left_cure_duration = duration
        self.details.clear_epoxy_left_time_is_running = running
        self.commit()

    # Clear right
    def getClearEpoxyRightCureDuration(self):
        return self.details.clear_epoxy_right_cure_duration

    def recordClearEpoxyRightCureDuration(self, duration, running):
        self.details.clear_epoxy_right_cure_duration = duration
        self.details.clear_epoxy_right_time_is_running = running
        self.commit()

    # Silver left
    def getSilverEpoxyLeftCureDuration(self):
        return self.details.silver_epoxy_left_cure_duration

    def recordSilverEpoxyLeftCureDuration(self, duration, running):
        self.details.silver_epoxy_left_cure_duration = duration
        self.details.silver_epoxy_left_time_is_running = running
        self.commit()

    # Silver right
    def getSilverEpoxyRightCureDuration(self):
        return self.details.silver_epoxy_right_cure_duration

    def recordSilverEpoxyRightCureDuration(self, duration, running):
        self.details.silver_epoxy_right_cure_duration = duration
        self.details.silver_epoxy_right_time_is_running = running
        self.commit()

    ##########################
    ## Get time_is_running ##
    ##########################
    def getClearEpoxyLeftTimeIsRunning(self):
        return self.details.clear_epoxy_left_time_is_running

    def getClearEpoxyRightTimeIsRunning(self):
        return self.details.clear_epoxy_right_time_is_running

    def getSilverEpoxyLeftTimeIsRunning(self):
        return self.details.silver_epoxy_left_time_is_running

    def getSilverEpoxyRightTimeIsRunning(self):
        return self.details.silver_epoxy_right_time_is_running


# HV
class Pan5Procedure(PanelProcedure):
    __mapper_args__ = {"polymorphic_identity": "pan5"}

    def __init__(self, station, straw_location, create_key):
        assert (
            station.id == "pan5"
        ), f"Error. Tried to construct Pan5Procedure for a station '{station.id}' not 'pan5'."
        super().__init__(station, straw_location, create_key)

    # There's nothing we want to save here that isn't wire-by-wire
    def _getDetailsClass(self):
        # Should this have an ID? An autoincrementing one?
        class Details(BASE, OBJECT):
            __tablename__ = "procedure_details_pan5"
            # id            = Column(Integer, primary_key =True)
            procedure = Column(Integer, ForeignKey("procedure.id"), primary_key=True)

        return Details

    def recordHVMeasurement(self, position, side, current, voltage, is_tripped):
        from guis.common.db_classes.measurements_panel import MeasurementPan5

        record = MeasurementPan5(
            procedure=self.id,
            position=position,
            current_left=current if side == "Left" else None,
            current_right=current if side == "Right" else None,
            voltage=voltage,
            is_tripped=is_tripped,
        )
        return record.commit()

    def getHVMeasurements(self):
        measurements = self._queryMeasurements().all()
        lst = [None for _ in range(96)]
        for m in measurements:
            lst[m.position] = m
        return lst

    def getHVMeasurement(self, position):
        return self._queryMeasurement(position).one_or_none()

    def _queryMeasurement(self, position):
        from guis.common.db_classes.measurements_panel import MeasurementPan5

        return self._queryMeasurements().filter(MeasurementPan5.position == position)

    def _queryMeasurements(self):
        from guis.common.db_classes.measurements_panel import MeasurementPan5

        return (
            MeasurementPan5.query()
            .filter(MeasurementPan5.procedure == self.id)
            .order_by(MeasurementPan5.position.asc())
        )


# Manifold
class Pan6Procedure(PanelProcedure):
    __mapper_args__ = {"polymorphic_identity": "pan6"}

    def __init__(self, station, straw_location, create_key):
        assert (
            station.id == "pan6"
        ), f"Error. Tried to construct Pan6Procedure for a station '{station.id}' not 'pan6'."
        super().__init__(station, straw_location, create_key)

    def _getDetailsClass(self):
        class Details(BASE, OBJECT):
            __tablename__ = "procedure_details_pan6"
            id = Column(Integer, primary_key=True)
            procedure = Column(Integer, ForeignKey("procedure.id"), primary_key=True)
            baseplate_ribs_MIR_gap_left = Column(Integer)
            baseplate_ribs_MIR_gap_right = Column(Integer)
            base_plate_epoxy_batch = Column(Integer)
            baseplate_installation_time = Column(REAL)
            baseplate_installation_time_running = Column(BOOLEAN)
            frame_epoxy_batch_wetting = Column(Integer)
            frame_epoxy_batch_bead = Column(Integer)
            frame_installation_time = Column(REAL)
            frame_installation_time_running = Column(BOOLEAN)
            PAAS_A_max_temp = Column(REAL)
            PAAS_C_max_temp = Column(REAL)
            heat_time = Column(Integer)
            heat_time_running = Column(BOOLEAN)

        return Details

    def getBaseplateRibsMIRGapLeft(self):
        return self.details.baseplate_ribs_MIR_gap_left

    def recordBaseplateRibsMIRGapLeft(self, gap):
        self.details.baseplate_ribs_MIR_gap_left = gap
        self.commit()

    def getBaseplateRibsMIRGapRight(self):
        return self.details.baseplate_ribs_MIR_gap_right

    def recordBaseplateRibsMIRGapRight(self, gap):
        self.details.baseplate_ribs_MIR_gap_right = gap
        self.commit()

    def getBaseplateEpoxyBatch(self):
        return self.details.base_plate_epoxy_batch

    def recordBaseplateEpoxyBatch(self, batch):
        self.details.base_plate_epoxy_batch = batch
        self.commit()

    def getBaseplateInstallationTime(self):
        return self.details.baseplate_installation_time

    def getBaseplateInstallationTimeRunning(self):
        return self.details.baseplate_installation_time_running

    def recordBaseplateInstallationTime(self, time, running):
        self.details.baseplate_installation_time = time
        self.details.baseplate_installation_time_running = running
        self.commit()

    def getFrameEpoxyBatchWetting(self):
        return self.details.frame_epoxy_batch_wetting

    def recordFrameEpoxyBatchWetting(self, batch):
        self.details.frame_epoxy_batch_wetting = batch
        self.commit()

    def getFrameEpoxyBatchBead(self):
        return self.details.frame_epoxy_batch_bead

    def recordFrameEpoxyBatchBead(self, batch):
        self.details.frame_epoxy_batch_bead = batch
        self.commit()

    def getFrameInstallationTime(self):
        return self.details.frame_installation_time

    def getFrameInstallationTimeRunning(self):
        return self.details.frame_installation_time_running

    def recordFrameInstallationTime(self, time, running):
        self.details.frame_installation_time = time
        self.details.frame_installation_time_running = running
        self.commit()

    def getPaasAMaxTemp(self):
        return self.details.PAAS_A_max_temp

    def recordPaasAMaxTemp(self, temp):
        self.details.PAAS_A_max_temp = temp
        self.commit()

    def getPaasCMaxTemp(self):
        return self.details.PAAS_C_max_temp

    def recordPaasCMaxTemp(self, temp):
        self.details.PAAS_C_max_temp = temp
        self.commit()

    def getHeatTime(self):
        return self.details.heat_time

    def getHeatTimeRunning(self):
        return self.details.heat_time_running

    def recordHeatTime(self, time, running):
        self.details.heat_time = time
        self.details.heat_time_running = running
        self.commit()

    # HV measurements

    def getHVMeasurements(self):
        measurements = self._queryMeasurementsHV().all()
        lst = []
        for m in measurements:
            lst += [m]
        return lst

    def _queryMeasurementHV(self, position):
        from guis.common.db_classes.measurements_panel import MeasurementPan5

        return self._queryMeasurementsHV().filter(MeasurementPan5.position == position)

    def _queryMeasurementsHV(self):
        from guis.common.db_classes.measurements_panel import MeasurementPan5

        return (
            MeasurementPan5.query()
            .filter(MeasurementPan5.procedure == self.id)
            .order_by(MeasurementPan5.position.asc())
        )

    def recordHVMeasurement(self, position, side, current, voltage, is_tripped):
        from guis.common.db_classes.measurements_panel import MeasurementPan5

        MeasurementPan5(
            procedure=self.id,
            position=position,
            current_left=current if side == "Left" else None,
            current_right=current if side == "Right" else None,
            voltage=voltage,
            is_tripped=is_tripped,
        ).commit()


# Flooding
class Pan7Procedure(PanelProcedure):
    __mapper_args__ = {"polymorphic_identity": "pan7"}

    def __init__(self, station, straw_location, create_key):
        assert (
            station.id == "pan7"
        ), f"Error. Tried to construct Pan7Procedure for a station '{station.id}' not 'pan7'."
        super().__init__(station, straw_location, create_key)

    def _getDetailsClass(self):
        class Details(BASE, OBJECT):
            __tablename__ = "procedure_details_pan7"
            id = Column(Integer, primary_key=True)
            procedure = Column(Integer, ForeignKey("procedure.id"))
            epoxy_batch_left = Column(Integer)
            epoxy_time_left = Column(Integer)
            epoxy_time_left_running = Column(BOOLEAN)
            epoxy_batch_right = Column(Integer)
            epoxy_time_right = Column(Integer)
            epoxy_time_right_running = Column(BOOLEAN)
            epoxy_time_left_timestamp = Column(Integer)
            epoxy_time_right_timestamp = Column(Integer)
            epoxy_batch_left_828 = Column(Integer)
            epoxy_batch_right_828 = Column(Integer)

        return Details

    def getEpoxyBatchLeft828(self):
        return self.details.epoxy_batch_left_828

    def getEpoxyBatchRight828(self):
        return self.details.epoxy_batch_right_828

    def recordEpoxyBatchLeft828(self, batch):
        self.details.epoxy_batch_left_828 = batch
        self.commit()

    def recordEpoxyBatchRight828(self, batch):
        self.details.epoxy_batch_right_828 = batch
        self.commit()

    def getEpoxyBatchLeft(self):
        return self.details.epoxy_batch_left

    def recordEpoxyBatchLeft(self, batch):
        self.details.epoxy_batch_left = batch
        self.commit()

    def getEpoxyTimeLeft(self):
        if self.details.epoxy_time_left_running == 0:
            return self.details.epoxy_time_left
        if self.details.epoxy_time_left_running == 1:
            return (
                int(datetime.now().timestamp())
                - self.details.epoxy_time_left_timestamp
                + self.details.epoxy_time_left
            )

    def getEpoxyTimeLeftRunning(self):
        return self.details.epoxy_time_left_running

    def recordEpoxyTimeLeft(self, time, running):
        self.details.epoxy_time_left = time
        self.details.epoxy_time_left_running = running
        self.commit()

    def getEpoxyBatchRight(self):
        return self.details.epoxy_batch_right

    def recordEpoxyBatchRight(self, batch):
        self.details.epoxy_batch_right = batch
        self.commit()

    def getEpoxyTimeRight(self):
        if self.details.epoxy_time_right_running == 0:
            return self.details.epoxy_time_right
        if self.details.epoxy_time_right_running == 1:
            return (
                int(datetime.now().timestamp())
                - self.details.epoxy_time_right_timestamp
                + self.details.epoxy_time_right
            )

    def getEpoxyTimeRightRunning(self):
        return self.details.epoxy_time_right_running

    def recordEpoxyTimeRight(self, time, running):
        self.details.epoxy_time_right = time
        self.details.epoxy_time_right_running = running
        self.commit()


# Process 8
class Pan8Procedure(PanelProcedure):
    __mapper_args__ = {"polymorphic_identity": "pan8"}

    def __init__(self, station, straw_location, create_key):
        assert (
            station.id == "pan8"
        ), f"Error. Tried to construct Pan8Procedure for a station '{station.id}' not 'pan8'."
        super().__init__(station, straw_location, create_key)

    def _getDetailsClass(self):
        class Details(BASE, OBJECT):
            __tablename__ = "procedure_details_pan8"
            id = Column(Integer, primary_key=True)
            procedure = Column(Integer, ForeignKey("procedure.id"))

            left_cover = Column(Integer)
            center_cover = Column(Integer)
            right_cover = Column(Integer)

            left_ring = Column(String)
            center_ring = Column(String)
            right_ring = Column(String)

            leak_rate = Column(Integer)

            stage = Column(String)

        return Details

    def getLeftCover(self):
        return self.details.left_cover

    def recordLeftCover(self, left_cover):
        self.details.left_cover = left_cover
        self.commit()

    def getRightCover(self):
        return self.details.right_cover

    def recordRightCover(self, right_cover):
        self.details.right_cover = right_cover
        self.commit()

    def getCenterCover(self):
        return self.details.center_cover

    def recordCenterCover(self, center_cover):
        self.details.center_cover = center_cover
        self.commit()

    def getLeftRing(self):
        return self.details.left_ring

    def recordLeftRing(self, left_ring):
        self.details.left_ring = left_ring
        self.commit()

    def getRightRing(self):
        return self.details.right_ring

    def recordRightRing(self, right_ring):
        self.details.right_ring = right_ring
        self.commit()

    def getCenterRing(self):
        return self.details.center_ring

    def recordCenterRing(self, center_ring):
        self.details.center_ring = center_ring
        self.commit()

    def record_leak_rate(self, lr):
        self.details.leak_rate = lr
        self.commit()

    def get_leak_rate(self):
        return self.details.leak_rate

    def recordStage(self, stage):
        self.details.stage = stage
        self.commit()

    def getStage(self):
        return self.details.stage

    def getBadWires(self):
        wires = self._queryBadWires().all()
        lst = []
        logger.debug(wires)
        for w in wires:
            lst.append(w)
        return lst

    def _queryBadWire(self, position):
        from guis.common.db_classes.measurements_panel import BadWire

        return self._queryBadWires().filter(BadWire.position == position)

    def _queryBadWires(self):
        from guis.common.db_classes.measurements_panel import BadWire

        return (
            BadWire.query()
            .filter(BadWire.procedure == self.id)
            .order_by(BadWire.position.asc())
        )
