import threading
import numpy as np
from time import time
from core.ToneGenerator import ToneGenerator
from core.KeyerObserver import KeyerObserver


class SoundKeyer(KeyerObserver):

    # State machine init. dit dah
    def __init__(self, wpm : int = 10):
        # Dit dah variables
        self._dit = False
        self._dah = False

        self._dit_pressed = False
        self._dah_pressed = False

        # wmp
        self._wpm = wpm

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


    def on_dah(self, pressed: bool):
        if pressed:
            self._dah_pressed = True
            self._set_dah(True)
        else:
            self._dah_pressed = False

    def on_dit(self, pressed: bool):
        if pressed:
            self._dit_pressed = True
            self._set_dit(True)
        else:
             self._dit_pressed = False


    def start(self):
        # Start listeners

        # Start principal thread
        self._thread_stop = False
        self._thread.start()

        ### Start tone generator
        self._tone_generator.start()


    def stop(self):
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


    def _set_dit(self, dit: bool):
        if self._dit != dit:
            with self._thread_lock_dit:
                self._dit = dit

    def _set_dah(self, dah: bool):
        if self._dah != dah:
            with self._thread_lock_dah:
                self._dah = dah

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
