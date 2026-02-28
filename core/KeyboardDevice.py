from core.Device import Device
from pynput.keyboard import Key, Listener

class KeyboardDevice(Device):

    def __init__(self):
        super().__init__()
        self._kb_listener = Listener(on_press=self._on_press_key, on_release=self._on_release_key)

    def start(self):
        self._kb_listener.start()

    def stop(self):
        self._kb_listener.stop()

    def _on_press_key(self, key):
        if key == Key.ctrl_r:
            self._set_dah(True)
        elif key == Key.ctrl_l:
            self._set_dit(True)

    def _on_release_key(self, key):
        if key == Key.ctrl_r:
            self._set_dah(False)
        elif key == Key.ctrl_l:
            self._set_dit(False)