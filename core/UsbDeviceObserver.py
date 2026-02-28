
from abc import ABC, abstractmethod


"""
Interface for observing keyer events. Implement this interface to receive notifications when the dit or dah is pressed or released.
"""
class UsbDeviceObserver(ABC):

    """
    Called when the dit is pressed or released. The pressed parameter is True when the dit is pressed and False when it is released.
    """
    @abstractmethod
    def on_dit(self, pressed: bool):
        pass

    """
    Called when the dah is pressed or released. The pressed parameter is True when the dah is pressed and False when it is released.
    """
    @abstractmethod
    def on_dah(self, pressed: bool):
        pass