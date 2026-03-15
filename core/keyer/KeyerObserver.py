import queue
import threading
from abc import ABC, abstractmethod

class KeyerItem:

    def __init__(self, time: float, silence: float):
        self.time = time
        self.silence = silence

class KeyerObserver(ABC):

    def __init__(self):
        # Principal thread to tak tics from dit and dah
        self._queue = queue.SimpleQueue()
        self._thread = threading.Thread(target=self._run_thread, daemon=True, name="KeyerObserver Thread")
        self._thread_stop = False

    def _run_thread(self):
        while not self._thread_stop:

            item = self._queue.get()
            self._process_item(item)

            pass

    def stop(self):
        self._thread_stop = True

    def start(self):
        self._thread.start()

    def add_keyer_item(self, time : float, silence: float):
        self._queue.put(KeyerItem(time, silence))

    """
    Function called to send signal dah.
    """
    @abstractmethod
    def _process_item(self, keyer_item: KeyerItem):
        pass
