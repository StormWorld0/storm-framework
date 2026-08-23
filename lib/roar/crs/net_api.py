from .protocol import (
    http_requests,
    requests as dns,
    Socket,
    TelnetClient as Telnet,
)

# Define wrapper protocol
# For registration on high level API calls
__all__ = [
    "http_requests",
    "dns",
    "Socket",
    "Telnet",
]
