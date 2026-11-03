import os
import smf
import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any
from rootmap import ROOT
from lib.smf.exception import SMFDatabaseError, SMFConfigDatabaseError


class BinaryManager:
    def __init__(self):
        self._BASE_DIR = Path(ROOT).resolve()
        self._DB_PATH = self._BASE_DIR / "lib" / "sqlite" / "cached" / "cache.db"
        self.bin_dirs = {
            "module": self._BASE_DIR / "external" / "source" / "out" / "modules",
            "core": self._BASE_DIR / "external" / "source" / "out" / "core",
        }
        self._VALID_EXTENSIONS = {".so", ".dll", ".dylib", ".exe", ".bin", ".pyd"}

        self._DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        try:
            # check_same_thread=False aman asal query dijalankan terisolasi per method/cursor lokal
            self.conn = sqlite3.connect(self._DB_PATH, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row

            # Konfigurasi pragmas untuk performa tinggi (WAL mode)
            cursor = self.conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("PRAGMA synchronous=NORMAL;")
            cursor.close()

            self._init_db()
        except Exception as e:
            smf.printd("Failed to connect or configure SQLite database", e, level="ERROR")
            raise SMFConfigDatabaseError(
                "Failed to connect or configure SQLite Database.", e
            )

    def _init_db(self):
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS binary (
                        filename TEXT PRIMARY KEY,
                        stem TEXT NOT NULL,
                        path TEXT NOT NULL,
                        category TEXT,
                        mtime REAL
                    )
                """)
                # Primary Key sudah otomatis mengindeks filename, hapus idx_filename yang redundan
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_path ON binary(path)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_stem ON binary(stem)")
        except sqlite3.Error as e:
            smf.printd("Failed to initialize SQLite cache schema", e, level="CRITICAL")
            raise SMFConfigDatabaseError(
                "Failed to initialize SQLite cache schema."
            ) from e

    def _fast_scan(
        self, folder: Path, current_disk_files: Dict[str, Dict[str, Any]], category: str
    ):
        """Helper rekursif/iteratif untuk memindai direktori binary secara efisien."""
        if not folder.exists() or not folder.is_dir():
            return

        try:
            with os.scandir(folder) as it:
                for entry in it:
                    if entry.is_dir(follow_symlinks=False):
                        self._fast_scan(Path(entry.path), current_disk_files, category)
                    elif entry.is_file(follow_symlinks=False):
                        entry_path = Path(entry.path)
                        suffix = entry_path.suffix.lower()
                        is_valid = suffix in self._VALID_EXTENSIONS
                        is_linux_binary = (suffix == "") and os.access(
                            entry_path, os.X_OK
                        )

                        if is_valid or is_linux_binary:
                            base_name = entry_path.name.split(".")[0]
                            try:
                                st_mtime = entry_path.stat().st_mtime
                            except OSError:
                                continue

                            current_disk_files[entry_path.name] = {
                                "stem": base_name,
                                "path": str(entry_path.absolute()),
                                "category": category,
                                "mtime": st_mtime,
                            }
                            smf.printd(
                                f"Binary extracted: {entry_path.name}",
                                category,
                                level="DEBUG",
                            )
        except Exception as e:
            smf.printd(f"Error scanning directory: {folder}", e, level="ERROR")

    def sync_bin(self) -> Optional[bool]:
        smf.printd("Starting binary cache synchronization scan...", level="INFO")
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT filename FROM binary")
            db_state = {row[0] for row in cursor.fetchall()}

            current_disk_files: Dict[str, Dict[str, Any]] = {}
            for category, folder_path in self.bin_dirs.items():
                self._fast_scan(folder_path, current_disk_files, category)

            deleted_files = db_state - set(current_disk_files.keys())
            if current_disk_files or deleted_files:
                with self.conn:
                    tx_cursor = self.conn.cursor()
                    updated_count = 0

                    if current_disk_files:
                        # Batching menggunakan executemany untuk performa optimal
                        payloads = [
                            (
                                filename,
                                data["stem"],
                                data["path"],
                                data["category"],
                                data["mtime"],
                            )
                            for filename, data in current_disk_files.items()
                        ]

                        tx_cursor.executemany(
                            """
                            INSERT INTO binary (filename, stem, path, category, mtime)
                            VALUES (?, ?, ?, ?, ?)
                            ON CONFLICT(filename) DO UPDATE SET
                                stem = excluded.stem,
                                path = excluded.path,
                                category = excluded.category,
                                mtime = excluded.mtime
                            WHERE mtime != excluded.mtime
                            """,
                            payloads,
                        )
                        # Hitung rowcount jika driver mendukung, atau asumsikan sukses sinkronisasi batch
                        updated_count = len(payloads)

                    if deleted_files:
                        removed = [(name,) for name in deleted_files]
                        tx_cursor.executemany(
                            "DELETE FROM binary WHERE filename = ?", removed
                        )
                        smf.printd(
                            f"Cleaned {len(removed)} binaries no longer in cache.",
                            level="INFO",
                        )

                    smf.printd(
                        f"DB sync complete. Total scanned: {len(current_disk_files)}, Processed: {updated_count}",
                        level="INFO",
                    )
            else:
                smf.printd("No drift detected. Sync skipped.", level="INFO")

            return True
        except Exception as e:
            smf.printd("Fatal error during sync", e, level="ERROR")
            return None

    def query_db(self, column: str, value: str) -> Optional[str]:
        try:
            if column not in ("filename", "stem"):
                raise ValueError("Invalid query column")

            cursor = self.conn.cursor()
            # Parameterized query aman dari SQL Injection
            cursor.execute(
                f"SELECT path FROM binary WHERE {column} = ?",
                (value,),
            )
            row = cursor.fetchone()
            cursor.close()
            return row["path"] if row else None
        except sqlite3.Error as e:
            smf.printd(f"DB error looking up {value}", e, level="ERROR")
            raise SMFDatabaseError(f"Database error locking up {value}") from e
