import config
import smf

from pydantic import BaseModel
from typing import Optional, List
from pathlib import Path

from .db_manager import DBManager
from .db_models import Workspace, Host, Service, Vuln


# Inisialisasi DB Engine tunggal di Server
config_path = Path.home() / ".smf" / "database.yml"
db = DBManager(config_path)

# ==========================================
# Pydantic Schemas (Data Validation)
# ==========================================
class HostReportSchema(BaseModel):
    address: str
    workspace_name: Optional[str] = "default"
    mac: Optional[str] = None
    os_name: Optional[str] = None
    os_flavor: Optional[str] = None
    purpose: Optional[str] = None
    info: Optional[str] = None

class ServiceReportSchema(BaseModel):
    address: str
    port: int
    proto: str
    workspace_name: Optional[str] = "default"
    name: Optional[str] = None
    state: Optional[str] = None
    info: Optional[str] = None

class VulnReportSchema(BaseModel):
    address: str
    name: str
    workspace_name: Optional[str] = "default"
    port: Optional[int] = None
    proto: Optional[str] = None
    info: Optional[str] = None

class WorkspaceCreateSchema(BaseModel):
    name: str

# ==========================================
# ENDPOINTS FOR REPL (View / Query Data)
# ==========================================

def get_status():
    """Ekuivalen dengan `db_status`"""
    try:
        db.session.execute("SELECT 1")
        return {"status": "connected", "database": db.db_name, "backend": "PostgreSQL"}
    except Exception as e:
        smf.printd("Database error", e, level="ERROR")
        return

@app.get("/workspaces")
def list_workspaces():
    """Ekuivalen dengan `workspace`"""
    workspaces = db.session.query(Workspace).all()
    return [{"id": w.id, "name": w.name, "host_count": len(w.hosts)} for w in workspaces]

def create_workspace(payload: WorkspaceCreateSchema):
    """Ekuivalen dengan `workspace -a <name>`"""
    existing = db.session.query(Workspace).filter_by(name=payload.name).first()
    if existing:
        smf.printd("Workspace already exists", level="INFO")
        return
    
    ws = Workspace(name=payload.name)
    db.session.add(ws)
    db.session.commit()
    return {"message": f"Workspace '{payload.name}' created"}

def get_hosts(workspace_name: str):
    """Ekuivalen dengan `hosts`"""
    ws = db.session.query(Workspace).filter_by(name=workspace_name).first()
    if not ws:
        smf.printd("Workspace not found", level="WARN")
        return
    
    hosts = db.session.query(Host).filter_by(workspace_id=ws.id).all()
    return [{
        "address": h.address,
        "mac": h.mac or "",
        "os_name": h.os_name or "Unknown",
        "os_flavor": h.os_flavor or "",
        "purpose": h.purpose or "",
        "info": h.info or ""
    } for h in hosts]

def get_services(workspace_name: str):
    """Ekuivalen dengan `services`"""
    ws = db.session.query(Workspace).filter_by(name=workspace_name).first()
    if not ws:
        smf.printd("Workspace not found", level="WARN")
        return
    
    services = db.session.query(Service).join(Host).filter(Host.workspace_id == ws.id).all()
    return [{
        "host": s.host.address,
        "port": s.port,
        "proto": s.proto,
        "name": s.name or "",
        "state": s.state or "",
        "info": s.info or ""
    } for s in services]

# ==========================================
# ENDPOINTS FOR CORE / MODULES (Ingest Data)
# ==========================================

def report_host(payload: HostReportSchema):
    """Dipanggil oleh core untuk mencatat host (Idempotent)"""
    host = db.report_host(
        address=payload.address,
        workspace_name=payload.workspace_name,
        mac=payload.mac,
        os_name=payload.os_name,
        os_flavor=payload.os_flavor,
        purpose=payload.purpose,
        info=payload.info
    )
    return {"status": "success", "host_id": host.id}

def report_service(payload: ServiceReportSchema):
    """Dipanggil oleh core untuk mencatat service (Idempotent)"""
    service = db.report_service(
        address=payload.address,
        port=payload.port,
        proto=payload.proto,
        workspace_name=payload.workspace_name,
        name=payload.name,
        state=payload.state,
        info=payload.info
    )
    return {"status": "success", "service_id": service.id}

def report_vuln(payload: VulnReportSchema):
    """Dipanggil oleh core untuk mencatat vulnerability (Idempotent)"""
    vuln = db.report_vuln(
        address=payload.address,
        name=payload.name,
        port=payload.port,
        proto=payload.proto,
        workspace_name=payload.workspace_name,
        info=payload.info
    )
    return {"status": "success", "vuln_id": vuln.id}
  
