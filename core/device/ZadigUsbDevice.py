import logging
import threading
import traceback
from time import sleep

import usb.util
import usb.backend.libusb1 as libusb1
import usb.core
import hid

from core.common import BaseItem
#os.environ['PYUSB_DEBUG'] = 'debug'
from core.device import Device

"""
This class represents a USB device that is used to control the keyer. It uses the pyusb library to communicate with the device.
"""
class HidDeviceItem(BaseItem):

    TESTED_DEVICES = [
        {"vendor_id": 0x413d, "product_id": 0x2107, "interface": 0, "endpoint": 0x81, "max_packet_size": 8}, # Vail
        {"vendor_id": 0x413d, "product_id": 0x2107, "interface": 1, "endpoint": 0x82, "max_packet_size": 4}  # Left click/right
    ]


    HID_INTERFACE = 0x3

    def __init__(self, product_id, vendor_id, interface, endpoint, max_packet_size, manufacturer_string):
        super().__init__()
        self._product_id = hex(product_id)
        self._vendor_id = hex(vendor_id)
        self._interface = interface
        self._endpoint = endpoint
        self._max_packet_size = max_packet_size
        self._name = "" if manufacturer_string is None else manufacturer_string
        if self._is_tested_device():
            self._name += " (DEVICE OK)"


    def _is_tested_device(self):
        for device in self.TESTED_DEVICES:
            if device["vendor_id"] == int(self._vendor_id,16) and device["product_id"] == int(self._product_id,16) and device["interface"] == self._interface and device["endpoint"] == self._endpoint and device["max_packet_size"] == self._max_packet_size:
                return True
        return False

    def build_key(self):
        return f"{self._vendor_id}:{self._product_id}:{self._interface}:{self._endpoint}:{self._max_packet_size}"

    @staticmethod
    def build_vendor_product_id_from_key(key):
        vendor_id, product_id, interface, endpoint, max_packet_size = key.split(":")
        return int(vendor_id,16), int(product_id,16), int(interface), int(endpoint), int(max_packet_size)

    def _to_string(self):
        return f"[{self._vendor_id}] {self._product_id}:{self._interface} - {self._name}"


class ZadigUsbDevice(Device):

    CLICK_LEFT = 0x01
    CLICK_RIGHT = 0x02
    CLICK_BOTH = 0x03

    # Init USB device
    def __init__(self, id_vendor, id_product, interface, endpoint, max_packet_size, call_on_stop=None):
        super().__init__()
        self._logger = logging.getLogger(__name__)

        self._id_vendor = id_vendor
        self._id_product = id_product
        self._endpoint = endpoint
        self._interface = interface
        self._max_packet_size = max_packet_size

        self._logger.info("Init Zadig USB device with { \"vendor_id\": " +hex(id_vendor)
                          + ", \"product_id\": " + hex(id_product)
                          + ", \"interface\": " +str(interface)
                          + ", \"endpoint\": " + hex(endpoint)
                          + ", \"max_packet_size\": " + str(max_packet_size) + "}")


        self._call_on_stop = call_on_stop

        self._stop = True
        self._thread = None

    @staticmethod
    def get_hid_devices():
        devices = []
        backend = libusb1.get_backend(find_library=lambda x: "./libs/libusb-1.0.dll")
        for device in usb.core.find(find_all=True, backend=backend):
            for config in device.configurations():
                for interface in config.interfaces():
                    if interface.bInterfaceClass == HidDeviceItem.HID_INTERFACE:
                        for endpoint in interface.endpoints():
                            devices.append(HidDeviceItem(
                                vendor_id=device.idVendor,
                                product_id=device.idProduct,
                                interface=interface.bInterfaceNumber,
                                endpoint=endpoint.bEndpointAddress,
                                max_packet_size=endpoint.wMaxPacketSize,
                                manufacturer_string=usb.util.get_string(device, device.iManufacturer)
                            ))

        devices.sort()
        return devices


    def start(self):
        if self._stop:
            self._thread = threading.Thread(target=self._run_usb_device_collect, daemon=True)
            self._thread.start()
            self._stop = False

    def stop(self):
        if not self._stop:
            self._stop = True

    def is_running(self):
        return not self._stop


    """
    Set dit and dah values and control the state of the keyer. This is used to avoid concurrent modification of dit and 
    dah values when both are set at the same time.
    """
    def _set_dit_dah(self, dit, dah):
        # Set dit
        if dit and not self._dit:
            self._set_dit(True)
        elif not dit and self._dit:
            self._set_dit(False)

        # Set dah
        if dah and not self._dah:
            self._set_dah(True)
        elif not dah and self._dah:
            self._set_dah(False)


    def _zadig_device(self):
        self._logger.info("Starting USB device collect thread.")
        # Claim interface

        self._backend = libusb1.get_backend(find_library=lambda x: "./libs/libusb-1.0.dll")
        self._device = usb.core.find(idVendor=self._id_vendor, idProduct=self._id_product, backend=self._backend)

        if self._device is None:
            self._logger.error("Could not find USB device.")
            raise ValueError('Device not found ' + self._id_vendor + '/' + self._id_product)


        try:
            self._device.reset()
        except Exception as e:
            self._logger.error("USB error: " + str(e))

        try:
            if self._device.is_kernel_driver_active(self._interface):
                self._device.detach_kernel_driver(self._interface)
        except Exception as e:
            self._logger.error("USB detaching error: " + str(e))

        try:
            usb.util.claim_interface(self._device, self._interface)
            while not self._stop:
                try:
                    data = self._device.read(self._endpoint, self._max_packet_size)
                    self._logger.debug("Received data from USB device." + str(data))
                    if data[0] == self.CLICK_BOTH or (data[2] > 0 and data[3] > 0):
                        self._set_dit_dah(True, True)
                    elif data[0] == self.CLICK_LEFT or data[2] > 0:
                        self._set_dit_dah(True, False)
                    elif data[0] == self.CLICK_RIGHT or data[3] > 0:
                        self._set_dit_dah(False, True)
                    else:
                        self._set_dit_dah(False, False)

                except usb.core.USBError as e:
                    self._logger.error("USB error: " + str(e))
                    return False
        finally:
            # Release interface
            usb.util.release_interface(self._device, self._interface)
            usb.util.dispose_resources(self._device)
        return True

    """
    Main loop to collect data from the USB device. It will read data from the device and set the dit and dah values 
    accordingly.
    """
    def _run_usb_device_collect(self):
       self._zadig_device()
       self._stop = True
       if self._call_on_stop is not None:
           self._call_on_stop()
       self._logger.info("Stopped USB device collect thread.")