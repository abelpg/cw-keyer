import logging
import threading
from enum import Enum
import hid

from core.device import Device

class DeviceType(Enum):
    KEYBOARD = 0x06
    MOUSE = 0x02

    @staticmethod
    def from_str(label):
        if label == DeviceType.KEYBOARD.name:
            return DeviceType.KEYBOARD
        elif label == DeviceType.MOUSE.name:
            return DeviceType.MOUSE
        else:
            raise NotImplementedError

class HidDeviceItem:

    PRODUCT_ID = 'product_id'
    VENDOR_ID = 'vendor_id'
    PATH = 'path'
    NAME = 'manufacturer_string'
    USAGE_TYPE = 'usage'


    def __init__(self, hid_device_info):
        self._product_id = hex(int(hid_device_info[HidDeviceItem.PRODUCT_ID]))
        self._vendor_id = hex(int(hid_device_info[HidDeviceItem.VENDOR_ID]))
        self._path = hid_device_info[HidDeviceItem.PATH]
        self._name = hid_device_info[HidDeviceItem.NAME]

        if hid_device_info[HidDeviceItem.USAGE_TYPE] == DeviceType.MOUSE.value:
            self._type = DeviceType.MOUSE
        elif hid_device_info[HidDeviceItem.USAGE_TYPE] == DeviceType.KEYBOARD.value:
            self._type = DeviceType.KEYBOARD

    @staticmethod
    def is_valid_device(hid_device_info):
        return (hid_device_info[HidDeviceItem.USAGE_TYPE] == DeviceType.MOUSE.value or
                hid_device_info[HidDeviceItem.USAGE_TYPE] == DeviceType.KEYBOARD.value)

    def build_key(self):
        return f"{self._vendor_id}:{self._product_id}:{self._type.name}"

    @staticmethod
    def build_vendor_product_id_from_key(key):
        vendor_id, product_id, path = key.split(":")
        return int(vendor_id,16), int(product_id,16), path

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"[{self._type.name}] {self._vendor_id}:{self._product_id} - {self._name}"

    def __lt__(self, other):
        return str(self) < str(other)

    def __gt__(self, other):
        return str(self) > str(other)

    def __le__(self, other):
        return str(self) <= str(other)

    def __ge__(self, other):
        return str(self) >= str(other)

class HidDevice (Device):

    def __init__(self, id_vendor, id_product, device_type : DeviceType):
        super().__init__()
        self._logger = logging.getLogger(__name__)

        self._id_vendor = id_vendor
        self._id_product = id_product
        self._device_type = device_type

        self._device = HidDevice.find_device(id_vendor, id_product, device_type)
        if self._device is None:
            self._logger.error("Could not find HID device.")
            raise ValueError('Device not found ' + hex(id_vendor) + '/' + hex(id_product))

        self._stop = True
        self._thread = None

    def start(self):
        self._logger.debug("HidDevice.start "+ str(self._device))
        if self._stop:
            self._thread = threading.Thread(target=self._run_hid_device_collect, daemon=True)
            self._thread.start()
            self._stop = False

    """
       Main loop to collect data from the USB device. It will read data from the device and set the dit and dah values 
       accordingly.
       """
    def _run_hid_device_collect(self):
        self._logger.info("Starting USB HID device collect thread. ")

        device = hid.device()
        device.open_path(self._device['path'])
        device.set_nonblocking(True)
        while not self._stop:
            self._logger.debug("Collecting data from HID device.")
            try:
                data = device.read(4, timeout_ms=100)
                if len(data) > 0:
                    self._logger.debug("Data read from HID device: " + str(data))
                    self._set_dit(data[0] == 1)
                    self._set_dah(data[1] == 1)
            except Exception as e:
                self._logger.error("Error reading from HID device: " + str(e))
                #break
        device.close()


    def stop(self):
        self._logger.debug("HidDevice.stop")
        if not self._stop:
            self._stop = True

    @staticmethod
    def find_device(id_vendor, id_product, device_type):
        logger = logging.getLogger(__name__)
        logger.debug("Finding HID device with vendor id " + hex(id_vendor) + " and product id " + hex(id_product) + " and type " + device_type.name)
        for device in hid.enumerate():
            if (device[HidDeviceItem.VENDOR_ID] == id_vendor
                and device[HidDeviceItem.PRODUCT_ID] == id_product
                and device[HidDeviceItem.USAGE_TYPE] == device_type.value    ):
                logger.debug("HID device found: " + str(device))
                return device
        return None

    @staticmethod
    def get_hid_devices():
        devices = []
        for device in hid.enumerate():
            if HidDeviceItem.is_valid_device(device):
                devices.append(HidDeviceItem(device))
        devices.sort()
        return devices


