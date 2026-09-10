from urllib.parse import urlparse
import socket


def parse_url(url):
    val = url.strip()
    if "://" not in val:
        res = "//" + val
    else:
        res = val
      
    parsed = urlparse(res)
    return {
        "scheme": parsed.scheme,
        "domain": parsed.hostname,
        "port": parsed.port,
        "path": parsed.path,
        "query": parsed.query,
    }

def domain_to_ip(domain):
    try:
        results = socket.getaddrinfo(
            domain,
            None,
            proto=socket.IPPROTO_TCP
        )
        ips = sorted({
            result[4][0]
            for result in results
        })
        return ips
    except socket.gaierror:
        return []
