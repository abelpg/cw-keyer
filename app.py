import logging
import sys

from gui import AppGui

try:
    from PySide6 import  QtWidgets
    from PySide6.QtWidgets import QApplication
except Exception:
    QtWidgets = None
    QApplication = None

def main(args=None):
    logging.basicConfig(level=logging.DEBUG)
    __logger = logging.getLogger(__name__)

    if QtWidgets is None:
        __logger.error("PySide6 is not installed. Install with: python -m pip install PySide6")
        return 2

    q_application = QApplication(args)
    app = AppGui()
    app.show()

    return q_application.exec()

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))


