from time import sleep
from unittest import case

from core.KeyboardKeyer import KeyboardKeyer
from core.Keyer import Keyer
from core.SoundKeyer import SoundKeyer
from core.UsbDevice import UsbDevice
from os import system
# Logi 0x046d:0xc52b
# Key 0x413d:0x2107

class App:
    def __init__(self):
        self._device = None
        self._sound_keyer = None
        self._keyboard_keyer = None
        self._keyer = None

    def _start_sound_keyer(self):
        if self._sound_keyer is None:
            self._sound_keyer = SoundKeyer()
            self._sound_keyer.start()
            self._keyer.attach_observer(self._sound_keyer)
        else:
            print("Sound keyer is already running.")

    def _stop_sound_keyer(self):
        if self._sound_keyer is not None:
            self._sound_keyer.stop()
            self._keyer.detach_observer(self._sound_keyer)
            self._sound_keyer = None
        else:
            print("Sound keyer is not running, skipping stop.")

    def _start_keyboard_keyer(self):
        if self._keyboard_keyer is  None:
            self._keyboard_keyer = KeyboardKeyer()
            self._keyer.attach_observer(self._keyboard_keyer)
        else:
            print("Keyboard keyer is already running.")

    def _stop_keyboard_keyer(self):
        if self._sound_keyer is not None:
            self._keyer.detach_observer(self._keyboard_keyer)
            self._keyboard_keyer = None
        else:
            print("Keyboard keyer is not running, skipping stop.")

    def _start_keyer(self):
        if self._keyer is None:
            self._keyer = Keyer(wpm=20)
            self._keyer.start()
        else:
            print("Keyer is already running.")

    def _stop_keyer(self):
        if self._keyer is not None:
            self._keyer.stop()
            self._keyer = None
        else:
            print("Keyer is not running, skipping stop.")

    def _start_usb_device(self):
        if self._device is None:
            self._device = UsbDevice(0x413d,0x2107)
            self._device.start()
        else:
            print("USB device is already running.")

    def _stop_device(self):
        if self._device is not None:
            self._device.stop()
            self._device = None
        else:
            print("Device is not running, skipping stop.")

    def _stop(self):
        self._stop_device()
        self._stop_keyer()
        self._stop_sound_keyer()
        self._stop_keyboard_keyer()


    def _menu(self):
        print("1. Input keyboard device")
        print("2. Input USB device: ", "OFF" if self._device is None else "ON" )
        print("3. Keyboard keyer: ", "OFF" if self._keyboard_keyer is None else "ON" )
        print("4. Sound keyer: ", "OFF" if self._sound_keyer is None else "ON" )
        print("5. Keyer: ", "OFF" if self._keyer is None else "ON")
        print("9. Exit")
        try:
            val = int(input("Select an option: "))
        except ValueError:
            return

        match val:
            case 1:
                self._start_usb_device()
            case 2:
                if self._device is not None:
                    self._stop_device()
                self._start_usb_device()

            case 3:
                if self._keyboard_keyer is None:
                    self._start_keyboard_keyer()
                else:
                    self._stop_keyboard_keyer()
            case 4:
                if self._sound_keyer is None:
                    self._start_sound_keyer()
                else:
                    self._stop_sound_keyer()
            case 5:
                if self._keyer is None:
                    self._start_keyer()
                else:
                    self._stop_keyer()
            case 9:
                self._stop()
                exit(0)

    def run(self):
        self._start_usb_device()
        self._start_keyer()
        self._start_keyboard_keyer()
        while True:
            self._menu()

app = App()
app.run()




