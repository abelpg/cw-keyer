from pynput.keyboard import Key, Controller, Listener
from core.UsbDeviceObserver import UsbDeviceObserver

"""
This class is responsible for listening to the keyboard events and sending the corresponding events to the keyer. 
It implements the UsbDeviceObserver interface to receive notifications when the dit or dah is pressed or released.
"""
class Keyboard(UsbDeviceObserver):

    def __init__(self):
        # KB listener
        self._kbListener = Listener(on_press=self._on_press_key)
        self._esc_pressed = False
        self._controller = Controller()


    def is_esc_pressed(self):
        return self._esc_pressed

    def start(self):
        self._kbListener.start()

    def stop(self):
        self._kbListener.stop()

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

    ####################################################################################################################
    def _on_press_key(self, key):
        if key == Key.esc:
            self._esc_pressed = True