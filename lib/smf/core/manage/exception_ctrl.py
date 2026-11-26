from lib.smf.telemetry import trace_ms
from typing import Any, Iterable, Mapping
from lib.smf.exception import (
    CRSBrokenError,
    CRSException,
    CRSKeyboardInterrupt,
    CRSRuntimeError,
    HttpError,
    HttpTimeout,
    SocketConnectionRefused,
    SocketError,
    SocketTimeout,
    SocketValueError,
)


class ExceptionGate:
    __slots__ = ()

    EXCEPTION_CLASSES: dict[str, type[Exception]] = {
        "CRITICAL": CRSRuntimeError,
        "BROKEN": CRSBrokenError,
        "ERROR": CRSException,
        "INTER": CRSKeyboardInterrupt,
        "S-ALERT": SocketConnectionRefused,
        "S-TIMEOUT": SocketTimeout,
        "S-ERROR": SocketError,
        "S-WARN": SocketValueError,
        "H-TIMEOUT": HttpTimeout,
        "H-ERROR": HttpError,
    }

    TWO_ARG_STATUSES: frozenset[str] = frozenset({"CRITICAL", "BROKEN", "ERROR", "INTER"})

    @classmethod
    def gate_item(cls, item: Mapping[str, Any]) -> None:
        status = item.get("status")
        if status is None:
            return

        exc_cls = cls.EXCEPTION_CLASSES.get(status)  # type: ignore[arg-type]
        if exc_cls is None:
            return

        message = item.get("message", "UNKNOWN")
        msg_id = item.get("msg_id", "UNKNOWN")

        if status in cls.TWO_ARG_STATUSES:
            raise exc_cls(status, message)
        raise exc_cls(message)

    @classmethod
    def gate_stream(cls, stream: Iterable[Mapping[str, Any]]) -> None:
        gate_item = cls.gate_item
        for item in stream:
            if isinstance(item, Mapping):
                gate_item(item)
