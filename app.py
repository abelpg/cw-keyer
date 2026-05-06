import logging
import sys
from gui import AppGui

try:
    sys.getwindowsversion()
except AttributeError:
    isWindows = False
else:
    isWindows = True

try:
    from PySide6 import  QtWidgets
    from PySide6.QtWidgets import QApplication
except Exception:
    QtWidgets = None
    QApplication = None


def high_priority():
    """ Set the priority of the process to below-normal."""
    if isWindows:
        # Based on:
        #   "Recipe 496767: Set Process Priority In Windows" on ActiveState
        #   http://code.activestate.com/recipes/496767/
        import win32api, win32process, win32con

        pid = win32api.GetCurrentProcessId()
        handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
        win32process.SetPriorityClass(handle, win32process.ABOVE_NORMAL_PRIORITY_CLASS)
    else:
        import os
        os.nice(-5)

def main(args=None):
    logging.basicConfig(level=logging.INFO)
    __logger = logging.getLogger(__name__)
    high_priority()

    if QtWidgets is None:
        __logger.error("PySide6 is not installed. Install with: python -m pip install PySide6")
        return 2

    q_application = QApplication(args)
    app = AppGui()
    app.show()

    return q_application.exec()

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))



