import logging

from PySide6 import QtWidgets

from core.device import UsbDevice, KeyboardDevice, DeviceObserver


class DevicesForm:

    def __init__(self, parent: QtWidgets.QBoxLayout, stop_callback=None):
        self._parent = parent

        self._logger = logging.getLogger(__name__)

        self._stop_callback = stop_callback

        try:
            self._usb_device = UsbDevice(0x413d, 0x2107)
        except Exception as e:
            self._logger.warning("Error initializing USB device: ", e)
            self._usb_device = None

        self._keyboard_device = None

        layout = QtWidgets.QVBoxLayout()
        widget = QtWidgets.QWidget()

        self._button_keyboard_device = QtWidgets.QPushButton("Keyboard device")
        self._button_keyboard_device.clicked.connect(self._click_keyboard_device)
        layout.addWidget(self._button_keyboard_device)

        self._button_usb_device = QtWidgets.QPushButton("USB device")
        self._button_usb_device.clicked.connect(self._click_usb_device)
        layout.addWidget(self._button_usb_device)

        widget.setLayout(layout)

        parent.addWidget(widget)

    def _click_keyboard_device(self):
        self._stop_callback()
        if self._keyboard_device is None:
            self._start_keyboard_device()
        else:
            self._stop_keyboard_device()

    def _click_usb_device(self):
        self._stop_callback()
        if self._usb_device is not None:
            self._start_usb_device()
        else:
            self._stop_usb_device()

    def _start_usb_device(self):
        if self._usb_device is not None and not self._usb_device.is_running():
            self._usb_device.start()
            self._button_usb_device.setStyleSheet("background-color: green; ")
            self._logger.debug("Usb device started.")
        else:
            self._logger.debug("USB device is already running.")

    def _start_keyboard_device(self):
        if self._keyboard_device is None:
            self._keyboard_device = KeyboardDevice()
            self._keyboard_device.start()
            self._button_keyboard_device.setStyleSheet("background-color: green; ")
            self._logger.debug("Keyboard device started.")
        else:
            self._logger.debug("Keyboard device is already running.")

    def _stop_usb_device(self):
        if self._is_usb_device():
            self._usb_device.stop()
            self._button_usb_device.setStyleSheet("background-color: red; ")
            self._logger.debug("Usb device stopped.")
        else:
            self._logger.debug("USB Device is not running, skipping stop.")

    def _stop_keyboard_device(self):
        if self._is_keyboard_device():
            self._keyboard_device.stop()
            self._keyboard_device = None
            self._button_keyboard_device.setStyleSheet("background-color: red; ")
            self._logger.debug("Keyboard device stopped.")
        else:
            self._logger.debug("Keyboard device is not running, skipping stop.")

    def _is_keyboard_device(self):
        return self._keyboard_device is not None

    def _is_usb_device(self):
        return self._usb_device is not None and self._usb_device.is_running()

    def start(self):
        if self._usb_device is not None:
            self._start_usb_device()
        else:
            self._start_keyboard_device()

    def stop_all(self):
        self._stop_keyboard_device()
        self._stop_usb_device()

    def attach_observer(self, observer : DeviceObserver):
        if self._is_usb_device():
            self._usb_device.attach_observer(observer)
        elif self._is_keyboard_device():
            self._keyboard_device.attach_observer(observer)

    def detach_observer(self, observer: DeviceObserver):
        if self._is_usb_device():
            self._usb_device.detach_observer(observer)
        elif self._is_keyboard_device():
            self._keyboard_device.detach_observer(observer)