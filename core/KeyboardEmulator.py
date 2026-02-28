from pynput.keyboard import Key, Controller, Listener
from core.DeviceObserver import DeviceObserver

"""
This class is responsible for listening to the keyboard events and sending the corresponding events to the keyer. 
It implements the UsbDeviceObserver interface to receive notifications when the dit or dah is pressed or released.
"""
class KeyboardEmulator(DeviceObserver):

    def __init__(self):
        # KB listener
        self._controller = Controller()

    """
    Proxy method to translate the dit and dah events to keyboard events.
    """
    def on_dah(self, pressed:bool):
        if pressed:
            self._controller.press(Key.ctrl_r)
        else :
            self._controller.release(Key.ctrl_r)

    """
    Proxy method to translate the dit and dah events to keyboard events.
    """
    def on_dit(self, pressed:bool):
        if pressed:
            self._controller.press(Key.ctrl_l)
        else :
            self._controller.release(Key.ctrl_l)
