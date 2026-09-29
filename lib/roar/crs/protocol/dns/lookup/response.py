# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author zxelzy

from typing import Dict, Any, List
from lib.smf.ingest import DataBuilder
from .exception import StackTrace, TimeoutTrace, NXDomain


class DNSResponse:
    """
    Data Transfer Object (DTO) untuk membungkus raw dictionary dari respons DNS Go.
    Menyediakan Type-Safety dan kemudahan akses atribut (dot notation).
    """

    def __init__(self, raw_response: Dict[str, Any]):
        self.raw_response = raw_response
        self._status: str = raw_response.get("status", "UNKNOWN")
        self._message: str = raw_response.get("message", "UNKNOWN")

        # Ekstraksi payload "Data" dari Go IPC
        self._data: Dict[str, Any] = raw_response.get("data", {})

    @property
    def status(self) -> str:
        """Pengecekan level IPC (Apakah request berhasil dikirim & diproses)."""
        return self._status

    @property
    def message(self) -> str:
        """Mengecek pesan response untuk mengetahui (ERROR/SUCCESS/TIMEOUT)"""
        return self._message

    @property
    def rcode(self) -> int:
        """DNS Response Code (contoh: 0 = NOERROR, 3 = NXDOMAIN)."""
        return self._data.get("rcode", -1)

    @property
    def rcode_str(self) -> str:
        """Representasi string dari RCODE."""
        return self._data.get("rcode_str", "UNKNOWN")

    @property
    def records(self) -> List[Any]:
        """Daftar hasil resolusi / answers dari DNS server."""
        return self._data.get("records", [])

    @property
    def truncated(self) -> bool:
        """Indikator jika payload UDP terlalu besar dan dipotong (biasanya memicu retry via TCP)."""
        return self._data.get("truncated", False)

    @property
    def authoritative(self) -> bool:
        """Indikator apakah respons berasal dari Authoritative Name Server langsung."""
        return self._data.get("authoritative", False)

    @property
    def ok(self) -> bool:
        """
        Validasi level DNS: Operasi IPC sukses DAN RCODE adalah NOERROR (0).
        Sangat berguna untuk logika validasi di layer aplikasi.
        """
        return self.status.upper() == "SUCCESS" and self.rcode == 0

    def _to_db_payload(self, domain: str, proto: str) -> Dict[str, Any]:
        """Menyimpan ke database PostgreSQL"""
        payload = (
            DataBuilder()
            .add_host(hostname=domain)
            .add_service(proto=proto, name="DNS.Lookup", state=self.rcode)
            .add_note(ntype="dns.record.dump", data=self.records)
            .build()
        )
        return payload

    def _trace(self):
        """Melempar Exception"""
        if self.status.upper() in {"ERROR", "CRITICAL"}:
            raise StackTrace(self.message)
        return None

    def _timeout(self):
        """Melempar Exception Timeout"""
        if self.status.upper() == "TIMEOUT":
            raise TimeoutTrace(self.message)
        return None

    def _nxdomain(self):
        """Melempar Exception Timeout"""
        if self.rcode == 3:
            raise NXDomain(self.message)
        return None

    def __bool__(self):
        """Memungkinkan sintaks shorthand: if response: ..."""
        return self.ok

    def __repr__(self):
        return f"<DNSResponse Status={self.status} RCode={self.rcode_str} Records={len(self.records)}>"
