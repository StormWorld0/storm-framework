from typing import Dict, Any, List, Optional, Union
from datetime import datetime


class DataBuilder:
    """
    DTO Builder tersinkronisasi penuh dengan skema db_models & ingest_telemetry.
    Mendukung type-hinting, auto-complete, dan multi-item ingestion.
    """

    def __init__(self):
        self.payload: Dict[str, Any] = {
            "host": {},
            "services": [],
            "vulns": [],
            "notes": [],
            "credentials": [],
            "loots": [],
        }

    def add_host(
        self,
        address: str,
        hostnames: Optional[List[str]] = None,
        mac: Optional[str] = None,
        os_name: Optional[str] = None,
        os_flavor: Optional[str] = None,
        purpose: Optional[str] = None,
        info: Optional[str] = None,
        **kwargs,
    ):
        """Metadata target host berdasarkan model Host."""
        self.payload["host"] = {
            "address": address,
            "hostnames": hostnames or [],
            "mac": mac,
            "os_name": os_name,
            "os_flavor": os_flavor,
            "purpose": purpose,
            "info": info,
            **kwargs,
        }
        return self

    def add_service(
        self,
        port: int,
        proto: str = "tcp",
        state: Optional[str] = None,
        name: Optional[str] = None,
        info: Optional[str] = None,
        tls_info: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        """Detail layanan. Jika ada TLS Info, bisa dimasukkan langsung di parameter tls_info."""
        svc = {
            "port": port,
            "proto": proto.lower(),
            "state": state,
            "name": name,
            "info": info,
            **kwargs,
        }
        if tls_info:
            svc["tls_info"] = tls_info

        self.payload["services"].append(svc)
        return self

    def add_vuln(
        self,
        name: str,
        info: Optional[str] = None,
        exploited_at: Optional[datetime] = None,
        **kwargs,
    ):
        """Temuan kerentanan berdasarkan model Vuln."""
        self.payload["vulns"].append(
            {"name": name, "info": info, "exploited_at": exploited_at, **kwargs}
        )
        return self

    def add_note(self, ntype: str, data: Union[Dict, List, str], **kwargs):
        """Temuan tidak terstruktur berdasarkan model Note."""
        self.payload["notes"].append({"ntype": ntype, "data": data, **kwargs})
        return self

    def add_credential(
        self,
        public: Optional[str] = None,
        private: Optional[str] = None,
        private_type: Optional[str] = None,
        realm: Optional[str] = None,
        login_status: Optional[str] = None,
        access_level: Optional[str] = None,
        **kwargs,
    ):
        """Data kredensial dan status login-nya."""
        cred = {
            "public": public,
            "private": private,
            "private_type": private_type,
            "realm": realm,
            **kwargs,
        }
        self.payload["credentials"].append(cred)
        if login_status:
            self.payload_meta["login_status"] = login_status
        if access_level:
            self.payload_meta["access_level"] = access_level
        return self

    def add_loot(
        self,
        path: str,
        ltype: Optional[str] = None,
        data: Optional[str] = None,
        content_type: Optional[str] = None,
        **kwargs,
    ):
        """Bukti eksploitasi/file dump berdasarkan model Loot."""
        self.payload["loots"].append(
            {
                "path": path,
                "ltype": ltype,
                "data": data,
                "content_type": content_type,
                **kwargs,
            }
        )
        return self

    def build(self) -> Dict[str, Any]:
        """Mengembalikan MURNI dictionary untuk dimasukkan ke Queue."""
        output = {}

        # 1. Masukkan host (jika diisi)
        if self.payload["host"]:
            output["host"] = {
                k: v for k, v in self.payload["host"].items() if v is not None
            }

        # 2. Backward compatibility: Jika item list cuma 1, kirim sebagai dict tunggal
        # Agar ingest_telemetry kamu yang sekarang langsung bisa membaca tanpa ubah kode!
        for key in ["services", "vulns", "notes", "credentials", "loots"]:
            items = self.payload[key]
            if not items:
                continue

            # Map ke nama singular (services -> service, vulns -> vuln)
            singular_key = key.rstrip("s") if key != "credentials" else "credential"

            if len(items) == 1:
                output[singular_key] = {
                    k: v for k, v in items[0].items() if v is not None
                }
            else:
                output[key] = [
                    {k: v for k, v in item.items() if v is not None} for item in items
                ]

        return output
