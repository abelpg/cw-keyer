import logging

from PySide6 import QtWidgets

from core.emulator import CommEmulatorWithKeyer, KeyboardEmulator
from core.keyer import Keyer
from core.sound import SoundProcessor


class KeyerForm:
    def __init__(self, parent: QtWidgets.QBoxLayout,
                 callback_attach_device_observer=None,
                 callback_detach_device_observer=None):

        self._callback_attach_device_observer = callback_attach_device_observer
        self._callback_detach_device_observer = callback_detach_device_observer
        self._logger = logging.getLogger(__name__)

        self._keyer = None
        self._comm_emulator_with_keyer = None
        self._keyer = None
        ####
        self._sound_processor = None

        layout = QtWidgets.QVBoxLayout()
        widget = QtWidgets.QWidget()

        self._button_keyer = QtWidgets.QPushButton("Keyer")
        self._button_keyer.clicked.connect(self._click_keyer)
        layout.addWidget(self._button_keyer)

        self._button_comm_emulator_with_keyer = QtWidgets.QPushButton("Comm emulator with keyer")
        self._button_comm_emulator_with_keyer.clicked.connect(self._click_comm_emulator_with_keyer)
        layout.addWidget(self._button_comm_emulator_with_keyer)

        self._button_sound_processor = QtWidgets.QPushButton("Sound processor")
        self._button_sound_processor.clicked.connect(self._click_sound_processor)
        layout.addWidget(self._button_sound_processor)

        widget.setLayout(layout)
        parent.addWidget(widget)

    def _start_sound_processor(self):
        if self._sound_processor is None:
            self._sound_processor = SoundProcessor()
            self._sound_processor.start()
            self._keyer.attach_observer(self._sound_processor)

            self._button_sound_processor.setStyleSheet("background-color: green; ")
            self._logger.debug("Sound processor started.")
        else:
            self._logger.debug("Sound keyer is already running.")

    def _stop_sound_processor(self):
        if self._sound_processor is not None:
            self._sound_processor.stop()
            self._keyer.detach_observer(self._sound_processor)
            self._sound_processor = None

            self._button_sound_processor.setStyleSheet("background-color: red; ")
            self._logger.debug("Sound processor stopped.")
        else:
            self._logger.debug("Sound keyer is not running, skipping stop.")

    def _start_comm_emulator_with_keyer(self):
        if self._comm_emulator_with_keyer is None:
            self._comm_emulator_with_keyer = CommEmulatorWithKeyer()
            self._comm_emulator_with_keyer.start()
            self._keyer.attach_observer(self._comm_emulator_with_keyer)

            self._button_comm_emulator_with_keyer.setStyleSheet("background-color: green; ")
            self._logger.debug("Comm emulator started.")
        else:
            self._logger.debug("Comm emulator is already running.")

    def _stop_comm_emulator_with_keyer(self):
        if self._comm_emulator_with_keyer is not None:
            if self._keyer is not None:
                self._keyer.detach_observer(self._comm_emulator_with_keyer)

            self._comm_emulator_with_keyer.stop()
            self._comm_emulator_with_keyer = None
            self._button_comm_emulator_with_keyer.setStyleSheet("background-color: red; ")
            self._logger.debug("Comm emulator stopped.")
        else:
            self._logger.debug("Comm emulator is not running, skipping stop.")

    def _click_keyer(self):
        if self._keyer is None:
            self.start()
        else:
            self.stop()

    def _click_sound_processor(self):
        if self._sound_processor is None:
            self._start_sound_processor()
        else:
            self._stop_sound_processor()

    def _click_comm_emulator_with_keyer(self):
        if self._comm_emulator_with_keyer is None:
            self._start_comm_emulator_with_keyer()
        else:
            self._stop_comm_emulator_with_keyer()

    def stop(self):
        if self._keyer is not None:
            self._stop_sound_processor()
            self._callback_detach_device_observer(self._keyer)
            self._keyer.stop()
            self._keyer = None

            self._button_keyer.setStyleSheet("background-color: red; ")
            self._logger.debug("Keyer stopped.")
        else:
            self._logger.debug("Keyer is not running, skipping stop.")

    def start(self):
        if self._keyer is None:
            self._keyer = Keyer(wpm=20)
            self._keyer.start()

            self._callback_attach_device_observer(self._keyer)

            self._start_sound_processor()

            self._button_keyer.setStyleSheet("background-color: green; ")
            self._logger.debug("Keyer started.")
        else:
            self._logger.debug("Keyer is already running.")