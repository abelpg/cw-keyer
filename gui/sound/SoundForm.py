import logging

from PySide6 import QtWidgets

from core.config import Configuration
from core.sound import SoundProcessor

class SoundForm:

    CONFIG_SOUND_FREQUENCY_KEY = "sound_frequency"

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


    def _click_sound_processor(self):
        if self._sound_processor is None:
            self.start()
        else:
            self.stop()


    def start(self):
        if self._sound_processor is None:

            frequency = self._text_frequency.text()
            self._config.put_config(__name__, key=SoundForm.CONFIG_SOUND_FREQUENCY_KEY, value=frequency)

            self._sound_processor = SoundProcessor(frequency=int(frequency))
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