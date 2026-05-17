import logging
import threading
import traceback
from time import sleep

import usb.util
import usb.backend.libusb1 as libusb1
import usb.core
import hid

from core.common import BaseItem
#os.environ['PYUSB_DEBUG'] = 'debug'
from core.device import Device
from core.emulator import CommSerial


class N1MMDevice(Device, CommSerial):

    # Init USB device
    def __init__(self, port: str = 'COM4', baud_rate: int = 9600 ):
        Device.__init__(self)
        CommSerial.__init__(self, port=port, baud_rate=baud_rate, rts_cts=False)
        self._logger = logging.getLogger(__name__)

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
                self._logger.debug("Collecting N1MM data..." + str(self._serial.dsr))
                self._last_value = self._serial.dsr



