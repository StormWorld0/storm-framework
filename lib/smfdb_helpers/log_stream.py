import sqlite3
import datetime
import smf

from pathlib import Path
from rootmap import ROOT
from apps.utility.colors import *


def dump_log():
    """
    Dump logs from internal SQLite database.
    """

    # Path to database location
    db_dir = Path(ROOT) / "lib" / "sqlite" / "logging"
    db_path = db_dir / "log.db"

    # Database validation
    if not db_path.exists():
        smf.printd("Database not found", db_path, level="WARN")
        return

    try:
        # Use mode=ro for better stability
        uri_path = f"file:{db_path.absolute()}?mode=ro"

        # Set up database connection
        with sqlite3.connect(uri_path, uri=True) as conn:
            cursor = conn.cursor()

            # Performing database queries
            query = """
                SELECT timestamp, level, label, payload, traceback, caller_info 
                FROM system_logs 
                ORDER BY timestamp DESC
            """

            # Execution and iteration on cursor
            for row in cursor.execute(query):
                ts, lvl, label, payload, traceback, caller = row

                # Convert f64 Unix Epoch to Date Format
                dt_str = datetime.datetime.fromtimestamp(ts).strftime(
                    "%Y-%m-%d %H:%M:%S.%f"
                )[:-3]

                # Neat writing format
                smf.printf(f"[{dt_str}] [{lvl}]\n")
                smf.printf(f" CALLER  : {caller}\n")
                smf.printf(f" LABEL   : {label}\n")

                # Show if any
                if payload:
                    smf.printf(f" PAYLOAD : {payload}\n")

                # Show if any
                if traceback:
                    smf.printf(f"\n{CC.RED} TRACEBACK:{CC.RESET}\n")
                    for line in traceback.split("\n"):
                        smf.printf(f"{CC.RED}     {line}{CC.RESET}\n")

    except sqlite3.Error as e:
        smf.printf(f"[-]{CC.RED} A Database Log I/O error occurred{CC.RESET}")
        smf.printd("A Database Log I/O error occurred", e, level="ERROR")
    except Exception as e:
        smf.printf(f"[-]{CC.RED} Dump failure occurred{CC.RESET}")
        smf.printd("Dump failure occurred", e, level="ERROR")
