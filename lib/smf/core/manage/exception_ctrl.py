import threading
import queue
import smf
from typing import List
from lib.smf.exception import (
    CRSRuntimeError,
    CRSException,
    CRSBrokenError,
    CRSKeyboardInterrupt,
    SocketConnectionRefused,
    SocketTimeout,
    SocketValueError,
    SocketError,
)


class ExceptionManager:
    # Mapping table: O(1) Lookup
    EXCEPTION_MAP = {
        "CRITICAL": lambda status, msg: CRSRuntimeError(status, msg),
        "BROKEN": lambda status, msg: CRSBrokenError(status, msg),
        "ERROR": lambda status, msg: CRSException(status, msg),
        "INTER": lambda status, msg: CRSKeyboardInterrupt(status, msg),
        "S-ALERT": lambda _, msg: SocketConnectionRefused(msg),
        "S-TIMEOUT": lambda _, msg: SocketTimeout(msg),
        "S-ERROR": lambda _, msg: SocketError(msg),
        "S-WARN": lambda _, msg: SocketValueError(msg),
        # --> Later if it increases.
    }
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

                if _status not in cls.EXCEPTION_MAP.get(_status):
                    continue

                smf.printd(
                    "Target Alert Captured",
                    f"Msg ID {_msg_id} | Status: {_status} | Msg: {_message}",
                    level="WARN",
                )

                # Define exceptions by status
                # O(1) Exception Dispatcher
                exc_factory = cls.EXCEPTION_MAP.get(_status)
                exc_to_raise = exc_factory(_status, _message) if exc_factory else None

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
