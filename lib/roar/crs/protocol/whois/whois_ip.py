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
        self._raw_body: Dict[str, Any] = self._data.get("body", {})
        self._headers: Dict[str, str] = self._data.get("headers") or {}

        if isinstance(self._raw_body, str):
            try:
                # Buka "amplop" kedua dari Go
                self._body = json.loads(self._raw_body)
            except json.JSONDecodeError:
                self._body = {}
        elif isinstance(self._raw_body, dict):
            self._body = self._raw_body
        else:
            self._body = {}

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

    def _parse_vcard(self, vcard: list) -> Dict[str, str]:
        """Ekstraksi jCard tanpa prefix role, kembalikan key yang bersih."""
        res = {}
        if not isinstance(vcard, list) or len(vcard) < 2:
            return res

        for item in vcard[1]:
            if not isinstance(item, list) or len(item) < 4:
                continue

            prop, params = item[0], item[1]
            params_dict = params if isinstance(params, dict) else {}
            val = item[3] if len(item) == 4 else item[3:]

            prop_map = {
                "fn": "Name",
                "email": "Email",
                "tel": "Phone",
                "org": "Organization",
                "kind": "Entity_Type",
                "title": "Title",
            }

            if prop in prop_map:
                mapped_prop = prop_map[prop]
                if isinstance(val, list):
                    val_str = ", ".join(str(v).strip() for v in val if v)
                else:
                    val_str = str(val).strip()
                    if prop == "tel" and val_str.startswith("tel:"):
                        val_str = val_str[4:]
                res[mapped_prop] = val_str

            elif prop == "adr":
                label = params_dict.get("label", "").replace("\n", ", ")
                if not label:
                    label = ", ".join(
                        filter(None, val if isinstance(val, list) else [val])
                    )
                res["Address"] = label
        return res

    def _extract_entities(self, obj: Any, extracted_roles: Dict[str, Dict]):
        """Secara rekursif mencari object 'entity' dan mengelompokkannya berdasarkan roles."""
        if isinstance(obj, dict):
            if "vcardArray" in obj and "roles" in obj:
                contact_info = self._parse_vcard(obj["vcardArray"])
                contact_info["Handle"] = obj.get("handle", "N/A")
                for role in obj["roles"]:
                    role_name = role.capitalize()
                    if role_name not in extracted_roles:
                        extracted_roles[role_name] = []
                    extracted_roles[role_name].append(contact_info)

            for v in obj.values():
                self._extract_entities(v, extracted_roles)

        elif isinstance(obj, list):
            for item in obj:
                self._extract_entities(item, extracted_roles)

    @property
    def data(self) -> str:
        """Menghasilkan report summary yang bersih dan Human-Readable."""
        output = []
        output.append("=== NETWORK INFORMATION ===")
        output.append(f"Network Name : {self._body.get('name', 'N/A')}")
        output.append(
            f"IP Range     : {self._body.get('startAddress', 'N/A')} - {self._body.get('endAddress', 'N/A')}"
        )
        output.append(f"Type         : {self._body.get('type', 'N/A')}")
        output.append(f"Status       : {', '.join(self._body.get('status', []))}")

        try:
            cidr = self._body.get("cidr0_cidrs", [{}])[0]
            output.append(f"CIDR         : {cidr.get('v4prefix')}/{cidr.get('length')}")
        except IndexError:
            pass

        output.append("\n=== ENTITY CONTACTS ===")
        extracted_roles = {}
        self._extract_entities(self._body, extracted_roles)
        for role, contacts in extracted_roles.items():
            output.append(f"\n[{role.upper()} CONTACT]")
            for idx, contact in enumerate(contacts):
                if len(contacts) > 1:
                    output.append(f"  --- Contact #{idx+1} ---")
                for k, v in contact.items():
                    output.append(f"  {k:<13}: {v}")
        return "\n".join(output)

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
