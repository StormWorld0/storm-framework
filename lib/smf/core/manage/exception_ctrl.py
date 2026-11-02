import threading
import queue
import time
import smf
from typing import Generator, Dict, Any, List, Callable

from lib.smf.exception import (
    CRSRuntimeError,
    CRSException,
    CRSBrokenError,
    CRSKeybordInterrupt,
    CRSConnectionRefused,
)


class ExceptionManager:
    TARGET_STATUSES = {"ERROR", "CRITICAL", "BROKEN", "INTER", "ALERT"}

    @classmethod
    def _worker(
        cls,
        data_queue: queue.Queue,
        error_holder: list,
        alert_logs: list,
        lock: threading.Lock,
    ) -> None:
        """Consumer worker that processes data from the queue asynchronously."""
        while True:
            try:
                raw_response = data_queue.get()
                if raw_response is None:
                    data_queue.task_done()
                    break

                _status: str = raw_response.get("status", "UNKNOWN").upper()
                _message: str = raw_response.get("message", "UNKNOWN")
                _msg_id: str = raw_response.get("msg_id", "UNKNOWN")

                if _status not in cls.TARGET_STATUSES:
                    data_queue.task_done()
                    continue

                with lock:
                    log_entry = {
                        "msg_id": _msg_id,
                        "status": _status,
                        "message": _message,
                        "timestamp": time.time(),
                    }
                    alert_logs.append(log_entry)

                smf.printd(
                    "Target Alert Captured",
                    f"Msg ID {_msg_id} | Status: {_status} | Msg: {_message}",
                    level="WARN",
                )

                # Define exceptions by status
                exc_to_raise = None
                if _status == "CRITICAL":
                    exc_to_raise = CRSRuntimeError(_status, _message)
                elif _status == "BROKEN":
                    exc_to_raise = CRSBrokenError(_status, _message)
                elif _status == "INTER":
                    exc_to_raise = CRSKeybordInterrupt(_status, _message)
                elif _status == "ERROR":
                    exc_to_raise = CRSException(_status, _message)
                elif _status == "ALERT":
                    exc_to_raise = CRSConnectionRefused(_status, _message)

                if exc_to_raise:
                    with lock:
                        if not error_holder:
                            error_holder.append(exc_to_raise)

            except Exception as e:
                smf.printd("Unexpected parsing error in worker", e, level="ERROR")
                data_queue.task_done()

    @classmethod
    def process_exc(
        cls,
        data: Callable[[], Generator[Dict[str, Any], None, None]],
    ) -> List[Dict[str, Any]]:
        """Main functions with Queue-Worker architecture"""
        alert_logs: List[Dict[str, Any]] = []
        error_holder: List[Exception] = []
        local_lock = threading.Lock()
        data_queue = queue.Queue(maxsize=10000)

        # Producer Thread: Puts stream data into queue
        def producer():
            try:
                for raw_response in data:
                    if isinstance(raw_response, dict):
                        data_queue.put(raw_response)
            finally:
                data_queue.put(None)

        producer_thread = threading.Thread(
            target=producer, name="Data-Producer", daemon=True
        )
        producer_thread.start()

        # Consumer Worker Thread
        worker_thread = threading.Thread(
            target=cls._worker,
            args=(data_queue, error_holder, alert_logs, local_lock),
            name="StreamWorker-Exception",
        )
        worker_thread.start()

        # Wait until the producer and worker have finished processing
        producer_thread.join()
        data_queue.join()
        worker_thread.join()
        if error_holder:
            raise error_holder[0]
        return alert_logs
