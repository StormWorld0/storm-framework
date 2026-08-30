from .protocol import (
    http_requests as HTTP,
    requests as DNS,
    Socket,
    TelnetClient as Telnet,
)

# Define wrapper protocol
# For registration on high level API calls
__all__ = [
    "HTTP",
    "DNS",
    "Socket",
    "Telnet",
]
