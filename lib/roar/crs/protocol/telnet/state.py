import smf

from ..socket import Socket
from apps.utility.colors import CC


class TelnetState:
    """Managing Telnet State"""

    def __init__(
        self, 
        host: str,
        port: int = 23,
        timeout: int | float = 3.0,
        raw: bool = False,
        **kwargs,
    ):
        """Open Telnet connection over TCP Socket"""

        # Open Socket
        self.sock = Socket()
        self.sock.timeout(timeout)
        self.sock.create_connection((host, port))

        # options
        self.raw = raw
        # Buffer storage
        self._buffer = b""
        # Telnet handshake variables
        self._iac_fragment = b""

        if kwargs:
            smf.printf(
                f"[!] {CC.YELLOW}Unrecognized parameters dropped =>{CC.RESET}", kwargs
            )
