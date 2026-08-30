# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author zxelzy
import json
import smf
from typing import Dict, Any, Optional, Union

from apps.utility.colors import CC
from ...transport import CRS


class HTTPTLSMetadata:
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
        return f"<HTTPTLSMetadata Version={self.tls_version} Cipher={self.cipher_suite} Host={self.hostname}>"


class HTTPResponse:
    """
    Wrapper DTO untuk mengelola respons HTTP dari Go Engine.
    Menyediakan Type-Safety, Case-Insensitive Headers, dan JSON Parser.
    """

    def __init__(self, raw_response: Dict[str, Any]):
        self.raw_response = raw_response
        self._status: str = raw_response.get("status", "UNKNOWN")
        self._message: str = raw_response.get("message", "UNKNOWN")
        # Payload "Data" dari Go IPC
        self._data: Dict[str, Any] = raw_response.get("data", {})
        self._headers: Dict[str, str] = self._data.get("headers") or {}

    @property
    def status(self) -> str:
        """
        Pengecekan level Transport IPC
        (Apakah Go berhasil mengirim/menerima HTTP paket).
        """
        return self._status

    @property
    def status_code(self) -> int:
        """HTTP Status Code (contoh: 200, 404, 500)."""
        return int(self._data.get("status_code", 0))

    @property
    def ok(self) -> bool:
        """Shorthand validasi HTTP: Transport sukses dan Status Code 2xx / 3xx."""
        return self.status.upper() == "SUCCESS" and (200 <= self.status_code < 400)

    @property
    def message(self) -> str:
        """Mengembalikan pesan ERROR/TIMEOUT/SUCCESS."""
        return self._message

    @property
    def text(self) -> str:
        """Mengembalikan body response dalam bentuk UTF-8 string."""
        return self._data.get("body", "")

    @property
    def content(self) -> bytes:
        """Mengembalikan body response dalam bentuk raw bytes."""
        return self.text.encode("utf-8")

    @property
    def headers(self) -> Dict[str, str]:
        """Dictionary headers asli dari respons."""
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
    def proto(self) -> str:
        """Protocol HTTP versi Go (contoh: HTTP/1.1, HTTP/2.0)."""
        return self._data.get("protocol", "")

    @property
    def engine(self) -> str:
        """Engine penyedia koneksi dari Go Backend (contoh: retryablehttp)."""
        return self._data.get("engine", "")

    @property
    def tls(self) -> Optional[HTTPTLSMetadata]:
        """Objek HTTPTLSMetadata jika info_tls diaktifkan dan tersedia."""
        tls_data = self._data.get("info_tls")
        if tls_data and isinstance(tls_data, dict):
            return HTTPTLSMetadata(tls_data)
        return None

    def json(self) -> Union[Dict[str, Any], list, None]:
        """
        [Lazy Evaluation] Mem-parsing string body menjadi JSON dict/list.
        Mengembalikan None jika body bukan format JSON valid.
        """
        if not self.text:
            return None
        try:
            return json.loads(self.text)
        except json.JSONDecodeError:
            smf.printd("Failed to parse response body as JSON", level="WARN")
            return None

    def __bool__(self):
        """Shorthand: if response: ... (True jika request HTTP bernilai OK/Sukses)."""
        return self.ok

    def __repr__(self):
        return f"<HTTPResponse [{self.status_code}] Engine={self.engine} Size={len(self.text)}b>"


class HTTPClient:
    """
    Namespace Stateless untuk mengeksekusi HTTP Request via CRS Engine.
    """

    @staticmethod
    def send(
        method: str,
        url: str,
        headers: dict = None,
        body: str = "",
        redirect: bool = True,
        rawhttp: bool = False,
        infotls: bool = False,
        verify: bool = True,
        retry: int = 2,
        ratelimit: int = 150,
        timeout: float = 5.0,
        con: int = 50,
        **kwargs,
    ) -> HTTPResponse:
        """
        Membangun payload HTTP_SEND dan mengirimkannya ke CRS Engine.
        """
        packet = {
            "primitive": "HTTP_SEND",
            "goroutine": con,
            "method": method.upper(),
            "url": url,
            "headers": headers or {},
            "body": body,
            "redirect": redirect,
            "rawmode": rawhttp,
            "info_tls": infotls,
            "verify": verify,
            "retry": retry,
            "ratelimit": ratelimit,
            "timeout": timeout,
        }

        if kwargs:
            smf.printf(
                f"[!] {CC.YELLOW}Unrecognized parameters dropped =>{CC.RESET}", kwargs
            )

        raw_res = CRS.send(packet)

        return HTTPResponse(raw_res)


# Alias untuk Backward Compatibility
http_requests = HTTPClient.send
