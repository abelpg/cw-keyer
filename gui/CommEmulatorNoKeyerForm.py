import logging

from PySide6 import QtWidgets
from core.emulator import CommEmulator
from gui.common.SerialForm import SerialForm

class CommEmulatorNoKeyerForm(SerialForm):

    def __init__(self, parent: QtWidgets.QBoxLayout,
                 callback_attach_device_observer=None,
                 callback_detach_device_observer=None):
        super().__init__(parent, __name__, button_text= "Comm emulator",callback_click=self._click_comm_emulator )
        self._callback_attach_device_observer = callback_attach_device_observer
        self._callback_detach_device_observer = callback_detach_device_observer
        self._logger = logging.getLogger(__name__)


    def _start_comm_emulator(self):
        # Protect concurrent loop
        if self._comm_emulator is  None:
            self._comm_emulator = CommEmulator(port=super()._get_port())
            self._callback_attach_device_observer(self._comm_emulator)
            self._comm_emulator.start()
            self._button_comm_emulator.setStyleSheet("background-color: green; ")
            self._logger.debug("Comm emulator started.")
        else:
            self._logger.debug("Comm emulator is already running.")

    def _stop_comm_emulator(self):
        if self._comm_emulator is not None:
            self._callback_detach_device_observer(self._comm_emulator)
            self._comm_emulator.stop()
            self._comm_emulator = None
            self._button_comm_emulator.setStyleSheet("background-color: red; ")
            self._logger.debug("Comm emulator stopped.")
        else:
            self._logger.debug("Comm emulator is not running, skipping stop.")

    def _click_comm_emulator(self):
        if self._comm_emulator is None:
            self._start_comm_emulator()
        else:
            self._stop_comm_emulator()

    def stop(self):
        self._stop_comm_emulator()