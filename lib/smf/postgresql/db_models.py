from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB, INET, ARRAY

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

    address = Column(INET, nullable=False)  # IP Address (IPv4/IPv6)
    hostname = Column(ARRAY(String), server_default="{}")  # URL/Domain
    mac = Column(String(255))  # Mac Address
    os_name = Column(String(255))  # OS Name
    os_flavor = Column(String(255))  # OS specific
    os_version = Column(String(255))  # OS Version
    purpose = Column(String(255))  # client, server, device, dll
    info = Column(Text)  # Additional information
    created = Column(
        DateTime(timezone=True), server_default=func.now()
    )  # Time of creation
    updated = Column(DateTime(timezone=True), onupdate=func.now())  # Time updated

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

    port = Column(Integer, nullable=False)  # 80, 443
    proto = Column(String(16), nullable=False)  # tcp, udp
    state = Column(String(255))  # open, closed, filtered
    name = Column(String(255))  # http, ssh, smb
    info = Column(Text)  # Additional information
    created = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(DateTime(timezone=True), onupdate=func.now())

    host = relationship("Host", back_populates="services")
    vulns = relationship("Vuln", back_populates="service", cascade="all, delete-orphan")
    tls_info = relationship(
        "TLSInfo", back_populates="service", cascade="all, delete-orphan"
    )
    logins = relationship("Login", back_populates="service", cascade="all, delete-orphan")


class TLSInfo(Base):
    """
    Menyimpan profil kriptografi dan detail sertifikat X.509 dari sebuah Service.
    Dioptimalkan dengan JSONB PostgreSQL untuk query spesifik pada array/dictionary.
    """

    __tablename__ = "tls_info"

    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)

    # --- X.509 Certificate Metadata ---
    subject = Column(String(512))
    issuer = Column(String(512))
    # JSONB untuk Array string (misal: ["*.target.com", "target.local"])
    subject_alt_name = Column(JSONB, server_default="[]")

    # --- Validity ---
    not_before = Column(DateTime(timezone=True))
    not_after = Column(DateTime(timezone=True))

    # --- Identification & Fingerprinting ---
    serial_number = Column(String(128))
    sha1_fingerprint = Column(String(40), index=True)
    sha256_fingerprint = Column(String(64), index=True)

    # --- Cryptographic Key Properties ---
    pubkey_algorithm = Column(String(64))
    pubkey_size = Column(Integer)

    # --- Protocol & Cipher Context (JSONB Powers) ---
    # Bisa menyimpan list: ["TLSv1.2", "TLSv1.3"]
    supported_protocol = Column(JSONB, server_default="[]")

    # Bisa menyimpan dictionary kompleks:
    # {"TLSv1.2": ["TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256", ...]}
    accepted_cipher = Column(JSONB, server_default="{}")

    # Bisa menyimpan list of dictionaries untuk detail vulnerability
    # [{"cipher": "RC4-SHA", "reason": "Sweet32", "severity": "Medium"}]
    weak_cipher = Column(JSONB, server_default="[]")

    # --- Raw Data ---
    raw_certificate = Column(Text)

    created = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(DateTime(timezone=True), onupdate=func.now())

    service = relationship("Service", back_populates="tls_info")


class Vuln(Base):
    """Temuan kerentanan pada Host atau Service."""

    __tablename__ = "vulns"

    id = Column(Integer, primary_key=True)
    host_id = Column(Integer, ForeignKey("hosts.id"), nullable=False)
    service_id = Column(
        Integer, ForeignKey("services.id"), nullable=True
    )  # Opsional, vuln bisa di OS level

    name = Column(String(255), nullable=False)  # Exploit name / target name
    info = Column(Text)  # Additional information
    exploited = Column(DateTime(timezone=True))  # Time in exploitation
    created = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(DateTime(timezone=True), onupdate=func.now())

    host = relationship("Host", back_populates="vulns")
    service = relationship("Service", back_populates="vulns")


class Note(Base):
    """
    Menyimpan data tidak terstruktur atau temuan unik (misal: SMB hashes, SSL certs, banner).
    Seharusnya Note menggunakan polymorphic association (bisa nempel ke Host, Service, atau Workspace).
    """

    __tablename__ = "notes"

    id = Column(Integer, primary_key=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    host_id = Column(Integer, ForeignKey("hosts.id"), nullable=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=True)

    ntype = Column(String(255))  # note type (misal: 'smb.fingerprint', 'host.os.guess')
    data = Column(Text)  # Biasanya menyimpan JSON payload
    created = Column(DateTime(timezone=True), server_default=func.now())


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
    created = Column(DateTime(timezone=True), server_default=func.now())

    logins = relationship(
        "Login", back_populates="credential", cascade="all, delete-orphan"
    )


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
    last_attempted = Column(DateTime(timezone=True))

    credential = relationship("Credential", back_populates="logins")
    service = relationship("Service", back_populates="logins")


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
    created = Column(DateTime(timezone=True), server_default=func.now())
