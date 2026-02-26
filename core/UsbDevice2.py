# From pyusb

import os
os.environ['PYUSB_DEBUG'] = 'debug'
import usb.util
import usb.backend.libusb1 as libusb1
import usb.core

be = libusb1.get_backend(find_library=lambda x: "../libs/libusb-1.0.dll")

# Logi 0x046d:0xc52b
# Key 0x413d:0x2107
dev = usb.core.find(idVendor=0x413d, idProduct=0x2107,backend=be)

if dev is None:
    raise ValueError('Device not found')


cfg = usb.util.find_descriptor(dev, bConfigurationValue=1)
dev.set_configuration(cfg)
try:
    dev.set_interface_altsetting(interface = 0, alternate_setting = 0)
except USBError:
    pass

print("#################")
print(cfg)
print("#################")

interface = cfg[(1,0)]
#interface = cfg[(0,0)]
endpoint = interface[0]

print(interface)

print("#################")
print("Addr", endpoint.bEndpointAddress, " packet",endpoint.wMaxPacketSize)

usb.util.claim_interface(dev, interface)

while True:
    try:
        data = dev.read(endpoint.bEndpointAddress, endpoint.wMaxPacketSize)

        # print(" ".join("{:02x}".format(ord(c)) for c in data))
        print (data)
    except usb.core.USBError as e:
        data = None
        if e.args == ('Operation timed out',):
            continue

        # For keyboard interrupt
    except KeyboardInterrupt:
        print("Read interrupted by user. Exiting.")
        break


# release the device
usb.util.release_interface(dev, interface)
