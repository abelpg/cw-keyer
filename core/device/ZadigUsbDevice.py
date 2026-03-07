import logging
import threading
import usb.util
import usb.backend.libusb1 as libusb1
import usb.core
#os.environ['PYUSB_DEBUG'] = 'debug'
from core.device import Device


class HidDeviceItem:

    TESTED_DEVICES = [
        {"vendor_id": 0x413d, "product_id": 0x2107, "interface": 1, "endpoint": 0x82, "max_packet_size": 4}
    ]


    HID_INTERFACE = 0x3

    def __init__(self, product_id, vendor_id, interface, endpoint, max_packet_size, manufacturer_string):
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

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"[{self._vendor_id}] {self._product_id}:{self._interface} - {self._name}"

    def __lt__(self, other):
        return str(self) < str(other)

    def __gt__(self, other):
        return str(self) > str(other)

    def __le__(self, other):
        return str(self) <= str(other)

    def __ge__(self, other):
        return str(self) >= str(other)


class ZadigUsbDevice(Device):

    CLICK_LEFT = 0x01
    CLICK_RIGHT = 0x02
    CLICK_BOTH = 0x03

    # Init USB device
    def __init__(self, id_vendor, id_product, interface, endpoint, max_packet_size):
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

        self._backend = libusb1.get_backend(find_library=lambda x: "./libs/libusb-1.0.dll")
        self._device = usb.core.find(idVendor=id_vendor, idProduct=id_product, backend=self._backend)

        if self._device is None:
            self._logger.error("Could not find USB device.")
            raise ValueError('Device not found ' + id_vendor + '/' + id_product)

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

    """
    Main loop to collect data from the USB device. It will read data from the device and set the dit and dah values 
    accordingly.
    """
    def _run_usb_device_collect(self):
        self._logger.info("Starting USB device collect thread.")
        # Claim interface

        try:
            usb.util.claim_interface(self._device, self._interface)
            while not self._stop:
                try:
                    data = self._device.read(self._endpoint,self._max_packet_size)
                    if data[0] == self.CLICK_BOTH:
                        self._set_dit_dah( True,True)
                    elif data[0] == self.CLICK_LEFT:
                        self._set_dit_dah( True,False)
                    elif data[0] == self.CLICK_RIGHT:
                        self._set_dit_dah(False,True)
                    else:
                        self._set_dit_dah(False, False)

                except usb.core.USBError as e:
                    data = None
                    if e.args == ('Operation timed out',):
                        continue
        finally:
            # Release interface
            usb.util.release_interface(self._device, self._interface)
            usb.util.dispose_resources(self._device)
            self._logger.info("Stopped USB device collect thread.")