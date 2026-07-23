# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author zxelzy
import smf

from apps.utility.colors import *
from ..transport import CRS


def dns_request(
    domain: str, 
    type: str = "A", # Type: A, AAAA, TXT, ...
    protocol: str = "tcp", # UDP / TCP
    timeout: float = 2.0, 
    ratelimit: int = 0, # Default 0 = Unlimited
    **kwargs # Drop excess parameters
) -> dict:
    """Wrapper DNS"""

    packet = {
        "primitive": "DNS_SEND",
        "domain": domain,
        "type": type,
        "protocol": protocol,
        "timeout": timeout,
        "ratelimit": ratelimit,
    }

    if kwargs:
        smf.printf(f"[!] {CC.YELLOW}Data is not recognized =>{CC.RESET}", kwargs)

    return CRS.send(packet)
