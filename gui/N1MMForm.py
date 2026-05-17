import logging

from PySide6 import QtWidgets
from gui.common.SerialForm import SerialForm
from core.device import N1MMDevice
from core.config import Configuration
class N1MMForm(SerialForm):

    def __init__(self, parent: QtWidgets.QBoxLayout):
        super().__init__(parent, __name__, button_text="N1MM input port", callback_click=self._click_comm_emulator)
        self._comm_n1mm = None


    def _start_comm_emulator(self):
        # Protect concurrent loop
        if self._comm_n1mm is  None:
            self._comm_n1mm = N1MMDevice(port=super()._get_port())
            self._comm_n1mm.start()
            self._button_comm_emulator.setStyleSheet("background-color: green; ")
            self._logger.debug("Comm N1MM started.")
        else:
            self._logger.debug("Comm N1MM is already running.")

    def _stop_comm_emulator(self):
        if self._comm_n1mm is not None:
            self._comm_n1mm.stop()
            self._comm_n1mm = None
            self._button_comm_emulator.setStyleSheet("background-color: red; ")
            self._logger.debug("Comm N1MM stopped.")
        else:
            self._logger.debug("Comm N1MM is not running, skipping stop.")

    def _click_comm_emulator(self):
        if self._comm_n1mm is None:
            self._start_comm_emulator()
        else:
            self._stop_comm_emulator()

    def start(self):
        self._start_comm_emulator()

    def stop(self):
        self._stop_comm_emulator()