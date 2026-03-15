import logging
import struct
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
                 sample_rate: int = 44100,
                 frames_per_buffer: int = 500,
                 frequency: int = 600,
                 amplitude: float = 0.3,
                 output_device : AudioDevice = None):
        self._logger = logging.getLogger(__name__)
        # Init audio
        self._audio = pyaudio.PyAudio()

        self._sample_rate = sample_rate
        self._frames_per_buffer = frames_per_buffer
        self._frequency = frequency
        self._amplitude = amplitude

        self._output_device = output_device

        self._omega = float(self._frequency) * (np.pi * 2.0) / float(self._sample_rate)

        self._audio_stream = None
        self._silence_cycle = None
        self._started = False



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

    def _generate_tone(self, tone_duration: float):
        tone_cycles = int(self._frequency * tone_duration)  # repeat for T cycles
        range_n = self._calculate_points_cycle()
        time_scale = self._frequency * 2 * np.pi /  self._sample_rate

        total_points = tone_cycles * range_n

        envelope_samples = int(total_points * 10.0 / 100.0)


        self._logger.debug("Generating tone with frequency: " + str(self._frequency)
                           + " Hz, duration: " + str(tone_duration)
                           + " seconds, which corresponds to "
                           + str(tone_cycles) + " cycles and envelope samples: " + str(envelope_samples))
        tone_complete = []
        current_point = 0
        for cyc in range(tone_cycles):
            # Calculate 1 cycle
            data = []

            for n in range(range_n):
                local_amplitude = self._amplitude
                if current_point < envelope_samples:
                    local_amplitude *= np.minimum(0.5 - (0.5 * np.cos(np.pi * cyc / envelope_samples)), 1.0)
                elif current_point >= (total_points - envelope_samples):
                    local_amplitude *= np.minimum(0.5 - (0.5 * np.cos(np.pi * (total_points - current_point) / envelope_samples)),
                                                  1.0)

                xn =  np.sin(n * time_scale)
                data.append(struct.pack('f',  local_amplitude  * xn))
                current_point += 1
            # Append cycle
            tone_complete.append(b''.join(data))

        return tone_complete


    def _generate_silence_cycle(self):
        range_n = self._calculate_points_cycle()
        # Calculate 1 cycle
        data = []
        for n in range(range_n):
            data.append(struct.pack('f', 0))
        # Transform to bytes
        return b''.join(data)

    def play_tone(self, tone_duration: float, silence_duration: float = 0):
        if self._started:

            tone_data = self._generate_tone(tone_duration)
            for data in tone_data:
                self._audio_stream.write(data)

            if silence_duration > 0:
                silence_cycles = int(self._frequency * silence_duration)
                for n in range(silence_cycles):
                    self._audio_stream.write(self._silence_cycle)
        else:
            self._logger.warning("ToneGenerator is not started. Please call start() method before playing tones.")

    def start(self):

        self._logger.info("ToneGenerator is started " +str(self._sample_rate) +" sample rate and  output " + str(self._output_device))

        self._audio_stream = self._audio.open(format=pyaudio.paFloat32,
                                              rate=self._sample_rate,
                                              channels=1,
                                              output=True,
                                              output_device_index=self._output_device.index if self._output_device else None,
                                              frames_per_buffer=self._frames_per_buffer)

        self._silence_cycle = self._generate_silence_cycle()
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
            if device_info.get('maxOutputChannels') > 0:
                output_devices.append(AudioDevice(device_info))
        audio.terminate()
        output_devices.sort()
        return output_devices
