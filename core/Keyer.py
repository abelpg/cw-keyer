import threading
from time import sleep, time
from pynput import keyboard, mouse
import numpy as np
from ToneGenerator import ToneGenerator



class Keyer:


    # State machine init. dit dah
    def __init__(self, wpm : int = 10):
        # Dit dah variables
        self._dit = False
        self._dah = False

        self._dit_pressed = False
        self._dah_pressed = False

        # wmp
        self._wpm = wpm

        # KB listener
        self._kbListener = keyboard.Listener(on_press=self._on_press_key, on_release=self._on_release_key)
        # Mouse listener
        self._mouseListener = mouse.Listener(on_click=self._on_click)

        # Tone
        self._tone_generator = ToneGenerator(frequency=600, amplitude=0.5)

        # Principal thread to tak tics from dit and dah
        self._thread = threading.Thread(target=self._run_iambic, daemon=True)
        self._thread_stop = False

        # Locks to prevent concurrent modification
        self._thread_lock_dit = threading.Lock()
        self._thread_lock_dah = threading.Lock()


    def is_running(self) :
        return not self._thread_stop

    def _run_iambic(self):
        while not self._thread_stop:

            # If detects key pressed correct dit/dah values
            if self._dit_pressed:
                self._set_dit(True)
            if self._dah_pressed:
                self._set_dah(True)
            ts = time()
            if self._dit and self._dah:
                self.play_dit()
                self.play_dah()
                print("DIT DAH {}ms".format( np.ceil((time() - ts) * 1000 )))
            elif self._dit:
                self.play_dit()
                print("DIT {}ms".format(np.ceil((time() - ts) * 1000 )))
            elif self._dah:
                self.play_dah()
                print("DAH {}ms".format(np.ceil((time() - ts) * 1000 )))

    def _set_dit(self, dit: bool):
        if self._dit != dit:
            with self._thread_lock_dit:
                self._dit = dit

    def _set_dah(self, dah: bool):
        if self._dah != dah:
            with self._thread_lock_dah:
                self._dah = dah


    def _release_dit(self):
        self._dit_pressed = False

    def _release_dah(self):
        self._dah_pressed = False

    def _press_dit(self)   :
        self._dit_pressed = True
        self._set_dit(True)

    def _press_dah(self):
        self._dah_pressed = True
        self._set_dah(True)


    def start(self):
        # Start listeners
        self._kbListener.start()
        self._mouseListener.start()

        # Start principal thread
        self._thread_stop = False
        self._thread.start()

        ### Start tone generator
        self._tone_generator.start()


    def stop(self):
        self._kbListener.stop()
        self._mouseListener.stop()
        self._tone_generator.stop()
        self._thread_stop = True

    # Play dit and release dit
    def play_dit(self):
        t = 1.2 / float(self._wpm)
        self._tone_generator.play_tone(t, t)
        self._set_dit(False)

    # Play dah and release dah
    def play_dah(self):
        t = 2.5 / float(self._wpm)
        self._tone_generator.play_tone(t, t)
        self._set_dah(False)


    ####################################################################################################################
    ## KEYBOARD AND MOUSE LISTENERS
    ####################################################################################################################
    def _on_press_key(self, key):
        if key == keyboard.Key.ctrl_l:
            self._press_dit()
        elif key == keyboard.Key.ctrl_r:
            self._press_dah()
        #To test
        elif key == keyboard.Key.esc:
            self._thread_stop = True

    def _on_release_key(self, key):
        if key == keyboard.Key.ctrl_l:
            self._release_dit()
        elif key == keyboard.Key.ctrl_r:
            self._release_dah()

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


keyer = Keyer(15)
keyer.start()
while keyer.is_running():
        sleep(0.1)
        pass
