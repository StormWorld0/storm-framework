# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author: zxelzy

import threading
import queue
import time
import smf
from typing import Generator, Dict, Any, List, Callable

# Mengimpor custom exceptions dari modul modular terpisah milikmu
from .exceptions import (
    CRSRuntimeError,
    CRSException,
    CRSBrokenError,
    CRSKeybordInterrupt,
    CRSConnectionRefused,
)


class ExceptionManager:
    # Shared state di level class dengan thread-safe lock & storage
    _lock: threading.Lock = threading.Lock()
    _alert_logs: List[Dict[str, Any]] = []

    # Target status yang wajib dianalisis (selain ini akan langsung di-drop)
    TARGET_STATUSES = {"ERROR", "CRITICAL", "BROKEN", "INTER", "ALERT"}

    @classmethod
    def _worker(cls, data_queue: queue.Queue) -> None:
        """Consumer worker yang memproses data dari queue secara asynchronous & concurrent."""
        while True:
            try:
                # Mengambil data dari queue dengan timeout kecil agar worker bisa berhenti bersih
                raw_response = data_queue.get(timeout=0.1)
            except queue.Empty:
                break

            try:
                _status: str = raw_response.get("status", "UNKNOWN").upper()
                _message: str = raw_response.get("message", "UNKNOWN")
                _msg_id: str = raw_response.get("msg_id", "UNKNOWN")

                # --- FILTERING & DROPPING LOGIC ---
                if _status not in cls.TARGET_STATUSES:
                    continue  # Drop data

                # Catat log secara thread-safe
                with cls._lock:
                    log_entry = {
                        "msg_id": _msg_id,
                        "status": _status,
                        "message": _message,
                        "timestamp": time.time(),
                    }
                    cls._alert_logs.append(log_entry)

                smf.printd(
                    "Target Alert Captured",
                    f"Msg ID {_msg_id} | Status: {_status} | Msg: {_message}",
                    level="WARN",
                )

                # Mapping exception sesuai status
                if _status == "CRITICAL":
                    raise CRSRuntimeError(_status, _message)
                elif _status == "BROKEN":
                    raise CRSBrokenError(_status, _message)
                elif _status == "INTER":
                    raise CRSKeybordInterrupt(_status, _message)
                elif _status == "ERROR":
                    raise CRSException(_status, _message)
                elif _status == "ALERT":
                    raise CRSConnectionRefused(_status, _message)

            except Exception as e:
                smf.printd("Unexpected parsing error", e, level="ERROR")
            finally:
                data_queue.task_done()

    @classmethod
    def process_exc(
        cls,
        data: Callable[[], Generator[Dict[str, Any], None, None]],
    ) -> List[Dict[str, Any]]:
        """Fungsi utama"""
        # Bersihkan log sebelumnya
        with cls._lock:
            cls._alert_logs.clear()

        data_queue = queue.Queue(maxsize=10000)

        # Producer Thread: Memasukkan stream data ke dalam queue secara efisien
        def producer():
            for raw_response in data():
                if isinstance(raw_response, dict):
                    data_queue.put(raw_response)

        producer_thread = threading.Thread(
            target=producer, name="Data-Producer", daemon=True
        )
        producer_thread.start()

        # Consumer Worker Pool
        w = threading.Thread(
            target=cls._worker, args=(data_queue,), name=f"StreamWorker-Exception"
        )
        w.start()

        producer_thread.join()
        data_queue.join()

        with cls._lock:
            return list(cls._alert_logs)
