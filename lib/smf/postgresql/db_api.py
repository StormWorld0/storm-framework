import smf
import json

from typing import Dict, Any
from sqlalchemy import inspect, text
from sqlalchemy.types import Integer, String, Text, Boolean
from sqlalchemy.dialects.postgresql import JSONB, INET, ARRAY
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
    if db and hasattr(db, "session"):
        return db.session
    return None


# ==========================================
# FUNCTIONS FOR REPL (View / Query Data)
# ==========================================


def send_connect(inp):
    """Ekuivalen dengan `db_connect`"""
    if not inp:
        return {"status": "warn"}
    try:
        if res := db._apply_dynamic(inp):
            return {"status": "success"}
        else:
            return {"status": "warn"}
    except Exception as e:
        smf.printd("Failed to connect", e, level="ERROR")
        return {"status": "error"}


def close_db() -> bool | None:
    """Ekuivalen dengan `db_close`"""
    if not db and not get_session():
        return None
    try:
        db.session.remove()
        db.engine.dispose()
        db.is_connected = False
        return True
    except Exception as e:
        smf.printd("Failed to close database connection", e, level="ERROR")
        return False


def get_status():
    """Ekuivalen dengan `db_status`"""
    if db and not getattr(db, "is_connected", False):
        db.bootstrap_db()

    # Cek apakah objek db dan session valid/tersedia
    if not db or not get_session():
        return {
            "status": "disconnected",
            "reason": "PostgreSQL service offline or not bootstrapped",
        }

    # Jika session valid, lakukan ping
    try:
        db.session.execute(text("SELECT 1"))
        return {
            "status": "connected",
            "database": getattr(db, "db_name"),
            "backend": "PostgreSQL",
        }
    except Exception as e:
        smf.printd("Database heartbeat failed", e, level="ERROR")
        db.is_connected = False
        return {
            "status": "error",
            "reason": str(e),
        }


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
        db.session.rollback()
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
        db.session.rollback()
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
        db.session.rollback()
        smf.printd("Failed to get vulns", e, level="ERROR")
        return []


def get_creds(workspace_name: str = None):
    """Mengambil seluruh credential yang terisolasi dalam satu workspace."""
    target_ws = workspace_name or get_current_workspace()
    try:
        ws = db.session.query(Workspace).filter_by(name=target_ws).first()
        if not ws:
            smf.printd(f"Workspace '{target_ws}' not found", level="WARN")
            return []

        # ARCHITECTURE UPGRADE:
        # 1. Filter langsung dari Credential.workspace_id (O(1) index lookup)
        # 2. Outerjoin ke Host dan Login untuk eager load (menghemat N+1 query)
        creds_query = (
            db.session.query(Credential)
            .outerjoin(Host)
            .outerjoin(Login)
            .filter(Credential.workspace_id == ws.id)
            .all()
        )

        results = []
        for v in creds_query:
            # Mengatasi relasi One-to-Many pada Login.
            # Mengambil data login terakhir/pertama jika credential ini pernah digunakan.
            logn = v.logins[0] if v.logins else None
            serv = logn.service if logn else None

            results.append(
                {
                    "addr": v.host.address if v.host else "",
                    "host": v.host.hostname if v.host else "",
                    "port": serv.port if serv and hasattr(serv, "port") else "",
                    "public": v.public or "",
                    "private": v.private or "",
                    "type": v.private_type or "",
                    "realm": v.realm or "",
                    "created": v.created or None,
                    "status": logn.status if logn else "",
                    "level": logn.access_level if logn else "",
                }
            )

        return results
    except Exception as e:
        db.session.rollback()
        smf.printd("Failed to get credential", e, level="ERROR")
        return []


# ==========================================
# FUNCTIONS FOR CORE / MODULES (Ingest Data)
# ==========================================


def _clean_payload(model_cls, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Intelligent payload cleaner & type coercer.
    Mengambil dict kotor dan menyesuaikan tipe datanya dengan skema SQLAlchemy.
    """
    mapper = inspect(model_cls).mapper
    clean_data = {}

    for col_attr in mapper.column_attrs:
        key = col_attr.key

        # Skip jika key tidak ada di payload, biar mekanisme default database bekerja
        if key not in payload:
            continue

        val = payload[key]

        # Handle Null/None
        if val is None:
            clean_data[key] = None
            continue

        # Dapatkan tipe data asli dari kolom SQLAlchemy
        col_type = col_attr.columns[0].type

        try:
            if isinstance(col_type, Integer):
                clean_data[key] = int(val)

            elif isinstance(col_type, (String, Text, INET)):
                # Jika user passing Dict/List tapi kolomnya Text/String, otomatis Serialize!
                if isinstance(val, (dict, list)):
                    clean_data[key] = json.dumps(val)
                else:
                    clean_data[key] = str(val)

            elif isinstance(col_type, JSONB):
                # PostgreSQL JSONB butuh tipe dict/list native Python.
                # Jika user terlanjur passing string JSON, ini akan parse kembali.
                if isinstance(val, str):
                    try:
                        clean_data[key] = json.loads(val)
                    except json.JSONDecodeError:
                        clean_data[key] = val
                else:
                    clean_data[key] = val

            elif isinstance(col_type, ARRAY):
                # Pastikan data selalu dalam bentuk list
                if not isinstance(val, list):
                    clean_data[key] = [val]
                else:
                    clean_data[key] = val

            elif isinstance(col_type, Boolean):
                # Handle string boolean ("true", "false", "1", "0")
                if isinstance(val, str):
                    clean_data[key] = val.lower() in ("true", "1", "yes", "y")
                else:
                    clean_data[key] = bool(val)
            else:
                # Fallback untuk tipe lain (DateTime dsb)
                clean_data[key] = val

        except (ValueError, TypeError):
            pass

    return clean_data


def ingest_telemetry(data: Dict[str, Any], workspace: str = "default") -> bool:
    if not (session := get_session()):
        return False

    try:
        # 1. Workspace
        ws = session.query(Workspace).filter_by(name=workspace).first()
        if not ws:
            ws = Workspace(name=workspace)
            session.add(ws)
            session.flush()

        host_inst = service_inst = cred_inst = None

        # 2. Host
        host_data = data.get("host")
        if host_data and isinstance(host_data, dict) and host_data.get("address"):
            clean_host = _clean_payload(Host, host_data)
            host_inst = (
                session.query(Host)
                .filter_by(workspace_id=ws.id, address=clean_host["address"])
                .first()
            )

            if not host_inst:
                host_inst = Host(workspace_id=ws.id, **clean_host)
                session.add(host_inst)
            else:
                for k, v in clean_host.items():
                    # Handle ARRAY append untuk hostnames secara native
                    if k == "hostname" and v:
                        existing = set(host_inst.hostname or [])
                        existing.update(v)
                        setattr(host_inst, k, list(existing))
                    elif v is not None:
                        setattr(host_inst, k, v)
            session.flush()

        # 3. Service
        srv_data = data.get("service")
        if srv_data and isinstance(srv_data, dict) and host_inst and srv_data.get("port"):
            clean_srv = _clean_payload(Service, srv_data)
            proto = clean_srv.get("proto", "tcp")

            service_inst = (
                session.query(Service)
                .filter_by(host_id=host_inst.id, port=clean_srv["port"], proto=proto)
                .first()
            )

            if not service_inst:
                service_inst = Service(host_id=host_inst.id, **clean_srv)
                session.add(service_inst)
            else:
                for k, v in clean_srv.items():
                    if v is not None:
                        setattr(service_inst, k, v)
            session.flush()

        # 3.5 TLS Info
        tls_data = data.get("tls_info")
        if tls_data and isinstance(tls_data, dict) and service_inst:
            clean_tls = _clean_payload(TLSInfo, tls_data)
            tls_inst = (
                session.query(TLSInfo).filter_by(service_id=service_inst.id).first()
            )

            if not tls_inst:
                tls_inst = TLSInfo(service_id=service_inst.id, **clean_tls)
                session.add(tls_inst)
            else:
                for k, v in clean_tls.items():
                    if v is not None:
                        setattr(tls_inst, k, v)
            session.flush()

        # 4. Vuln (WITH DEDUPLICATION)
        vuln_data = data.get("vuln")
        if (
            vuln_data
            and isinstance(vuln_data, dict)
            and host_inst
            and vuln_data.get("name")
        ):
            clean_vuln = _clean_payload(Vuln, vuln_data)
            sid = service_inst.id if service_inst else None

            vuln_inst = (
                session.query(Vuln)
                .filter_by(host_id=host_inst.id, service_id=sid, name=clean_vuln["name"])
                .first()
            )

            if not vuln_inst:
                vuln_inst = Vuln(host_id=host_inst.id, service_id=sid, **clean_vuln)
                session.add(vuln_inst)
            else:
                if clean_vuln.get("info"):
                    vuln_inst.info = clean_vuln["info"]
                if clean_vuln.get("exploited"):
                    vuln_inst.exploited = clean_vuln["exploited"]
            session.flush()

        # 5. Note (Tidak perlu lagi manual json.dumps)
        note_data = data.get("note")
        if note_data and isinstance(note_data, dict):
            clean_note = _clean_payload(Note, note_data)
            note_inst = Note(
                workspace_id=ws.id,
                host_id=host_inst.id if host_inst else None,
                service_id=service_inst.id if service_inst else None,
                **clean_note,
            )
            session.add(note_inst)

        # 6. Credential & Login
        cred_data = data.get("credential")
        if cred_data and isinstance(cred_data, dict) and cred_data.get("public"):
            clean_cred = _clean_payload(Credential, cred_data)
            cred_inst = (
                session.query(Credential)
                .filter_by(
                    workspace_id=ws.id,
                    public=clean_cred["public"],
                    private=clean_cred.get("private"),
                    realm=clean_cred.get("realm"),
                )
                .first()
            )

            if not cred_inst:
                cred_inst = Credential(workspace_id=ws.id, **clean_cred)
                session.add(cred_inst)
                session.flush()

            # Ingest Login mapping
            if service_inst and cred_inst and data.get("login_status"):
                login_inst = (
                    session.query(Login)
                    .filter_by(credential_id=cred_inst.id, service_id=service_inst.id)
                    .first()
                )

                if not login_inst:
                    login_inst = Login(
                        credential_id=cred_inst.id,
                        service_id=service_inst.id,
                        status=data.get("login_status", "Successful"),
                        access_level=data.get("access_level", "User"),
                    )
                    session.add(login_inst)
                else:
                    login_inst.status = data.get("login_status", login_inst.status)
                    login_inst.access_level = data.get(
                        "access_level", login_inst.access_level
                    )

        # 7. Loot
        loot_data = data.get("loot")
        if loot_data and isinstance(loot_data, dict):
            clean_loot = _clean_payload(Loot, loot_data)
            session.add(
                Loot(
                    workspace_id=ws.id,
                    host_id=host_inst.id if host_inst else None,
                    service_id=service_inst.id if service_inst else None,
                    **clean_loot,
                )
            )

        session.commit()
        return True
    except Exception as e:
        session.rollback()
        smf.printd(f"Ingestion Pipeline Failed", e, level="ERROR")
        return False
    finally:
        session.close()
