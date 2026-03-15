import logging

from core.keyer import KeyerObserver, KeyerItem
from core.sound import ToneGenerator, AudioDevice


class SoundProcessor(KeyerObserver):

    # State machine init. dit dah
    def __init__(self, frequency: int = 600, output_device: AudioDevice = None ):
        KeyerObserver.__init__(self)

        self._logger = logging.getLogger(__name__)
        # Tone
        self._tone_generator = None
        self._started = False
        self._frequency = frequency
        self._output_device = output_device

    def _process_item(self, keyer_item: KeyerItem):
        self._logger.debug(
            "Processing keyer item with time: " + str(keyer_item.time) + " and silence: " + str(keyer_item.silence))
        if self._started:
            self._tone_generator.play_tone(keyer_item.time, keyer_item.silence)
        else:
            self._logger.warning("SoundKeyer is not started. Please call start() method before playing tones.")

    def start(self):
        super().start()
        self._tone_generator = ToneGenerator(frequency=self._frequency, output_device=self._output_device)
        self._tone_generator.start()
        self._started = True

    def stop(self):
        super().stop()
        self._tone_generator.stop()
        self._started = False

