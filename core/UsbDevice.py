import os
import threading

#os.environ['PYUSB_DEBUG'] = 'debug'
import usb.util
import usb.backend.libusb1 as libusb1
import usb.core

class UsbDevice:

    BYTE_SIZE = 4
    INPUT_ADDR = 0x82
    CLICK_LEFT = 0x01
    CLICK_RIGHT = 0x02
    CLICK_BOTH = 0x03

    def __init__(self, id_vendor, id_product, keyboard = None):
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

        self._keyboard = keyboard
        

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop = True


    def _find_interface_endpoint(self):
        for config in self._device.configurations():
            for interface in config.interfaces():
                for endpoint in interface.endpoints():
                    if endpoint.bEndpointAddress == self.INPUT_ADDR and endpoint.wMaxPacketSize == self.BYTE_SIZE:
                        return interface, endpoint
        return None, None

    def _set_dit_dah(self, dit, dah):

        if dit and not self._dit:
            self._keyboard.press_ctrl_l()
        elif not dit and self._dit:
            self._keyboard.release_ctrl_l()

        if dah and not self._dah:
            self._keyboard.press_ctrl_r()
        elif not dah and self._dah:
            self._keyboard.release_ctrl_l()



    def _run_usb_device_collect(self):

        usb.util.claim_interface(self._device, self._interface)

        while not self._stop:
            try:
                data = self._device.read(self._endpoint.bEndpointAddress,self._endpoint.wMaxPacketSize)
                if data[0] == self.CLICK_BOTH:
                    self._set_dit_dah(True,True)
                elif data[0] == self.CLICK_LEFT:
                    self._set_dit_dah(True,False)
                elif data[0] == self.CLICK_RIGHT:
                    self._set_dit_dah(False,True)

            except usb.core.USBError as e:
                data = None
                if e.args == ('Operation timed out',):
                    continue

        usb.util.release_interface(self._device, self._interface)