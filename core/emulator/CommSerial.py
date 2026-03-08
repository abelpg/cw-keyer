import logging

import serial
import serial.tools.list_ports

class CommSerial:
    def __init__(self, port: str = 'COM4', baud_rate: int = 9600, rts_cts = False):
        self._logger = logging.getLogger(__name__)
        self._logger.debug(f"Initializing CommSerial with serial port {port} with baud rate {baud_rate} and rts/cts flow control {rts_cts}.")
        self._port = port
        self._baud_rate = baud_rate
        self._rts_cts = rts_cts

        self._serial = None

    def start(self):
        if self._serial is None:
            self._serial = serial.Serial()
            self._serial.baudrate = self._baud_rate
            self._serial.port = self._port

            self._serial.rtscts = self._rts_cts
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

    @staticmethod
    def list_ports():
        ports = serial.tools.list_ports.comports()
        return (port for  port, desc, hwid in ports)

