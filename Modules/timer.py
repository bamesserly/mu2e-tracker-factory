import sys
from pathlib import Path
from datetime import datetime, timedelta
from time import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from advancedthreading import LoopingReusableThread


class Timer:
    def __init__(self, elapsed_time=timedelta(), start_time=None):
        self._elapsed_time = elapsed_time
        self._start_time = start_time

    def setElapsedTime(self, time_delta):
        self._elapsed_time = time_delta
        self.display()

    def getElapsedTime(self):
        seconds = self._elapsed_time.total_seconds()
        if self.isRunning():
            seconds += time() - self.getStartTime()
        return timedelta(seconds=seconds)

    def setStartTime(self, start_time):
        self._start_time = start_time
        self.display()

    def getStartTime(self):
        return self._start_time

    def start(self):
        if self.getStartTime() is None:
            self.setStartTime(time())

    def stop(self):
        if self.getStartTime() is not None:
            self.setElapsedTime(self.getElapsedTime())
            self.setStartTime(None)
            self.display()

    def reset(self):
        if self.isRunning():
            self.stop()
        self.setElapsedTime(timedelta())
        self.display()

    def display(self):
        print(str(self.getElapsedTime()))

    def wasStarted(self):
        return bool(self.getElapsedTime())

    def isRunning(self):
        return self.getStartTime() is not None

    def hmsTuple(self):
        current = int(self.getElapsedTime().total_seconds())
        h = int(current / 3600)
        m = int(current / 60) % 60
        s = int(current) % 60
        return h, m, s


class ThreadTimer(Timer, LoopingReusableThread):
    def __init__(self, elapsed_time=timedelta(), start_time=None):
        Timer.__init__(self, elapsed_time=elapsed_time, start_time=start_time)
        LoopingReusableThread.__init__(self, target=self.display)

    def start(self):
        Timer.start(self)
        LoopingReusableThread.start(self)

    def stop(self):
        # Stop timer
        Timer.stop(self)
        # Re-Initialize thread
        LoopingReusableThread.join(self)


class QLCDTimer(ThreadTimer):
    def __init__(
        self,
        hour_disp,
        min_disp,
        sec_disp,
        emit_signal,
        max_time=float("inf"),
        elapsed_time=timedelta(),
        start_time=None,
    ):
        super().__init__(elapsed_time, start_time)

        # Initialize the QLCDNumber displays
        self.hour_disp = hour_disp
        self.min_disp = min_disp
        self.sec_disp = sec_disp
        self.__default_QLCD_display()

        # Max time - display turns red if elapsed time passes this number
        self.max_time = max_time

        # Connect the signal so that when emitted the current time is displayed
        self.emitSignal = emit_signal

    def getQLCDNumbers(self):
        return self.hour_disp, self.min_disp, self.sec_disp

    def display(self):
        for n, qlcd in zip(self.hmsTuple(), self.getQLCDNumbers()):
            qlcd.display(n)
        self.__checkMaxTime()

    def __checkMaxTime(self):
        if float(self.getElapsedTime().total_seconds()) > self.max_time:
            for qlcd in self.getQLCDNumbers():
                qlcd.setStyleSheet("background-color:rgb(255, 0, 0)")

    def __default_QLCD_display(self):
        for qlcd in self.getQLCDNumbers():
            qlcd.setNumDigits(2)
            qlcd.setSegmentStyle(2)


if __name__ == "__main__":
    pass
