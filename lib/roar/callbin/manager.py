# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import os
import sqlite3
from pathlib import Path
from typing import Optional

import smf
from rootmap import ROOT

_BASE_DIR = Path(ROOT).resolve()
_DB_PATH = _BASE_DIR / "lib" / "sqlite" / "cached" / "cache.db"
_VALID_EXTENSIONS = {".so", ".dll", ".dylib", ".exe", ".bin", ".pyd"}


def _get_db_connection() -> sqlite3.Connection:
    if not _DB_PATH.parent.exists():
        _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        smf.printd(
            f"The cache.db directory is created on", _DB_PATH.parent, level="INFO"
        )

    conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")

    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS db_bin (
                filename TEXT PRIMARY KEY,
                stem TEXT NOT NULL,
                path TEXT NOT NULL,
                category TEXT,
                last_mtime REAL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_bin_filename ON db_bin(filename)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_bin_stem ON db_bin(stem)")
    except sqlite3.Error as e:
        smf.printd("Failed to initialize SQLite cache schema", e, level="CRITICAL")
        raise

    return conn


def sync_bin() -> None:
    smf.printd("Starting binary cache synchronization scan...", level="INFO")
    search_targets = {
        "module": _BASE_DIR / "external" / "source" / "out" / "modules",
        "core": _BASE_DIR / "external" / "source" / "out" / "core",
    }

    found_on_disk = {}

    for cat, folder in search_targets.items():
        if not folder.exists():
            smf.printd(f"Target directory not found and skipped", folder, level="WARN")
            continue

        # Scan recursive
        for entry in folder.rglob("*"):
            if not entry.is_file():
                continue

            # Taking the very end extension
            suffix = entry.suffix.lower()
            is_valid = suffix in _VALID_EXTENSIONS
            is_linux = (suffix == "") and os.access(entry, os.X_OK)

            if is_valid or is_linux:
                # Dealing with multi-dot suffixes (example: 'lib.abi3.so' -> 'lib')
                # This ensures that 'stem' is actually the base name of the binary
                base_name = entry.name.split(".")[0]

                found_on_disk[entry.name] = {
                    "stem": base_name,
                    "path": str(entry.absolute()),
                    "category": cat,
                    "mtime": entry.stat().st_mtime,
                }
                smf.printd(f"Binary extracted: {entry.name}", cat, level="DEBUG")

    try:
        with _get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT filename FROM db_bin")
            cached_names = {row[0] for row in cursor.fetchall()}

            removed = [(name,) for name in cached_names if name not in found_on_disk]
            if removed:
                cursor.executemany("DELETE FROM db_bin WHERE filename = ?", removed)
                smf.printd(
                    f"Cleaned {len(removed)} binaries no longer in cache.", level="INFO"
                )

            updated_count = 0
            for filename, data in found_on_disk.items():
                cursor.execute(
                    """
                    INSERT INTO db_bin (filename, stem, path, category, last_mtime)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(filename) DO UPDATE SET
                        stem = excluded.stem,
                        path = excluded.path,
                        category = excluded.category,
                        last_mtime = excluded.last_mtime
                    WHERE last_mtime != excluded.last_mtime
                """,
                    (
                        filename,
                        data["stem"],
                        data["path"],
                        data["category"],
                        data["mtime"],
                    ),
                )

                if cursor.rowcount > 0:
                    updated_count += 1

            conn.commit()
            smf.printd(
                f"DB sync complete. Total: {len(found_on_disk)}, Updated/Inserted: {updated_count}",
                level="INFO",
            )

    except sqlite3.Error as e:
        smf.printd("I/O error during DB sync transaction.", e, level="ERROR")
        raise


def _query_db(query_column: str, query_value: str) -> Optional[str]:
    try:
        with _get_db_connection() as conn:
            cursor = conn.cursor()
            # Column validation to prevent SQL Injection
            if query_column not in ("filename", "stem"):
                raise ValueError("Invalid query column")

            cursor.execute(
                f"SELECT path FROM db_bin WHERE {query_column} = ?",
                (query_value,),
            )
            row = cursor.fetchone()
            return row[0] if row else None
    except sqlite3.Error as e:
        smf.printd(f"DB error looking up {query_value}", e, level="CRITICAL")
        raise
