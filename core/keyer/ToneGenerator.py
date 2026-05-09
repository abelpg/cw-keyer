import logging
from time import sleep, time
from concurrent.futures import ThreadPoolExecutor

import pyaudio
import numpy as np

from core.common import BaseItem

"""
This module provides a ToneGenerator class that can be used to generate and play tones through the audio output device.
"""
class AudioDevice(BaseItem):

    def __init__(self, device_info ):
        super().__init__()

        self.index = device_info["index"]
        self.name = device_info["name"]
        self.default_sample_rate = device_info["defaultSampleRate"]

    def _to_string(self):
        return f"{"0" +str(self.index) if self.index < 10 else self.index} : {self.name}"

class ToneGenerator:

    def __init__(self,
                 sample_rate: int = 44000,
                 frames_per_buffer: int = 100,
                 frequency: int = 650,
                 amplitude: float = 0.5,
                 output_device : AudioDevice = None):
        self._logger = logging.getLogger(__name__)
        # Init audio
        self._audio = pyaudio.PyAudio()

        self._sample_rate = sample_rate
        self._frames_per_buffer = frames_per_buffer
        self._frequency = frequency
        self._amplitude = amplitude

        self._output_device = output_device

        self._cache_audio_data = dict()
        self._cache_silence_data = dict()

        self._executor = ThreadPoolExecutor(max_workers=1)

        self._audio_stream = None
        self._started = False

    def _generate_silence(self, silence_duration: float):

        data = self._cache_silence_data.get(silence_duration)

        if data is None:
            self._logger.info("Generate silence " + str(silence_duration))
            t = np.linspace(0, silence_duration, int(self._sample_rate * silence_duration), endpoint=False)
            out = (t * 0).astype(np.int16)
            data = out.tobytes()

            self._cache_silence_data[silence_duration] = data

        return data

    def _generate_soft_tone(self, tone_duration: float):
        data = self._cache_audio_data.get(tone_duration)
        if data is None:
            self._logger.info("Generate tone " +str(tone_duration))
            # Eje de tiempo
            t = np.linspace(0, tone_duration, int(self._sample_rate * tone_duration), endpoint=False)
            # Generar onda senoidal pura
            # Formula: A * sin(2 * pi * f * t)
            waveform = self._amplitude * np.sin(2 * np.pi * self._frequency * t)

            # Definir tiempos de la envolvente (en segundos)
            attack_t = 0.006
            release_t = 0.004

            # Convertir tiempos a número de muestras
            att_samples = int(attack_t * self._sample_rate)
            rel_samples = int(release_t * self._sample_rate)
            sus_samples = len(waveform) - att_samples - rel_samples

            # Crear la envolvente (0 -> 1 -> 1 -> 0)
            envelope = np.concatenate([
                np.linspace(0, 1, att_samples),  # Attack
                np.ones(sus_samples),  # Sustain
                np.linspace(1, 0, rel_samples)  # Release
            ])

            # Aplicar envolvente al audio
            soft_audio = waveform * envelope

            # Guardar como archivo WAV de 16 bits
            out = (soft_audio * 32767).astype(np.int16)
            data = out.tobytes()
            self._cache_audio_data[tone_duration] = data

        return data

    def _internal_play_tone(self, tone_duration: float, silence_duration: float):
        if self._started:
            self._audio_stream.write(self._generate_soft_tone(tone_duration))
            self._audio_stream.write(self._generate_silence(silence_duration))
        else:
            self._logger.warning("ToneGenerator is not started. Please call start() method before playing tones.")

    def play_tone(self, tone_duration: float, silence_duration: float = 0):
       self._executor.submit(self._internal_play_tone, tone_duration, silence_duration)

    def start(self):

        self._logger.info("ToneGenerator is started " +str(self._sample_rate)
                          + " amplitude: " + str(self._amplitude)
                          +" sample rate and  output " + str(self._output_device))

        self._audio_stream = self._audio.open(format=pyaudio.paInt16,
                                              rate=self._sample_rate,
                                              channels=1,
                                              output=True,
                                              output_device_index=self._output_device.index if self._output_device else None,
                                              frames_per_buffer=self._frames_per_buffer)
        self._cache_silence_data.clear()
        self._started = True

    def stop(self):
        self._audio_stream.close()
        self._audio.terminate()
        self._started = False

    """
    Get the list of available output audio devices.
    Each device is represented as an AudioDevice object containing its index, name, and default sample rate.
    The list is sorted by device index for easier selection.
    """
    @staticmethod
    def get_available_output_devices():
        audio = pyaudio.PyAudio()
        output_devices = []
        for i in range(audio.get_device_count()):
            device_info = audio.get_device_info_by_index(i)
            if device_info.get('maxOutputChannels') > 0 and device_info.get('hostApi') == 0:
                output_devices.append(AudioDevice(device_info))
        audio.terminate()
        output_devices.sort()
        return output_devices
