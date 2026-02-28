from core.KeyerOberver import KeyerObserver
from core.ToneGenerator import ToneGenerator

class SoundKeyer(KeyerObserver):

    # State machine init. dit dah
    def __init__(self):
        # Tone
        self._tone_generator = ToneGenerator()

    # Play dit and release dit
    def play_dit(self,time_dit:float, silence: float):
        print("Play dit {}s with silence {}s".format(time_dit, silence))
        self._tone_generator.play_tone(time_dit, silence)


    # Play dah and release dah
    def play_dah(self , time_dah:float, silence: float):
        print("Play dah {}s with silence {}s".format(time_dah, silence))
        self._tone_generator.play_tone(time_dah, silence)

    def start(self):
        self._tone_generator.start()

    def stop(self):
        self._tone_generator.stop()

