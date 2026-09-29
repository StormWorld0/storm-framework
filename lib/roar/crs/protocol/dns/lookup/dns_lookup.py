# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author zxelzy

import smf

from lib.smf.ingest import push_to_queue
from ...transport import CRS

from .response import DNSResponse
from .state_build import DNState, IPCPayloadBuilder
from .exception import StackTrace, TimeoutTrace, NXDomain


class DNSResolver(DNState):
    """Namespace OOP untuk operasi DNS"""

    DTrace = StackTrace
    Timeout = TimeoutTrace
    NXDOMAIN = NXDomain

    def query(
        self,
        domain: str,
        type: str = None,
        proto: str = None,
        timeout: float = None,
        **kwargs,
    ):
        """Saving Query values"""
        self.domains = domain
        if type is not None:
            self.types = type
        if proto is not None:
            self.protocol = proto
        if timeout is not None:
            self._timeout = timeout
        return self

    def concurrency(self, con: int):
        """store Concurrency values"""
        self.goroutine = con
        return self

    def setlimit(self, ratelimit: int, frate: int):
        """set limit options"""
        self.ratelimit = ratelimit
        self.fixed_ratelimit = frate
        return self

    def run(self):
        """Running DNS Lookup"""
        packet = IPCPayloadBuilder.build(state=self)

        raw_res = CRS.send(packet)
        res = DNSResponse(raw_res)
        res._trace()
        res._timeout()
        res._nxdomain()

        try:
            db_payload = res._to_db_payload(self.domains, self.protocol)
            push_to_queue(db_payload)
        except Exception as e:
            smf.printd("Failed to push DNSL payload to queue", e, level="ERROR")

        return res
