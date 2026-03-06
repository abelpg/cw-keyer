import logging

from PySide6 import QtWidgets

from core.emulator import CommEmulatorWithKeyer
from gui.common.SerialForm import SerialForm

class CommEmulatorKeyerForm(SerialForm):

    def __init__(self, parent: QtWidgets.QBoxLayout,
                 callback_attach_device_observer=None,
                 callback_detach_device_observer=None):

        super().__init__(parent, __name__, button_text="Comm emulator with keyer",
                         callback_click=self._click_comm_emulator)

        self._logger = logging.getLogger(__name__)

        self._callback_attach_device_observer = callback_attach_device_observer
        self._callback_detach_device_observer = callback_detach_device_observer

        self._keyer = None
        self._comm_emulator_with_keyer = None



    def _click_comm_emulator(self):
        if self._comm_emulator_with_keyer is None:
            self.start()
        else:
            self.stop()


    def start(self):
        if self._comm_emulator_with_keyer is None:
            self._comm_emulator_with_keyer = CommEmulatorWithKeyer()
            self._comm_emulator_with_keyer.start()
            self._callback_attach_device_observer(self._comm_emulator_with_keyer)

            self._button_comm_emulator.setStyleSheet("background-color: green; ")
            self._logger.debug("Comm emulator started.")
        else:
            self._logger.debug("Comm emulator is already running.")

    def stop(self):
        if self._comm_emulator_with_keyer is not None:
            if self._keyer is not None:
                self._keyer.detach_observer(self._comm_emulator_with_keyer)
            self._comm_emulator_with_keyer.stop()
            self._comm_emulator_with_keyer = None
            self._button_comm_emulator.setStyleSheet("background-color: red; ")
            self._logger.debug("Comm emulator stopped.")
        else:
            self._logger.debug("Comm emulator is not running, skipping stop.")