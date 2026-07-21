# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author zxelzy
import smf

from apps.utility.colors import CC
from ..transport import CRS


def socket(
    host: dict = None,
    port: int = None,
    headers: dict = None,
    body: str = "",
    protocol: str = "tcp",
    timeout: float = 5.0,
    **kwargs,
) -> dict:
    """Wrapper to send Socket to CRS Engine"""

    packet = {
        "primitive": "NETWORK_SEND",
        "host": host,
        "port": port,
        "headers": headers or {},
        "body": body,
        "protocol": protocol,
        "timeout": timeout,
    }

    if kwargs:
        smf.printf(f"[!] {CC.YELLOW}Unrecognized parameters dropped =>{CC.RESET}", kwargs)

    return CRS.send(packet)
