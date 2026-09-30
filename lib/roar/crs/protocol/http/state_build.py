# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author zxelzy

import smf

from typing import Dict
from apps.utility.colors import CC

from .rawhttp import RawHttp


class HTTPState:
    """Manajemen Konfigurasi & State Sesi."""

    def __init__(
        self,
        method: str = "GET",
        url: str = "",
        headers: dict = None,
        body: str | bytes = b"",
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
        self.ratelimit = rlimit
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
        body_str = ""
        if isinstance(state._body, str):
            body = state._body
            body_bytes = body.encode("utf-8")
            body_str = base64.b64encode(body_bytes).decode("utf-8")
            encode = "string"
            
        if isinstance(state._body, bytes):
            body = state._body
            body_str = base64.b64encode(body).decode("utf-8")
            encode = "bytes"
            

        return {
            "primitive": "HTTP_SEND",
            "method": state._method,
            "url": state._url,
            "headers": state._headers or {},
            "body": body_str if state._body is not None else "",
            "redirect": state._redirect,
            "rawmode": state._rawhttp,
            "info_tls": state._tls,
            "verify": state._verify,
            "retry": state._retry,
            "timeout": state._timeout,
            "ratelimit": state.ratelimit,
            "frate": state.fixed_ratelimit,
            "goroutine": state.goroutine,
            "encoding": encode
        }
