import threading
from time import sleep, time
from pynput import keyboard, mouse
import numpy as np
from ToneGenerator import ToneGenerator



class KeyerProxy:


    # State machine init. dit dah
    def __init__(self):
        # Dit dah variables
        self._dit_pressed = False
        self._dah_pressed = False

        self._kb_controller = keyboard.Controller()

        self._mouseListener = None


    def _release_dit(self):
        self._dit_pressed = False
        self._kb_controller.release(keyboard.Key.ctrl_l)
        print("released dit")

    def _release_dah(self):
        self._dah_pressed = False
        self._kb_controller.release(keyboard.Key.ctrl_r)
        print("released dah")


    def _press_dit(self)   :
        self._dit_pressed = True
        self._kb_controller.press(keyboard.Key.ctrl_l)
        print("pressed dit")

    def _press_dah(self):
        self._dah_pressed = True
        self._kb_controller.press(keyboard.Key.ctrl_r)
        print("pressed dah")


    def start(self, join=False):
        # Start listeners
        if join:
            with mouse.Listener(on_click=self._on_click, win32_event_filter=self._messages) as listener:
                listener.join()
        else:
            self._mouseListener = mouse.Listener(on_click=self._on_click)
            self._mouseListener.start()


    def stop(self):
        self._mouseListener.stop()

    def _messages(self,msg, data):
        print("MSG {} {}".format(msg, data))

    ####################################################################################################################
    ## KEYBOARD AND MOUSE LISTENERS
    ####################################################################################################################
    def _on_click(self, x, y, button, pressed):

        if pressed:
            if button == mouse.Button.left:
                self._press_dit()
            elif button == mouse.Button.right:
                self._press_dah()
        else:
            if button == mouse.Button.left:
                self._release_dit()
            elif button == mouse.Button.right:
                self._release_dah()


keyer = KeyerProxy()
keyer.start(True)