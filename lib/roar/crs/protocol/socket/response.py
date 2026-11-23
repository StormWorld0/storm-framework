import base64
import socket
from typing import Dict, Any, Optional
from .metadata import TLSMetadata


class SocketResponse:
    """
    Wrapper for managing dynamic responses.
    Provides Type-Safety, Property Access, and Lazy Decoding.
    """

    def __init__(self, raw_response: Dict[str, Any]):
        self.raw_response = raw_response
        self._status: str = raw_response.get("status", "UNKNOWN")
        self._message: str = raw_response.get("message", "UNKNOWN")

        # Retrieve the "Data" payload from the response
        self._data: Dict[str, Any] = raw_response.get("data", {})

    @property
    def ok(self) -> bool:
        """Returns True if the response is successful"""
        return self._status.upper() == "SUCCESS"

    @property
    def status(self) -> str:
        """Makes it easier to check response status"""
        return self._status

    @property
    def message(self) -> str:
        """Returns ERROR/SUCCESS/TIMEOUT message"""
        return self._message

    @property
    def raw_bytes(self) -> bytes:
        """Returns pure raw bytes"""
        raw_val = self._data.get("raw_bytes")

        if isinstance(raw_val, bytes):
            return raw_val

        if isinstance(raw_val, str) and raw_val:
            try:
                return base64.b64decode(raw_val)
            except Exception:
                return raw_val.encode("utf-8")

        return b""

    @property
    def str_bytes(self) -> str:
        """Returns raw bytes as a string"""
        return self.raw_bytes.decode("utf-8", errors="ignore")

    @property
    def hex_bytes(self) -> str:
        """Returns raw bytes in HEX format"""
        return self._data.get("hex_bytes", "")

    @property
    def int_bytes(self) -> int:
        """Returns raw bytes as a number"""
        return self._data.get("read_bytes", 0)

    @property
    def remote_ip(self) -> tuple[str, int]:
        """Return Server IP"""
        addr = self._data.get("remote_ip", "unknown")
        ip, port = addr.rsplit(":", 1)
        return (ip, int(port))

    @property
    def local_ip(self) -> tuple[str, int]:
        """Checking outgoing IP before going to global internet"""
        val = self._data.get("local_ip", "unknown")
        if isinstance(val, dict):
            addr = val.get("Addr", 0)
            port = val.get("Port", 0)
            return (addr, int(port))

        ip, port = val.rsplit(":", 1)
        return (ip, int(port))

    @property
    def addrinfo(self) -> list[tuple]:
        """Converts 'results' data from getaddrinfo to a standard tuple list."""
        if self.status != "SUCCESS":
            return []

        results = self._data.get("results", [])
        parsed = []

        for item in results:
            family = item.get("family", 0)
            socktype = item.get("socktype", 0)
            protocol = item.get("protocol", 0)
            canonname = item.get("canonname", "")
            ip = item.get("ip", "")
            port = item.get("port")

            if family == socket.AF_INET6:
                flow = item.get("flowinfo", 0)
                scope = item.get("scope_id", 0)
                sockaddr = (ip, port, flow, scope)
            else:
                sockaddr = (ip, port)

            parsed.append((family, socktype, protocol, canonname, sockaddr))
        return parsed

    @property
    def nameinfo(self) -> tuple[str, str]:
        """Returns a 'tuple' from getnameinfo"""
        if self.status != "SUCCESS":
            return ("", "")

        host = self._data.get("host", "")
        serv = self._data.get("service", "")
        return (host, serv)

    @property
    def rtt_ms(self) -> int:
        """Round Trip Time in milliseconds"""
        return self._data.get("rtt_ms", 0)

    @property
    def is_reused(self) -> bool:
        """See if the connection used is the same as before."""
        return self._data.get("is_reused", False)

    @property
    def checked_type(self) -> str:
        """Go interface reflection type (reflect.TypeOf(conn).String())"""
        return self._data.get("Cheked", "")

    @property
    def status_tls(self) -> bool:
        """Translating boolean strings from `isAlreadyTLS`"""
        val = self._data.get("isAlreadyTLS", "false")
        return val.lower() == "true"

    @property
    def tls(self) -> Optional[TLSMetadata]:
        """TLSMetadata object if info_tls is available, otherwise None."""
        tls_data = self._data.get("info_tls")
        if tls_data and isinstance(tls_data, dict):
            return TLSMetadata(tls_data)
        return None

    def _client_fd(self):
        """Returns Golang table CFD"""
        if not (fd := self._data.get("client_fd")):
            return -1
        return fd

    def __iter__(self):
        return iter(self.addrinfo)

    def __bool__(self):
        """Allows syntax: if r.ok:"""
        return self.ok

    def __repr__(self):
        return f"<SocketResponse Status={self.status} Read={self.int_bytes}b RTT={self.rtt_ms}ms>"
