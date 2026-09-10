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

    # TAMBAHAN: Relasi 1-to-1 (atau 1-to-many jika menyimpan histori sertifikat) ke tabel TLS
    tls_info = relationship("TLSInfo", back_populates="service", cascade="all, delete-orphan")

class TLSInfo(Base):
    """
    Menyimpan profil kriptografi dan detail sertifikat X.509 dari sebuah Service.
    Sangat berguna untuk query audit: expired certs, weak ciphers, atau insecure protocols.
    """

    __tablename__ = "tls_info"

    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    
    # --- X.509 Certificate Metadata ---
    subject = Column(String(512))            # ex: CN=www.target.com, O=Target Corp
    issuer = Column(String(512))             # ex: CN=Let's Encrypt Authority X3
    subject_alt_names = Column(Text)         # SANs (Bisa menyimpan array JSON berupa String/List)
    
    # --- Validity (Penting untuk deteksi Expired Certs) ---
    not_before = Column(DateTime(timezone=True))
    not_after = Column(DateTime(timezone=True))
    
    # --- Identification & Fingerprinting ---
    serial_number = Column(String(128))      # Hex string dari serial number
    sha1_fingerprint = Column(String(40), index=True)   # Indexing untuk pencarian pivoting/threat intel
    sha256_fingerprint = Column(String(64), index=True) 
    
    # --- Cryptographic Key Properties ---
    pubkey_algorithm = Column(String(64))    # ex: RSA, ECDSA, Ed25519
    pubkey_size = Column(Integer)            # ex: 2048, 4096, 256
    
    # --- Protocol & Cipher Context ---
    # Menggunakan Text di sini sebagai fallback yang aman (dapat diisi string JSON).
    supported_protocols = Column(Text)       # ex: ["TLSv1.2", "TLSv1.3"] -> Deteksi SSLv2/SSLv3/TLS 1.0
    accepted_ciphers = Column(Text)          # Daftar ciphersuite yang didukung
    weak_ciphers = Column(Text)              # Daftar weak ciphers spesifik (RC4, DES, 3DES, Sweet32)
    
    # --- Raw Data ---
    raw_certificate = Column(Text)           # Simpan format PEM untuk ekstraksi offline/analisis manual
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relasi kembali ke Service
    service = relationship("Service", back_populates="tls_info")
    

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
