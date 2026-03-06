import logging
from logging import Logger

import serial
from time import sleep

from core.device import DeviceObserver


class CommEmulator(DeviceObserver):

    def __init__(self):
        super().__init__()

        self._logger = logging.getLogger(__name__)

        self._serial = None

    def start(self):
        if self._serial is None:
            self._serial = serial.Serial()
            self._serial.baudrate = 9600
            self._serial.port = 'COM4'

            self._serial.rtscts = False
            self._serial.dtr = False
            self._serial.rts = False

            self._serial.parity = serial.PARITY_NONE
            self._serial.bytesize = serial.EIGHTBITS
            self._serial.stopbits = serial.STOPBITS_ONE

            self._serial.open()
        else:
            self._logger.warning("Serial port is already open. Please call stop() method before starting again.")

    def stop(self):
        if self._serial is not None:
            self._serial.close()
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