from time import sleep

from core.KeyBoard import Keyboard
from core.Keyer import Keyer
from core.SoundKeyer import SoundKeyer
from core.UsbDevice import UsbDevice

# Logi 0x046d:0xc52b
# Key 0x413d:0x2107


keyboard = Keyboard()
keyboard.start()

keyer = Keyer(wpm=20)
keyer.start()

sound_keyer = SoundKeyer()
sound_keyer.start()

keyer.attach_observer(sound_keyer)

usb_device = UsbDevice(0x413d,0x2107)
usb_device.attach_observer(keyboard)
usb_device.attach_observer(keyer)
usb_device.start()

while not keyboard.is_esc_pressed():
    sleep(0.1)

usb_device.stop()
sound_keyer.stop()
keyer.stop()
keyboard.stop()

