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
        rlimit: int = 150,
        frate: int = 10,
        timeout: float = 5.0,
        con: int = 50,
        **kwargs,
    ):
        self.method = method
        self.url = url
        self.headers = headers
        self.body = body
        self.redirect = redirect
        self.rawhttp = rawhttp
        self.tls = tls
        self.verify = verify
        self.ratelimit = rlimit
        self.fixed_ratelimit = frate
        self._timeout = timeout
        self.goroutine = con

        if kwargs:
            smf.printf(
                f"[!] {CC.YELLOW}Unrecognized parameters dropped =>{CC.RESET}", kwargs
            )

    def _reset(self):
        """Reset state instance ini kembali ke default"""
        super().__init__()
        return self


class IPCPayloadBuilder:
    """Data Marshalling & Data Transformation."""

    @staticmethod
    def build(
        self,
        method: str,
        url: str,
        headers: dict = None,
        body: str = "",
        redirect: bool = True,
        rawhttp: bool = False,
        tls: bool = False,
        verify: bool = True,
        retry: int = 2,
        rl: int = 150,
        frl: int = 10,
        timeout: float = 5.0,
        con: int = 50,
        **kwargs,
    ) -> Dict:

        return {
            "primitive": "HTTP_SEND",
            "goroutine": con,
            "method": method.upper(),
            "url": url,
            "headers": headers or {},
            "body": body,
            "redirect": redirect,
            "rawmode": rawhttp,
            "info_tls": tls,
            "verify": verify,
            "retry": retry,
            "ratelimit": rl,
            "frate": frl,
            "timeout": timeout,
        }


class HTTPClient(HTTPState):
    """Namespace OOP untuk operasi HTTP"""

    def run(self, **kwargs) -> HTTPResponse:
        """Running HTTP Requests"""
        packet = IPCPayloadBuilder.build(state=self)

        raw_res = CRS.send(packet)
        res = HTTPResponse(raw_res)
        res._trace()

        try:
            db_payload = res._to_db_payload(method, url, tls)
            push_to_queue(db_payload)
        except Exception as e:
            smf.printd("Failed to push HTTP payload to queue", e, level="ERROR")
        return res
