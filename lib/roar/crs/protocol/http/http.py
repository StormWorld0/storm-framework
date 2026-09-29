# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author zxelzy
import smf

from typing import Dict

from apps.utility.colors import CC
from lib.smf.ingest import push_to_queue

from ...transport import CRS
from .response import HTTPResponse


class HTTPState:
    """Manajemen Konfigurasi & State Sesi."""

    def __init__(
        self,
        method: str = "GET",
        url: str = "",
        headers: dict = None,
        body: str = "",
        redirect: bool = True,
        rawhttp: bool = False,
        tls: bool = False,
        verify: bool = True,
        retry: int = 2,
        timeout: float = 5.0,
        rlimit: int = 150,
        frate: int = 10,
        con: int = 50,
        **kwargs,
    ):
        self._method = method.upper()
        self._url = url
        self._headers = headers
        self._body = body
        self._redirect = redirect
        self._rawhttp = rawhttp
        self._tls = tls
        self._verify = verify
        self._retry = retry
        self._timeout = timeout
        self._ratelimit = rlimit
        self.fixed_ratelimit = frate
        self.goroutine = con

        if kwargs:
            smf.printf(
                f"[!] {CC.YELLOW}Unrecognized parameters dropped =>{CC.RESET}", kwargs
            )

        self.rawhttp = RawHttp(state=self)

    def _reset(self):
        """Reset state instance ini kembali ke default"""
        super().__init__()
        return self


class IPCPayloadBuilder:
    """Data Marshalling & Data Transformation."""

    @staticmethod
    def build(state: HTTPState) -> Dict:

        return {
            "primitive": "HTTP_SEND",
            "goroutine": state.goroutine,
            "method": state.method,
            "url": state.url,
            "headers": state.headers or {},
            "body": state.body,
            "redirect": state.redirect,
            "rawmode": state.rawhttp,
            "info_tls": state.tls,
            "verify": state.verify,
            "retry": state.retry,
            "ratelimit": state.ratelimit,
            "frate": state.frate,
            "timeout": state.timeout,
        }


class HTTPClient(HTTPState):
    """Namespace OOP untuk operasi HTTP"""

    def requests(self, method: str, url: str, **kwargs):
        """"""
        if not isinstance(url, str):
            raise TypeError("URL must be a string")
        
        self._method = method
        self._url = url
        return self

    def concurrency(self, con: int, **kwargs):
        """"""
        self.goroutine = con
        return self

    def setlimit(self, ratelimit: int, frate: int, **kwargs):
        """"""
        self.ratelimit = ratelimit
        self.frate = frate
        return self

    def timeout(self, value: float, **kwargs):
        """"""
        if not isinstance(value, float):
            raise TypeError("value must be a float")
            
        self._timeout = value
        return self

    def run(self, **kwargs) -> HTTPResponse:
        """Running HTTP Requests"""
        packet = IPCPayloadBuilder.build(state=self)

        raw_res = CRS.send(packet)
        res = HTTPResponse(raw_res)
        res._trace()

        try:
            db_payload = res._to_db_payload(self._method, self._url, self._tls)
            push_to_queue(db_payload)
        except Exception as e:
            smf.printd("Failed to push HTTP payload to queue", e, level="ERROR")
        return res
