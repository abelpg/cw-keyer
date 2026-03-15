import logging
import time
from typing import List
from concurrent.futures import ThreadPoolExecutor
from core.device import DeviceObserver
from abc import ABC, abstractmethod

class Device(ABC):

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._dit = False
        self._dah = False
        self._observers: List[DeviceObserver] = []

    def attach_observer(self, observer: DeviceObserver):
        self._logger.debug("attach observer to device")
        self._observers.append(observer)

    def detach_observer(self, observer: DeviceObserver):
        self._logger.debug("detach observer to device")
        self._observers.remove(observer)

    def _set_dit(self, dit):
        time_init = time.time()
        self._dit = dit
        if len(self._observers) > 0:
            for observer in self._observers:
                observer.on_dit(dit)
        else:
            self._logger.warning("No observers attached to device, skipping notification dit.")

        self._print_time(time_init, "dit")

    def _set_dah(self, dah):
        time_init = time.time()
        self._dah = dah
        if len(self._observers) > 0:
            for observer in self._observers:
                observer.on_dah(dah)
        else:
            self._logger.warning("No observers attached to device, skipping notification dah.")
        self._print_time(time_init, "dah")

    def _print_time(self, time_init, action):
        if self._logger.isEnabledFor(logging.DEBUG):
            total_time = time.time() - time_init
            total_time = round(total_time, 4)
            self._logger.debug(f"Set {action} took {total_time} seconds.")

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass