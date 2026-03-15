import logging

from time import sleep
from core.emulator.CommSerial import CommSerial
from core.keyer import KeyerObserver, KeyerItem


class CommEmulatorWithKeyer(KeyerObserver, CommSerial):

    def __init__(self, port: str = 'COM4', baud_rate: int = 9600):
        KeyerObserver.__init__(self)
        CommSerial.__init__(self, port=port, baud_rate=baud_rate, rts_cts=True)

        self._logger = logging.getLogger(__name__)
        self._serial = None

    """
    Proxy method to translate the dit and dah events to serial.
    """
    def _process_item(self, keyer_item : KeyerItem):
        self._logger.debug("Processing keyer item with time: " + str(keyer_item.time) + " and silence: " + str(keyer_item.silence))
        self._serial.dtr = True
        sleep(keyer_item.time)
        self._serial.dtr = False
        sleep(keyer_item.silence)

    def start(self):
        CommSerial.start(self)
        KeyerObserver.start(self)

    def stop(self):
        CommSerial.stop(self)
        KeyerObserver.stop(self)

