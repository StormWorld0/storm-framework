import smf

class DNState:
    """Manajemen Konfigurasi & State Sesi."""

    def __init__(
        self,
        domain: str = "example.com",
        type: str = "A",
        proto: str = "tcp",
        timeout: float = 2.0,
        rlimit: int = 150,
        frate: int = 10,
        con: int = 0,
        **kwargs,
    ):
        self.domains = domain
        self.types = type
        self.protocol = proto
        self._timeout = timeout
        self.ratelimit = rlimit
        self.fixed_ratelimit = frate
        self.goroutine = con

        if kwargs:
            smf.printf(
                f"[!] {CC.YELLOW}Unrecognized parameters dropped =>{CC.RESET}", kwargs
            )

class IPCPayloadBuilder:
    """Data Marshalling & Data Transformation."""

    @staticmethod
    def build(state: DNState) -> dict:

        return {
            "primitive": "DNS_SEND",
            "mode": "DNSLookup",
            "domain": state.domains,
            "type": state.types,
            "protocol": state.protocol,
            "timeout": state._timeout,
            "ratelimit": state.ratelimit,
            "frate": state.fixed_ratelimit,
            "goroutine": state.goroutine,
        }
