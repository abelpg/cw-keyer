import logging

from PySide6 import QtWidgets
from core.config import Configuration
from core.emulator.CommSerial import CommSerial

class SerialForm:

    CONFIG_SERIAL_PORT_KEY = "comm_emulator_port"

    def __init__(self, parent: QtWidgets.QBoxLayout, class_name, button_text : str, callback_click=None):
        self._logger = logging.getLogger(__name__)

        self.parent = parent
        self._config = Configuration()

        self._class_name = class_name

        self._comm_emulator = None

        layout = QtWidgets.QHBoxLayout()
        widget = QtWidgets.QWidget()

        widget.setLayout(layout)

        self._button_comm_emulator = QtWidgets.QPushButton(button_text)
        self._button_comm_emulator.clicked.connect(callback_click)

        self._comm_emulator_port = QtWidgets.QComboBox()
        self._set_ports()

        layout.addWidget(self._button_comm_emulator)
        layout.addWidget(self._comm_emulator_port)

        parent.addWidget(widget)

    def _set_ports(self):
        if self._comm_emulator_port is not None:
            config_port = self._config.get_config(self._class_name, SerialForm.CONFIG_SERIAL_PORT_KEY)
            index = 0
            found = False
            for port in CommSerial.list_ports():
                self._comm_emulator_port.addItem(port, port)
                if port == config_port and not found:
                    found = True
                elif not found:
                    index += 1
            self._logger.debug(f"Found {index} {found} ports.")
            if found:
                self._comm_emulator_port.setCurrentIndex(index)

    def _get_port(self):
        port = self._comm_emulator_port.currentData()
        self._config.put_config(self._class_name, SerialForm.CONFIG_SERIAL_PORT_KEY, port)
        return port

