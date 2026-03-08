import logging
from logging import Logger

import serial
from time import sleep

from core.device import DeviceObserver
from core.emulator.CommSerial import CommSerial


class CommEmulator(DeviceObserver, CommSerial):

    def __init__(self, port: str = 'COM4', baud_rate: int = 9600):
        DeviceObserver.__init__(self)
        CommSerial.__init__(self, port=port, baud_rate=baud_rate, rts_cts=False)

        self._logger = logging.getLogger(__name__)
        self._serial = None

    """
    Proxy method to translate the dit and dah events to keyboard events.
    """
    def on_dah(self, pressed: bool):
        self._logger.debug("DAH: " + str(pressed))
        self._serial.rts = pressed


    """
    Proxy method to translate the dit and dah events to keyboard events.
    """
    def on_dit(self, pressed: bool):
        self._logger.debug("DIT: " + str(pressed))
        self._serial.dtr = pressed