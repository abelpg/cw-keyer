import logging

from PySide6 import QtWidgets

from core.config import Configuration
from core.sound import SoundProcessor, ToneGenerator


class SoundForm:

    CONFIG_SOUND_FREQUENCY_KEY = "sound_frequency"
    CONFIG_SOUND_DEVICE_OUTPUT = "sound_device_output"

    def __init__(self, parent: QtWidgets.QBoxLayout, callback_attach_device_observer, callback_detach_device_observer):
        self._logger = logging.getLogger(__name__)

        self._callback_attach_device_observer = callback_attach_device_observer
        self._callback_detach_device_observer = callback_detach_device_observer

        self._sound_processor = None

        self._config = Configuration()

        layout = QtWidgets.QVBoxLayout()
        widget = QtWidgets.QWidget()

        self._button_sound_processor = QtWidgets.QPushButton("Sidetone processor")
        self._button_sound_processor.clicked.connect(self._click_sound_processor)
        layout.addWidget(self._button_sound_processor)

        ##################
        widget_h = QtWidgets.QWidget()
        layout_h = QtWidgets.QHBoxLayout()

        label = QtWidgets.QLabel("Sound Frequency:")
        label.setMaximumWidth(100)
        layout_h.addWidget(label)

        self._logger.info(str( ToneGenerator.get_available_output_devices()))
        self._original_device_list = ToneGenerator.get_available_output_devices()
        self._device_list = QtWidgets.QComboBox()
        self._set_devices()
        layout_h.addWidget(self._device_list)


        self._text_frequency = QtWidgets.QLineEdit(self._config.get_config(__name__,
                                                                     key=SoundForm.CONFIG_SOUND_FREQUENCY_KEY,
                                                                     default_value="600"))
        self._text_frequency.setMaximumWidth(50)

        layout_h.addWidget(self._text_frequency)

        widget_h.setLayout(layout_h)
        layout.addWidget(widget_h)
        ##################

        widget.setLayout(layout)
        parent.addWidget(widget)

    def _set_devices(self):

        device_config = self._config.get_config(__name__, SoundForm.CONFIG_SOUND_DEVICE_OUTPUT)
        index = 0
        found = False

        for device in self._original_device_list:
            device_index = device.index
            self._device_list.addItem(str(device), device_index)
            if device_config is not None and device_index == int(device_config) and not found:
                found = True
            elif not found:
                index += 1
        self._logger.debug(f"Found {index} {found} devices.")
        if found:
            self._device_list.setCurrentIndex(index)


    def _click_sound_processor(self):
        if self._sound_processor is None:
            self.start()
        else:
            self.stop()

    def _get_device(self):
        device = self._device_list.currentData()
        if device is not None:
            self._config.put_config(__name__, SoundForm.CONFIG_SOUND_DEVICE_OUTPUT, str(device))
            for original_device in self._original_device_list:
                if device == original_device.index:
                     return original_device
        return None

    def _get_frequency(self)    :
        frequency = self._text_frequency.text()
        self._config.put_config(__name__, key=SoundForm.CONFIG_SOUND_FREQUENCY_KEY, value=frequency)
        return int(frequency)

    def start(self):
        if self._sound_processor is None:
            self._sound_processor = SoundProcessor(frequency=self._get_frequency(), output_device=self._get_device())
            self._sound_processor.start()
            self._callback_attach_device_observer(self._sound_processor)


            self._button_sound_processor.setStyleSheet("background-color: green; ")
            self._logger.debug("Sound processor started.")
        else:
            self._logger.debug("Sound keyer is already running.")

    def stop(self):
        if self._sound_processor is not None:
            self._sound_processor.stop()
            self._callback_detach_device_observer(self._sound_processor)
            self._sound_processor = None

            self._button_sound_processor.setStyleSheet("background-color: red; ")
            self._logger.debug("Sound processor stopped.")
        else:
            self._logger.debug("Sound keyer is not running, skipping stop.")