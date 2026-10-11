# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author zxelzy

import smf

from lib.smf.ingest import push_to_queue
from ....transport import CRS

from .response import DNSResponse
from .state_build import DNState, IPCPayloadBuilder
from .exception import StackTrace, NXDomain


class DNSResolver(DNState):
    """Namespace OOP untuk operasi DNS"""

    DTrace = StackTrace
    NXDOMAIN = NXDomain

    def __init__(self):
        super().__init__()
        self.query = self
        
    def tcp(
        self, 
        domain: str, 
        type: str = None,
        **kwargs,
    ):
        """TCP Protocol"""
        self.domains = domain
        if type is not None:
            self.types = type
        self.protocol = "tcp"
        return self

    def udp(
        self,
        domain: str,
        type: str = None,
        **kwargs,
    ):
        """UDP Protocol"""
        self.domains = domain
        if type is not None:
            self.types = type
        self.protocol = "udp"
        return self

    def concurrency(self, con: int, **kwargs):
        """store Concurrency values"""
        self.goroutine = con
        return self

    def setlimit(self, ratelimit: int, frate: int, **kwargs):
        """set limit options"""
        self.ratelimit = ratelimit
        self.fixed_ratelimit = frate
        return self

    def timeout(self, value: float, **kwargs):
        """Stores global timeout state"""
        self._timeout = value
        return self

    def run(self, **kwargs) -> DNSResponse:
        """Running DNS Lookup"""
        packet = IPCPayloadBuilder.build(state=self)

        raw_res = CRS.send(packet)
        res = DNSResponse(raw_res)
        res._trace()
        res._nxdomain()

        try:
            db_payload = res._to_db_payload(self.domains, self.protocol)
            push_to_queue(db_payload)
        except Exception as e:
            smf.printd("Failed to push DNSL payload to queue", e, level="ERROR")
        return res

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            smf.printd("Context failed with", exc_type, exc_val, exc_tb, level="WARN")
        self._reset()
        return False

    def __repr__(self):
        return (
            f"<DNSL Domain='{self.domains}' Proto='{self.protocol}' Type='{self.types}'>"
        )
