from time import sleep
from unittest import case

from core.KeyboardEmulator import KeyboardEmulator
from core.Keyer import Keyer
from core.SoundProcessor import SoundProcessor
from core.UsbDevice import UsbDevice
from os import system
# Logi 0x046d:0xc52b
# Key 0x413d:0x2107

class App:
    def __init__(self):
        self._device = None
        #####
        self._keyboard_emulator = None
        self._keyer = None
        ####
        self._sound_processor = None


    def _start_sound_processor(self):
        if self._sound_processor is None:
            self._sound_processor = SoundProcessor()
            self._sound_processor.start()
            self._keyer.attach_observer(self._sound_processor)
        else:
            print("Sound keyer is already running.")

    def _stop_sound_processor(self):
        if self._sound_processor is not None:
            self._sound_processor.stop()
            self._keyer.detach_observer(self._sound_processor)
            self._sound_processor = None
        else:
            print("Sound keyer is not running, skipping stop.")

    def _start_keyboard_emulator(self):
        if self._keyboard_emulator is  None:
            self._keyboard_emulator = KeyboardEmulator()
            self._device.attach_observer(self._keyboard_emulator)
        else:
            print("Keyboard keyer is already running.")

    def _stop_keyboard_emulator(self):
        if self._keyboard_emulator is not None:
            self._device.detach_observer(self._keyboard_emulator)
            self._keyboard_emulator = None
        else:
            print("Keyboard keyer is not running, skipping stop.")

    def _start_keyer(self):
        if self._keyer is None:
            self._keyer = Keyer(wpm=20)
            self._keyer.start()
            self._device.attach_observer(self._keyer)
        else:
            print("Keyer is already running.")

    def _stop_keyer(self):
        if self._keyer is not None:
            self._device.detach_observer(self._keyer)
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
        self._stop_sound_processor()
        self._stop_keyer()
        self._stop_keyboard_emulator()
        self._stop_device()


    def _menu(self):
        print("1. Input USB device", "OFF" if self._device is None else "ON")
        print("2. Input Keyboard device: " )
        print("3. Keyboard emulator: ", "OFF" if self._keyboard_emulator is None else "ON" )
        print("4. Sound processor: ", "OFF" if self._sound_processor is None else "ON" )
        print("5. Keyer: ", "OFF" if self._keyer is None else "ON")
        print("9. Exit")
        try:
            val = int(input("Select an option: "))
        except ValueError:
            return

        match val:
            case 1:
                if self._device is None:
                    self._start_usb_device()
                else:
                    self._stop_device()
            case 2:
                print("Not implemented yet.")

            case 3:
                if self._keyboard_emulator is None:
                    self._start_keyboard_emulator()
                else:
                    self._stop_keyboard_emulator()
            case 4:
                if self._sound_processor is None:
                    self._start_sound_processor()
                else:
                    self._stop_sound_processor()
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
        self._start_keyboard_emulator()
        while True:
            self._menu()

app = App()
app.run()




