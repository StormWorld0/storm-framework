from .protocol.http import http_requests
from .protocol.dns import requests
from .protocol.network import Socket

# from .ftp import ftp_login
# from .smb import smb_enum

# Define wrapper protocol
__all__ = [
    "http_requests",
    "requests",
    "Socket",
]
