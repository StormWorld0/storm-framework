import yaml
import smf

from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import OperationalError, DBAPIError

from .db_models import Base, Workspace


class DBManager:
    def __init__(self, config_path):
        """Membangun koneksi menggunakan parameter dari database.yml"""
        self.config_path = config_path
        self.current_workspace = "default"
        self.is_connected = False
        self.db_name = "smf"

        # Buat engine konfigurasi
        self.engine = self._create_engine_from_config(config_path)

        # Siapkan Session Factory
        if self.engine:
            self.SessionLocal = scoped_session(sessionmaker(bind=self.engine))
        else:
            self.SessionLocal = None

        # Jalankan bootstrap
        self.bootstrap_db()

    @property
    def session(self):
        """Helper untuk mengambil instance session tunggal."""
        if self.SessionLocal and self.is_connected:
            return self.SessionLocal()
        return None

    def _create_engine_from_config(self, config_path):
        """Parsing YAML dan mengonstruksi PostgreSQL connection string."""
        if not Path(config_path).exists():
            smf.printd("Config file not found", config_path, level="WARN")
            return None

        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)["production"]

            self.db_name = config.get("database", "smf")

            dsn = (
                f"postgresql+psycopg2://{config['username']}:{config['password']}"
                f"@{config['host']}:{config['port']}/{self.db_name}"
            )

            return create_engine(
                dsn,
                pool_size=config.get("pool", 5),
                pool_timeout=config.get("timeout", 10),
            )
        except Exception as e:
            smf.printd("Failed to create engine from config", e, level="ERROR")
            return None

    def bootstrap_db(self) -> bool:
        """Handshake & skema migrasi yang aman dari Crash."""
        if not self.engine:
            self.is_connected = False
            return False

        try:
            # Test socket & DDL creation
            Base.metadata.create_all(self.engine)
            self.is_connected = True

            # Pastikan workspace default tersedia
            self._ensure_default_workspace()
            return True
        except (OperationalError, DBAPIError):
            self.is_connected = False
            return False
        except Exception as e:
            self.is_connected = False
            smf.printd("Unexpected database bootstrap failure", e, level="ERROR")
            return False

    def _ensure_default_workspace(self):
        """Memastikan workspace 'default' selalu ada saat startup."""
        session = self.session
        if not session:
            return

        try:
            workspace = session.query(Workspace).filter_by(name="default").first()
            if not workspace:
                workspace = Workspace(name="default")
                session.add(workspace)
                session.commit()
        except Exception as e:
            session.rollback()
            smf.printd("Failed to create default workspace", e, level="ERROR")
        finally:
            session.close()
