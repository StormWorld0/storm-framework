import smf

from ..socket import Socket
from apps.utility.colors import CC


class TelnetState:
    """Mengelola State Telnet"""

    def __init__(
        self,
        host: str,
        port: int = 23,
        timeout: float = 3.0,
        **kwargs,
    ):
        """Open koneksi Telnet di atas TCP Socket"""

        # Open Inheritance
        self.sock = Socket()
        # Set Timeout Default Socket
        self.sock.timeout(timeout)
        # Create an Instant TCP connection
        self.resp_con = self.sock.create_connection(host, port)
        # Set Timeout Telnet Default
        self._timeout = timeout
        # Buffer storage
        self._buffer = b""
        # Telnet handshake variables
        self._iac_fragment = b""
        # Sessions State
        self._is_closed = False

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
