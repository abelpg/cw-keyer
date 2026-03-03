import sys

from core.emulator import CommEmulatorWithKeyer, KeyboardEmulator, CommEmulator
from core.keyer import Keyer
from core.sound import SoundProcessor
from core.device import UsbDevice, KeyboardDevice

# Logi 0x046d:0xc52b
# Key 0x413d:0x2107

try:
    from PySide6 import QtCore, QtGui, QtWidgets
    from PySide6.QtWidgets import QApplication, QWidget
except Exception:  # pragma: no cover - optional runtime dependency
    QtCore = None
    QtGui = None
    QtWidgets = None
    QWidget = None

if QtWidgets is not None:
    MainWindowBase = QtWidgets.QMainWindow
else:  # pragma: no cover - fallback for non-GUI modes
    class MainWindowBase:  # type: ignore[too-many-ancestors]
        pass

class App(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Keyer application")
        #self.resize(800, 600)
        self.setMinimumSize(300, 300)
        self._create_form()

        ################################################################################################################
        try:
            self._usb_device = UsbDevice(0x413d,0x2107)
        except Exception as e:
            print("Error initializing USB device: ", e)
            self._usb_device = None

        self._keyboard_device = None
        #####
        self._comm_emulator_with_keyer = None
        self._comm_emulator = None
        self._keyboard_emulator = None
        self._keyer = None
        ####
        self._sound_processor = None


    def _create_form(self):
        self._layout = QtWidgets.QVBoxLayout(self)

        self._button_keyboard_device = QtWidgets.QPushButton("Keyboard device")
        self._button_keyboard_device.clicked.connect(self._click_keyboard_device)
        self._layout.addWidget(self._button_keyboard_device)

        self._button_usb_device = QtWidgets.QPushButton("USB device")
        self._button_usb_device.clicked.connect(self._click_usb_device)
        self._layout.addWidget(self._button_usb_device)


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
            print("Sound processor started.")
        else:
            print("Sound keyer is already running.")

    def _stop_sound_processor(self):
        if self._sound_processor is not None:
            self._sound_processor.stop()
            self._keyer.detach_observer(self._sound_processor)
            self._sound_processor = None

            self._button_sound_processor.setStyleSheet("background-color: red; ")
            print("Sound processor stopped.")
        else:
            print("Sound keyer is not running, skipping stop.")

    def _start_comm_emulator_with_keyer(self):
        if self._comm_emulator_with_keyer is None:
            self._comm_emulator_with_keyer = CommEmulatorWithKeyer()
            self._comm_emulator_with_keyer.start()
            self._keyer.attach_observer(self._comm_emulator_with_keyer)

            self._button_comm_emulator_with_keyer.setStyleSheet("background-color: green; ")
            print("Comm emulator started.")
        else:
            print("Comm emulator is already running.")

    def _stop_comm_emulator_with_keyer(self):
        if self._comm_emulator_with_keyer is not None:

            if self._keyer is not None:
                self._keyer.detach_observer(self._comm_emulator_with_keyer)

            self._comm_emulator_with_keyer.stop()
            self._comm_emulator_with_keyer = None
            self._button_comm_emulator_with_keyer.setStyleSheet("background-color: red; ")
            print("Comm emulator stopped.")
        else:
            print("Comm emulator is not running, skipping stop.")

    def _start_keyboard_emulator(self):
        # Protect concurrent loop
        self._stop_keyboard_device()

        if self._keyboard_emulator is  None:
            self._keyboard_emulator = KeyboardEmulator()
            self._usb_device.attach_observer(self._keyboard_emulator)

            self._button_keyboard_emulator.setStyleSheet("background-color: green; ")
            print("Keyboard emulator started.")
        else:
            print("Keyboard keyer is already running.")

    def _stop_keyboard_emulator(self):
        if self._keyboard_emulator is not None:
            self._usb_device.detach_observer(self._keyboard_emulator)
            self._keyboard_emulator = None

            self._button_keyboard_emulator.setStyleSheet("background-color: red; ")
            print("Keyboard emulator stopped.")
        else:
            print("Keyboard keyer is not running, skipping stop.")

    def _start_comm_emulator(self):
        # Protect concurrent loop
        if self._comm_emulator is  None:
            self._comm_emulator = CommEmulator()
            if self._is_usb_device():
                self._usb_device.attach_observer(self._comm_emulator)
            elif self._is_keyboard_device():
                self._keyboard_device.attach_observer(self._comm_emulator)

            self._comm_emulator.start()

            self._button_comm_emulator.setStyleSheet("background-color: green; ")
            print("Comm emulator started.")
        else:
            print("Comm emulator is already running.")

    def _stop_comm_emulator(self):
        if self._comm_emulator is not None:
            if self._is_usb_device():
                self._usb_device.detach_observer(self._comm_emulator)
            elif self._is_keyboard_device():
                self._keyboard_device.detach_observer(self._comm_emulator)
            self._comm_emulator.stop()
            self._comm_emulator = None
            self._button_comm_emulator.setStyleSheet("background-color: red; ")
            print("Comm emulator stopped.")
        else:
            print("Comm emulator is not running, skipping stop.")

    def _start_keyer(self):
        if self._keyer is None:
            self._keyer = Keyer(wpm=20)
            self._keyer.start()
            if self._is_usb_device():
                self._usb_device.attach_observer(self._keyer)
            elif self._is_keyboard_device():
                self._keyboard_device.attach_observer(self._keyer)
            self._start_sound_processor()

            self._button_keyer.setStyleSheet("background-color: green; ")
            print("Keyer started.")
        else:
            print("Keyer is already running.")

    def _stop_keyer(self):
        if self._keyer is not None:

            self._stop_sound_processor()

            if self._is_usb_device():
                self._usb_device.detach_observer(self._keyer)
            elif self._is_keyboard_device():
                self._keyboard_device.detach_observer(self._keyer)
            self._keyer.stop()
            self._keyer = None

            self._button_keyer.setStyleSheet("background-color: red; ")
            print("Keyer stopped.")
        else:
            print("Keyer is not running, skipping stop.")

    def _start_usb_device(self):
        if self._usb_device is not None and not self._usb_device.is_running():
            self._usb_device.start()
            self._button_usb_device.setStyleSheet("background-color: green; ")
            print("Usb device started.")
        else:
            print("USB device is already running.")

    def _stop_usb_device(self):
        if self._usb_device is not None and self._usb_device.is_running():
            self._usb_device.stop()
            self._button_usb_device.setStyleSheet("background-color: red; ")
            print("Usb device stopped.")
        else:
            print("USB Device is not running, skipping stop.")

    def _start_keyboard_device(self):
        # Protect concurrent loop
        self._stop_keyboard_emulator()
        if self._keyboard_device is None:
            self._keyboard_device = KeyboardDevice()
            self._keyboard_device.start()
            self._button_keyboard_device.setStyleSheet("background-color: green; ")
            print("Keyboard device started.")
        else:
            print("Keyboard device is already running.")

    def _stop_keyboard_device(self):
        if self._keyboard_device is not None:
            self._keyboard_device.stop()
            self._keyboard_device = None
            self._button_keyboard_device.setStyleSheet("background-color: red; ")
            print("Keyboard device stopped.")
        else:
            print("Keyboard device is not running, skipping stop.")

    def _is_keyboard_device(self):
        return self._keyboard_device is not None

    def _is_usb_device(self):
        return self._usb_device is not None and self._usb_device.is_running()

    def _stop(self):

        self._stop_keyer()
        self._stop_keyboard_emulator()
        self._stop_comm_emulator()
        self._stop_comm_emulator_with_keyer()
        self._stop_keyboard_device()
        self._stop_usb_device()

    def _click_keyboard_device(self):
        print("Keyboard device button clicked.")
        self._stop()
        if self._keyboard_device is None:
            self._start_keyboard_device()
        else:
            self._stop_keyboard_device()

    def _click_usb_device(self):
        self._stop()
        if self._usb_device is not None:
            self._start_usb_device()
        else:
            self._stop_usb_device()

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
        if self._usb_device is not None:
            self._start_usb_device()
            self._start_keyboard_emulator()
        else:
            self._start_keyboard_device()
        self._start_keyer()



    def closeEvent(self, event):
        self._stop()
        super().closeEvent(event)


#app = App()
#app.run()

def main(args=None):
    if QtWidgets is None:
        print("PySide6 is not installed. Install with: python -m pip install PySide6")
        return 2


    q_application = QApplication(args)
    app = App()
    app.show()

    return q_application.exec()

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))


