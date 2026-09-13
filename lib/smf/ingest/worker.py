import smf

from queue import Queue
from threading import Thread
from ..postgresql import ingest_telemetry, get_current_workspace

# Queue Thread-Safe di Memori
ingest_queue = Queue(maxsize=10000)


def _db_worker():
    while True:
        item = ingest_queue.get()
        if item is None:
            break
        try:
            data_dict, active_ws = item
            # Eksekusi ingest universal ke multi-tabel
            ingest_telemetry(data_dict, active_ws)
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
