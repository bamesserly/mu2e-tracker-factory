from datetime import timedelta
import time
from threading import Thread


class Timer:
    def __init__(self, elapsed_time=timedelta(), start_time=None):
        self.elapsed_time = elapsed_time
        self.start_time = start_time
        if self.elapsed_time:
            self.started = True
        else:
            self.started = False

    def start(self):
        if self.start_time is None:
            self.start_time = self.now()
            if not self.started:
                self.started = True

    def stop(self):
        if self.start_time is not None:
            self.elapsed_time = self.getElapsedTime()
            self.start_time = None

    def clear(self):
        self.elapsed_time = timedelta()
        self.start_time = None

    def wasStarted(self):
        return self.started

    def isRunning(self):
        return self.start_time is not None

    def setElapsedTime(self, time_delta):
        self.elapsed_time = time_delta

    def getElapsedTime(self):
        seconds = self.elapsed_time.total_seconds()
        if self.isRunning():
            seconds += self.now() - self.start_time
        return timedelta(seconds=seconds)

    def hmsTuple(self):
        current = int(self.getElapsedTime().total_seconds())
        h = int(current / 3600)
        m = int(current / 60) % 60
        s = int(current) % 60
        return h, m, s

    @staticmethod
    def now():
        return time.time()


class QLCDTimer(Timer):
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

    def start(self):
        super().start()
        self.__startThreadMethod()

    def stop(self):
        super().stop()
        self.display()

    def clear(self):
        super().clear()
        self.display()

    def setElapsedTime(self, time_delta):
        super().setElapsedTime(time_delta)
        self.display()

    def reset(self):
        self.clear()
        self.display()

    def __getHMSDisplays(self):
        return self.hour_disp, self.min_disp, self.sec_disp

    def display(self):
        for n, qlcd in zip(self.hmsTuple(), self.__getHMSDisplays()):
            qlcd.display(n)
        self.__checkMaxTime()

    def __checkMaxTime(self):
        if float(self.getElapsedTime().total_seconds()) > self.max_time:
            for qlcd in self.__getHMSDisplays():
                qlcd.setStyleSheet("background-color:rgb(255, 0, 0)")

    def __default_QLCD_display(self):
        for qlcd in self.__getHMSDisplays():
            qlcd.setNumDigits(2)
            qlcd.setSegmentStyle(2)

    def __startThreadMethod(self):
        Thread(target=self.__threadMethod, daemon=True).start()

    def __threadMethod(self):
        update = 0
        while True:
            if self.isRunning():
                update += 1
                if update % 25 == 0:
                    self.emitSignal()
                time.sleep(0.01)
            else:
                break
