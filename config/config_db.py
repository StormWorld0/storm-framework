from pathlib import Path

# Defines the default working directory
SMF_BASE_DIR = Path.home() / ".smf"
DB_DATA_DIR = SMF_BASE_DIR / "db"
CONFIG_FILE = SMF_BASE_DIR / "database.yml"

# Default Database Parameters
DB_USER = "smf"
DB_NAME = "smf"
DB_HOST = "127.0.0.1"
DB_PORT = "5433"
DB_POOL = "200"

ADDRESS = "localhost"
PORT = "5443"
