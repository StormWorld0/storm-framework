# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author zxelzy

import re
import smf
import json

from typing import Dict, Any, Optional, Union, List

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

        # State untuk RDAP Contacts
        self._categorized_contacts: Dict[str, List[Dict[str, str]]] = {}
        self._is_contact_parsed: bool = False

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

    # ==========================================
    # LAZY PARSER RDAP CONTACTS
    # ==========================================
    def _trigger_contact_parsing(self):
        """Memicu ekstraksi vCard hanya jika di-request oleh user (O(1) setelah dipanggil)."""
        if not self._is_contact_parsed:
            if self._body:
                self._extract_entities(self._body)
            self._is_contact_parsed = True

    @property
    def technical(self) -> List[Dict[str, str]]:
        self._trigger_contact_parsing()
        return self._categorized_contacts.get("Technical", [])

    @property
    def admin(self) -> List[Dict[str, str]]:
        self._trigger_contact_parsing()
        return self._categorized_contacts.get("Administrative", [])

    @property
    def abuse(self) -> List[Dict[str, str]]:
        self._trigger_contact_parsing()
        return self._categorized_contacts.get("Abuse", [])

    @property
    def registrant(self) -> List[Dict[str, str]]:
        self._trigger_contact_parsing()
        return self._categorized_contacts.get("Registrant", [])

        def _extract_entities(self, obj: Any):
        if not isinstance(obj, dict):
            return

        # 1. Ekstrak vCard jika node saat ini adalah entitas kontak
        if "vcardArray" in obj and "roles" in obj:
            contact_info = self._parse_vcard(obj["vcardArray"])
            contact_info["Handle"] = obj.get("handle", "N/A")

            for role in obj.get("roles", []):
                role_name = role.capitalize()
                if role_name not in self._categorized_contacts:
                    self._categorized_contacts[role_name] = []
                self._categorized_contacts[role_name].append(contact_info)

        # 2. Hanya telusuri ke bawah HANYA pada key "entities" (Targeted Traversal)
        if "entities" in obj and isinstance(obj["entities"], list):
            for sub_entity in obj["entities"]:
                self._extract_entities(sub_entity)

    def _parse_vcard(self, vcard: list) -> Dict[str, str]:
        res = {}
        if not isinstance(vcard, list) or len(vcard) < 2:
            return res

        prop_map = {
            "fn": "Name",
            "email": "Email",
            "tel": "Phone",
            "org": "Organization",
            "kind": "Entity_Type",
            "title": "Title",
        }

        for item in vcard[1]:
            if not isinstance(item, list) or len(item) < 4:
                continue

            prop, params = item[0], item[1]
            params_dict = params if isinstance(params, dict) else {}
            val = item[3] if len(item) == 4 else item[3:]

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

    # ==========================================
    # HTTP METADATA & UTILITIES
    # ==========================================
    @property
    def status(self) -> str:
        return self._status

    @property
    def status_code(self) -> int:
        return self._data.get("status_code", 0)

    @property
    def message(self) -> str:
        return self._message

    @property
    def proto(self) -> str:
        return self._data.get("protocol", "")

    @property
    def engine(self) -> str:
        return self._data.get("engine", "")

    @property
    def raw_data(self) -> Union[str, Dict]:
        return self._body

    def data_json(self) -> Union[Dict[str, Any], list, None]:
        if not self.raw_data:
            return None
        if isinstance(self.raw_data, (dict, list)):
            return self.raw_data
        try:
            return json.loads(self.raw_data)
        except json.JSONDecodeError:
            smf.printd("Failed to parse response body as JSON", level="WARN")
            return None

    @property
    def headers(self) -> Dict[str, str]:
        return self._headers

    def get_headers(self, name: str, default: Optional[str] = None) -> Optional[str]:
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
        return self.status.upper() == "SUCCESS"

    def __bool__(self):
        return self.ok

    def __repr__(self):
        return f"<WHOISResponse Status={self.status} Code={self.status_code} Engine={self.engine}>"


class WhoisDomain:
    """Namespace Stateless untuk mengeksekusi WHOIS IP via CRS Engine."""

    @staticmethod
    def whois(
        domain: str,
        timeout: float = 3.0,
        rl: int = 150,
        frl: int = 10,
        con: int = 0,
        **kwargs,
    ) -> WHOISResponse:
        """Menyiapkan packet WHOIS_SEND"""

        packet = {
            "primitive": "WHOIS_SEND",
            "mode": "DOMWhois",
            "domain": domain,
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


domwhois = WhoisDomain.whois
