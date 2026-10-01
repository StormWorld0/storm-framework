from typing import Dict, Any, Optional

class TLSMetadata:
    """
    Data Transfer Object (DTO) untuk metadata TLS dari Go Engine.
    """

    def __init__(self, data: Dict[str, Any]):
        self.version: str = data.get("tls_version", "Unknown")
        self.cipher_suite: str = data.get("cipher_suite", "Unknown")
        self.protocol: str = data.get("protocol", "")
        self.hostname: str = data.get("hostname", "")
        self.handshake: bool = data.get("handshake", False)
        self.session_resume: bool = data.get("session_resume", False)

        # Sertifikat Data (Bisa None jika tidak ada)
        self.subject: Optional[str] = data.get("subject")
        self.issuer: Optional[str] = data.get("issuer")
        self.dns_name: list = data.get("dns_name", [])
        self.expires: Optional[str] = data.get("expires")
        self.cert_chain: int = data.get("cert_chain", 0)

    def __repr__(self):
        return f"<TLSMetadata {self.version} Cipher={self.cipher_suite} Host={self.hostname}>"
