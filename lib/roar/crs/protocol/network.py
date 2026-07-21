# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author zxelzy
import smf

from apps.utility.colors import CC
from ..transport import CRS


def socket(
    host: str = "",
    port: int = None,
    body: str = "",
    protocol: str = "tcp",
    timeout: float = 5.0,
    encoding: str = "",
    readsize: int = None,
    **kwargs,
) -> dict:
    """Wrapper to send Socket to CRS Engine"""

    packet = {
        "primitive": "NETWORK_SEND",
        "host": host,
        "port": port,
        "body": body,
        "protocol": protocol,
        "timeout": timeout,
        "encoding": encoding,
        "readsize": readsize,
    }

    if kwargs:
        smf.printf(f"[!] {CC.YELLOW}Unrecognized parameters dropped =>{CC.RESET}", kwargs)

    return CRS.send(packet)
