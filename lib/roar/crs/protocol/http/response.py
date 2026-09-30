# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author zxelzy

import json
import smf
import re

from typing import Dict, Any, Optional, Union

from apps.utility.parse import parse_url, domain_to_ip
from lib.smf.ingest import DataBuilder

from .exception import StackTrace
from .metadata import HTTPTLSMetadata


class HTTPResponse:
    """Wrapper DTO untuk mengelola respons HTTP"""

    def __init__(self, raw_response: Dict[str, Any]):
        self.raw_response = raw_response
        self._status: str = raw_response.get("status", "UNKNOWN")
        self._message: str = raw_response.get("message", "UNKNOWN")
        # Payload "Data" dari Go IPC
        self._data: Dict[str, Any] = raw_response.get("data", {})
        self._headers: Dict[str, str] = self._data.get("headers") or {}

    @property
    def status(self) -> str:
        """Pengecekan level IPC (Apakah request berhasil dikirim & diproses)."""
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
    def body(self) -> str:
        """Mengembalikan body response dalam bentuk string."""
        return self._data.get("body", "")

    @property
    def raw_bytes(self) -> bytes:
        """Mengembalikan body response dalam bentuk raw bytes."""
        return self.body.encode("utf-8")

    @property
    def headers(self) -> Dict[str, str]:
        """Dictionary headers asli dari respons."""
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
        if not self.body:
            return None
        try:
            return json.loads(self.body)
        except json.JSONDecodeError:
            smf.printd("Failed to parse response body as JSON", level="WARN")
            return None

    def _to_db_payload(
        self,
        method: str,
        host: str,
        tls: bool = False,
    ) -> Dict[str, Any]:
        """Mengubah response HTTP menjadi structured dictionary untuk db_api."""

        res = parse_url(host)
        ips = domain_to_ip(res["domain"])

        ipv4 = ips["ipv4"]
        ipv6 = ips["ipv6"]

        primary_ip = ipv4[0] if ipv4 else ipv6[0] if ipv6 else None

        server_header = self.get_headers("server")
        content_type = self.get_headers("content-type", "unknown")

        MAX_BODY_LEN = 4096
        raw_body = self.body
        is_truncated = False

        if len(raw_body) > MAX_BODY_LEN:
            raw_body = raw_body[:MAX_BODY_LEN]
            is_truncated = True

        extracted_port = res.get("port")
        if not extracted_port:
            extracted_port = 443 if res["scheme"] == "https" else 80

        info = (
            f"Status: {self.status_code} | Server: {server_header} | Proto: {self.proto}"[
                :255
            ]
        )

        note_data = {
            "headers": self.headers,
            "body_preview": raw_body,
            "method": method,
            "content_type": content_type,
            "original_length": len(self.body),
            "is_truncated": is_truncated,
        }

        tls_dict = None
        if tls and self.tls:
            tls_dict = {
                "subject": self.tls.subject,
                "issuer": self.tls.issuer,
                "alt_name": self.tls.dns_name,
                "not_after": self.tls.expires,
                "protocol": (
                    [self.tls.version]
                    if getattr(self.tls, "version", "Unknown") != "Unknown"
                    else []
                ),
                "cipher": (
                    {"ciphers": [self.tls.cipher]}
                    if getattr(self.tls, "cipher", "Unknown") != "Unknown"
                    else {}
                ),
                "certificate": json.dumps(
                    {
                        "cert_chain": getattr(self.tls, "cert_chain", None),
                        "hostname": getattr(self.tls, "hostname", None),
                        "protocol": getattr(self.tls, "protocol", None),
                        "handshake": getattr(self.tls, "handshake", None),
                        "session_resume": getattr(self.tls, "session_resume", None),
                    }
                ),
            }

        payload = (
            DataBuilder()
            .add_host(
                address=primary_ip,
                hostname=[res["domain"]] if res.get("domain") else [],
            )
            .add_service(
                port=int(extracted_port),
                proto="tcp",
                name="https" if res["scheme"] == "https" else "http",
                state="open" if self.ok else "closed",
                info=info,
                tls_info=tls_dict,
            )
            .add_note(ntype="http.headers", data=note_data)
            .build()
        )
        return payload

    def _trace(self) -> None:
        """Melempar stack trace"""
        if (sts := self.status.upper()) in {"ERROR", "CRITICAL"}:
            msg = self.message
            raise StackTrace(sts, msg)
        return None

    def __bool__(self):
        """Shorthand: if r.ok: ... (True jika request HTTP bernilai OK/Sukses)."""
        return self.ok

    def __repr__(self):
        return f"<HTTPTLSMetadata Version={self.version} Cipher={self.cipher} Host={self.hostname}>"
