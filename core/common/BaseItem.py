import logging
from abc import ABC, abstractmethod

"""
BaseItem is an abstract class that represents a generic item in the application. 
It provides a common interface for all items and implements comparison methods based on their string representation. 
This allows items to be easily sorted and compared based on their string representation.
"""
class BaseItem(ABC):

    def __init__(self):
        self._logger = logging.getLogger(__name__)

    @abstractmethod
    def _to_string(self):
        pass

    def __str__(self):
        return self._to_string()

    def __repr__(self):
        return self.__str__()

    def __lt__(self, other):
        return str(self) < str(other)

    def __gt__(self, other):
        return str(self) > str(other)

    def __le__(self, other):
        return str(self) <= str(other)

    def __ge__(self, other):
        return str(self) >= str(other)