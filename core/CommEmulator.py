from core.DeviceObserver import DeviceObserver


class CommEmulator(DeviceObserver):

    def __init__(self):
        super().__init__()

    """
        Proxy method to translate the dit and dah events to keyboard events.
        """

    def on_dah(self, pressed: bool):
        print("on dah", pressed)

    """
    Proxy method to translate the dit and dah events to keyboard events.
    """

    def on_dit(self, pressed: bool):
        print("on dit", pressed)
