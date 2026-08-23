from .protocol.http import http_requests
from .protocol.dns import requests as dns
from .protocol.network import Socket
from .protocol.telnet import TelnetClient as Telnet

# Define wrapper protocol
# For registration on high level API calls
__all__ = [
    "http_requests",
    "dns",
    "Socket",
    "Telnet",
]
