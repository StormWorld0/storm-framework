from .protocol.http import http_request
from .protocol.dns import dns_request
# from .ftp import ftp_login
# from .smb import smb_enum

# Define wrapper protocol
__all__ = [
    "http_request",
    "dns_request",
]
