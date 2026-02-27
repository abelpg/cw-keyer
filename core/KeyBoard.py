from pynput.keyboard import Key, Controller, Listener
from core.KeyerObserver import KeyerObserver



class Keyboard(KeyerObserver):

    def __init__(self):
        # KB listener
        self._kbListener = Listener(on_press=self._on_press_key)
        self._esc_pressed = False
        self._controller = Controller()
        #self._kbListener.start()


    def is_esc_pressed(self):
        return self._esc_pressed

    def start(self):
        self._kbListener.start()

    def stop(self):
        self._kbListener.stop()


    def on_dah(self, pressed:bool):
        if pressed:
            self._controller.press(Key.ctrl_r)
        else :
            self._controller.release(Key.ctrl_r)

    def on_dit(self, pressed:bool):
        if pressed:
            self._controller.press(Key.ctrl_l)
        else :
            self._controller.release(Key.ctrl_l)

    ####################################################################################################################
    def _on_press_key(self, key):
        if key == Key.esc:
            self._esc_pressed = True