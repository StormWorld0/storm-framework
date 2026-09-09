# Tambahkan ke models.py yang sebelumnya


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
