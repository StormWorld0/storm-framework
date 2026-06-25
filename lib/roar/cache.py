# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import os
import sqlite3
import ast
import json
import smf

from typing import List, Set, Tuple, Dict
from rootmap import ROOT


class StormSmartCache:
    def __init__(self):
        self.db_path = os.path.join(ROOT, "lib", "sqlite", "cached", "cache.db")
        self.modules_dir = os.path.join(ROOT, "modules")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        smf.printd(f"Initializing StormSmartCache at {self.db_path}", level="INFO")

        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.cursor = self.conn.cursor()

            self.cursor.execute("PRAGMA journal_mode=WAL;")
            self.cursor.execute("PRAGMA synchronous=NORMAL;")
            self._init_db()
        except Exception as e:
            smf.printd(
                "Failed to connect or configure SQLite database", e, level="CRITICAL"
            )
            raise

    def _init_db(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS module_cache (
                    path TEXT PRIMARY KEY,
                    mtime REAL,
                    category TEXT,
                    module_name TEXT,
                    module_path TEXT,
                    description TEXT,
                    author TEXT,
                    actions TEXT,
                    default_action TEXT,
                    cve TEXT,
                    saverity TEXT
                )
            """)
            self.cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_category ON module_cache(category)"
            )
            self.cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_module_path ON module_cache(module_path)"
            )
            self.cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_module_name ON module_cache(module_name)"
            )
            self.cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_description ON module_cache(description)"
            )
            self.cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_author ON module_cache(author)"
            )
            self.cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_actions ON module_cache(actions)"
            )
            self.cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_default_action ON module_cache(default_action)"
            )
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_cve ON module_cache(cve)")
            self.cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_saverity ON module_cache(saverity)"
            )
            self.conn.commit()
        except Exception as e:
            smf.printd("Failed to initialize database schema", e, level="CRITICAL")
            raise

    def _extract_metadata(self, file_path: str) -> dict:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source_code = f.read()

            tree = ast.parse(source_code, filename=file_path)

            for node in tree.body:
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == "metadata":
                            if isinstance(node.value, ast.Dict):
                                return ast.literal_eval(node.value)

                            smf.printd(
                                f"metadata in {file_path} is not a literal dict",
                                level="WARNING",
                            )
                            return {}

            return {}

        except Exception as e:
            smf.printd(f"Extract metadata failed: {file_path}", e, level="ERROR")
            return {}

    def _fast_scan(
        self,
        directory: str,
        db_state: Dict[str, float],
        current_disk_files: Set[str],
        to_upsert: List[Tuple],
    ):
        try:
            with os.scandir(directory) as it:
                for entry in it:
                    if entry.is_dir(follow_symlinks=False):
                        self._fast_scan(
                            entry.path, db_state, current_disk_files, to_upsert
                        )
                    elif entry.is_file(follow_symlinks=False):
                        if entry.name.endswith(".py") and entry.name != "__init__.py":
                            full_path = entry.path
                            current_disk_files.add(full_path)
                            mtime = entry.stat().st_mtime

                            if full_path not in db_state or db_state[full_path] != mtime:
                                rel_path = os.path.relpath(full_path, self.modules_dir)
                                module_path = rel_path.replace(os.sep, "/").replace(
                                    ".py", ""
                                )
                                module_name = entry.name.replace(".py", "")
                                category = (
                                    module_path.split("/")[0]
                                    if "/" in module_path
                                    else module_path
                                )

                                meta = self._extract_metadata(full_path)

                                if not meta:
                                    continue

                                raw_desc = meta.get("Description", "")
                                clean_desc = " ".join(raw_desc.split())

                                author_json = json.dumps(meta.get("Author", []))
                                actions_json = json.dumps(meta.get("Action", []))
                                def_action = str(meta.get("DefaultAction", ""))

                                vuln = meta.get("Vulnerability") or {}
                                cve = vuln.get("CVE", "")
                                severity = vuln.get("Severity", "")

                                to_upsert.append(
                                    (
                                        full_path,
                                        mtime,
                                        category,
                                        module_name,
                                        module_path,
                                        clean_desc,
                                        author_json,
                                        actions_json,
                                        def_action,
                                        cve,
                                        saverity
                                    )
                                )
        except Exception as e:
            smf.printd(f"Error scanning directory: {directory}", e, level="ERROR")

    def sync_modules(self) -> None:
        smf.printd("Starting module synchronization routine", level="INFO")
        try:
            self.cursor.execute("SELECT path, mtime FROM module_cache")
            db_state = {row[0]: row[1] for row in self.cursor.fetchall()}
            current_disk_files: Set[str] = set()
            to_upsert: List[Tuple] = []

            self._fast_scan(self.modules_dir, db_state, current_disk_files, to_upsert)
            deleted_files = set(db_state.keys()) - current_disk_files

            if to_upsert or deleted_files:
                with self.conn:
                    if to_upsert:
                        self.cursor.executemany(
                            """
                            INSERT OR REPLACE INTO module_cache 
                            (path, mtime, category, module_name, module_path, description, author, actions, default_action, cve, saverity) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                            to_upsert,
                        )
                    if deleted_files:
                        delete_payload = [(path,) for path in deleted_files]
                        self.cursor.executemany(
                            "DELETE FROM module_cache WHERE path = ?", delete_payload
                        )
            else:
                smf.printd("No drift detected. Sync skipped.", level="INFO")
        except Exception as e:
            smf.printd("Fatal error during sync", e, level="CRITICAL")
            raise


# Global register untuk sync saat booting
cache_modules = StormSmartCache()
