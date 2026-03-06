import logging

import serial
from time import sleep

from core.emulator.CommSerial import CommSerial
from core.keyer import KeyerObserver


class CommEmulatorWithKeyer(KeyerObserver, CommSerial):

    def __init__(self, port: str = 'COM4', baud_rate: int = 9600):
        KeyerObserver.__init__(self)
        CommSerial.__init__(self, port=port, baud_rate=baud_rate, rts_cts=True)

        self._logger = logging.getLogger(__name__)
        self._serial = None

    """
    Proxy method to translate the dit and dah events to keyboard events.
    """
    def play_dah(self,time_dah:float, silence: float):
        self._logger.debug("on dah")
        self._serial.dtr = True
        sleep(time_dah)
        self._serial.dtr = False

        sleep(silence)

    """
    Proxy method to translate the dit and dah events to keyboard events.
    """
    def play_dit(self, time_dit: float, silence: float):
        self._logger.debug("on dit")
        self._serial.dtr = True
        sleep(time_dit)
        self._serial.dtr = False

        sleep(silence)

