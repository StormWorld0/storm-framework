# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author zxelzy
import smf

from apps.utility.colors import *
from ..transport import CRS


def dns_request(
    domain: str, type: str = "A", protocol: str = "", timeout: float = 2.0, **kwargs
) -> dict:
    """Wrapper DNS"""

    packet = {
        "primitive": "DNS_LOOKUP",
        "domain": domain,
        "type": record_type,
        "protocol": protocol,
        "timeout": timeout,
    }

    if kwargs:
        smf.printf(f"[!] {CC.YELLOW}Data is not recognized =>{CC.RESET}", kwargs)

    return CRS.send(packet)
