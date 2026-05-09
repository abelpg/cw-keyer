import logging
import threading
from time import time, sleep

from core.keyer import AudioDevice, ToneGenerator, CommEmulatorWithKeyer
from core.device import DeviceObserver


class Keyer(DeviceObserver):

    # 1WPM dit = 1200 ms mark, 1200 ms space
    TIME_BASE = 1200

    def __init__(self, wpm : int, frequency: int = 600, amplitude : float = 0.5, output_device: AudioDevice = None):
        self._logger = logging.getLogger(__name__)

        # State machine init. dit dah
        self._dit_pressed = False
        self._dah_pressed = False

        # wmp
        self._dit_time, self._dah_time, self._space_time = self._calculate(wpm)

        self._tone_generator = None
        self._frequency = frequency
        self._amplitude = amplitude
        self._output_device = output_device

        self._comm_emulator_with_keyer = None

        # Principal thread to tak tics from dit and dah
        self._thread = threading.Thread(target=self._run_iambic, daemon=True)
        self._thread_stop = False

        # Locks to prevent concurrent modification
        self._started = False

        self._queue_dit = False
        self._queue_dah = False

        self._last_send = time()


    """
    Called when the dah is pressed or released. The pressed parameter is True when the dah is pressed and False when it is released.
    """
    def on_dah(self, pressed: bool):
        self._check_started()
        if pressed:
            self._dah_pressed = True
            self._queue_dah = True
        else:
            self._dah_pressed = False


    """
    Called when the dit is pressed or released. The pressed parameter is True when the dit is pressed and False when it is released.
    """
    def on_dit(self, pressed: bool):
        if pressed:
            self._dit_pressed = True
            self._queue_dit = True

        else:
            self._dit_pressed = False

    def start(self):
        self._thread.start()
        self._tone_generator = ToneGenerator(frequency=self._frequency,
                                             amplitude=self._amplitude,
                                             output_device=self._output_device)
        self._tone_generator.start()
        self._started = True

    def stop(self):
        self._tone_generator.stop()
        self.stop_serial()
        self._thread_stop = True
        self._started = False

    def is_serial_started(self):
        return self._comm_emulator_with_keyer is not None

    def start_serial(self, port):
        if not self.is_serial_started():
            self._comm_emulator_with_keyer = CommEmulatorWithKeyer(port=port)
            self._comm_emulator_with_keyer.start()
        else:
            self._logger.debug("Comm emulator is already running.")

    def stop_serial(self):
        if self.is_serial_started():
            self._comm_emulator_with_keyer.stop()
            self._comm_emulator_with_keyer = None
        else:
            self._logger.debug("Comm emulator is not running, skipping stop.")

    def _call_serial(self, duration):
        if self.is_serial_started():
            self._comm_emulator_with_keyer.send(duration)


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
        self._last_send = time()

        self._call_serial(self._dit_time)
        self._tone_generator.play_tone(self._dit_time, self._space_time)
        sleep(self._dit_time + self._space_time)
        self._queue_dit = False

        self._print_time(self._last_send, "dit")


    """
    Loop observes notify and wait dah time with space. Finally, release dah
    """
    def _send_dah(self):
        self._last_send = time()

        self._call_serial(self._dah_time)
        self._tone_generator.play_tone(self._dah_time, self._space_time)
        sleep(self._dah_time + self._space_time)
        self._queue_dah = False

        self._print_time(self._last_send, "dah")


    """
    Main loop to control the state of the keyer. It will check the state of the dit and dah and send the corresponding signal. 
    If both are pressed, it will send both signals. To improve timing, there are two sleeps after and before.
    """
    def _run_iambic(self):

        while not self._thread_stop:

            self._condition = None

            if self._queue_dit:
                # When dah is pressed when start dit

                if self._dah_pressed:
                    self._queue_dah = True

                self._send_dit()

                if self._dah_pressed:
                    self._queue_dah = True
                elif self._dit_pressed:
                    self._queue_dit = True

            # not elif because enqueue last.
            if self._queue_dah:

                # When dit is pressed when start dah
                if self._dit_pressed:
                    self._queue_dit = True

                self._send_dah()

                if self._dit_pressed:
                    self._queue_dit = True
                elif self._dah_pressed:
                    self._queue_dah = True

            # Sleep to avoid high CPU usage when no signal is being sent. If the last send was more than 10 times the dit time, sleep for the dit time.
            if time() - self._last_send > (self._dit_time * 10):
                sleep(self._dit_time)

