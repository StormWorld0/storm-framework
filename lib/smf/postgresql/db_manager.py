import yaml
import smf

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .db_models import Base, Workspace, Host, Service, Vuln


class DBManager:
    def __init__(self, config_path):
        """Membangun koneksi menggunakan parameter dari database.yml"""
        self.engine = self._create_engine_from_config(config_path)

        # State workspace aktif (Default: "default")
        self.current_workspace = "default"

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

        self.db_name = config.get("database", "msf")

        # Format: postgresql+psycopg2://user:password@host:port/dbname
        dsn = (
            f"postgresql+psycopg2://{config['username']}:{config['password']}"
            f"@{config['host']}:{config['port']}/{self.db_name}"
        )

        return create_engine(
            dsn, pool_size=config.get("pool", 5), pool_timeout=config.get("timeout", 10)
        )

    def _ensure_default_workspace(self):
        """Memastikan workspace 'default' selalu ada saat startup."""
        try:
            workspace = self.session.query(Workspace).filter_by(name="default").first()
            if not workspace:
                workspace = Workspace(name="default")
                self.session.add(workspace)
                self.session.commit()
        except Exception as e:
            self.session.rollback()
            smf.printd("Failed to create default workspace", e, level="ERROR")

    def report_host(self, address, workspace_name=None, **kwargs):
        """Idempotent Host creation."""
        ws_name = workspace_name or self.current_workspace
        try:
            # Ambil workspace, buat baru jika tidak ditemukan
            workspace = self.session.query(Workspace).filter_by(name=ws_name).first()
            if not workspace:
                workspace = Workspace(name=ws_name)
                self.session.add(workspace)
                self.session.flush()

            # Cek apakah host sudah ada di workspace ini
            host = (
                self.session.query(Host)
                .filter_by(workspace_id=workspace.id, address=address)
                .first()
            )

            if host:
                for key, value in kwargs.items():
                    if hasattr(host, key):
                        setattr(host, key, value)
            else:
                host = Host(workspace_id=workspace.id, address=address, **kwargs)
                self.session.add(host)

            self.session.commit()
            return host
        except Exception as e:
            self.session.rollback()
            smf.printd(f"Error on report_host ({address})", e, level="ERROR")
            return None

    def report_service(self, address, port, proto, workspace_name=None, **kwargs):
        """Melaporkan service yang terbuka (Otomatis membuat Host jika belum ada)."""
        ws_name = workspace_name or self.current_workspace
        try:
            host = self.report_host(address, workspace_name=ws_name)
            if not host:
                return None

            service = (
                self.session.query(Service)
                .filter_by(host_id=host.id, port=port, proto=proto)
                .first()
            )

            if service:
                for key, value in kwargs.items():
                    if hasattr(service, key):
                        setattr(service, key, value)
            else:
                service = Service(host_id=host.id, port=port, proto=proto, **kwargs)
                self.session.add(service)

            self.session.commit()
            return service
        except Exception as e:
            self.session.rollback()
            smf.printd(f"Error pada report_service ({address}:{port})", e, level="ERROR")
            return None

    def report_vuln(
        self, address, name, workspace_name=None, port=None, proto=None, **kwargs
    ):
        """Melaporkan vulnerability pada Host atau Service."""
        ws_name = workspace_name or self.current_workspace
        try:
            host = self.report_host(address, workspace_name=ws_name)
            if not host:
                return None

            service = None
            if port and proto:
                service = self.report_service(
                    address, port, proto, workspace_name=ws_name
                )

            query = self.session.query(Vuln).filter_by(host_id=host.id, name=name)
            if service:
                query = query.filter_by(service_id=service.id)

            vuln = query.first()

            if vuln:
                for key, value in kwargs.items():
                    if hasattr(vuln, key):
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
        except Exception as e:
            self.session.rollback()
            smf.printd(f"Error on report_vuln ({name})", e, level="ERROR")
            return None
