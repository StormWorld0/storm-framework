# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author zxelzy
import smf

from typing import Dict

from apps.utility.colors import CC
from lib.smf.ingest import push_to_queue

from ...transport import CRS
from .state_build import HTTPState, IPCPayloadBuilder
from .normal_http import HTTPMethod
from .response import HTTPResponse



class HTTPClient(HTTPState, HTTPMethod):
    """Namespace OOP untuk operasi HTTP"""

    def setoptions(
        self, 
        redirect: bool = None, 
        retry: int = None, 
        verify: bool = None, 
        tls: bool = None, 
        **kwargs
    ):
        """Saving Options values"""
        self._redirect = redirect
        self._retry = retry
        self._verify = verify
        self._tls = tls
        return self

    def concurrency(self, con: int, **kwargs):
        """Storing Concurrency values"""
        self.goroutine = con
        return self

    def setlimit(self, ratelimit: int, frate: int = None, **kwargs):
        """Save ratelimiting value"""
        self.ratelimit = ratelimit
        self.fixed_ratelimit = frate
        return self

    def timeout(self, value: float, **kwargs):
        """Timeout value settings"""
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
