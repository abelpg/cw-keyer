import logging

from core.device import Device

class HidDevice (Device):

    def __init__(self):
        super().__init__()
        self._logger = logging.getLogger(__name__)


    def start(self):
        self._logger.debug("HidDevice.start")

    def stop(self):
        self._logger.debug("HidDevice.stop")

