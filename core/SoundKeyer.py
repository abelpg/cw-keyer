import threading
import numpy as np
from time import time, sleep
from core.ToneGenerator import ToneGenerator
from core.KeyerObserver import KeyerObserver


class SoundKeyer(KeyerObserver):

    # 1WPM dit = 1200 ms mark, 1200 ms space
    TIME_BASE = 1200

    # State machine init. dit dah
    def __init__(self, wpm : int = 10):
        # Dit dah variables
        self._dit = False
        self._dah = False

        self._dit_pressed = False
        self._dah_pressed = False

        # Tone
        self._tone_generator = ToneGenerator(frequency=800, amplitude=0.5)

        # Principal thread to tak tics from dit and dah
        self._thread = threading.Thread(target=self._run_iambic, daemon=True)
        self._thread_stop = False

        # Locks to prevent concurrent modification
        self._thread_lock_dit = threading.Lock()
        self._thread_lock_dah = threading.Lock()

        # wmp
        self._character_time, self._character_space_time = self._calculate(wpm)


    """
    So the word PARIS has been chosen to represent the standard word length for measuring the speed of sending CW.    
    The word PARIS comprises a total of 50 units; one unit is the length of one dit. Those 50 units are made up of 22 mark units and 28 space units.
    """
    def _calculate(self, wpm):
        # Calculate space times for Farnsworth (word rate < char rate)
        # There are 50 units in "PARIS " - 36 are in the characters, 14 are in the spaces
        t_total = (self.TIME_BASE / wpm) * 50
        t_chars = (self.TIME_BASE / wpm) * 36
        space_time = (t_total - t_chars) / 14  # Time for 1 space (ms)
        # Character and word spacing
        character_space_time = space_time * 2
        word_space_time = space_time * 4
        character_time = self.TIME_BASE / wpm
        print("Total time for PARIS: character time: {}ms, character space time: {}ms,  word space time: {}ms".format(character_time, character_space_time,word_space_time))
        return character_time, character_space_time


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
        ts = time()
        character_time = self._character_time / 1000.0
        space_time = self._character_space_time / 1000.0
        self._tone_generator.play_bg_tone(character_time, space_time)
        sleep( character_time + space_time)
        self._set_dit(False)
        print("DIT {}ms / {}ms".format(np.ceil((time() - ts)*1000) /1000.0, character_time))

    # Play dah and release dah
    def play_dah(self):
        ts = time()
        character_time = self._character_time * 2 / 1000.0
        space_time = self._character_space_time / 1000.0
        self._tone_generator.play_bg_tone(character_time,  space_time)
        sleep(character_time + space_time)
        self._set_dah(False)
        print("DAH {}ms / {}ms".format(np.ceil((time() - ts)*1000) /1000.0,  character_time ))

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
            ts = time()
            # If detects key pressed correct dit/dah values
            if self._dit_pressed:
                self._set_dit(True)
            if self._dah_pressed:
                self._set_dah(True)

            if self._dit and self._dah:
                self.play_dit()
                self.play_dah()
            elif self._dit:
                self.play_dit()
            elif self._dah:
                self.play_dah()
            else:
                # always sleep for the character space time to avoid busy waiting and to give time for the keyer to release the keys
                sleep(self._character_space_time / 1000.0)
            #print("Bucle {}ms".format(np.ceil((time() - ts) * 1000) / 1000.0))
