import logging

from PySide6 import QtWidgets


from core.emulator import CommEmulator
from core.emulator.CommSerial import CommSerial


class CommEmulatorNoKeyerForm:
    def __init__(self, parent: QtWidgets.QBoxLayout,
                 callback_attach_device_observer=None,
                 callback_detach_device_observer=None):
        self._logger = logging.getLogger(__name__)

        self.parent = parent
        self._callback_attach_device_observer = callback_attach_device_observer
        self._callback_detach_device_observer = callback_detach_device_observer


        self._comm_emulator = None

        layout = QtWidgets.QHBoxLayout()
        widget = QtWidgets.QWidget()
        widget.setMaximumHeight(45)

        widget.setLayout(layout)

        self._button_comm_emulator = QtWidgets.QPushButton("Comm emulator")
        self._button_comm_emulator.clicked.connect(self._click_comm_emulator)

        self._comm_emulator_port = QtWidgets.QComboBox()
        for port in CommSerial.list_ports():
            self._comm_emulator_port.addItem(port, port)

        self._comm_emulator_port.currentIndexChanged.connect(self._on_comm_emulator_port_changed)

        layout.addWidget(self._button_comm_emulator)
        layout.addWidget(self._comm_emulator_port)

        parent.addWidget(widget)

    def _on_comm_emulator_port_changed(self, _index: int) -> None:
        mode =  self._comm_emulator_port.currentData()
        self._logger.debug("Mode: {}".format(mode))

    def _start_comm_emulator(self):
        # Protect concurrent loop
        if self._comm_emulator is  None:
            self._comm_emulator = CommEmulator()
            self._callback_attach_device_observer(self._comm_emulator)
            self._comm_emulator.start()

            self._button_comm_emulator.setStyleSheet("background-color: green; ")
            self._logger.debug("Comm emulator started.")
        else:
            self._logger.debug("Comm emulator is already running.")

    def _stop_comm_emulator(self):
        if self._comm_emulator is not None:
            self._callback_detach_device_observer(self._comm_emulator)
            self._comm_emulator.stop()
            self._comm_emulator = None
            self._button_comm_emulator.setStyleSheet("background-color: red; ")
            self._logger.debug("Comm emulator stopped.")
        else:
            self._logger.debug("Comm emulator is not running, skipping stop.")

    def _click_comm_emulator(self):
        if self._comm_emulator is None:
            self._start_comm_emulator()
        else:
            self._stop_comm_emulator()

    def stop(self):
        self._stop_comm_emulator()