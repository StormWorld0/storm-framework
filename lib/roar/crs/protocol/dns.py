# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author zxelzy
import smf

from apps.utility.colors import *
from ..transport import CRS
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass(frozen=True)
class DNSRecord:
    """Model untuk individual DNS answer record."""
    name: str
    record_type: str
    value: str
    ttl: int
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DNSRecord":
        """Factory method maps a single record dict"""
        return cls(
            name=data.get("name", data.get("Header", {}).get("Name", "")),
            record_type=data.get("type", data.get("Header", {}).get("Rrtype", "")),
            value=data.get("data", data.get("value", data.get("txt", ""))),
            ttl=data.get("ttl", data.get("Header", {}).get("Ttl", 0)),
            raw=data
        )

@dataclass
class DNSResult:
    """The main DTO model for wrapping ResponsePacket"""
    status: str
    rcode: int
    rcode_str: str
    truncated: bool
    authoritative: bool
    answers: List[DNSRecord]
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def parse(cls, resp: Dict[str, Any]) -> "DNSResult":
        """Special parser to absorb ResponsePacket CRS."""
        if not isinstance(resp, dict):
            return cls(
                status="ERROR",
                rcode=-1,
                rcode_str="INVALID_RESPONSE",
                truncated=False,
                authoritative=False,
                answers=[],
                raw={}
            )

        # Ambil inner dictionary "data" dari ResponsePacket
        data = resp.get("data", {})
        raw_answers = data.get("answers", []) or []

        parsed_answers = [
            DNSRecord.from_dict(item) if isinstance(item, dict) else item 
            for item in raw_answers
        ]

        return cls(
            status=resp.get("status", "UNKNOWN"),
            rcode=data.get("rcode", -1),
            rcode_str=data.get("rcode_str", "UNKNOWN"),
            truncated=data.get("truncated", False),
            authoritative=data.get("authoritative", False),
            records=parsed_answers,
            raw=resp
        )

    # --- Helper Properties (Bonus DX) ---
    @property
    def is_success(self) -> bool:
        """Cek langsung apakah query sukses tanpa NXDOMAIN/SERVFAIL"""
        return self.status == "SUCCESS" and self.rcode_str == "NOERROR"

    @property
    def first_answer(self) -> Optional[DNSRecord]:
        """Quick access to the first record without having to check len(res.answers)"""
        return self.answers[0] if self.answers else None

# ----------------------------------------
# Functions to send DNS Records to domains
# ----------------------------------------
def dns_request(
    domain: str,
    type: str = "A",
    protocol: str = "tcp",
    timeout: float = 2.0,
    ratelimit: int = 0,
    **kwargs,
) -> DNSResult:
    """Wrapper DNS"""

    packet = {
        "primitive": "DNS_SEND",
        "domain": domain,
        "type": type,
        "protocol": protocol,
        "timeout": timeout,
        "ratelimit": ratelimit,
    }

    if kwargs:
        smf.printf(f"[!] {CC.YELLOW}Data is not recognized =>{CC.RESET}", kwargs)

    resp = CRS.send(packet)
    
    return DNSResult.parse(resp)
