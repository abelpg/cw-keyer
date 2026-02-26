from time import sleep

from core.KeyBoard import Keyboard
from core.UsbDevice import UsbDevice

# Logi 0x046d:0xc52b
# Key 0x413d:0x2107


keyboard = Keyboard()
keyboard.start()

usb_device = UsbDevice(0x413d,0x2107, keyboard)
usb_device.start()


while not keyboard.is_esc_pressed():
    sleep(0.5)

usb_device.stop()

