import subprocess
import smf
import secrets
import string
import shutil
import config


class PostgresManager:
    def __init__(self):
        self.pg_ctl = shutil.which("pg_ctl")
        self.initdb = shutil.which("initdb")
        self.createuser = shutil.which("createuser")
        self.createdb = shutil.which("createdb")
        self.psql = shutil.which("psql")

        self._check_dependencies()

    def _check_dependencies(self):
        """Verifying the availability of PostgreSQL binaries on the system ($PATH)."""
        if not all([self.pg_ctl, self.initdb, self.createuser, self.createdb]):
            smf.printd("PostgreSQL binaries not found.", level="WARN")
            smf.printf("[!] PostgreSQL binaries not found.")
            return

    def _run_cmd(self, cmd, capture_output=False, check=True):
        """Command execution wrapper with exception handling."""
        smf.printd(f"Executing: {' '.join(cmd)}", level="DEBUG")
        try:
            return subprocess.run(
                cmd, check=check, capture_output=capture_output, text=True
            )
        except subprocess.CalledProcessError as e:
            smf.printd(
                f"Command failed with exit code {e.returncode}: {' '.join(cmd)}",
                level="ERROR",
            )
            if e.stderr:
                smf.printd(f"Stderr", e.stderr.strip(), level="ERROR")
            if check:
                raise

    def init_database(self):
        """Initializing a new PostgreSQL cluster (-D /path/to/db)."""
        if config.DB_DATA_DIR.exists() and any(config.DB_DATA_DIR.iterdir()):
            smf.printd(
                "The database directory already exists and is not empty. Skip initdb.",
                level="WARN",
            )
            return

        smf.printd("Initializing local PostgreSQL database structure...", level="INFO")
        config.DB_DATA_DIR.mkdir(parents=True, exist_ok=True)
        self._run_cmd([self.initdb, "-D", str(config.DB_DATA_DIR), "--auth=trust"])

    def start(self):
        """Starting a PostgreSQL instance."""
        smf.printd("Starting the local PostgreSQL service...", level="INFO")
        self._run_cmd(
            [
                self.pg_ctl,
                "-D",
                str(config.DB_DATA_DIR),
                "-l",
                str(config.DB_DATA_DIR / "pg.log"),
                "-o",
                f"-p {config.DB_PORT}",
                "start",
            ],
            check=False,
        )  # check=False karena pg_ctl bisa return non-zero jika sudah jalan

    def stop(self):
        """Stopping the PostgreSQL instance."""
        smf.printd("Stopping the local PostgreSQL service...", level="INFO")
        self._run_cmd(
            [self.pg_ctl, "-D", str(config.DB_DATA_DIR), "stop", "-m", "fast"],
            check=False,
        )

    def status(self):
        """Checking instance status."""
        result = self._run_cmd(
            [self.pg_ctl, "-D", str(config.DB_DATA_DIR), "status"],
            capture_output=True,
            check=False,
        )
        smf.printf(result.stdout.strip())
        if result.stderr:
            smf.printf(result.stderr.strip())

    def provision_roles_and_db(self):
        """Create a dedicated user and database for SMF."""
        password = "".join(
            secrets.choice(string.ascii_letters + string.digits) for i in range(16)
        )

        smf.printd(f"Create a database user", config.DB_USER, level="INFO")
        # Ignore error jika role sudah ada
        self._run_cmd(
            [
                self.createuser,
                "-p",
                config.DB_PORT,
                "-h",
                config.DB_HOST,
                "-s",
                config.DB_USER,
            ],
            check=False,
        )

        smf.printd(f"Configuring password", config.DB_USER, level="INFO")
        sql = f"ALTER USER {config.DB_USER} WITH ENCRYPTED PASSWORD '{password}';"
        self._run_cmd(
            [self.psql, "-p", config.DB_PORT, "-h", config.DB_HOST, "-c", sql, "postgres"]
        )

        smf.printd(f"Creating a database", config.DB_NAME, level="INFO")
        self._run_cmd(
            [
                self.createdb,
                "-p",
                config.DB_PORT,
                "-h",
                config.DB_HOST,
                "-O",
                config.DB_USER,
                config.DB_NAME,
            ],
            check=False,
        )

        return password

    def generate_config(self, password):
        """Building the database.yml file."""
        smf.printd(f"Writing configuration", config.CONFIG_FILE, level="INFO")

        # Format yaml standar (Production environment)
        yaml_content = f"""production:
  adapter: postgresql
  database: {config.DB_NAME}
  username: {config.DB_USER}
  password: {password}
  host: {config.DB_HOST}
  port: {config.DB_PORT}
  pool: {config.DB_POOL}
  timeout: 5
"""
        config.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(config.CONFIG_FILE, "w") as f:
            f.write(yaml_content)

        # Set permission (Restrictive 600 untuk security)
        config.CONFIG_FILE.chmod(0o600)
        smf.printd("Database.yml configuration successfully created", level="INFO")
