import logging
import threading
import traceback
from time import sleep

import serial
import usb.util
import usb.backend.libusb1 as libusb1
import usb.core
import hid

from core.common import BaseItem
#os.environ['PYUSB_DEBUG'] = 'debug'
from core.device import Device



class N1MMDevice(Device):

    # Init USB device
    def __init__(self, port: str = 'COM4', baud_rate: int = 9600 ):
        Device.__init__(self)
        self._logger = logging.getLogger(__name__)

        self._port = port
        self._baud_rate = baud_rate
        self._rts_cts = True
        self._thread = None
        self._serial = None
        self._last_value = None

        self._logger.info(
            f"Initializing N1MMDevice with serial port {port} with baud rate {baud_rate} and rts/cts flow control {self._rts_cts}.")

    def start(self):
        if self._serial is None:
            self._serial = serial.Serial()
            self._serial.baudrate = self._baud_rate
            self._serial.port = self._port

            self._serial.parity = serial.PARITY_NONE
            self._serial.bytesize = serial.EIGHTBITS
            self._serial.stopbits = serial.STOPBITS_ONE

            self._serial.dsrdtr = True
            self._serial.rtscts = False

            self._serial.open()

            self._logger.info("N1MM Starting")
            self._thread = threading.Thread(target=self._run_dtr_collect, daemon=True)

            self._thread.start()
        else:
            self._logger.warning("Serial port is already open. Please call stop() method before starting again.")

    def stop(self):
        if self._serial is not None:
            self._serial.close()
            self._serial = None
            self._thread = None

    def is_running(self):
        return self._serial is not None

    def _run_dtr_collect(self):
        while self._serial is not None:
            #if self._serial is not None and self._last_value != self._serial:
            self._last_value = self._serial.rts
            self._logger.debug("Collecting N1MM data..." + str(self._serial.dsr) + " / " + str(self._serial.dtr))
            sleep(0.01)
