from .protocol import (
    http_requests as HTTPR,
    requests as DNSL,
    Socket,
    TelnetClient as Telnet,
)

# Define wrapper protocol
# For registration on high level API calls
__all__ = [
    "HTTPR",
    "DNSL",
    "Socket",
    "Telnet",
]
