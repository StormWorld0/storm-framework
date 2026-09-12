import yaml
import smf

from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
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
        self.inp = ""

        # Buat engine konfigurasi
        self.engine = self._create_engine_from_config(config_path, config_ext)

        # Siapkan Session Factory
        self._setup_session()

        # Jalankan bootstrap
        self.bootstrap_db()

    def _setup_session(self):
        """Mengekstrak logika pembuatan session agar bisa dipanggil berulang."""
        if self.engine:
            self.SessionLocal = scoped_session(sessionmaker(bind=self.engine))
        else:
            self.SessionLocal = None

    @property
    def session(self):
        """Helper untuk mengambil instance session tunggal."""
        if self.SessionLocal and self.is_connected:
            return self.SessionLocal()
        return None

    def _apply_dynamic(self, dynamic_inp: dict) -> bool:
        """
        Metode ini dipanggil SETELAH instance dibuat untuk menimpa
        koneksi YAML ke koneksi Eksternal (Regex Parsed).
        """
        self.inp = dynamic_inp
        
        # Security: Dispose pool lama untuk mencegah memory/socket leak
        if self.engine:
            self.engine.dispose()
            
        # Rebuild engine. Masuk mode Eksternal.
        self.engine = self._create_engine_from_config(self.config_path)
        self._setup_session()
        
        return self.bootstrap_db()

    def _create_engine_from_config(self, config_path):
        """Parsing YAML dan mengonstruksi PostgreSQL connection string."""
        # MODE 1: EKSTERNAL (Override mode)
        if self.inp:
            required_keys = {"username", "password", "host", "port", "database"}

            # Memastikan semua key ada DAN valuenya tidak None/kosong
            if not required_keys.issubset(self.inp.keys()) or not all(
                self.inp[k] for k in required_keys
            ):
                smf.printd(
                    "Invalid or missing keys in external configuration dict", level="WARN"
                )
                return None

            try:
                db_url = URL.create(
                    drivername="postgresql+psycopg2",
                    username=self.inp["username"],
                    password=self.inp["password"],
                    host=self.inp["host"],
                    port=self.inp["port"],
                    database=self.inp["database"],
                )

                # Menggunakan konfigurasi pool default untuk koneksi eksternal
                return create_engine(db_url, pool_size=200, pool_timeout=10)
            except Exception as e:
                smf.printd("Failed to build external DB URL", e, level="ERROR")
                return None

        # MODE 2: DEFAULT (YAML Config)
        path = Path(config_path)
        if not path.is_file():
            smf.printd("Config file not found", config_path, level="WARN")
            return None

        try:
            with open(path, "r") as f:
                yaml_data = yaml.safe_load(f)

            # Validasi struktur YAML untuk mencegah KeyError
            if not yaml_data or "production" not in yaml_data:
                smf.printd("YAML config missing 'production' node", level="WARN")
                return None

            config = yaml_data["production"]
            self.db_name = config.get("database", "smf")

            db_url = URL.create(
                drivername="postgresql+psycopg2",
                username=config.get("username"),
                password=config.get("password"),
                host=config.get("host"),
                port=config.get("port"),
                database=self.db_name,
            )

            return create_engine(
                db_url,
                pool_size=config.get("pool", 5),
                pool_timeout=config.get("timeout", 10),
            )
        except Exception as e:
            smf.printd("Failed to create engine", e, level="ERROR")
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
            smf.printd(
                "Database connectivity failed during handshake (Auth/Network issue)",
                level="ERROR",
            )
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
