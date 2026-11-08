import base64
import socket

from typing import Dict, Any, Optional
from .metadata import TLSMetadata


class SocketResponse:
    """
    Wrapper untuk mengelola respons dinamis dari CRS (IPC).
    Menyediakan Type-Safety, Property Access, dan Lazy Decoding.
    """

    def __init__(self, raw_response: Dict[str, Any]):
        self.raw_response = raw_response
        self._status: str = raw_response.get("status", "UNKNOWN")
        self._message: str = raw_response.get("message", "UNKNOWN")

        # Retrieve the "Data" payload from the response
        self._data: Dict[str, Any] = raw_response.get("data", {})

    @property
    def ok(self) -> bool:
        """Mengembalikan True jika response berhasil"""
        return self._status.upper() == "SUCCESS"

    @property
    def status(self) -> str:
        """Mempermudah pengecekan status respons."""
        return self._status

    @property
    def message(self) -> str:
        """Mengembalikan pesan ERROR/SUCCESS/TIMEOUT."""
        return self._message

    @property
    def raw_bytes(self) -> bytes:
        """Mengembalikan raw bytes murni."""
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
        """Mengembalikan raw bytes sebagai string."""
        return self.raw_bytes.decode("utf-8", errors="ignore")

    @property
    def hex_bytes(self) -> str:
        """Mengembalikan bytes berupa HEX"""
        return self._data.get("hex_bytes", "")

    @property
    def int_bytes(self) -> int:
        """Mengembalikan bytes berupa angka"""
        return self._data.get("read_bytes", 0)

    @property
    def remote_ip(self) -> str:
        """Mengembalikan IP Server"""
        addr = self._data.get("remote_ip", "unknown")
        ip, port = addr.rsplit(":", 0)
        return (ip, port)

    @property
    def local_ip(self) -> str:
        """Mengecek IP keluar sebelum ke internet global"""
        val = self._data.get("local_ip", "unknown")
        if isinstance(val, dict):
            addr = val.get("Addr", 0)
            port = val.get("Port", 0)
            return (addr, port)

        ip, port = val.rsplit(":", 0)
        return (ip, port)

    @property
    def addrinfo(self) -> list[tuple]:
        """Mengonversi data 'results' dari getaddrinfo ke daftar tuple standar"""
        if self.status != "SUCCESS":
            return [("", "", "", "", ("", ""))]

        results = self._data.get("results", [])
        parsed = []
        for item in results:
            family = item.get("family", 0)
            socktype = item.get("socktype", 0)
            protocol = item.get("protocol", 0)
            canonname = item.get("canonname", "")
            ip = item.get("ip", "")
            port = item.get("port", 0)

            # Format sockaddr tuple
            if family == socket.AF_INET:  # AF_INET
                sockaddr = (ip, port)
            elif family == socket.AF_INET6:  # AF_INET6
                flowinfo = item.get("flowinfo", 0)
                scope_id = item.get("scope_id", 0)
                sockaddr = (ip, port, flowinfo, scope_id)
            else:
                sockaddr = (ip, port)
            parsed.append((family, socktype, protocol, canonname, sockaddr))
        return parsed

    @property
    def nameinfo(self) -> tuple[str, str]:
        """Mengembalikan 'tuple' dari getnameinfo."""
        if self.status != "SUCCESS":
            return ("", "")

        host = self._data.get("host", "")
        serv = self._data.get("service", "")
        return (host, serv)

    @property
    def rmsg(self) -> list[tuple[int, int, bytes]]:
        """Mengembalikan 'list[tuple]' Ancillary data"""
        if self.status != "SUCCESS":
            return [(0, 0, b"")]

        res = self._data.get("ancdata", [])
        parsed = []
        for item in res:
            level = item.get("msg_level", 0)
            types = item.get("msg_type", 0)
            data64 = item.get("msg_data")

            data = b""
            if isinstance(data64, str) and data64:
                try:
                    data = base64.b64decode(data64)
                except Exception:
                    data = data64.encode("utf-8")

            parsed.append((level, types, data))
        return parsed

    @property
    def rtt_ms(self) -> int:
        """Round Trip Time dalam millisecond."""
        return self._data.get("rtt_ms", 0)

    @property
    def is_reused(self) -> bool:
        """Melihat apakah koneksi yang di gunakan sama dengan sebelumnya"""
        return self._data.get("is_reused", False)

    @property
    def checked_type(self) -> str:
        """Tipe refleksi interface Go (reflect.TypeOf(conn).String())"""
        return self._data.get("Cheked", "")

    @property
    def status_tls(self) -> bool:
        """Menerjemahkan string boolean dari Go (strconv.FormatBool) ke native Python bool."""
        val = self._data.get("isAlreadyTLS", "false")
        return val.lower() == "true"

    @property
    def tls(self) -> Optional[TLSMetadata]:
        """Objek TLSMetadata jika info_tls tersedia, sebaliknya None."""
        tls_data = self._data.get("info_tls")
        if tls_data and isinstance(tls_data, dict):
            return TLSMetadata(tls_data)
        return None

    @property
    def _flags(self):
        return self._data.get("flags", 0)

    def _client_fd(self):
        """Mengembalikan CFD tabel Golang"""
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
