# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author zxelzy

from .state_build import SocketState
from .constants import ConstantsMix

from .socket_core import SocketCore
from .socket_io import SocketIO
from .socket_options import SocketOptions
from .socket_tls import SocketTLS
from .socket_resolver import SocketResolver


class Socket(
    SocketState,
    SocketCore,
    SocketIO,
    SocketOptions,
    SocketTLS,
    SocketResolver,
    ConstantsMix,
):
    """
    Facade Antarmuka Socket.
    Mewarisi SocketState untuk mempertahankan kompatibilitas atribut (Backward Compatibility).
    Hanya berfokus sebagai Register Domain Socket.
    """

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __repr__(self):
        tls_state = "TLS" if self.is_tls else "TCP/UDP"
        return f"<Socket host='{self.host}:{self.port}' proto='{tls_state}' sessid='{self.sessid}' closed={self._is_closed}>"
