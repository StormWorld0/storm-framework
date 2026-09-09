from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Workspace(Base):
    """Isolasi data per project/pentest."""

    __tablename__ = "workspaces"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relasi: 1 Workspace memiliki banyak Hosts
    hosts = relationship("Host", back_populates="workspace", cascade="all, delete-orphan")


class Host(Base):
    """Menyimpan entitas target."""

    __tablename__ = "hosts"

    id = Column(Integer, primary_key=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    address = Column(String(255), nullable=False)  # IP Address (IPv4/IPv6)
    mac = Column(String(255))
    os_name = Column(String(255))
    os_flavor = Column(String(255))
    purpose = Column(String(255))  # client, server, device, dll
    info = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    workspace = relationship("Workspace", back_populates="hosts")
    services = relationship(
        "Service", back_populates="host", cascade="all, delete-orphan"
    )
    vulns = relationship("Vuln", back_populates="host", cascade="all, delete-orphan")


class Service(Base):
    """Layanan yang berjalan di atas Host."""

    __tablename__ = "services"

    id = Column(Integer, primary_key=True)
    host_id = Column(Integer, ForeignKey("hosts.id"), nullable=False)
    port = Column(Integer, nullable=False)
    proto = Column(String(16), nullable=False)  # tcp, udp
    state = Column(String(255))  # open, closed, filtered
    name = Column(String(255))  # http, ssh, smb
    info = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    host = relationship("Host", back_populates="services")
    vulns = relationship("Vuln", back_populates="service", cascade="all, delete-orphan")


class Vuln(Base):
    """Temuan kerentanan pada Host atau Service."""

    __tablename__ = "vulns"

    id = Column(Integer, primary_key=True)
    host_id = Column(Integer, ForeignKey("hosts.id"), nullable=False)
    service_id = Column(
        Integer, ForeignKey("services.id"), nullable=True
    )  # Opsional, vuln bisa di OS level
    name = Column(String(255), nullable=False)
    info = Column(Text)
    exploited_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    host = relationship("Host", back_populates="vulns")
    service = relationship("Service", back_populates="vulns")


class Note(Base):
    """
    Menyimpan data tidak terstruktur atau temuan unik (misal: SMB hashes, SSL certs, banner).
    Di Metasploit, Note menggunakan polymorphic association (bisa nempel ke Host, Service, atau Workspace).
    """

    __tablename__ = "notes"

    id = Column(Integer, primary_key=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    host_id = Column(Integer, ForeignKey("hosts.id"), nullable=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=True)
    ntype = Column(String(255))  # note type (misal: 'smb.fingerprint', 'host.os.guess')
    data = Column(Text)  # Biasanya menyimpan JSON payload
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Credential(Base):
    """
    Pemisahan entitas kredensial murni (username/hash/password).
    """

    __tablename__ = "credentials"

    id = Column(Integer, primary_key=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    public = Column(String(255))  # Username
    private = Column(Text)  # Password atau Hash
    private_type = Column(String(255))  # 'password', 'ntlm_hash', 'ssh_key'
    realm = Column(String(255))  # Domain / Workgroup
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Login(Base):
    """
    Tabel mapping (Join Table) yang membuktikan bahwa sebuah Credential
    valid (sukses digunakan) pada sebuah Service tertentu.
    """

    __tablename__ = "logins"

    id = Column(Integer, primary_key=True)
    credential_id = Column(Integer, ForeignKey("credentials.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    status = Column(String(255))  # 'Successful', 'Denied'
    access_level = Column(String(255))  # 'Admin', 'User'
    last_attempted_at = Column(DateTime(timezone=True))


class Loot(Base):
    """
    Menyimpan bukti eksploitasi (file unduhan, memory dump, registry hive).
    """

    __tablename__ = "loots"

    id = Column(Integer, primary_key=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    host_id = Column(Integer, ForeignKey("hosts.id"), nullable=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=True)
    ltype = Column(String(255))  # loot type (misal: 'windows.hashdump', 'cisco.config')
    path = Column(Text, nullable=False)  # Path fisik ke file di disk (~/.msf4/loot/)
    data = Column(Text)  # Info tambahan
    content_type = Column(String(255))  # MIME type (application/zip, text/plain)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
