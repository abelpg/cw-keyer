import logging
from statistics import mode

from PySide6 import QtWidgets

from core.config import Configuration
from core.keyer import Keyer,Mode,ToneGenerator
from gui.keyer import CommEmulatorKeyerForm
from gui.keyer.N1MMForm import N1MMForm


class KeyerForm:

    CONFIG_KEYER_WPM_KEY = "wpm"
    CONFIG_KEYER_MODE = "mode"
    CONFIG_SOUND_FREQUENCY_KEY = "sound_frequency"
    CONFIG_SOUND_AMPLITUDE_KEY = "sound_amplitude_percentage"
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

        layout.addWidget(self._add_form_keyer())
        layout.addWidget(self._add_form_devices())
        layout.addWidget(self._add_form_sound())
        layout.addWidget(self._add_form_mode())
        ##################


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

    def _add_form_mode(self):
        widget_h = QtWidgets.QWidget()
        layout_h = QtWidgets.QHBoxLayout()

        label = QtWidgets.QLabel("Mode:")
        label.setMaximumWidth(100)
        layout_h.addWidget(label)

        self._mode_list = QtWidgets.QComboBox()
        self._set_mode_list()
        layout_h.addWidget(self._mode_list)


        widget_h.setLayout(layout_h)
        return widget_h

    def _add_form_sound(self):
        widget_h = QtWidgets.QWidget()
        layout_h = QtWidgets.QHBoxLayout()

        label = QtWidgets.QLabel("Sound Frequency:")
        label.setMaximumWidth(100)
        layout_h.addWidget(label)
        self._text_frequency = QtWidgets.QSpinBox(minimum=300, maximum=900, value=self._get_frequency_config())
        self._text_frequency.setMaximumWidth(90)
        layout_h.addWidget(self._text_frequency)

        label = QtWidgets.QLabel("Amplitude:")
        label.setMaximumWidth(100)
        layout_h.addWidget(label)
        self._text_amplitude =  QtWidgets.QSpinBox(minimum=0, maximum=100, value=self._get_amplitude_config())
        self._text_amplitude.setMaximumWidth(90)
        layout_h.addWidget(self._text_amplitude)

        widget_h.setLayout(layout_h)
        return  widget_h

    def _add_form_devices(self):

        widget_h = QtWidgets.QWidget()
        layout_h = QtWidgets.QHBoxLayout()

        label = QtWidgets.QLabel("Output:")
        label.setMaximumWidth(80)
        layout_h.addWidget(label)
        self._original_device_list = []
        self._device_list = QtWidgets.QComboBox()
        self._set_devices()
        layout_h.addWidget(self._device_list)


        widget_h.setLayout(layout_h)
        return widget_h

    def _add_form_keyer(self):
        widget_h = QtWidgets.QWidget()
        layout_h = QtWidgets.QHBoxLayout()

        self._button_keyer = QtWidgets.QPushButton("Keyer")
        self._button_keyer.clicked.connect(self._click_keyer)
        layout_h.addWidget(self._button_keyer)

        label = QtWidgets.QLabel("WPM:")
        label.setMaximumWidth(40)
        layout_h.addWidget(label)

        self._text_wpm = QtWidgets.QSpinBox(minimum=10, maximum=40, value=self._get_wpm_config())
        self._text_wpm.setMaximumWidth(90)

        layout_h.addWidget(self._text_wpm)

        widget_h.setLayout(layout_h)
        return widget_h

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

    def _set_mode_list(self):

        mode_config = Configuration.get_config(__name__, KeyerForm.CONFIG_KEYER_MODE)
        index = 0
        found = False

        for mode in Mode:
            self._mode_list.addItem( mode.value, mode.name)
            if mode_config is not None and mode.name == mode_config and not found:
                found = True
            elif not found:
                index += 1

        if found:
            self._mode_list.setCurrentIndex(index)

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

    def _get_mode(self):
        mode = self._mode_list.currentData()
        if mode is not None:
            Configuration.put_config(__name__, KeyerForm.CONFIG_KEYER_MODE, mode)
            return Mode[mode]
        return None

    def _get_device(self):
        device = self._device_list.currentData()
        if device is not None:
            Configuration.put_config(__name__, KeyerForm.CONFIG_SOUND_DEVICE_OUTPUT, device)
            for original_device in self._original_device_list:
                if device == original_device.name:
                    return original_device
        return None

    def _get_wmp(self):
        wpm = self._text_wpm.text()
        Configuration.put_config(__name__, key=KeyerForm.CONFIG_KEYER_WPM_KEY, value=wpm)
        return int(wpm)

    def _get_frequency(self):
        frequency = self._text_frequency.text()
        Configuration.put_config(__name__, key=KeyerForm.CONFIG_SOUND_FREQUENCY_KEY, value=frequency)
        return int(frequency)

    def _get_amplitude(self):
        amplitude = self._text_amplitude.text()
        Configuration.put_config(__name__, key=KeyerForm.CONFIG_SOUND_AMPLITUDE_KEY, value=amplitude)
        return float(int(amplitude) / 100.0)


    @staticmethod
    def _get_frequency_config():
        return int(Configuration.get_config(__name__,
                                 key=KeyerForm.CONFIG_SOUND_FREQUENCY_KEY,
                                 default_value="600"))

    @staticmethod
    def _get_amplitude_config():
        return int(Configuration.get_config(__name__,
                                 key=KeyerForm.CONFIG_SOUND_AMPLITUDE_KEY,
                                 default_value="50"))

    @staticmethod
    def _get_wpm_config():
        return int(Configuration.get_config(__name__,
                                 key=KeyerForm.CONFIG_KEYER_WPM_KEY,
                                 default_value="20"))


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


            self._get_mode()
            self._keyer = Keyer(wpm=self._get_wmp(),
                                frequency=self._get_frequency(),
                                amplitude=self._get_amplitude(),
                                output_device=self._get_device(),
                                mode=self._get_mode())
            self._keyer.start()

            self._callback_attach_device_observer(self._keyer)

            self._button_keyer.setStyleSheet("background-color: green; ")
            self._logger.debug("Keyer started.")
        else:
            self._logger.debug("Keyer is already running.")