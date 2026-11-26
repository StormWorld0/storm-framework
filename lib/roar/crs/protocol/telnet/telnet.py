# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author zxelzy (Refactored)

from .state import TelnetState
from .io import TelnetIO
from .iac import TelnetIAC


class TelnetClient(TelnetState, TelnetIAC, TelnetIO):
    """
    Telnet Protocol Wrapper di atas Socket.
    Terintegrasi dengan TelnetCmd & TelnetOpt untuk kontrol granular dan Type-Safety.
    """

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
