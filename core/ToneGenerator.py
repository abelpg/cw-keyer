import struct

import pyaudio
import numpy as np
from concurrent.futures import ThreadPoolExecutor

class ToneGenerator:
    def __init__(self, sample_rate: int = 44100, frames_per_buffer: int = 1000, frequency: int = 800, amplitude: float = 1):
        # Init audio
        self._audio = pyaudio.PyAudio()

        self._sample_rate = sample_rate
        self._frames_per_buffer = frames_per_buffer
        self._frequency = frequency
        self._amplitude = amplitude

        self._omega = float(self._frequency) * (np.pi * 2.0) / float(self._sample_rate)

        self._audio_stream = None

        self._tone_cycle = None
        self._silence_cycle = None
        self._thread_pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="ToneGeneratorThreadPool")



    def _calculate_points_cycle(self):
        return int(self._sample_rate / self._frequency)

    def _generate_tone_cycle(self):
        range_n = self._calculate_points_cycle()

        dt = 1.0 / self._sample_rate

        # Calculate 1 cycle
        cycle =  (self._amplitude * np.sin(2 * np.pi * self._frequency * n * dt) for n in range(range_n))
        # Transform to bytes
        data = b''.join(struct.pack('f', samp) for samp in cycle)
        return data

    def _generate_silence_cycle(self):
        range_n = self._calculate_points_cycle()
        # Calculate 1 cycle
        cycle =  (0 for n in range(range_n))
        # Transform to bytes
        data = b''.join(struct.pack('f', samp) for samp in cycle)
        return data

    def play_tone(self, tone_duration: float, silence_duration: float = 0):
        tone_cycles = int(self._frequency * tone_duration)  # repeat for T cycles
        for n in range(tone_cycles):
            self._audio_stream.write(self._tone_cycle)

        if silence_duration > 0:
            silence_cycles = int(self._frequency * silence_duration)
            for n in range(silence_cycles):
                self._audio_stream.write(self._silence_cycle)

    def play_bg_tone(self, tone_duration: float, silence_duration: float = 0):
        self._thread_pool.submit(self.play_tone, tone_duration, silence_duration)



    def start(self):
        self._audio_stream = self._audio.open(format=pyaudio.paFloat32,
                                              rate=self._sample_rate,
                                              channels=1,
                                              output=True,
                                              frames_per_buffer=self._frames_per_buffer)


        self._tone_cycle = self._generate_tone_cycle()
        self._silence_cycle = self._generate_silence_cycle()


    def stop(self):
        self._audio_stream.close()
        self._audio.terminate()

