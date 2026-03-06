import logging
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
        self._thread_pool = ThreadPoolExecutor(max_workers=4, thread_name_prefix="UsbDevice observers ThreadPool")

    def attach_observer(self, observer: DeviceObserver):
        self._logger.debug("attach observer to device")
        self._observers.append(observer)

    def detach_observer(self, observer: DeviceObserver):
        self._logger.debug("detach observer to device")
        self._observers.remove(observer)

    def _set_dit(self, dit):
        self._dit = dit
        if len(self._observers) > 0:
            for observer in self._observers:
                self._thread_pool.submit(observer.on_dit,dit)
        else:
            self._logger.warning("No observers attached to device, skipping notification dit.")


    def _set_dah(self, dah):
        self._dah = dah
        if len(self._observers) > 0:
            for observer in self._observers:
                self._thread_pool.submit(observer.on_dah,dah)
        else:
            self._logger.warning("No observers attached to device, skipping notification dah.")

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass