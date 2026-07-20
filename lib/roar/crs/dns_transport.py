import dns.resolver
import dns.exception
import socket

class DNSTransport:
    """Core Engine untuk menangani operasional jaringan DNS."""
    
    def __init__(self, nameservers=None, timeout=2.0, lifetime=3.0):
        self.resolver = dns.resolver.Resolver(configure=False)
        self.resolver.nameservers = nameservers or ["8.8.8.8", "1.1.1.1"]
        self.resolver.timeout = timeout
        self.resolver.lifetime = lifetime

    def resolve_record(self, domain: str, record_type: str, tcp: bool = True):
        """
        Mengeksekusi lookup DNS tunggal dan mengembalikan data yang sudah diparse.
        Memisahkan exception handling jaringan dari logika modul.
        """
        try:
            answers = self.resolver.resolve(domain, record_type, tcp=tcp)
            # Mengembalikan list string hasil query
            return {"status": "SUCCESS", "data": [str(rdata) for rdata in answers]}
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            return {"status": "NO_ANSWER", "data": []}
        except dns.exception.Timeout:
            return {"status": "TIMEOUT", "data": []}
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}

    def is_domain_resolvable(self, domain: str) -> bool:
        """Helper untuk verifikasi eksistensi domain."""
        try:
            socket.gethostbyname(domain)
            return True
        except socket.gaierror:
            return False
          
