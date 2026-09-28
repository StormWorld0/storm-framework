import smf
import base64

from typing import Dict, Any, Optional
from .utils_fd import real_fd


class StackTrace:
    """Melempar stack trace dari response stderr CRS"""

    def __init__(self, status: str, message: str):
        raise Exception(status, message)


class TLSMetadata:
    """
    Data Transfer Object (DTO) untuk metadata TLS dari Go Engine.
    """

    def __init__(self, data: Dict[str, Any]):
        self.version: str = data.get("tls_version", "Unknown")
        self.cipher_suite: str = data.get("cipher_suite", "Unknown")
        self.protocol: str = data.get("protocol", "")
        self.hostname: str = data.get("hostname", "")
        self.handshake: bool = data.get("handshake", False)
        self.session_resume: bool = data.get("session_resume", False)

        # Sertifikat Data (Bisa None jika tidak ada)
        self.subject: Optional[str] = data.get("subject")
        self.issuer: Optional[str] = data.get("issuer")
        self.dns_name: list = data.get("dns_name", [])
        self.expires: Optional[str] = data.get("expires")
        self.cert_chain: int = data.get("cert_chain", 0)

    def __repr__(self):
        return f"<TLSMetadata {self.version} Cipher={self.cipher_suite} Host={self.hostname}>"


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

    def _trace(self) -> None:
        """Melempar stack trace"""
        if (sts := self.status.upper()) == "CRITICAL":
            msg = self.message
            return StackTrace(sts, msg)
        return None

    @property
    def fileno(self) -> int:
        """Mengembalikan respons FD (File-Descriptor) dari Open Socket."""
        if not (uds := self._data.get("uds_path")):
            return -1

        fd = real_fd(uds)
        return fd

    @property
    def raw_bytes(self) -> bytes:
        """Mengembalikan raw bytes murni."""
        raw_val = self._data.get("raw_bytes")

        if isinstance(raw_val, bytes):
            return raw_val

        if isinstance(raw_val, str) and raw_val:
            try:
                return base64.b64decode(raw_val)
            except Exception as e:
                smf.printd(f"Base64 decode error", e, level="ERROR")
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
        """Mengecek IP Server"""
        return self._data.get("remote_ip", "unknown")

    @property
    def local_ip(self) -> str:
        """Mengecek IP keluar sebelum ke internet global"""
        value = self._data.get("local_ip", "unknown")
        if isinstance(value, dict):
            addr = value.get("Addr")
            port = value.get("Port")
            if addr is not None and port is not None:
                return f"{'.'.join(map(str, addr))}:{port}"
        return value

    @property
    def rtt_ms(self) -> int:
        """Round Trip Time dalam millisecond."""
        return self._data.get("rtt_ms", 0)

    @property
    def isreused(self) -> bool:
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

    def __bool__(self):
        """Allows syntax: if r.ok:"""
        return self.ok

    def __repr__(self):
        return f"<SocketResponse Status={self.status} Read={self.int_bytes}b RTT={self.rtt_ms}ms>"
