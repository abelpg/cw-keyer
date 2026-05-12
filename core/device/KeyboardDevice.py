import logging

from core.device import Device
from pynput.keyboard import Key, Listener
from pynput.mouse import Listener as MouseListener

class KeyboardDevice(Device):

    def __init__(self):
        super().__init__()
        self._logger = logging.getLogger(__name__)
        self._kb_listener = Listener(on_press=self._on_press_key, on_release=self._on_release_key)

        self._dah_pressed = False
        self._dit_pressed = False

    def start(self):
        self._kb_listener.start()

    def stop(self):
        self._kb_listener.stop()

    @staticmethod
    def _is_key_dit(key):
        return hasattr(key, 'vk') and key.vk == 186

    @staticmethod
    def _is_key_dah(key):
        return hasattr(key, 'vk') and key.vk == 187

    def _on_press_key(self, key):
        if self._is_key_dah(key) and not self._dah_pressed:
            self._dah_pressed = True
            self._set_dah(True)
        elif self._is_key_dit(key) and not self._dit_pressed:
            self._dit_pressed  = True
            self._set_dit(True)

    def _on_release_key(self, key):
        if self._is_key_dah(key) and self._dah_pressed:
            self._dah_pressed = False
            self._set_dah(False)
        elif self._is_key_dit(key) and self._dit_pressed:
            self._dit_pressed = False
            self._set_dit(False)