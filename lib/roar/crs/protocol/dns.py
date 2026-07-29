# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author zxelzy
import smf

from apps.utility.colors import *
from ..transport import CRS


# ----------------------------------------
# Functions to send DNS Records to domains
# ----------------------------------------
def dns_request(
    domain: str,
    type: str = "A",
    protocol: str = "tcp",
    timeout: float = 2.0,
    ratelimit: int = 0,
    **kwargs,
) -> Dict:
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
