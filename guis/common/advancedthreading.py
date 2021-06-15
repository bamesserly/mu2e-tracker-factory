from threading import Thread, Event
from datetime import datetime

import logging

logger = logging.getLogger("root")


class StopThread(Thread):
    def stop(self):
        return self.join()


class ReusableThread(StopThread):
    def __init__(
        self, group=None, target=None, name=None, args=(), kwargs={}, daemon=None
    ):
        # Initialize thread
        StopThread.__init__(
            self,
            group=group,
            target=target,
            name=name,
            args=args,
            kwargs=kwargs,
            daemon=daemon,
        )

        # Save initialization args that won't be accessible after thread is started
        self.__target = target
        self.__args = args
        self.__kwargs = kwargs

        # Initialize method executed event
        self._method_executed = Event()

    def _resetThread(self):
        Thread.__init__(
            self,
            target=self.__target,
            name=self.getName(),
            args=self.__args,
            kwargs=self.__kwargs,
            daemon=self.isDaemon(),
        )

    def start(self):
        if not self.is_alive():
            StopThread.start(self)

    def join(self):
        if self.is_alive():
            Thread.join(self)
        self._resetThread()


class LoopingThread(StopThread):
    def __init__(
        self,
        target=None,
        name=None,
        args=(),
        kwargs={},
        daemon=None,
        execute_interval=1,
    ):
        StopThread.__init__(self, name=name, daemon=daemon)
        self._stop_event = Event()
        self._execute_interval = execute_interval

        # Save call of target, args, and kwargs. This will function as if target(*args,**kwargs) is being called repeatedly
        self._callable = lambda: target(*args, *kwargs) if target is not None else None

    def start(self):
        if not self.is_alive():
            StopThread.start(self)

    def join(self):
        if not self._stop_event.is_set():
            self._stop_event.set()
        if self.is_alive():
            Thread.join(self)
            # Call method one final time
            self._callable()

    def run(self):

        try:
            # Call target method right away
            self._callable()

            # Create new stop event
            self._stop_event = Event()

            # Begin loop waiting one execute_interval of time before running running again
            while not self._stop_event.wait(self._execute_interval):
                self._callable()
        except Exception as e:
            logger.warning(e)


class LoopingReusableThread(ReusableThread, LoopingThread):
    def __init__(
        self,
        group=None,
        target=None,
        name=None,
        args=(),
        kwargs={},
        daemon=None,
        execute_interval=1,
    ):
        ReusableThread.__init__(self, name=name, daemon=daemon)
        LoopingThread.__init__(
            self,
            target=target,
            name=name,
            args=args,
            kwargs=kwargs,
            daemon=daemon,
            execute_interval=execute_interval,
        )

    def join(self):
        LoopingThread.join(self)
        ReusableThread.join(self)

    def run(self):
        LoopingThread.run(self)


if __name__ == "__main__":
    pass
