from typing import Dict, Any, List, Optional, Union
from datetime import datetime


class DataBuilder:
    """
    DTO Builder tersinkronisasi penuh dengan skema db_models & ingest_telemetry.
    Satu instance builder = Satu payload event.
    """

    def __init__(self):
        # Struktur disamakan persis dengan ekspektasi ingest_telemetry
        self.payload: Dict[str, Any] = {}

    def add_host(
        self,
        address: str,
        hostname: Optional[List[str]] = None,
        mac: Optional[str] = None,
        os_name: Optional[str] = None,
        os_flavor: Optional[str] = None,
        purpose: Optional[str] = None,
        info: Optional[str] = None,
        **kwargs,
    ):
        self.payload["host"] = {
            "address": address,
            "hostname": hostname or [],
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
        self.payload["service"] = {
            "port": port,
            "proto": proto.lower(),
            "state": state,
            "name": name,
            "info": info,
            **kwargs,
        }
        if tls_info:
            self.payload["tls_info"] = tls_info
        return self

    def add_vuln(
        self,
        name: str,
        info: Optional[str] = None,
        exploited: Optional[datetime] = None,
        **kwargs,
    ):
        self.payload["vuln"] = {
            "name": name,
            "info": info,
            "exploited": exploited,
            **kwargs,
        }
        return self

    def add_note(self, ntype: str, data: Union[Dict, List, str], **kwargs):
        self.payload["note"] = {"ntype": ntype, "data": data, **kwargs}
        return self

    def add_credential(
        self,
        public: str,
        private: Optional[str] = None,
        private_type: Optional[str] = None,
        realm: Optional[str] = None,
        login_status: Optional[str] = None,
        access_level: Optional[str] = None,
        **kwargs,
    ):
        self.payload["credential"] = {
            "public": public,
            "private": private,
            "private_type": private_type,
            "realm": realm,
            **kwargs,
        }
        # Inject ke root level sesuai ekspektasi pipeline ingestion
        if login_status:
            self.payload["login_status"] = login_status
        if access_level:
            self.payload["access_level"] = access_level
        return self

    def add_loot(
        self,
        path: str,
        ltype: Optional[str] = None,
        data: Optional[str] = None,
        content_type: Optional[str] = None,
        **kwargs,
    ):
        self.payload["loot"] = {
            "path": path,
            "ltype": ltype,
            "data": data,
            "content_type": content_type,
            **kwargs,
        }
        return self

    def build(self) -> Dict[str, Any]:
        """Mengembalikan dictionary bersih (membuang None value)."""
        output = {}
        for section, data in self.payload.items():
            if isinstance(data, dict):
                # Filter k,v yang tidak None
                cleaned = {k: v for k, v in data.items() if v is not None}
                if cleaned:
                    output[section] = cleaned
            else:
                # Untuk key root level seperti login_status & access_level
                if data is not None:
                    output[section] = data

        return output
