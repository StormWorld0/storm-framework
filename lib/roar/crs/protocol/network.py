# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author zxelzy
import smf

from apps.utility.colors import CC
from ..transport import CRS


def socket(
    host: str = "",  # Host: IP / DOMAIN OR IP:PORT / DOMAIN:PORT
    port: int = 0,  # Default 0 = Considered non-existent
    body: str = "",  # Can be hex or byte payload etc.
    protocol: str = "tcp",  # TCP / TLS / SSL
    timeout: float = 5.0,  #
    encoding: str = "",  # Encoding: hex
    readsize: int = 4096,  # Read buffer default
    ratelimit: int = 0,  # Default 0 = Unlimited
    sessid: str = "",  # Must combo with keep_alive for stream
    keep_alive: bool = False,  # Default False, must be combo with sessid
    close_session: bool = False,  # Deleting active SessionsID
    mode: str = "duplex",  # Default duplex = Mode normal // or can send_only or recv_only
    verify: bool = True,  # Default True: It means default running verification
    cert: str = "",  # TLSCert: Can be used with path or raw pem
    key: str = "",  # TLSKey: Can be used with path or raw pem
    ca: str = "",  # TLSCA: Can be used with path or raw pem
    **kwargs,  # Drop excess parameters
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
        "session_id": sessid,
        "keep-alive": keep_alive,
        "close_session": close_session,
        "mode": mode,
        "verify": verify,
        "tls-cert": cert,
        "tls-key": key,
        "tls-ca": ca,
    }

    if kwargs:
        smf.printf(f"[!] {CC.YELLOW}Unrecognized parameters dropped =>{CC.RESET}", kwargs)

    return CRS.send(packet)
