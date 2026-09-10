import smf
import json

from typing import Dict, Any
from sqlalchemy import text
from sqlalchemy.inspection import inspect
from pathlib import Path

from .db_manager import DBManager
from .db_models import (
    Credential,
    Host,
    Login,
    Loot,
    Note,
    Service,
    TLSInfo,
    Vuln,
    Workspace,
)

# Inisialisasi DB Engine utama
config_path = Path.home() / ".smf" / "database.yml"
db = DBManager(config_path) if config_path.exists() else None


# ====================================
# SET WORKSPACE AND GET WORKSPACE
# ====================================


def set_workspace(name: str):
    """Dipanggil oleh command 'workspace <name>' di REPL"""
    if db:
        db.current_workspace = name


def get_current_workspace() -> str:
    """Dipanggil oleh siapa saja yang membutuhka nama workspace aktif"""
    if db and hasattr(db, "current_workspace"):
        return db.current_workspace
    return "default"


def get_session():
    """Mengembalikan session aktif"""
    if db and hasattr(db, "get_session"):
        return db.get_session
    return None


# ==========================================
# FUNCTIONS FOR REPL (View / Query Data)
# ==========================================


def get_status():
    """Ekuivalen dengan `db_status`"""
    try:
        db.session.execute(text("SELECT 1"))
        return {
            "status": "connected",
            "database": getattr(db, "db_name", "smf"),
            "backend": "PostgreSQL",
        }
    except Exception as e:
        smf.printd("Database error", e, level="ERROR")
        return None


def list_workspaces():
    """Ekuivalen dengan `workspace`"""
    try:
        workspaces = db.session.query(Workspace).all()
        return [
            {"id": w.id, "name": w.name, "host_count": len(w.hosts)} for w in workspaces
        ]
    except Exception as e:
        smf.printd("Failed to list workspaces", e, level="ERROR")
        return []


def create_workspace(name: str):
    """Ekuivalen dengan `workspace add <name>`"""
    try:
        existing = db.session.query(Workspace).filter_by(name=name).first()
        if existing:
            smf.printd("Workspace already exists", level="INFO")
            return None

        ws = Workspace(name=name)
        db.session.add(ws)
        db.session.commit()
        return {"message": f"Workspace '{name}' created"}
    except Exception as e:
        db.session.rollback()
        smf.printd("Failed to create workspace", e, level="ERROR")
        return None


def get_hosts(workspace_name: str = None):
    """Ekuivalen dengan `hosts`"""
    target_ws = workspace_name or get_current_workspace()
    try:
        ws = db.session.query(Workspace).filter_by(name=target_ws).first()
        if not ws:
            smf.printd(f"Workspace '{target_ws}' not found", level="WARN")
            return []

        hosts = db.session.query(Host).filter_by(workspace_id=ws.id).all()
        return [
            {
                "address": h.address,
                "mac": h.mac or "",
                "os_name": h.os_name or "Unknown",
                "os_flavor": h.os_flavor or "",
                "purpose": h.purpose or "",
                "info": h.info or "",
            }
            for h in hosts
        ]
    except Exception as e:
        smf.printd("Failed to get hosts", e, level="ERROR")
        return []


def get_services(workspace_name: str = None):
    """Ekuivalen dengan `services`"""
    target_ws = workspace_name or get_current_workspace()
    try:
        ws = db.session.query(Workspace).filter_by(name=target_ws).first()
        if not ws:
            smf.printd(f"Workspace '{target_ws}' not found", level="WARN")
            return []

        services = (
            db.session.query(Service).join(Host).filter(Host.workspace_id == ws.id).all()
        )
        return [
            {
                "host": s.host.address if s.host else "",
                "port": s.port,
                "proto": s.proto,
                "name": s.name or "",
                "state": s.state or "",
                "info": s.info or "",
            }
            for s in services
        ]
    except Exception as e:
        smf.printd("Failed to get services", e, level="ERROR")
        return []


def get_vulns(workspace_name: str = None):
    """Ekuivalen dengan `vulns`"""
    target_ws = workspace_name or get_current_workspace()
    try:
        ws = db.session.query(Workspace).filter_by(name=target_ws).first()
        if not ws:
            smf.printd(f"Workspace '{target_ws}' not found", level="WARN")
            return []

        vulns = db.session.query(Vuln).join(Host).filter(Host.workspace_id == ws.id).all()
        return [
            {
                "host": v.host.address if v.host else "",
                "port": v.service.port if v.service else "",
                "proto": v.service.proto if v.service else "",
                "name": v.name or "",
                "info": v.info or "",
            }
            for v in vulns
        ]
    except Exception as e:
        smf.printd("Failed to get vulns", e, level="ERROR")
        return []


# ==========================================
# FUNCTIONS FOR CORE / MODULES (Ingest Data)
# ==========================================


def _clean_payload(model_cls, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Membuang argumen yang tidak cocok dengan kolom model agar tidak TypeError."""
    valid_cols = {c.key for c in inspect(model_cls).mapper.column_attrs}
    return {k: v for k, v in payload.items() if k in valid_cols and v is not None}


def ingest_telemetry(data: Dict[str, Any], workspace: str = "default") -> bool:
    """Universal Ingestion Function.

    Memproses payload bertingkat dari DTO/Worker dan menyimpannya ke tabel
    PostgreSQL secara atomic (Host, Service, Vuln, Note, Creds, Loot).
    """
    if not db or not (session := get_session()):
        return False

    try:
        # 1. Pastikan Workspace Ada (Get or Create)
        ws = session.query(Workspace).filter_by(name=workspace).first()
        if not ws:
            ws = Workspace(name=workspace)
            session.add(ws)
            session.flush()

        host_inst = None
        service_inst = None

        # 2. Ingest Host (jika ada data target/host di payload)
        host_data = data.get("host")
        if host_data and isinstance(host_data, dict):
            address = host_data.get("address")
            if address:
                host_inst = (
                    session.query(Host)
                    .filter_by(workspace_id=ws.id, address=address)
                    .first()
                )
                clean_host = _clean_payload(Host, host_data)
                if not host_inst:
                    host_inst = Host(workspace_id=ws.id, **clean_host)
                    session.add(host_inst)
                else:
                    # Update metadata host jika ada perubahan (misal os_name)
                    for k, v in clean_host.items():
                        setattr(host_inst, k, v)
                session.flush()

        # 3. Ingest Service (jika ada data port/service di payload)
        srv_data = data.get("service")
        if srv_data and isinstance(srv_data, dict) and host_inst:
            port = srv_data.get("port")
            proto = srv_data.get("proto", "tcp")
            if port:
                service_inst = (
                    session.query(Service)
                    .filter_by(host_id=host_inst.id, port=port, proto=proto)
                    .first()
                )
                clean_srv = _clean_payload(Service, srv_data)
                if not service_inst:
                    service_inst = Service(host_id=host_inst.id, **clean_srv)
                    session.add(service_inst)
                else:
                    for k, v in clean_srv.items():
                        setattr(service_inst, k, v)
                session.flush()

        # =========================================================================
        # 3.5. Ingest TLS Info (Penting: Harus berjalan jika service_inst terbentuk)
        # =========================================================================
        tls_data = data.get("tls_info")
        if tls_data and isinstance(tls_data, dict) and service_inst:
            # Karena relasinya 1-to-1, kita cek apakah TLS info untuk service ini sudah ada
            tls_inst = (
                session.query(TLSInfo).filter_by(service_id=service_inst.id).first()
            )

            clean_tls = _clean_payload(TLSInfo, tls_data)

            # NOTE untuk PostgreSQL JSONB:
            # psycopg2 / asyncpg bawaan SQLAlchemy secara otomatis mengkonversi
            # Python dict/list menjadi tipe data JSONB di PostgreSQL.

            if not tls_inst:
                tls_inst = TLSInfo(service_id=service_inst.id, **clean_tls)
                session.add(tls_inst)
            else:
                # Update (Overwrite) state sertifikat terbaru dari hasil scan
                for k, v in clean_tls.items():
                    setattr(tls_inst, k, v)
            session.flush()

        # 4. Ingest Vuln (Kerentanan)
        vuln_data = data.get("vuln")
        if vuln_data and isinstance(vuln_data, dict) and host_inst:
            clean_vuln = _clean_payload(Vuln, vuln_data)
            vuln_inst = Vuln(
                host_id=host_inst.id,
                service_id=service_inst.id if service_inst else None,
                **clean_vuln,
            )
            session.add(vuln_inst)

        # 5. Ingest Note (RDAP, HTTP Headers, Custom Banner JSON)
        note_data = data.get("note")
        if note_data and isinstance(note_data, dict):
            clean_note = _clean_payload(Note, note_data)
            # Encode data dict ke JSON string jika perlu
            if isinstance(clean_note.get("data"), (dict, list)):
                clean_note["data"] = json.dumps(clean_note["data"])

            note_inst = Note(
                workspace_id=ws.id,
                host_id=host_inst.id if host_inst else None,
                service_id=service_inst.id if service_inst else None,
                **clean_note,
            )
            session.add(note_inst)

        # 6. Ingest Credential & Login
        cred_data = data.get("credential")
        if cred_data and isinstance(cred_data, dict):
            clean_cred = _clean_payload(Credential, cred_data)
            cred_inst = Credential(workspace_id=ws.id, **clean_cred)
            session.add(cred_inst)
            session.flush()

            # Jika login sukses pada service tertentu
            if service_inst and data.get("login_status"):
                login_inst = Login(
                    credential_id=cred_inst.id,
                    service_id=service_inst.id,
                    status=data.get("login_status", "Successful"),
                    access_level=data.get("access_level", "User"),
                )
                session.add(login_inst)

        # 7. Ingest Loot (File dump / artifacts)
        loot_data = data.get("loot")
        if loot_data and isinstance(loot_data, dict):
            clean_loot = _clean_payload(Loot, loot_data)
            loot_inst = Loot(
                workspace_id=ws.id,
                host_id=host_inst.id if host_inst else None,
                service_id=service_inst.id if service_inst else None,
                **clean_loot,
            )
            session.add(loot_inst)

        # Commit Satu Kali untuk Seluruh Transaksi
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        smf.printd("Ingestion Pipeline Transaction Failed", e, level="ERROR")
        return False
    finally:
        session.close()
