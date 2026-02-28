from core.KeyerObserver import KeyerObserver
from core.ToneGenerator import ToneGenerator

class SoundProcessor(KeyerObserver):

    # State machine init. dit dah
    def __init__(self):
        # Tone
        self._tone_generator = ToneGenerator()
        self._started = False

    # Play dit and release dit
    def play_dit(self,time_dit:float, silence: float):
        self._play_tone(time_dit, silence)

    # Play dah and release dah
    def play_dah(self , time_dah:float, silence: float):
        self._play_tone(time_dah, silence)

    def _play_tone(self, time_to_play:float, silence: float):
        if self._started:
            self._tone_generator.play_tone(time_to_play, silence)
        else:
            print("SoundKeyer is not started. Please call start() method before playing tones.")

    def start(self):
        self._tone_generator.start()
        self._started = True

    def stop(self):
        self._tone_generator.stop()
        self._started = False

