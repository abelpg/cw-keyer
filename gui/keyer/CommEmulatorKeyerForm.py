import logging

from PySide6 import QtWidgets
from gui.common import SerialForm
from core.keyer import CommEmulatorWithKeyer

class CommEmulatorKeyerForm(SerialForm):

    def __init__(self,
                 parent: QtWidgets.QBoxLayout):

        super().__init__(parent, __name__, button_text="Comm emulator with keyer",
                         callback_click=self._click_comm_emulator)

        self._logger = logging.getLogger(__name__)

        self._keyer = None
        self._comm_emulator_with_keyer = None

    def _click_comm_emulator(self):
        if self._comm_emulator_with_keyer is None:
            self.start()
        else:
            self.stop()

    def on_serial(self):
        if self._comm_emulator_with_keyer is not None:
            self._comm_emulator_with_keyer.on()

    def off_serial(self):
        if self._comm_emulator_with_keyer is not None:
            self._comm_emulator_with_keyer.off()

    def start(self):
        if self._comm_emulator_with_keyer is None:
            self._comm_emulator_with_keyer = CommEmulatorWithKeyer(port=self._get_port())
            self._comm_emulator_with_keyer.start()
            self._button_comm_emulator.setStyleSheet("background-color: green; ")
            self._logger.debug("Comm emulator started.")
        else:
            self._logger.debug("Comm emulator is already running.")

    def stop(self):
        if self._comm_emulator_with_keyer is not None:
            self._comm_emulator_with_keyer.stop()
            self._comm_emulator_with_keyer = None
            self._button_comm_emulator.setStyleSheet("background-color: red; ")
            self._logger.debug("Comm emulator stopped.")
        else:
            self._logger.debug("Comm emulator is not running, skipping stop.")