import logging
from concurrent.futures import ThreadPoolExecutor
from time import sleep

from core.emulator.CommSerial import CommSerial


class CommEmulatorWithKeyer(CommSerial):


    def __init__(self, port: str = 'COM4', baud_rate: int = 9600):
        CommSerial.__init__(self, port=port, baud_rate=baud_rate, rts_cts=True)

        self._executor = ThreadPoolExecutor(max_workers=4)

        self._logger = logging.getLogger(__name__)

    def send(self, duration):
        self._executor.submit(self._background_send, duration)

    def turn_on(self):
        if not self._serial.dtr:
            self._logger.debug("Turning on DTR.")
            self._serial.dtr = True

    def turn_off(self):
        if self._serial.dtr:
            self._logger.debug("Turning on DTR.")
            self._serial.dtr = False

    def _background_send(self, duration):
        if self._serial is not None:
            self.turn_on()
            sleep(duration)
            self.turn_off()

