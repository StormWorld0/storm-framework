import smf

from queue import Queue
from threading import Thread
from ..postgresql import ingest_telemetry, get_current_workspace

# Queue Thread-Safe di Memori
ingest_queue = Queue()


def _db_worker():
    while True:
        item = ingest_queue.get()
        if item is None:
            break
        smf.printd(
            "Inspeksi Worker Item", f"Tipe: {type(item)} | Isi: {item}", level="DEBUG"
        )
        try:
            # Tarik workspace aktif di memori secara konstan
            active_ws = get_current_workspace()
            # Eksekusi ingest universal ke multi-tabel (Host, Service, Vuln, Note, dll)
            ingest_telemetry(item, active_ws)
        except Exception as e:
            smf.printd("DB Worker Ingest error", e, level="ERROR")
        finally:
            ingest_queue.task_done()


# Jalankan Worker Daemon Thread saat module di-import
worker_thread = Thread(target=_db_worker, daemon=True)
worker_thread.start()


def push_to_queue(data: dict):
    """Non-blocking function untuk melempar data ke queue memori."""
    ws = get_current_workspace()
    try:
        ingest_queue.put_nowait((data, ws))
    except Exception:
        pass  # Jika queue penuh, drop silently
