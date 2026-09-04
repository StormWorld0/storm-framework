from .protocol import (
    http_requests as HTTPR,
    requests as DNSL,
    ipwhois as IPWhois,
    domwhois as DWhois,
    Socket,
    TelnetClient as Telnet,
)

# Define wrapper protocol
# For registration on high level API calls
__all__ = [
    "HTTPR",
    "DNSL",
    "IPWhois",
    "DWhois",
    "Socket",
    "Telnet",
]
