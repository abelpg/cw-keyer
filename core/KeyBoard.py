
from pynput.keyboard import Key, Controller, Listener

class Keyboard:

    def __init__(self):
        # KB listener
        self._kbListener = Listener(on_press=self._on_press_key)
        self._esc_pressed = False
        self._controller = Controller()
        #self._kbListener.start()

    def _on_press_key(self, key):
        if key == Key.esc:
            self._esc_pressed = True

    def is_esc_pressed(self):
        return self._esc_pressed

    def start(self):
        self._kbListener.start()

    def press_ctrl_r(self):
        self._controller.press(Key.ctrl_r)

    def press_ctrl_l(self):
        self._controller.press(Key.ctrl_l)

    def release_ctrl_r(self):
        self._controller.release(Key.ctrl_r)

    def release_ctrl_l(self):
        self._controller.release(Key.ctrl_l)