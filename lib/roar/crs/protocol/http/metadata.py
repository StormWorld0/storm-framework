from typing import Dict, Any, Optional, Union

class HTTPTLSMetadata:
    """Data Transfer Object (DTO) untuk metadata TLS"""

    def __init__(self, data: Dict[str, Any]):
        self.subject: Optional[str] = data.get("subject", "")
        self.issuer: Optional[str] = data.get("issuer", "")
        self.dns_name: list = data.get("dns_name", [])
        self.expires: Optional[str] = data.get("expires", "")

        self.version: str = data.get("tls_version", "Unknown")
        self.cipher: str = data.get("cipher_suite", "Unknown")
        self.protocol: str = data.get("protocol", "")
        self.hostname: str = data.get("hostname", "")
        self.handshake: bool = data.get("handshake", False)
        self.session_resume: bool = data.get("session_resume", False)
        self.cert_chain: list = data.get("cert_chain", [])

    def __repr__(self):
        return f"<HTTPTLSMetadata Version={self.tls_version} Cipher={self.cipher_suite} Host={self.hostname}>"
