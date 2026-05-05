import logging
import threading
from asyncio import timeout_at
from concurrent.futures import ThreadPoolExecutor
from time import sleep, time

from typing import List
from core.keyer import KeyerObserver
from core.device import DeviceObserver


class Keyer(DeviceObserver):

    # 1WPM dit = 1200 ms mark, 1200 ms space
    TIME_BASE = 1200

    def __init__(self, wpm : int):
        self._logger = logging.getLogger(__name__)

        # State machine init. dit dah
        self._dit_pressed = False
        self._dah_pressed = False

        # wmp
        self._dit_time, self._dah_time, self._space_time = self._calculate(wpm)

        # Principal thread to tak tics from dit and dah
        self._thread = threading.Thread(target=self._run_iambic, daemon=True)
        self._thread_stop = False


        # Locks to prevent concurrent modification
        self._thread_lock = threading.Lock()

        self._observers: List[KeyerObserver] = []
        self._started = False

        self._queue_dit = False
        self._queue_dah = False



    """
    Called when the dah is pressed or released. The pressed parameter is True when the dah is pressed and False when it is released.
    """
    def on_dah(self, pressed: bool):
        self._check_started()
        if pressed:
            self._dah_pressed = True
            with self._thread_lock:
                self._queue_dah = True
        else:
            self._dah_pressed = False


    """
    Called when the dit is pressed or released. The pressed parameter is True when the dit is pressed and False when it is released.
    """
    def on_dit(self, pressed: bool):
        if pressed:
            self._dit_pressed = True
            with self._thread_lock:
                self._queue_dit = True
        else:
            self._dit_pressed = False

    """
    Add observer to keyer, this observer will be called when the dit or dah is pressed or released with calculated time. 
    """
    def attach_observer(self, observer: KeyerObserver):
        self._observers.append(observer)

    """
    Remove observer to keyer, this observer will be called when the dit or dah is pressed or released with calculated time. 
    """
    def detach_observer(self, observer: KeyerObserver):
        self._observers.remove(observer)

    def start(self):
        self._thread.start()
        self._started = True

    def stop(self):
        self._thread_stop = True
        self._started = False

    def _check_started(self):
        if not self._started:
            self._logger.warning("Keyer is not started. Please call start() method before sending signals.")

    """
    So the word PARIS has been chosen to represent the standard word length for measuring the speed of sending CW.    
    The word PARIS comprises a total of 50 units; one unit is the length of one dit. Those 50 units are made up of 22 mark units and 28 space units.
    Key Timing Formulas
    Dit Length () = 1200ms / WPM
    Dah Length () = 3x Dit Length
    Inter-element Space = 1 Dit Length
    Letter Space = 3 Dit Lengths
    Word Space = 7 Dit Lengths
    Example Speeds
    15 WPM: Dit = 80ms, Dah = 240ms
    20 WPM: Dit = 60ms, Dah = 180ms
    24 WPM: Dit = 50ms, Dah = 150ms
    30 WPM: Dit = 40ms, Dah = 120ms 
    """
    def _calculate(self, wpm:float):
        # Character and word spacing in seconds, rounded to 3 decimals
        dit_time = self.TIME_BASE / wpm / 1000.0
        dah_time = dit_time * 3.0
        space_time = dit_time

        self._logger.info("Total time for PARIS: DIT time: {}s, DAH time: {}s,  Space time: {}s".format(dit_time, dah_time,space_time))
        return dit_time, dah_time, space_time

    def _print_time(self, time_init, action):
        if self._logger.isEnabledFor(logging.DEBUG):
            total_time = time() - time_init
            total_time = round(total_time, 4)
            self._logger.debug(f"SEND {action} took {total_time} seconds.")

    """
    Loop observes notify and wait dit time with space, finally release dit.
    """
    def _send_dit(self) :
        if len(self._observers) > 0:
            for observer in self._observers:
                observer.add_keyer_item(self._dit_time, self._space_time)
        else:
            self._logger.warning("No observers attached to keyer, skipping dit signal.")

        sleep(self._dit_time + self._dit_time)

    """
    Loop observes notify and wait dah time with space. Finally, release dah
    """
    def _send_dah(self):
        if len(self._observers) > 0:
            for observer in self._observers:
                observer.add_keyer_item(self._dah_time, self._space_time)
        else:
            self._logger.warning("No observers attached to keyer, skipping dit signal.")

        sleep(self._dah_time + self._dit_time)


    """
    Main loop to control the state of the keyer. It will check the state of the dit and dah and send the corresponding signal. 
    If both are pressed, it will send both signals. To improve timing, there are two sleeps after and before.
    """
    def _run_iambic(self):

        while not self._thread_stop:

            if self._queue_dit:
                self._send_dit()
                with self._thread_lock:
                    self._queue_dit = False
                    if self._dah_pressed:
                        self._queue_dah = True
                    elif self._dit_pressed:
                        self._queue_dit = True

            if self._queue_dah:
                with self._thread_lock:
                    if self._dit_pressed:
                        self._queue_dit = True

                self._send_dah()

                with self._thread_lock:
                    self._queue_dah = False
                    if self._dit_pressed:
                        self._queue_dit = True
                    elif self._dah_pressed:
                        self._queue_dah = True



