import yaml

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .db_models import Base, Workspace, Host, Service, Vuln


class DBManager:
    def __init__(self, config_path):
        """Membangun koneksi menggunakan parameter dari database.yml"""
        self.engine = self._create_engine_from_config(config_path)

        # Membuat skema tabel (jika belum ada)
        Base.metadata.create_all(self.engine)

        # Inisialisasi Session Factory
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        # Pastikan workspace 'default' selalu ada
        self._ensure_default_workspace()

    def _create_engine_from_config(self, config_path):
        """Parsing YAML dan mengonstruksi PostgreSQL connection string."""
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)["production"]

        # Format: postgresql+psycopg2://user:password@host:port/dbname
        dsn = (
            f"postgresql+psycopg2://{config['username']}:{config['password']}"
            f"@{config['host']}:{config['port']}/{config['database']}"
        )

        return create_engine(
            dsn, pool_size=config["pool"], pool_timeout=config["timeout"]
        )

    def _ensure_default_workspace(self):
        """Metasploit selalu berjalan di atas workspace 'default' jika tidak ditentukan."""
        workspace = self.session.query(Workspace).filter_by(name="default").first()
        if not workspace:
            workspace = Workspace(name="default")
            self.session.add(workspace)
            self.session.commit()

    def report_host(self, address, workspace_name="default", **kwargs):
        """
        Idempotent Host creation. Sama seperti `framework.db.report_host`.
        """
        workspace = self.session.query(Workspace).filter_by(name=workspace_name).one()

        # Cek apakah host sudah ada di workspace ini
        host = (
            self.session.query(Host)
            .filter_by(workspace_id=workspace.id, address=address)
            .first()
        )

        if host:
            # Update atribut jika host sudah ada
            for key, value in kwargs.items():
                setattr(host, key, value)
        else:
            # Buat host baru
            host = Host(workspace_id=workspace.id, address=address, **kwargs)
            self.session.add(host)

        self.session.commit()
        return host

    def report_service(self, address, port, proto, workspace_name="default", **kwargs):
        """
        Melaporkan service yang terbuka. Akan secara otomatis membuat Host jika belum ada.
        """
        # Resolusi Host (Chain of trust)
        host = self.report_host(address, workspace_name=workspace_name)

        # Cek ketersediaan Service
        service = (
            self.session.query(Service)
            .filter_by(host_id=host.id, port=port, proto=proto)
            .first()
        )

        if service:
            for key, value in kwargs.items():
                setattr(service, key, value)
        else:
            service = Service(host_id=host.id, port=port, proto=proto, **kwargs)
            self.session.add(service)

        self.session.commit()
        return service

    def report_vuln(self, address, name, port=None, proto=None, **kwargs):
        """
        Melaporkan vulnerability. Dapat ditautkan ke service tertentu atau langsung ke host.
        """
        host = self.report_host(address)
        service = None

        if port and proto:
            service = self.report_service(address, port, proto)

        # Pencarian vuln berdasarkan nama dan scope
        query = self.session.query(Vuln).filter_by(host_id=host.id, name=name)
        if service:
            query = query.filter_by(service_id=service.id)

        vuln = query.first()

        if vuln:
            for key, value in kwargs.items():
                setattr(vuln, key, value)
        else:
            vuln = Vuln(
                host_id=host.id,
                service_id=service.id if service else None,
                name=name,
                **kwargs,
            )
            self.session.add(vuln)

        self.session.commit()
        return vuln
