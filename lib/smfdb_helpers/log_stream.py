import sqlite3
import datetime
import smf

from contextlib import closing
from pathlib import Path
from rootmap import ROOT
from apps.utility.colors import *

def dump_log():
    """
    Dump logs from internal SQLite database.
    """
    db_dir = Path(ROOT) / "lib" / "sqlite" / "logging"
    db_path = db_dir / "log.db"

    if not db_path.exists():
        smf.printd("Database not found", db_path, level="WARN")
        return

    try:
        # Pendekatan yang lebih efisien untuk mendapatkan awal hari ini (epoch)
        today_start = datetime.datetime.combine(
            datetime.date.today(), datetime.time.min
        ).timestamp()
        
        uri_path = f"file:{db_path.absolute()}?mode=ro"

        # 1. Gunakan contextlib.closing untuk menjamin koneksi SQLite benar-benar ditutup (conn.close())
        # 2. Tambahkan timeout=10.0 agar reader mau menunggu hingga 10 detik jika ada proses writing yang sedang berjalan
        with closing(sqlite3.connect(uri_path, uri=True, timeout=10.0)) as conn:
            cursor = conn.cursor()

            query = """
                SELECT timestamp, level, label, payload, traceback, caller_info 
                FROM system_logs 
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT 100;
            """

            # 3. Fetch data secepat mungkin dan tampung di RAM (batasan LIMIT 100 membuat memori sangat aman).
            #    Langkah ini segera melepaskan Shared Lock pada SQLite.
            cursor.execute(query, (today_start,))
            rows = cursor.fetchall()

        # 4. Operasi I/O (print terminal) yang memakan waktu dilakukan DI LUAR koneksi database.
        for row in rows:
            ts, lvl, label, payload, traceback, caller = row

            dt_str = datetime.datetime.fromtimestamp(ts).strftime(
                "%Y-%m-%d %H:%M:%S.%f"
            )[:-3]

            smf.printf(f"{CC.MAGENTA}-{CC.RESET}" * 60)
            smf.printf(f"[{CC.CYAN}{dt_str}{CC.RESET}] [{lvl}]")
            smf.printf(f"{CC.CYAN} CALLER {CC.RESET} : {CC.YELLOW}{caller}{CC.RESET}")
            smf.printf(f"{CC.CYAN} LABEL {CC.RESET}  : {CC.YELLOW}{label}{CC.RESET}")

            if payload:
                smf.printf(f"{CC.CYAN} PAYLOAD {CC.RESET}: {CC.YELLOW}{payload}{CC.YELLOW}")

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
