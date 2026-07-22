# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author zxelzy
import smf

from apps.utility.colors import CC
from ..transport import CRS


def http_request(
    method: str,             # Method: GET, PUT, POST, ...
    url: str,
    headers: dict = None,
    body: str = "",
    redirect: bool = True,   # Default True will do a redirect
    rawhttp: bool = False,   # Using rawhttp request
    infotls: bool = False,   # To display TLS response information: Default False
    verify: bool = True,
    retry: int = 2,          # Retry connection
    ratelimit: int = 0       # Default 0 = unlimited
    timeout: float = 5.0,
    **kwargs,                # Excessive parameter drop
) -> dict:
    """Wrapper to send HTTP Request to CRS Engine"""

    packet = {
        "primitive": "HTTP_SEND",
        "method": method.upper(),
        "url": url,
        "headers": headers or {},
        "body": body,
        "redirect": redirect,
        "rawmode": rawhttp,
        "info_tls": infotls,
        "verify": verify,
        "retry": retry,
        "ratelimit": ratelimit,
        "timeout": timeout,
    }

    if kwargs:
        smf.printf(f"[!] {CC.YELLOW}Unrecognized parameters dropped =>{CC.RESET}", kwargs)

    return CRS.send(packet)
