# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author zxelzy
import re
import smf
import json

from typing import Dict, Any, Optional, Union

from apps.utility.colors import CC
from ...transport import CRS


class WHOISResponse:
    """
    Data Transfer Object (DTO) untuk membungkus raw dictionary dari respons DNS Go.
    Menyediakan Type-Safety dan kemudahan akses atribut (dot notation).
    """

    def __init__(self, raw_response: Dict[str, Any]):
        self.raw_response = raw_response
        self._status: str = raw_response.get("status", "UNKNOWN")
        self._message: str = raw_response.get("message", "UNKNOWN")

        # Ekstraksi payload "Data" dari CRS Engine
        self._data: Dict[str, Any] = raw_response.get("data", {})
        self._body: Dict[str, Any] = self._data.get("body", {})
        self._headers: Dict[str, str] = self._data.get("headers") or {}

    @property
    def status(self) -> str:
        """Pengecekan level IPC (Apakah request berhasil dikirim & diproses)."""
        return self._status

    @property
    def status_code(self) -> int:
        """HTTP Status Code (contoh: 200, 404, 500)."""
        return self._data.get("status_code", 0)

    @property
    def message(self) -> str:
        """Mengecek pesan response untuk mengetahui (ERROR/SUCCESS/TIMEOUT)"""
        return self._message

    @property
    def proto(self) -> str:
        """Protocol HTTP versi Go (contoh: HTTP/1.1, HTTP/2.0)."""
        return self._data.get("protocol", "")

    @property
    def engine(self) -> str:
        """Engine penyedia koneksi dari Go Backend (contoh: retryablehttp)."""
        return self._data.get("engine", "")

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

    def _parse_vcard(self, vcard: list) -> Dict[str, str]:
        """Ekstraksi jCard RFC 7095 dengan penanganan duplikasi dan tipe data aman."""
        res = {}
        if not isinstance(vcard, list) or len(vcard) < 2:
            return res

        for item in vcard[1]:
            if not isinstance(item, list) or len(item) < 4:
                continue

            prop, params, type_, val = item[0], item[1], item[2], item[3]
            params_dict = params if isinstance(params, dict) else {}

            if prop in ("fn", "email", "tel"):
                mapped_prop = {"fn": "name", "email": "email", "tel": "phone"}[prop]
                if mapped_prop in res:
                    res[mapped_prop] = f"{res[mapped_prop]}, {val}"
                else:
                    res[mapped_prop] = val

            elif prop == "adr":
                label = params_dict.get("label", "").replace("\n", ", ")
                if not label:
                    label = ", ".join(
                        filter(None, val if isinstance(val, list) else [val])
                    )
                res["address"] = label
        return res

    def _extract_rdap(self, obj: Any, prefix: str = "") -> Dict[str, Any]:
        """Parser RDAP rekursif yang tahan terhadap collision."""
        res = {}
        if isinstance(obj, dict):
            if "vcardArray" in obj:
                vcard_data = self._parse_vcard(obj["vcardArray"])
                roles = obj.get("roles", [])
                role_prefix = "_".join(roles) if roles else "entity"
                for k, v in vcard_data.items():
                    if v:
                        full_key = (
                            f"{prefix}.{role_prefix}_{k}"
                            if prefix
                            else f"{role_prefix}_{k}"
                        )
                        res[full_key] = v

            for k, v in obj.items():
                if k == "vcardArray":
                    continue

                p = f"{prefix}.{k}" if prefix else k
                res.update(self._extract_rdap(v, p))

        elif isinstance(obj, list):
            if not obj:
                return res

            if all(isinstance(x, (str, int, bool)) for x in obj):
                clean_str = ", ".join(str(x).strip() for x in obj if str(x).strip())
                if clean_str:
                    res[prefix] = clean_str
            else:
                for i, x in enumerate(obj):
                    p = f"{prefix}[{i}]" if prefix else str(i)
                    res.update(self._extract_rdap(x, p))

        elif obj is not None and obj != "":
            res[prefix] = obj
        return res

    @property
    def data(self) -> str:
        """Mengembalikan data RDAP berupa Clean String"""
        return "\n".join(f"{k} = {v}" for k, v in self._extract_rdap(self._body).items())

    @property
    def raw_data(self) -> str:
        """Mengembalikan body response dalam bentuk UTF-8 string."""
        return self._body

    def data_json(self) -> Union[Dict[str, Any], list, None]:
        """
        [Lazy Evaluation] Mem-parsing string body menjadi JSON dict/list.
        Mengembalikan None jika body bukan format JSON valid.
        """
        if not self.text:
            return None
        try:
            return json.loads(self.raw_data)
        except json.JSONDecodeError:
            smf.printd("Failed to parse response body as JSON", level="WARN")
            return None

    @property
    def ok(self) -> bool:
        """
        Memvalidasi status response untuk menciptakan return boolean
        untuk membuat syntax bool seperti contoh: (if r.ok:)
        """
        return self.status.upper() == "SUCCESS"

    def __bool__(self):
        """Memungkinkan sintaks shorthand: if resp.ok: ..."""
        return self.ok

    def __repr__(self):
        return (
            f"<WHOISResponse Status={self.status} Data={self.data} Engine={self.engine}>"
        )


class WhoisIP:
    """Namespace Stateless untuk mengeksekusi WHOIS IP via CRS Engine."""

    @staticmethod
    def whois(
        ip: str,
        timeout: float = 3.0,
        rl: int = 150,
        frl: int = 10,
        con: int = 0,
        *kwargs,
    ) -> WHOISResponse:
        """Menyiapkan packet WHOIS_SEND"""

        packet = {
            "primitive": "WHOIS_SEND",
            "mode": "IPWhois",
            "ip": ip,
            "timeout": timeout,
            "ratelimit": rl,
            "frate": frl,
            "goroutine": con,
        }

        if kwargs:
            smf.printf(
                f"[!] {CC.YELLOW}Unrecognized parameters dropped =>{CC.RESET}", kwargs
            )

        raw_resp = CRS.send(packet)
        return WHOISResponse(raw_resp)


ipwhois = WhoisIP.whois
