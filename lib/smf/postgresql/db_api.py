import smf

from sqlalchemy import text
from pathlib import Path

from .db_manager import DBManager
from .db_models import Host, Service, Vuln, Workspace

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
    """Dipanggil oleh siapa saja yang butuh tau workspace aktif"""
    if db and hasattr(db, "current_workspace"):
        return db.current_workspace
    return "default"

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
    target_ws = workspace_name or getattr(db, "current_workspace", "default")
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
    target_ws = workspace_name or getattr(db, "current_workspace", "default")
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
    target_ws = workspace_name or getattr(db, "current_workspace", "default")
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


def report_host(address: str, workspace_name: str = None, **kwargs):
    """Dipanggil oleh core untuk mencatat host (Idempotent)"""
    target_ws = workspace_name or getattr(db, "current_workspace", "default")
    try:
        host = db.report_host(address=address, workspace_name=target_ws, **kwargs)
        if host:
            return {"status": "success", "host_id": host.id}
        return None
    except Exception as e:
        smf.printd("Failed to report host", e, level="ERROR")
        return None


def report_service(
    address: str, port: int, proto: str, workspace_name: str = None, **kwargs
):
    """Dipanggil oleh core untuk mencatat service (Idempotent)"""
    target_ws = workspace_name or getattr(db, "current_workspace", "default")
    try:
        service = db.report_service(
            address=address,
            port=port,
            proto=proto,
            workspace_name=target_ws,
            **kwargs,
        )
        if service:
            return {"status": "success", "service_id": service.id}
        return None
    except Exception as e:
        smf.printd("Failed to report service", e, level="ERROR")
        return None


def report_vuln(address: str, name: str, workspace_name: str = None, **kwargs):
    """Dipanggil oleh core untuk mencatat vulnerability (Idempotent)"""
    target_ws = workspace_name or getattr(db, "current_workspace", "default")
    try:
        vuln = db.report_vuln(
            address=address,
            name=name,
            workspace_name=target_ws,
            **kwargs,
        )
        if vuln:
            return {"status": "success", "vuln_id": vuln.id}
        return None
    except Exception as e:
        smf.printd("Failed to report vuln", e, level="ERROR")
        return None
