import logging

from PySide6 import QtWidgets

from core.config import Configuration
from core.keyer import Keyer
from gui.keyer import CommEmulatorKeyerForm
from gui.sound import SoundForm


class KeyerForm:

    CONFIG_KEYER_WPM_KEY = "wpm"

    def __init__(self, parent: QtWidgets.QBoxLayout,
                 callback_attach_device_observer=None,
                 callback_detach_device_observer=None):

        self._callback_attach_device_observer = callback_attach_device_observer
        self._callback_detach_device_observer = callback_detach_device_observer

        self._logger = logging.getLogger(__name__)

        self._config = Configuration()

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

        self._text_wpm = QtWidgets.QLineEdit(self._config.get_config(__name__,
                                                                     key=KeyerForm.CONFIG_KEYER_WPM_KEY,
                                                                     default_value="20"))
        self._text_wpm.setMaximumWidth(50)

        layout_h.addWidget(self._text_wpm)

        widget_h.setLayout(layout_h)
        layout.addWidget(widget_h)
        ##################

        self._sound_form = SoundForm(parent=layout,
                                     callback_attach_device_observer=self._attach_device_observer,
                                     callback_detach_device_observer=self._detach_device_observer)

        layout.addWidget(QtWidgets.QFrame(frameShape=QtWidgets.QFrame.HLine))

        ##################
        layout.addWidget(QtWidgets.QLabel("Run keyer with comm output (HL2):"))

        self._comm_form = CommEmulatorKeyerForm(layout,
                                                callback_attach_device_observer=self._attach_device_observer,
                                                callback_detach_device_observer=self._detach_device_observer)

        widget.setLayout(layout)
        parent.addWidget(widget)

    def _detach_device_observer(self, observer):
        if self._keyer is not None:
            self._keyer.detach_observer(observer)
    def _attach_device_observer(self, observer):
        if self._keyer is not None:
            self._keyer.attach_observer(observer)


    def _click_keyer(self):
        if self._keyer is None:
            self.start()
        else:
            self.stop()


    def stop(self):
        if self._keyer is not None:
            self._sound_form.stop()
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
            self._config.put_config(__name__, key=KeyerForm.CONFIG_KEYER_WPM_KEY, value=wpm)

            self._keyer = Keyer(wpm=int(wpm))
            self._keyer.start()

            self._callback_attach_device_observer(self._keyer)

            self._sound_form.start()

            self._button_keyer.setStyleSheet("background-color: green; ")
            self._logger.debug("Keyer started.")
        else:
            self._logger.debug("Keyer is already running.")