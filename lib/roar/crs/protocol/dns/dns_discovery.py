# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author zxelzy
import smf
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
    def status(self) -> bool:
        """Pengecekan level IPC (Apakah request berhasil dikirim & diproses)."""
        return self._status

    @property
    def status_code() -> int:
        """Mengambil status code response"""
        return self._data.get("status_code")

    @property
    def ok(self) -> bool:
        """Shorthand validasi HTTP: Transport sukses dan Status Code 2xx / 3xx."""
        return self.status and (200 <= self.status_code < 400)

    @property
    def message(self) -> str:
        """Mengecek pesan response untuk mengetahui (ERROR/SUCCESS/TIMEOUT)"""
        return self._message

    @property
    def proto(self) -> int:
        """Ambil protokol yang di gunakan dari response"""
        return self._data.get("protocol")

    @property
    def headers(self) -> str:
        """Representasi string dari RCODE."""
        return self._headers

    def get_headers(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Case-insensitive lookup untuk HTTP Headers.
        Contoh: res.get_header('content-type') akan menemukan 'Content-Type'.
        """
        target = name.lower()
        for key, value in self._headers.items():
            if key.lower() == target:
                return value
        return default

    @property
    def tls(self) -> Optional[HTTPTLSMetadata]:
        """Objek HTTPTLSMetadata jika info_tls diaktifkan dan tersedia."""
        tls_data = self._data.get("info_tls")
        if tls_data and isinstance(tls_data, dict):
            return TLSMetadata(tls_data)
        return None

    def __bool__(self):
        """Memungkinkan sintaks shorthand: if response: ..."""
        return self.is_valid_domain

    def __repr__(self):
        return f"<DNSResponse Status={self.status} RCode={self.rcode_str} Records={len(self.records)}>"


class DNSDiscovery:
    """
    Namespace OOP untuk operasi DNS.
    Menggunakan @staticmethod karena request bersifat stateless (tidak perlu menyimpan state internal).
    """

    @staticmethod
    def _wordlist_generator(wordlist_path: str) -> Iterator[str]:
        """
        Generator internal untuk membaca file wordlist baris demi baris secara streaming.
        Memastikan pemakaian RAM tetap mendekati 0 MB.
        """
        with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                word = line.strip()
                if word and not word.startswith("#"):
                    yield word

    @staticmethod
    def subdom(
        domain: str,
        wordlist: Optional[str] = None,
        timeout: float = 2.0,
        ratelimit: int = 150,
        con: int = 0,
        tls: bool = False,
        **kwargs,
    ) -> DNSResponse:
        """
        Membangun paket DNS dan mengirimkannya ke CRS Engine.
        Mengembalikan objek DNSResponse yang sudah di-wrap.
        """
        if wordlist:
            for subdomain in DNSDiscovery._wordlist_generator(wordlist):
                for proto in ("http://", "https://"):
                    target_url = f"{proto}{subdomain}.{domain}"
                    packet = {
                        "primitive": "DNS_SEND",
                        "mode": "Discovery",
                        "url": target_url,
                        "info_tls": tls,
                        "timeout": timeout,
                        "ratelimit": ratelimit,
                        "goroutine": con,
                    }
                    raw_res = CRS.send(packet)
            return DNSResponse(raw_res)
        else:
            smf.printf(f"[!] {CC.YELLOW}Wordlist required{CC.RESET}")

        if kwargs:
            smf.printf(
                f"[!] {CC.YELLOW}Unrecognized parameters dropped =>{CC.RESET}", kwargs
            )


# Alias untuk entry point
requests = DNSDiscovery.subdom
