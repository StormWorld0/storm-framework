import threading
import queue
import smf
from typing import List
from lib.smf.exception import (
    CRSRuntimeError,
    CRSException,
    CRSBrokenError,
    CRSKeybordInterrupt,
    CRSConnectionRefused,
)


class ExceptionManager:
    TARGET_STATUSES = {"ERROR", "CRITICAL", "BROKEN", "INTER", "ALERT"}
    _error_holder: List[Exception] = []
    _local_lock = threading.Lock()
    _data_queue = queue.Queue(maxsize=10000)

    @classmethod
    def _worker(cls) -> None:
        """Consumer worker that processes data from the queue asynchronously."""
        while True:
            try:
                resp = cls._data_queue.get()
                if resp is None:
                    break

                _status: str = resp.get("status", "UNKNOWN")
                _message: str = resp.get("message", "UNKNOWN")
                _msg_id: str = resp.get("msg_id", "UNKNOWN")

                if _status not in cls.TARGET_STATUSES:
                    continue

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
                    with cls._local_lock:
                        if not cls._error_holder:
                            cls._error_holder.append(exc_to_raise)

            except Exception as e:
                smf.printd("Unexpected parsing error in worker", e, level="ERROR")
            finally:
                cls._data_queue.task_done()

    @classmethod
    def process_exc(cls, data: dict) -> None:
        """Main functions with Queue-Worker architecture"""

        # Producer Thread: Puts stream data into queue
        try:
            for v in data:
                if isinstance(v, dict):
                    cls._data_queue.put_nowait(v)
        except Exception:
            pass

        with cls._local_lock:
            if cls._error_holder:
                err = cls._error_holder.pop(0)
                raise err


# Consumer Worker Thread
worker_thread = threading.Thread(target=ExceptionManager._worker, daemon=True)
worker_thread.start()
