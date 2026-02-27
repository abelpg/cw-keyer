import threading
from time import time

import usb.util
import usb.backend.libusb1 as libusb1
import usb.core
#os.environ['PYUSB_DEBUG'] = 'debug'
from typing import List
from core.KeyerObserver import KeyerObserver
from concurrent.futures import ThreadPoolExecutor

class UsbDevice:

    BYTE_SIZE = 4
    INPUT_ADDR = 0x82
    CLICK_LEFT = 0x01
    CLICK_RIGHT = 0x02
    CLICK_BOTH = 0x03



    # Init USB device
    def __init__(self, id_vendor, id_product):
        self._id_vendor = id_vendor
        self._id_product = id_product

        be = libusb1.get_backend(find_library=lambda x: "./libs/libusb-1.0.dll")
        self._device = usb.core.find(idVendor=id_vendor, idProduct=id_product, backend=be)

        if self._device is None:
            raise ValueError('Device not found ' + id_vendor + '/' + id_product)

        self._interface, self._endpoint = self._find_interface_endpoint()

        if self._interface is None or self._endpoint is None:
            raise ValueError('No interface or endpoint found')

        self._stop = False
        self._thread = threading.Thread(target=self._run_usb_device_collect, daemon=True)
        self._dit = None
        self._dah = None

        self._observers: List[KeyerObserver] = []
        self._thread_pool = ThreadPoolExecutor(max_workers=4, thread_name_prefix="UsbDevice observers ThreadPool")

    def attach_observer(self, observer: KeyerObserver):
        self._observers.append(observer)

    def detach_observer(self, observer: KeyerObserver):
        self._observers.remove(observer)

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop = True

    """
    Find the interface and endpoint of the USB device. It will look for the interface and endpoint that match the.
    Improve: calculate the endpoint address and packet size from the device instead of hardcoding it.
    """
    def _find_interface_endpoint(self):
        for config in self._device.configurations():
            for interface in config.interfaces():
                for endpoint in interface.endpoints():
                    if endpoint.bEndpointAddress == self.INPUT_ADDR and endpoint.wMaxPacketSize == self.BYTE_SIZE:
                        return interface, endpoint
        return None, None

    def _set_dit(self, dit):
        self._dit = dit
        for observer in self._observers:
            self._thread_pool.submit(observer.on_dit,dit)


    def _set_dah(self, dah):
        self._dah = dah
        for observer in self._observers:
            self._thread_pool.submit(observer.on_dah,dah)

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

        # Claim interface
        usb.util.claim_interface(self._device, self._interface)

        while not self._stop:
            try:
                data = self._device.read(self._endpoint.bEndpointAddress,self._endpoint.wMaxPacketSize)
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

        # Release interface
        usb.util.release_interface(self._device, self._interface)