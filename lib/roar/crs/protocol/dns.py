# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author zxelzy
import smf
from typing import Dict, Any, List

from apps.utility.colors import CC
from ..transport import CRS

class DNSResponse:
    """
    Data Transfer Object (DTO) untuk membungkus raw dictionary dari respons DNS Go.
    Menyediakan Type-Safety dan kemudahan akses atribut (dot notation).
    """
    def __init__(self, raw_response: Dict[str, Any]):
        self.raw_response = raw_response
        self._status: str = raw_response.get("status", "UNKNOWN")
        
        # Ekstraksi payload "Data" dari Go IPC
        self._data: Dict[str, Any] = raw_response.get("data", {})

    @property
    def status(self) -> bool:
        """Pengecekan level IPC (Apakah request berhasil dikirim & diproses)."""
        return self._status

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
    def valid_domain(self) -> bool:
        """
        Validasi level DNS: Operasi IPC sukses DAN RCODE adalah NOERROR (0).
        Sangat berguna untuk logika validasi di layer aplikasi.
        """
        return self.status and self.rcode == 0

    def __bool__(self):
        """Memungkinkan sintaks shorthand: if response: ..."""
        return self.is_valid_domain

    def __repr__(self):
        return f"<DNSResponse Status={self.status} RCode={self.rcode_str} Records={len(self.records)}>"


class DNSResolver:
    """
    Namespace OOP untuk operasi DNS. 
    Menggunakan @staticmethod karena request bersifat stateless (tidak perlu menyimpan state internal).
    """
    
    @staticmethod
    def query(
        domain: str,
        type: str = "A",
        protocol: str = "tcp",
        timeout: float = 2.0,
        ratelimit: int = 0,
        **kwargs,
    ) -> DNSResponse:
        """
        Membangun paket DNS dan mengirimkannya ke CRS Engine.
        Mengembalikan objek DNSResponse yang sudah di-wrap.
        """
        packet = {
            "primitive": "DNS_SEND",
            "domain": domain,
            "type": type,
            "protocol": protocol,
            "timeout": timeout,
            "ratelimit": ratelimit,
        }

        if kwargs:
            smf.printf(f"[!] {CC.YELLOW}Unrecognized parameters dropped =>{CC.RESET}", kwargs)

        # Kirim via IPC dan langsung bungkus hasilnya
        raw_res = CRS.send(packet)
        return DNSResponse(raw_res)

# Alias untuk entry point
requests = DNSResolver.query
