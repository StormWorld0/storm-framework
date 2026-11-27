import smf
import uuid
import base64
from apps.utility.colors import CC
from lib.smf.exception import (
    CRSRuntimeError,
    CRSException,
    SocketConnectionRefused,
    SocketError,
    SocketTimeout,
    SocketValueError,
)


class SocketState:
    """
    Configuration Management & Session State.
    Stores connection properties and validates socket lifecycle.
    """

    SocketError
    Timeout = SocketTimeout
    ValueError = SocketValueError
    ConnectionRefused = SocketConnectionRefused
    RuntimeError = CRSRuntimeError
    Exception = CRSException
    SocketException = (
        CRSException,
        CRSRuntimeError,
        SocketConnectionRefused,
        SocketValueError,
        SocketTimeout,
        SocketError,
    )

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        serv: str | int | None = None,
        timeout: float | None = None,
        af: int | None = None,
        type: int | None = None,
        proto: int | None = None,
        level: int | None = None,
        name: int | None = None,
        flags: int | None = None,
        how: int | None = None,
        value: int = 0,
        backlog: int = 0,
        file: str = "",
        buffer: int = 0,
        keepalive: bool = True,
        mode: str = "socket",
        verify: bool = True,
        infotls: bool = False,
        close_session: bool = False,
        cert: str = "",
        key: str = "",
        ca: str = "",
        flowinfo: int = 0,
        scopeid: int = 0,
        **kwargs,
    ):
        self.host = host
        self.port = port
        self.serv = serv
        self._timeout = timeout

        self.buffer = buffer
        self.ratelimit = 0
        self.keepalive = keepalive
        self.mode = mode
        self.infotls = infotls

        # AF_* and SOCK_* and IPPROTO_*
        self.family = af
        self.type = type
        self.proto = proto

        # SOL_* and SO_* and value and MSG_*
        self.level = level
        self.name = name
        self.value = value
        self.flags = flags
        self.how = how

        # IPv6 by getnameinfo
        self.flowinfo = flowinfo
        self.scopeid = scopeid

        # Used by listen
        self.backlog = backlog
        self.file = file
        self.cfd = -1  # Set default

        # CRS session isolation
        self.sessid = f"smf_sess_{uuid.uuid4().hex[:12]}"
        self._is_closed = False
        self.close_session = close_session

        # TLS Security Status
        self.is_tls = False
        self.verify = verify
        self.cert = cert
        self.key = key
        self.ca = ca

        # Set Goroutine 1 (True)
        self.con = 1

        # Cache File Descriptor. Set default -1
        self._sock_fd = -1
        self._client_fd = -1  # Default fallback only

        if kwargs:
            smf.printf(
                f"[!] {CC.YELLOW}Unrecognized parameters dropped =>{CC.RESET}", kwargs
            )

    def _ensure_open(self, operation: str):
        """Prevents execution of operations on closed sessions."""
        if self._is_closed:
            smf.printd(f"Cannot {operation} on a closed Socket session.", level="ERROR")
            raise RuntimeError(
                f"Cannot execute {operation}() on a closed Socket session."
            )


class IPCPayloadBuilder:
    """Data Marshalling & Payload Transformation."""

    @staticmethod
    def build(
        state: SocketState,
        host: str | None = None,
        port: int | None = None,
        serv: str | int | None = None,
        data: str | bytes = b"",
        addr_fam: str | int | None = None,
        stype: str | int | None = None,
        sproto: str | int | None = None,
        level: str | int | None = None,
        name: str | int | None = None,
        value: int | None = None,
        flag: str | int | None = None,
        how: str | int | None = None,
        backlog: int | None = None,
        file: str | None = None,
        infotls: bool | None = None,
        verify: bool | None = None,
        cert: str | None = None,
        key: str | None = None,
        ca: str | None = None,
        flowinfo: int | None = None,
        scopeid: int | None = None,
        buffer: int | None = None,
        timeout: float | None = None,
        ratelimit: int | None = None,
        cfd: int | None = None,
        mode: str | None = None,
        fileno: str | None = None,
        close_session: bool | None = None,
    ) -> dict:

        # Encoding data payload
        data_str = ""
        if data:
            data_bytes = data.encode("utf-8") if isinstance(data, str) else data
            data_str = base64.b64encode(data_bytes).decode("utf-8")

        return {
            "primitive": "SOCKET",
            "mode": mode if mode is not None else state.mode,
            "host": host if host is not None else state.host,
            "port": port if port is not None else state.port,
            "service": serv if serv is not None else state.serv,
            "data": data_str,
            "addr-fam": addr_fam if addr_fam is not None else state.family,
            "stype": stype if stype is not None else state.type,
            "sproto": sproto if sproto is not None else state.proto,
            "opt-level": level,
            "opt-name": name,
            "opt-value": value if value is not None else state.value,
            "flags": flag if flag is not None else state.flags,
            "how": how if how is not None else state.how,
            "backlog": backlog if backlog is not None else state.backlog,
            "file": file if file is not None else state.file,
            "timeout": timeout if timeout is not None else state._timeout,
            "buffer": buffer if buffer is not None else state.buffer,
            "ratelimit": ratelimit if ratelimit is not None else state.ratelimit,
            "client-fd": cfd if cfd is not None else state.cfd,
            "session_id": state.sessid,
            "keep-alive": state.keepalive,
            "close-session": (
                close_session if close_session is not None else state.close_session
            ),
            "verify": verify if verify is not None else state.verify,
            "info_tls": infotls if infotls is not None else state.infotls,
            "tls-cert": cert,
            "tls-key": key,
            "tls-ca": ca,
            "flowinfo": flowinfo if flowinfo is not None else state.flowinfo,
            "scope_id": scopeid if scopeid is not None else state.scopeid,
            "uds-path": fileno,
            "goroutine": state.con,
        }
