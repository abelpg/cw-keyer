import logging
import queue
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from time import time, sleep



from core.keyer import AudioDevice, ToneGenerator, CommEmulatorWithKeyer
from core.device import DeviceObserver

class KeyerItem(Enum):
    DIT = 1
    DAH = 2

class Mode(Enum):
    ULTIMATIC = 0
    IAMBIC_A = 1
    IAMBIC_B = 1


class Keyer(DeviceObserver):

    # 1WPM dit = 1200 ms mark, 1200 ms space
    TIME_BASE = 1200

    def __init__(self, wpm : int, frequency: int = 600, amplitude : float = 0.5, output_device: AudioDevice = None):
        self._logger = logging.getLogger(__name__)

        self._mode = Mode.IAMBIC_B

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
        self._queue = queue.Queue()

        self._pending = False
        self._last_squeeze = False
        self._last_queued = None
        self._last_pressed = None

        self._executor = ThreadPoolExecutor(max_workers=1)
    """
    Called when the dah is pressed or released. The pressed parameter is True when the dah is pressed and False when it is released.
    """
    def on_dah(self, pressed: bool):
        self._logger.debug("on dah  " + str(pressed))
        if pressed:
            self._dah_pressed = True
            self._last_pressed = KeyerItem.DAH
            self._enqueue(KeyerItem.DAH)
        else:
            self._dah_pressed = False

    """
    Called when the dit is pressed or released. The pressed parameter is True when the dit is pressed and False when it is released.
    """
    def on_dit(self, pressed: bool):
        self._logger.debug("on dit  " + str(pressed))
        if pressed:
            self._dit_pressed = True
            self._last_pressed = KeyerItem.DIT
            self._enqueue(KeyerItem.DIT)
        else:
            self._dit_pressed = False

    def _enqueue(self, item: KeyerItem):
        self._logger.debug("Queue " +str(self._queue.qsize()) +" - > " + str(item))
        if self._queue.qsize() < 1 or not self._pending:
            self._queue.put(item)
            self._last_queued = item
            if not self._pending:
                self._executor.submit(self._keyer_call)


    @staticmethod
    def _reverse( item: KeyerItem):
        if item == KeyerItem.DIT:
            return KeyerItem.DAH
        else:
            return KeyerItem.DIT

    def _keyer_call(self):
        squeeze = self._dit_pressed and self._dah_pressed
        self._pending = self._queue.qsize() > 0
        self._logger.debug("Queue " +str(self._queue.qsize()) )
        if self._pending:
            # process
            self._last_squeeze = squeeze
            dit_dah = self._queue.get_nowait()
            self._play_dit_dah(dit_dah)

            self._keyer_call()
        else:
            # process mode
            if squeeze:
                self._logger.debug("Squeeze")
                if self._mode == Mode.ULTIMATIC:
                    self._enqueue(self._last_pressed)
                elif self._mode == Mode.IAMBIC_A or self._mode == Mode.IAMBIC_B:
                    self._enqueue(Keyer._reverse(self._last_queued))

            elif self._dit_pressed:
                self._logger.debug("Dit pressed")
                self._enqueue(KeyerItem.DIT)

            elif self._dah_pressed:
                self._logger.debug("Dah pressed")
                self._enqueue(KeyerItem.DAH)

            elif self._mode == Mode.IAMBIC_B and self._last_squeeze:
                self._logger.debug("Last squeeze " + str(self._last_queued))
                self._enqueue(Keyer._reverse(self._last_queued))
                self._last_squeeze = False



    def start(self):
        self._tone_generator = ToneGenerator(frequency=self._frequency,
                                             amplitude=self._amplitude,
                                             output_device=self._output_device)
        self._tone_generator.start()

    def stop(self):
        self._tone_generator.stop()
        self.stop_serial()

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
    def _play_dit_dah(self, dit_dah : KeyerItem) :
        timer = time()

        time_send = 0
        if dit_dah == KeyerItem.DIT:
            time_send = self._dit_time
        elif dit_dah == KeyerItem.DAH:
            time_send = self._dah_time

        self._call_serial(time_send)

        self._tone_generator.play_tone(time_send, self._space_time)

        self._print_time(timer, dit_dah)



