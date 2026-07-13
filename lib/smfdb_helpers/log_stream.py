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
        time_log = datetime.datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        today = time_log.timestamp()
        # Use mode=ro for better stability
        uri_path = f"file:{db_path.absolute()}?mode=ro"

        # Set up database connection
        with sqlite3.connect(uri_path, uri=True) as conn:
            cursor = conn.cursor()

            # Performing database queries
            query = """
                SELECT timestamp, level, label, payload, traceback, caller_info 
                FROM system_logs 
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT 100;
            """

            # Execution and iteration on cursor
            for row in cursor.execute(query, (today,)):
                ts, lvl, label, payload, traceback, caller = row

                # Convert f64 Unix Epoch to Date Format
                dt_str = datetime.datetime.fromtimestamp(ts).strftime(
                    "%Y-%m-%d %H:%M:%S.%f"
                )[:-3]

                # Neat writing format
                smf.printf(f"{CC.MAGENTA}-{CC.RESET}" * 60)
                smf.printf(f"[{CC.CYAN}{dt_str}{CC.RESET}] [{lvl}]")
                smf.printf(f"{CC.CYAN} CALLER {CC.RESET} : {CC.YELLOW}{caller}{CC.RESET}")
                smf.printf(f"{CC.CYAN} LABEL {CC.RESET}  : {CC.YELLOW}{label}{CC.RESET}")

                # Show if any
                if payload:
                    smf.printf(
                        f"{CC.CYAN} PAYLOAD {CC.RESET}: {CC.YELLOW}{payload}{CC.YELLOW}"
                    )

                # Show if any
                if traceback:
                    smf.printf(f"\n{CC.CYAN} TRACEBACK:{CC.RESET}")
                    for line in traceback.split("\n"):
                        smf.printf(f"{CC.RED}     {line}{CC.RESET}")
                smf.printf(f"{CC.MAGENTA}-{CC.RESET}" * 60 + "\n")

    except sqlite3.Error as e:
        smf.printf(f"[-]{CC.RED} A Database Log I/O error occurred{CC.RESET}")
        smf.printd("A Database Log I/O error occurred", e, level="ERROR")
    except Exception as e:
        smf.printf(f"[-]{CC.RED} Dump failure occurred{CC.RESET}")
        smf.printd("Dump failure occurred", e, level="ERROR")
