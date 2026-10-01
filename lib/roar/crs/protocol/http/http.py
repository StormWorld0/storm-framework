# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author zxelzy
import smf

from lib.smf.ingest import push_to_queue

from .state_build import HTTPState, IPCPayloadBuilder
from .normal_http import HTTPMethod
from .response import HTTPResponse

from ...transport import CRS


class HTTPClient(HTTPState, HTTPMethod):
    """Namespace OOP untuk operasi HTTP (Hardened Engine)"""

    def setoptions(
        self,
        ca: str | None = None,
        retry: int | None = None,
        redirect: bool | None = None,
        verify: bool | None = None,
        tls: bool | None = None,
        **kwargs,
    ):
        """Saving Options values with strict type checking"""
        bool_opts = {"redirect": redirect, "verify": verify, "tls": tls}
        for k, v in bool_opts.items():
            if v is not None:
                if not isinstance(v, bool):
                    raise TypeError(
                        f"Option '{k}' must be a boolean, got {type(v).__name__}"
                    )
                setattr(self, f"_{k}", v)

        if retry is not None:
            if not isinstance(retry, int) or isinstance(retry, bool):
                raise TypeError(
                    f"Option 'retry' must be an integer, got {type(retry).__name__}"
                )
            if retry < 0 or retry > 100:
                raise ValueError("Option 'retry' must be between 0 and 100")
            self._retry = retry

        if ca is not None:
            if not isinstance(ca, str) or isinstance(ca, bool):
                raise TypeError(f"Option 'ca' must be string, got {type(ca).__name__}")
            self._TLSCA = ca

        return self

    def concurrency(self, con: int, **kwargs):
        """Storing Concurrency values (Strict Int & Bounds)"""
        if not isinstance(con, int) or isinstance(con, bool):
            raise TypeError(f"Concurrency must be an integer, got {type(con).__name__}")

        if con <= 0:
            raise ValueError("Concurrency must be greater than 0")

        self.goroutine = con
        return self

    def setlimit(self, ratelimit: int, frate: int | None = None, **kwargs):
        """Save ratelimiting value with type and bound checks"""
        limits = {"ratelimit": ratelimit, "fixed_ratelimit": frate}
        for k, v in limits.items():
            if v is not None:
                if not isinstance(v, int) or isinstance(v, bool):
                    raise TypeError(
                        f"Limit '{k}' must be an integer, got {type(v).__name__}"
                    )
                if v < 0:
                    raise ValueError(f"Limit '{k}' cannot be negative")

                setattr(self, f"_{k}", v)
        return self

    def timeout(self, value: float, **kwargs):
        """Timeout value settings (Coerces int to float safely)"""
        if isinstance(value, bool) or not isinstance(value, float):
            raise TypeError(f"Timeout must be a float or int, got {type(value).__name__}")

        v = float(value)
        if v <= 0:
            raise ValueError("Timeout must be greater than 0")

        self._timeout = v
        return self

    def _validate_state(self):
        """Pre-flight check"""
        if not getattr(self, "_url", None):
            raise ValueError("Cannot execute request: Target URL is missing or empty")
        if not getattr(self, "_method", None):
            raise ValueError("Cannot execute request: HTTP Method is not set")

    def run(self, **kwargs) -> HTTPResponse:
        """Running HTTP Requests with Pre-flight Guard"""
        self._validate_state()
        packet = IPCPayloadBuilder.build(state=self)

        raw_res = CRS.send(packet)
        res = HTTPResponse(raw_res)
        res._trace()

        try:
            db_payload = res._to_db_payload(
                self._method, self._url, getattr(self, "_tls", False)
            )
            push_to_queue(db_payload)
        except Exception as e:
            smf.printd("Failed to push HTTP payload to queue", e, level="ERROR")

        return res

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            smf.printd("Context failed with", exc_type, exc_val, exc_tb, level="WARN")
        self._reset()
        return False

    def __repr__(self):
        url = getattr(self, "_url", "UNSET")
        status = getattr(self, "status", "UNKNOWN")
        proto = getattr(self, "proto", "UNKNOWN")
        engine = getattr(self, "engine", "UNKNOWN")
        return (
            f"<HTTPR URL='{url}' Status='{status}' Protocol='{proto}' Engine='{engine}'>"
        )
