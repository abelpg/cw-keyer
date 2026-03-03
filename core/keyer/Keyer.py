import threading
from concurrent.futures import ThreadPoolExecutor
from time import sleep, time

from typing import List
from core.keyer import KeyerObserver
from core.device import DeviceObserver

LOG = False

def _log(message: str):
    if LOG:
        print("{} {}".format(time(), message))


class Keyer(DeviceObserver):

    # 1WPM dit = 1200 ms mark, 1200 ms space
    TIME_BASE = 1200

    def __init__(self, wpm : int):
        self._dit_pressed = False
        self._dah_pressed = False
        self._dit = False
        self._dah = False

        # wmp
        self._dit_time, self._dah_time, self._space_time = self._calculate(wpm)

        # Principal thread to tak tics from dit and dah
        self._thread = threading.Thread(target=self._run_iambic, daemon=True)
        self._thread_stop = False

        # Locks to prevent concurrent modification
        self._thread_lock = threading.Lock()

        self._observers: List[KeyerObserver] = []
        self._thread_pool = ThreadPoolExecutor(max_workers=4, thread_name_prefix="Keyer observers ThreadPool")

        self._started = False

    """
    Called when the dah is pressed or released. The pressed parameter is True when the dah is pressed and False when it is released.
    """
    def on_dah(self, pressed: bool):
        self._check_started()
        if pressed:
            self._dah_pressed, self._dah =  True, True
        else:
            self._dah_pressed = False

    """
    Called when the dit is pressed or released. The pressed parameter is True when the dit is pressed and False when it is released.
    """
    def on_dit(self, pressed: bool):
        self._check_started()
        if pressed:
            self._dit_pressed, self._dit = True, True
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
            print("Keyer is not started. Please call start() method before sending signals.")

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

        print("Total time for PARIS: DIT time: {}s, DAH time: {}s,  Space time: {}s".format(dit_time, dah_time,space_time))
        return dit_time, dah_time, space_time




    """
    Loop observes notify and wait dit time with space, finally release dit.
    """
    def _send_dit(self) :
        ts = time()
        total = self._dit_time + self._space_time

        if len(self._observers) > 0:
            for observer in self._observers:
                self._thread_pool.submit(observer.play_dit, self._dit_time, self._space_time)
        else:
            print("No observers attached to keyer, skipping dit signal.")

        sleep(total)
        with self._thread_lock:
            self._dit = False
        _log("SEND DIT {}s {}s".format(total, time() - ts))


    """
    Loop observes notify and wait dah time with space. Finally, release dah
    """
    def _send_dah(self):
        ts = time()
        total = self._dah_time + self._space_time
        for observer in self._observers:
            self._thread_pool.submit(observer.play_dah, self._dah_time, self._space_time)

        sleep(total)
        with self._thread_lock:
            self._dah = False
        _log("SEND DAH {}s {}s".format(total, time() - ts))


    """
    Main loop to control the state of the keyer. It will check the state of the dit and dah and send the corresponding signal. 
    If both are pressed, it will send both signals. If none is pressed, it will sleep for a short time to prevent high CPU usage.
    """
    def _run_iambic(self):
        while not self._thread_stop:

            _log("Iambic loop: dit_pressed: {}, dah_pressed: {}, dit: {}, dah: {}".format(self._dit_pressed, self._dah_pressed, self._dit, self._dah))

            if (self._dit or self._dit_pressed) and (self._dah or self._dah_pressed):
                self._send_dit()
                self._send_dah()
            elif self._dit or self._dit_pressed:
                self._send_dit()
            elif self._dah or self._dah_pressed:
                self._send_dah()
            else:
                # Default sleep to prevent high CPU usage when no key is pressed, this is not a problem because the
                sleep(self._space_time)