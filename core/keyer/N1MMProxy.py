import logging
import threading

from time import  time
from core.emulator import CommSerial
from core.keyer import Keyer



class N1MMProxy( CommSerial):

    # Init USB device
    def __init__(self, keyer : Keyer, port: str = 'COM4', baud_rate: int = 9600 ):
        CommSerial.__init__(self, port=port, baud_rate=baud_rate, rts_cts=False)
        self._logger = logging.getLogger(__name__)


        self._keyer = keyer
        self._thread = None
        self._last_value = None
        self._last_time = None

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

                self._last_value = self._serial.dsr
                if self._last_value:
                    self._last_time = time()
                    self._keyer.proxy_on()
                else:
                    timer = 0 if self._last_time is None else (time() - self._last_time)
                    self._logger.debug("Collecting N1MM data...  in " + str(timer))
                    self._keyer.proxy_off()





