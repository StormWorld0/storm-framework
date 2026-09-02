# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author zxelzy
import smf
import re

from typing import Dict, Any, Optional, Iterator

from apps.utility.colors import CC
from ...transport import CRS


class TLSMetadata:
    """
    Data Transfer Object (DTO) untuk metadata TLS dari HTTP Response Go Engine.
    """

    def __init__(self, data: Dict[str, Any]):
        self.subject: Optional[str] = data.get("subject")
        self.issuer: Optional[str] = data.get("issuer")
        # Menangani variasi penamaan key antar primitive IPC (dns_names / dns_name)
        self.dns_name: list = data.get("dns_names") or data.get("dns_name", [])
        self.expires: Optional[str] = data.get("expires_at") or data.get("expires")

        self.version: str = data.get("tls_version", "Unknown")
        self.cipher: str = data.get("cipher_suite", "Unknown")
        self.protocol: str = data.get("protocol", "")
        self.hostname: str = data.get("hostname", "")
        self.handshake: bool = data.get("handshake", False)
        self.session_resume: bool = data.get("session_resume", False)
        self.cert_chain: list = data.get("cert_chain", [])

    def __repr__(self):
        return f"<TLSMetadata Version={self.tls_version} Cipher={self.cipher_suite} Host={self.hostname}>"


class DNSResponse:
    """
    Data Transfer Object (DTO) untuk membungkus raw dictionary dari respons DNS Go.
    Menyediakan Type-Safety dan kemudahan akses atribut (dot notation).
    """

    def __init__(self, raw_response: Dict[str, Any]):
        self.raw_response = raw_response
        self._status: str = raw_response.get("status", "UNKNOWN")
        self._message: str = raw_response.get("message", "UNKNOWN")

        # Ekstraksi payload "Data" dari IPC
        self._data: Dict[str, Any] = raw_response.get("data", {})
        self._headers: Dict[str, str] = self._data.get("headers") or {}

    @property
    def status(self) -> str:
        """Pengecekan level IPC (Apakah request berhasil dikirim & diproses)."""
        return self._status

    @property
    def status_code(self) -> int:
        """Mengambil status code response"""
        return self._data.get("status_code", -1)

    @property
    def ok(self) -> bool:
        """Shorthand validasi HTTP"""
        return self.status.upper() == "SUCCESS"

    @property
    def message(self) -> str:
        """Mengecek pesan response untuk mengetahui (ERROR/SUCCESS/TIMEOUT)"""
        return self._message

    @property
    def proto(self) -> int:
        """Protocol HTTP versi Go (contoh: HTTP/1.1, HTTP/2.0)."""
        return self._data.get("protocol", "")

    @property
    def url(self) -> str:
        """Mengembalikan URL yang di targetkan"""
        return self._data.get("url", "")

    @property
    def url_active(self) -> int:
        """Mengembalikan jumlah URL Active"""
        return self._data.get("active-url", 0)

    @property
    def headers(self) -> str:
        """Mengambil headers saat koneksi"""
        return self._headers

    def get_headers(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Case-insensitive lookup untuk HTTP Headers.
        Contoh: res.get_headers('content-type') akan menemukan 'Content-Type'.
        """
        target = name.lower()
        for key, val in self._headers.items():
            if key.lower() == target:
                if val is None:
                    return default
                res = (
                    ", ".join(str(i) for i in val)
                    if isinstance(val, (list, tuple))
                    else str(val)
                )
                return re.sub(r"[\r\n]+", " ", res).strip() or default
        return default

    @property
    def tls(self) -> Optional[TLSMetadata]:
        """Objek TLSMetadata jika info_tls diaktifkan dan tersedia."""
        tls_data = self._data.get("info_tls")
        if tls_data and isinstance(tls_data, dict):
            return TLSMetadata(tls_data)
        return None

    @property
    def engine(self) -> str:
        """Melihat mesin mana yang menjalankan"""
        return self._data("engine", "")

    def __bool__(self):
        """Memungkinkan sintaks shorthand: if resp: ..."""
        return self.ok

    def __repr__(self):
        return f"<DNSResponse Status={self.status} Code={self.status_code} Engine={self.engine}>"


class DNSDiscovery:
    """
    Namespace OOP untuk operasi DNS.
    Menggunakan @staticmethod karena request bersifat stateless (tidak perlu menyimpan state internal).
    """

    @staticmethod
    def subdom(
        domain: str,
        wordlist: str = None,
        timeout: float = 2.0,
        rl: int = 150,
        frl: int = 10,
        con: int = 1,
        tls: bool = False,
        ua: str = "",
        **kwargs,
    ) -> Iterator[DNSResponse]:
        """
        Membangun paket DNS dan mengirimkannya ke CRS Engine.
        Mengembalikan objek DNSResponse yang sudah di-wrap.
        """
        if kwargs:
            smf.printf(
                f"[!] {CC.YELLOW}Unrecognized parameters dropped =>{CC.RESET}", kwargs
            )

        packet = {
            "primitive": "DNS_SEND",
            "mode": "DNSDiscovery",
            "domain": domain,
            "wordlist": wordlist,
            "info_tls": tls,
            "timeout": timeout,
            "rl": rl,
            "frate": frl,
            "concurrency": con,
            "user-agent": ua,
        }
        raw_res = CRS.send(packet)
        return DNSResponse(raw_res)


# Alias untuk entry point
discovery = DNSDiscovery.subdom
