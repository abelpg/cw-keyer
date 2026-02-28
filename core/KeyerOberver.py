from abc import ABC, abstractmethod

class KeyerObserver(ABC):

    """
    Function called to send signal dah.
    """
    @abstractmethod
    def play_dah(self, time_dah:float, silence: float):
        pass

    """
    Function called to send signal dit.   
    """
    @abstractmethod
    def play_dit(self, time_dit:float, silence: float):
        pass