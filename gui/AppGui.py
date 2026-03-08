import logging

from core.emulator import KeyboardEmulator
from gui.CommEmulatorNoKeyerForm import CommEmulatorNoKeyerForm
from gui.DevicesForm import DevicesForm
from gui.keyer.KeyerForm import KeyerForm

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
        self.setMinimumSize(400,400)
        self._create_form()

        self._keyboard_emulator = None

    def _create_form(self):
        self._layout = QtWidgets.QVBoxLayout(self)

        self._devices_form = DevicesForm(self._layout, device_stopped_callback=self._device_stopped, device_started_callback=self._device_started)

        self._layout.addWidget(QtWidgets.QFrame(frameShape=QtWidgets.QFrame.HLine))

        self._layout.addWidget(QtWidgets.QLabel("Send direct output from key to comm (CWType):"))
        self._comm_emulator_form = CommEmulatorNoKeyerForm(self._layout,
                                                           callback_attach_device_observer=self._devices_form.attach_observer,
                                                           callback_detach_device_observer=self._devices_form.detach_observer)

        self._layout.addWidget(QtWidgets.QFrame(frameShape=QtWidgets.QFrame.HLine))

        self._layout.addWidget(QtWidgets.QLabel("Send output from key to Ctr+L / Ctr+R (morse invaders):"))
        self._button_keyboard_emulator = QtWidgets.QPushButton("Keyboard emulator")
        self._button_keyboard_emulator.clicked.connect(self._click_keyboard_emulator)
        self._layout.addWidget(self._button_keyboard_emulator)

        self._layout.addWidget(QtWidgets.QFrame(frameShape=QtWidgets.QFrame.HLine))

        self._keyer_form = KeyerForm(self._layout,
                                    callback_attach_device_observer=self._devices_form.attach_observer,
                                    callback_detach_device_observer=self._devices_form.detach_observer)



    def _stop(self, from_device_form=False):
        self._keyer_form.stop()
        self._stop_keyboard_emulator()
        self._comm_emulator_form.stop()
        #self._stop_comm_emulator_with_keyer()
        if not from_device_form:
            self._devices_form.stop_all()


    def _click_keyboard_emulator(self):
        if self._keyboard_emulator is None:
            self._start_keyboard_emulator()
        else:
            self._stop_keyboard_emulator()

    def _start_keyboard_emulator(self):
        if self._keyboard_emulator is  None:
            self._keyboard_emulator = KeyboardEmulator()
            self._devices_form.attach_observer(self._keyboard_emulator)

            self._button_keyboard_emulator.setStyleSheet("background-color: green; ")
            self._logger.debug("Keyboard emulator started.")
        else:
            self._logger.debug("Keyboard keyer is already running.")

    def _stop_keyboard_emulator(self):
        if self._keyboard_emulator is not None:
            self._devices_form.detach_observer(self._keyboard_emulator)
            self._keyboard_emulator = None

            self._button_keyboard_emulator.setStyleSheet("background-color: red; ")
            self._logger.debug("Keyboard emulator stopped.")
        else:
            self._logger.debug("Keyboard keyer is not running, skipping stop.")

    def _device_started(self):
        self._keyer_form.start()

    def _device_stopped(self):
        self._stop(True)

    def show(self):
        super().show()
        self._devices_form.start()


    def closeEvent(self, event):
        self._stop()
        super().closeEvent(event)





