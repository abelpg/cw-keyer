import logging

from PySide6 import QtWidgets

from core.config import Configuration
from core.device import ZadigUsbDevice, KeyboardDevice, DeviceObserver


class DevicesForm:

    CONFIG_DEVICE_KEY = "usb_device"

    def __init__(self, parent: QtWidgets.QBoxLayout, stop_callback=None):
        self._parent = parent
        self._logger = logging.getLogger(__name__)
        self._stop_callback = stop_callback


        self._config = Configuration()

        self._usb_device = None
        self._keyboard_device = None

        layout = QtWidgets.QVBoxLayout()
        widget = QtWidgets.QWidget()

        self._button_keyboard_device = QtWidgets.QPushButton("Keyboard device Ctr+L / Ctr+R")
        self._button_keyboard_device.clicked.connect(self._click_keyboard_device)
        layout.addWidget(self._button_keyboard_device)

        #####
        widget_h = QtWidgets.QWidget()
        layout_h = QtWidgets.QHBoxLayout()

        self._button_usb_device = QtWidgets.QPushButton("Zadig USB device")
        self._button_usb_device.clicked.connect(self._click_usb_device)

        self._device_list = QtWidgets.QComboBox()
        self._set_devices()

        layout_h.addWidget(self._button_usb_device)
        layout_h.addWidget(self._device_list)

        widget_h.setLayout(layout_h)
        layout.addWidget(widget_h)
        #####

        widget.setLayout(layout)
        parent.addWidget(widget)

    def _set_devices(self):
        device_config = self._config.get_config(__name__, DevicesForm.CONFIG_DEVICE_KEY)
        index = 0
        found = False
        for device in ZadigUsbDevice.find_devices():
            str_device = hex(device[0]) + ":" + hex(device[1])
            self._device_list.addItem(str_device, str_device)
            if str_device == device_config and not found:
                found = True
            elif not found:
                index += 1
        self._logger.debug(f"Found {index} {found} devices.")
        if found:
            self._device_list.setCurrentIndex(index)

    def _get_device(self):
        device = self._device_list.currentData()
        self._config.put_config(__name__, DevicesForm.CONFIG_DEVICE_KEY, device)


        split_device = device.split(":")
        self._logger.debug("device " + str(split_device))
        return hex( int(split_device[0],16)), hex(int(split_device[1],16))

    def _click_keyboard_device(self):
        self._stop_callback(True)
        if self._keyboard_device is None:
            self._start_keyboard_device()
        else:
            self._stop_keyboard_device()

    def _click_usb_device(self):
        self._stop_callback(True)
        if self._usb_device is None:
            self._start_usb_device()
        else:
            self._stop_usb_device()

    def _start_usb_device(self):
        if self._usb_device is None:
            self.stop_all()
            self._logger.debug("Starting USB device with id: " + str(self._get_device()))

            try:
                self._usb_device = ZadigUsbDevice(0x413d, 0x2107)
            except Exception as e:
                self._logger.warning("Error initializing USB device: ", e)
                self._usb_device = None

            self._usb_device.start()
            self._button_usb_device.setStyleSheet("background-color: green; ")
            self._logger.debug("Usb device started.")
        else:
            self._logger.debug("USB device is already running.")

        return self._usb_device is not None


    def _stop_usb_device(self):
        if self._usb_device is not None:
            self._usb_device.stop()
            self._button_usb_device.setStyleSheet("background-color: red; ")
            self._logger.debug("Usb device stopped.")

            self._usb_device = None
        else:
            self._logger.debug("USB Device is not running, skipping stop.")

    def _start_keyboard_device(self):
        if self._keyboard_device is None:
            self.stop_all()
            self._keyboard_device = KeyboardDevice()
            self._keyboard_device.start()
            self._button_keyboard_device.setStyleSheet("background-color: green; ")
            self._logger.debug("Keyboard device started.")
        else:
            self._logger.debug("Keyboard device is already running.")

    def _stop_keyboard_device(self):
        if self._keyboard_device is not None:
            self._keyboard_device.stop()
            self._keyboard_device = None
            self._button_keyboard_device.setStyleSheet("background-color: red; ")
            self._logger.debug("Keyboard device stopped.")
        else:
            self._logger.debug("Keyboard device is not running, skipping stop.")


    def start(self):
        if not  self._start_usb_device():
            self._start_keyboard_device()

    def stop_all(self):
        self._stop_keyboard_device()
        self._stop_usb_device()

    def attach_observer(self, observer : DeviceObserver):
        if self._usb_device is not None:
            self._usb_device.attach_observer(observer)
        elif self._keyboard_device is not None:
            self._keyboard_device.attach_observer(observer)

    def detach_observer(self, observer: DeviceObserver):
        if self._usb_device is not None:
            self._usb_device.detach_observer(observer)
        elif self._keyboard_device is not None:
            self._keyboard_device.detach_observer(observer)