from .protocol import (
    http_requests as HTTP,
    requests as DNSL,
    discovery as DNSD,
    Socket,
    TelnetClient as Telnet,
)

# Define wrapper protocol
# For registration on high level API calls
__all__ = [
    "HTTP",
    "DNSL",
    "DNSD",
    "Socket",
    "Telnet",
]
