# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author zxelzy (Refactored)

from .state import TelnetState
from .response import TelnetResponse
from .io import TelnetIO
from .iac import TelnetIAC


class TelnetClient(TelnetState, TelnetResponse, TelnetIAC, TelnetIO):
    """
    Telnet Protocol Wrapper di atas Socket.
    Terintegrasi dengan TelnetCmd & TelnetOpt untuk kontrol granular dan Type-Safety.
    """

    def setoptions(self, raw: bool = False):
        if not isinstance(raw, bool):
            raise TypeError("setoptions must be bool")
        self.raw = raw
        return self

    def timeout(self, value: float):
        if not isinstance(value, float) or not isinstance(value, int):
            raise TypeError("Timeout must be float or int")
        self._timeout = float(value)
        return self

    def close(self):
        self.sock.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
