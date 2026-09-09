import smf

from queue import Queue
from threading import Thread
from ..postgresql import report_service, report_vuln, report_host, get_current_workspace

# Queue Thread-Safe di Memori
ingest_queue = Queue()


def _db_worker():
    while True:
        item = ingest_queue.get()
        if item is None:
            break

        try:
            payload, workspace = item
            record_type = payload.get("type")

            # Worker cuma bertugas router ke db_api
            if record_type == "service":
                report_service(
                    address=payload["address"],
                    port=payload["port"],
                    proto=payload.get("proto", "tcp"),
                    workspace_name=workspace,
                    name=payload.get("name"),
                    state=payload.get("state"),
                    info=payload.get("info"),
                )

            elif record_type == "host":
                report_host(
                    address=payload["address"],
                    workspace_name=workspace,
                    os_name=payload.get("os_name"),
                    info=payload.get("info"),
                )

            elif record_type == "vuln":
                report_vuln(
                    address=payload["address"],
                    name=payload["name"],
                    workspace_name=workspace,
                    port=payload.get("port"),
                    proto=payload.get("proto"),
                    info=payload.get("info"),
                )

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
        ingest_queue.put_nowait((raw_res, workspace))
    except Exception:
        pass  # Jika queue penuh, drop silently
