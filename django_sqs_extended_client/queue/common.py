from signal import SIGINT, SIGTERM, signal


class SignalHandler:
    received_signal = False

    def __init__(self):
        self.received_signal = False
        signal(SIGINT, self._signal_handler)
        signal(SIGTERM, self._signal_handler)

    def _signal_handler(self, signal_item, frame):
        print(f"handling signal {signal_item}, exiting gracefully")
        self.received_signal = True
