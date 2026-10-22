import smf

from ..socket import Socket
from apps.utility.colors import CC


class TelnetState:
    """Mengelola State Telnet"""

    def __init__(
        self,
        host: str = None,
        port: int = 23,
        timeout: float = 3.0,
        **kwargs,
    ):
        """Open koneksi Telnet di atas TCP Socket"""

        # Open Inheritance
        self.sock = Socket()
        # Set Goroutine so as not to block
        self.sock.goroutine(10)
        self.sock.timeout(timeout)
        self.sock.socket(self.sock.AF_INET, self.sock.SOCK_STREAM)

        self.host = host
        self.port = port

        # Set Timeout Telnet Default
        self._timeout = timeout
        # Buffer storage
        self._buffer = b""
        # Telnet handshake variables
        self._iac_fragment = b""
        # Sessions State
        self._is_closed = False
        # Default Raw
        self.raw = False

        if kwargs:
            smf.printf(
                f"[!] {CC.YELLOW}Unrecognized parameters dropped =>{CC.RESET}", kwargs
            )

    def _ensure_open(self, operation: str):
        """Validasi internal untuk mencegah eksekusi operasi pada sesi yang tertutup."""
        if self._is_closed:
            smf.printd(f"Cannot {operation} on a closed Telnet session.", level="ERROR")
            raise RuntimeError(
                f"Cannot execute {operation}() on a closed Telnet session."
            )
