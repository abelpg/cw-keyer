from time import sleep

from core.KeyBoard import Keyboard
from core.SoundKeyer import SoundKeyer
from core.UsbDevice import UsbDevice

# Logi 0x046d:0xc52b
# Key 0x413d:0x2107


keyboard = Keyboard()
keyboard.start()

sound_keyer = SoundKeyer(wpm=20)
sound_keyer.start()

usb_device = UsbDevice(0x413d,0x2107)
usb_device.attach_observer(keyboard)
#usb_device.attach_observer(sound_keyer)
usb_device.start()

while not keyboard.is_esc_pressed():
    sleep(0.5)

usb_device.stop()
sound_keyer.stop()
keyboard.stop()

