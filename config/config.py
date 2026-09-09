from pathlib import Path

# Mendefinisikan direktori kerja standar
SMF_BASE_DIR = Path.home() / ".smf"
DB_DATA_DIR = SMF_BASE_DIR / "db"
CONFIG_FILE = SMF_BASE_DIR / "database.yml"

# Parameter Database Default
DB_USER = "smf"
DB_NAME = "smf"
DB_HOST = "127.0.0.1"
DB_PORT = "8990"
