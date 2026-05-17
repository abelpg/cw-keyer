import logging
import queue
import threading

from time import time, sleep
from core.emulator import CommSerial
from core.keyer import Keyer
from numpy import round

class ItemSound:

    def __init__(self, duration: float, sound : bool ):
        self.duration = duration
        self.sound = sound

    def __str__(self):
        return "[" + str(self.duration) + "s, sound: " + str(self.sound) + "]"

class N1MMProxy( CommSerial):

    # Init USB device
    def __init__(self, keyer : Keyer, port: str = 'COM4', baud_rate: int = 9600 ):
        CommSerial.__init__(self, port=port, baud_rate=baud_rate, rts_cts=False)

        self._logger = logging.getLogger(__name__)

        self._keyer = keyer
        self._thread = None
        self._last_value = None


    def start(self):
        if  self._serial is  None:
            self._logger.info("N1MM Starting")
            self._thread = threading.Thread(target=self._run_dtr_collect, daemon=True)
            CommSerial.start(self)
            self._thread.start()

    def stop(self):
        if self._serial is not None:
            CommSerial.stop(self)

    def is_running(self):
        return self._serial is not None


    def _run_dtr_collect(self):

        while self._serial is not None:
            if self._serial is not None and self._last_value != self._serial.dsr:
                self._logger.debug("N1MM DTR Collecting " +str(self._serial.dsr)+" dsr")

                self._last_value = self._serial.dsr
                self._keyer.proxy_n1mm(self._last_value)






