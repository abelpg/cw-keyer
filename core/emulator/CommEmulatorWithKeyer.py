import serial
from time import sleep
from core.keyer import KeyerObserver


class CommEmulatorWithKeyer(KeyerObserver):

    def __init__(self):
        super().__init__()

        self._serial = None


    def start(self):
        if self._serial is None:
            self._serial = serial.Serial()
            self._serial.baudrate = 19200
            self._serial.port = 'COM4'

            self._serial.rtscts = True
            self._serial.dtr = False
            self._serial.rts = False

            self._serial.parity = serial.PARITY_NONE
            self._serial.bytesize = serial.EIGHTBITS
            self._serial.stopbits = serial.STOPBITS_ONE

            self._serial.open()
        else:
            print("Serial port is already open. Please call stop() method before starting again.")

    def stop(self):
        if self._serial is not None:
            self._serial.close()
            self._serial = None
    """
    Proxy method to translate the dit and dah events to keyboard events.
    """
    def play_dah(self,time_dah:float, silence: float):
        print("on dah")
        self._serial.dtr = True
        sleep(time_dah)
        self._serial.dtr = False

        sleep(silence)

    """
    Proxy method to translate the dit and dah events to keyboard events.
    """
    def play_dit(self, time_dit: float, silence: float):
        print("on dit")
        self._serial.dtr = True
        sleep(time_dit)
        self._serial.dtr = False

        sleep(silence)

