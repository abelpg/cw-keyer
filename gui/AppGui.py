import logging
import sys

from core.emulator import CommEmulatorWithKeyer, KeyboardEmulator, CommEmulator
from core.keyer import Keyer
from core.sound import SoundProcessor
from core.device import UsbDevice, KeyboardDevice
from gui.DevicesForm import DevicesForm

# Logi 0x046d:0xc52b
# Key 0x413d:0x2107

try:
    from PySide6 import  QtWidgets
    from PySide6.QtWidgets import  QWidget
except Exception:
    QtWidgets = None
    QWidget = None

class AppGui(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._logger = logging.getLogger(__name__)

        self.setWindowTitle("Keyer application")
        #self.resize(800, 600)
        self.setMinimumSize(300, 300)
        self._create_form()

        ################################################################################################################

        self._comm_emulator_with_keyer = None
        self._comm_emulator = None
        self._keyboard_emulator = None
        self._keyer = None
        ####
        self._sound_processor = None


    def _create_form(self):
        self._layout = QtWidgets.QVBoxLayout(self)

        self._devices_form = DevicesForm(self._layout, stop_callback=self._stop)

        self._layout.addWidget(QtWidgets.QFrame(frameShape=QtWidgets.QFrame.HLine))

        self._button_keyer = QtWidgets.QPushButton("Keyer")
        self._button_keyer.clicked.connect(self._click_keyer)
        self._layout.addWidget(self._button_keyer)

        self._layout_comm_emulator = QtWidgets.QHBoxLayout()
        self._layout_comm_emulator_widget = QtWidgets.QWidget()
        self._layout_comm_emulator_widget.setMaximumHeight(45)

        self._layout_comm_emulator_widget.setLayout(self._layout_comm_emulator)

        self._button_comm_emulator = QtWidgets.QPushButton("Comm emulator")
        self._button_comm_emulator.clicked.connect(self._click_comm_emulator)

        self._comm_emulator_port =   QtWidgets.QTextEdit()
        self._comm_emulator_port.setText("COM4")
        self._comm_emulator_port.setMaximumHeight(25)
        self._comm_emulator_port.setMaximumWidth(100)

        self._layout_comm_emulator.addWidget(self._button_comm_emulator)
        self._layout_comm_emulator.addWidget(self._comm_emulator_port)

        self._layout.addWidget(self._layout_comm_emulator_widget)

        self._button_keyboard_emulator = QtWidgets.QPushButton("Keyboard emulator")
        self._button_keyboard_emulator.clicked.connect(self._click_keyboard_emulator)
        self._layout.addWidget(self._button_keyboard_emulator)

        self._button_comm_emulator_with_keyer = QtWidgets.QPushButton("Comm emulator with keyer")
        self._button_comm_emulator_with_keyer.clicked.connect(self._click_comm_emulator_with_keyer)
        self._layout.addWidget(self._button_comm_emulator_with_keyer)

        self._button_sound_processor = QtWidgets.QPushButton("Sound processor")
        self._button_sound_processor.clicked.connect(self._click_sound_processor)
        self._layout.addWidget(self._button_sound_processor)

    def _start_sound_processor(self):
        if self._sound_processor is None:
            self._start_keyer()
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

    def _start_keyboard_emulator(self):
        if self._keyboard_emulator is  None:
            self._keyboard_emulator = KeyboardEmulator()
            self._devices_form.attach_observer(self._comm_emulator)

            self._button_keyboard_emulator.setStyleSheet("background-color: green; ")
            self._logger.debug("Keyboard emulator started.")
        else:
            self._logger.debug("Keyboard keyer is already running.")

    def _stop_keyboard_emulator(self):
        if self._keyboard_emulator is not None:
            self._devices_form.detach_observer(self._comm_emulator)
            self._keyboard_emulator = None

            self._button_keyboard_emulator.setStyleSheet("background-color: red; ")
            self._logger.debug("Keyboard emulator stopped.")
        else:
            self._logger.debug("Keyboard keyer is not running, skipping stop.")

    def _start_comm_emulator(self):
        # Protect concurrent loop
        if self._comm_emulator is  None:
            self._comm_emulator = CommEmulator()
            self._devices_form.attach_observer(self._comm_emulator)
            self._comm_emulator.start()

            self._button_comm_emulator.setStyleSheet("background-color: green; ")
            self._logger.debug("Comm emulator started.")
        else:
            self._logger.debug("Comm emulator is already running.")

    def _stop_comm_emulator(self):
        if self._comm_emulator is not None:
            self._devices_form.detach_observer(self._comm_emulator)
            self._comm_emulator.stop()
            self._comm_emulator = None
            self._button_comm_emulator.setStyleSheet("background-color: red; ")
            self._logger.debug("Comm emulator stopped.")
        else:
            self._logger.debug("Comm emulator is not running, skipping stop.")

    def _start_keyer(self):
        if self._keyer is None:
            self._keyer = Keyer(wpm=20)
            self._keyer.start()

            self._devices_form.attach_observer(self._keyer)

            self._start_sound_processor()

            self._button_keyer.setStyleSheet("background-color: green; ")
            self._logger.debug("Keyer started.")
        else:
            self._logger.debug("Keyer is already running.")

    def _stop_keyer(self):
        if self._keyer is not None:

            self._stop_sound_processor()
            self._devices_form.detach_observer(self._keyer)
            self._keyer.stop()
            self._keyer = None

            self._button_keyer.setStyleSheet("background-color: red; ")
            self._logger.debug("Keyer stopped.")
        else:
            self._logger.debug("Keyer is not running, skipping stop.")

    def _stop(self):

        self._stop_keyer()
        self._stop_keyboard_emulator()
        self._stop_comm_emulator()
        self._stop_comm_emulator_with_keyer()
        self._devices_form.stop_all()


    def _click_keyer(self):
        if self._keyer is None:
            self._start_keyer()
        else:
            self._stop_keyer()

    def _click_keyboard_emulator(self):
        if self._keyboard_emulator is None:
            self._start_keyboard_emulator()
        else:
            self._stop_keyboard_emulator()

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

    def _click_comm_emulator(self):
        if self._comm_emulator is None:
            self._start_comm_emulator()
        else:
            self._stop_comm_emulator()

    def show(self):
        super().show()
        self._devices_form.start()
        self._start_keyer()


    def closeEvent(self, event):
        self._stop()
        super().closeEvent(event)





