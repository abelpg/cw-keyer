import logging
from core.emulator.CommSerial import CommSerial

class CommEmulatorWithKeyer(CommSerial):

    def __init__(self, port: str = 'COM4', baud_rate: int = 115200):
        CommSerial.__init__(self, port=port, baud_rate=baud_rate, rts_cts=True)

        self._logger = logging.getLogger(__name__)

    def on(self):
        if self._serial is not None:
            self._logger.debug("Turning on DTR.")
            self._serial.dtr = True

    def off(self):
        if self._serial is not None:
            self._logger.debug("Turning off DTR.")
            self._serial.dtr = False
