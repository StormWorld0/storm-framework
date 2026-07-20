# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author zxelzy
import smf

from apps.utility.colors import *
from ..transport import CRS


def dns_request(
    domain: str, record_type: str = "A", timeout: float = 2.0, **kwargs
) -> dict:
    """Wrapper DNS"""

    packet = {
        "primitive": "DNS_LOOKUP",
        "domain": domain,
        "record_type": record_type,
        "timeout": timeout,
    }

    if kwargs:
        smf.printf(f"[!] {CC.YELLOW}Data is not recognized =>{CC.RESET}", kwargs)

    return CRS.send(packet)
