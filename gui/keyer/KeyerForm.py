import logging

from PySide6 import QtWidgets

from core.config import Configuration
from core.keyer import Keyer,ToneGenerator
from gui.keyer import CommEmulatorKeyerForm
from gui.keyer.N1MMForm import N1MMForm


class KeyerForm:

    CONFIG_KEYER_WPM_KEY = "wpm"
    CONFIG_SOUND_FREQUENCY_KEY = "sound_frequency"
    CONFIG_SOUND_AMPLITUDE_KEY = "sound_amplitude"
    CONFIG_SOUND_DEVICE_OUTPUT = "sound_device_name_output"

    def __init__(self, parent: QtWidgets.QBoxLayout,
                 callback_attach_device_observer=None,
                 callback_detach_device_observer=None):

        self._callback_attach_device_observer = callback_attach_device_observer
        self._callback_detach_device_observer = callback_detach_device_observer

        self._logger = logging.getLogger(__name__)

        self._keyer = None
        layout = QtWidgets.QVBoxLayout()
        widget = QtWidgets.QWidget()

        ##################
        widget_h = QtWidgets.QWidget()
        layout_h = QtWidgets.QHBoxLayout()

        self._button_keyer = QtWidgets.QPushButton("Keyer")
        self._button_keyer.clicked.connect(self._click_keyer)
        layout_h.addWidget(self._button_keyer)

        label = QtWidgets.QLabel("WPM:")
        label.setMaximumWidth(40)
        layout_h.addWidget(label)

        self._text_wpm = QtWidgets.QLineEdit(Configuration.get_config(__name__,
                                                                     key=KeyerForm.CONFIG_KEYER_WPM_KEY,
                                                                     default_value="20"))
        self._text_wpm.setMaximumWidth(50)

        layout_h.addWidget(self._text_wpm)

        widget_h.setLayout(layout_h)
        layout.addWidget(widget_h)
        ##################

        ##################
        widget_h = QtWidgets.QWidget()
        layout_h = QtWidgets.QHBoxLayout()

        label = QtWidgets.QLabel("Sound Frequency:")
        label.setMaximumWidth(80)
        layout_h.addWidget(label)

        self._original_device_list = []
        self._device_list = QtWidgets.QComboBox()
        self._set_devices()
        layout_h.addWidget(self._device_list)

        self._text_frequency = QtWidgets.QLineEdit(Configuration.get_config(__name__,
                                                                            key=KeyerForm.CONFIG_SOUND_FREQUENCY_KEY,
                                                                            default_value="600"))
        self._text_frequency.setMaximumWidth(50)

        layout_h.addWidget(self._text_frequency)

        self._text_amplitude = QtWidgets.QLineEdit(Configuration.get_config(__name__,
                                                                            key=KeyerForm.CONFIG_SOUND_AMPLITUDE_KEY,
                                                                            default_value="0.5"))
        self._text_amplitude.setMaximumWidth(50)
        layout_h.addWidget(self._text_amplitude)

        widget_h.setLayout(layout_h)
        layout.addWidget(widget_h)

        ##################
        layout.addWidget(QtWidgets.QFrame(frameShape=QtWidgets.QFrame.HLine))
        layout.addWidget(QtWidgets.QLabel("Input keyer from N1MM:"))
        self._comm_n1mm_form = N1MMForm(layout, call_back_get_keyer = self._get_keyer)

        ##################
        layout.addWidget(QtWidgets.QFrame(frameShape=QtWidgets.QFrame.HLine))
        layout.addWidget(QtWidgets.QLabel("Run keyer with comm output (HL2):"))
        self._comm_form = CommEmulatorKeyerForm(layout, call_back_get_keyer = self._get_keyer)

        widget.setLayout(layout)
        parent.addWidget(widget)

    def _detach_device_observer(self, observer):
        if self._keyer is not None:
            self._keyer.detach_observer(observer)
    def _attach_device_observer(self, observer):
        if self._keyer is not None:
            self._keyer.attach_observer(observer)

    def _get_keyer(self):
        return self._keyer

    def _click_keyer(self):
        if self._keyer is None:
            self.start()
        else:
            self.stop()

    def _set_devices(self):
        self._original_device_list = ToneGenerator.get_available_output_devices()

        for device in self._original_device_list:
            self._logger.info(f"Device: {device}, index: {device.index}")

        device_config = Configuration.get_config(__name__, KeyerForm.CONFIG_SOUND_DEVICE_OUTPUT)
        index = 0
        found = False

        for device in self._original_device_list:
            device_name = device.name
            self._device_list.addItem(str(device), device_name)
            if device_config is not None and device_name == device_config and not found:
                found = True
            elif not found:
                index += 1
        self._logger.debug(f"Found {index} {found} devices.")
        if found:
            self._device_list.setCurrentIndex(index)

    def _get_device(self):
        device = self._device_list.currentData()
        if device is not None:
            Configuration.put_config(__name__, KeyerForm.CONFIG_SOUND_DEVICE_OUTPUT, device)
            for original_device in self._original_device_list:
                if device == original_device.name:
                    return original_device
        return None

    def _get_frequency(self):
        frequency = self._text_frequency.text()
        Configuration.put_config(__name__, key=KeyerForm.CONFIG_SOUND_FREQUENCY_KEY, value=frequency)
        return int(frequency)

    def _get_amplitude(self):
        amplitude = self._text_amplitude.text()
        Configuration.put_config(__name__, key=KeyerForm.CONFIG_SOUND_AMPLITUDE_KEY, value=amplitude)
        return float(amplitude)

    def stop(self):
        if self._keyer is not None:
            self._comm_form.stop()
            self._callback_detach_device_observer(self._keyer)
            self._keyer.stop()
            self._keyer = None

            self._button_keyer.setStyleSheet("background-color: red; ")
            self._logger.debug("Keyer stopped.")
        else:
            self._logger.debug("Keyer is not running, skipping stop.")

    def start(self):
        if self._keyer is None:

            wpm = self._text_wpm.text()
            Configuration.put_config(__name__, key=KeyerForm.CONFIG_KEYER_WPM_KEY, value=wpm)

            self._keyer = Keyer(wpm=int(wpm),frequency=self._get_frequency(),  amplitude=self._get_amplitude(), output_device=self._get_device())
            self._keyer.start()

            self._callback_attach_device_observer(self._keyer)

            self._button_keyer.setStyleSheet("background-color: green; ")
            self._logger.debug("Keyer started.")
        else:
            self._logger.debug("Keyer is already running.")