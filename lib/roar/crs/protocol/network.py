# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author zxelzy
import smf

from apps.utility.colors import CC
from ..transport import CRS


def socket(
    host: str = "",          # Host: IP / URL
    port: int = None,
    body: str = "",
    protocol: str = "tcp",   # TCP / TLS / SSL
    timeout: float = 5.0,
    encoding: str = "",      # Encoding: hex
    readsize: int = None,    # Read buffer
    ratelimit: int = 0,      # Default 0 = Unlimited
    **kwargs,                # Drop excess parameters
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
        "ratelimit": ratelimit,
    }

    if kwargs:
        smf.printf(f"[!] {CC.YELLOW}Unrecognized parameters dropped =>{CC.RESET}", kwargs)

    return CRS.send(packet)
