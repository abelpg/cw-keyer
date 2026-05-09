import logging

from PySide6 import QtWidgets
from gui.common import SerialForm
from core.keyer import CommEmulatorWithKeyer

class CommEmulatorKeyerForm(SerialForm):

    def __init__(self,parent: QtWidgets.QBoxLayout, call_back_get_keyer=None):

        super().__init__(parent, __name__, button_text="Comm emulator with keyer",
                         callback_click=self._click_comm_emulator)

        self._logger = logging.getLogger(__name__)

        self._get_keyer = call_back_get_keyer

    def _click_comm_emulator(self):
        if self._get_keyer().is_serial_started():
            self.stop()
        else:
            self.start()


    def start(self):
        if not self._get_keyer().is_serial_started():
            self._get_keyer().start_serial(self._get_port())
            self._button_comm_emulator.setStyleSheet("background-color: green; ")
            self._logger.debug("Comm emulator started.")
        else:
            self._logger.debug("Comm emulator is already running.")

    def stop(self):
        if self._get_keyer().is_serial_started():
            self._get_keyer().stop_serial()
            self._button_comm_emulator.setStyleSheet("background-color: red; ")
            self._logger.debug("Comm emulator stopped.")
        else:
            self._logger.debug("Comm emulator is not running, skipping stop.")