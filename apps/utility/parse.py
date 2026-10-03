import ipaddress

from lib.roar.crs.net_api import Socket
from urllib.parse import urlparse


def parse_url(url):
    """Returns a Dict of URL fragments"""
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
    """Returning IPV4 and IPV6"""
    sock = Socket()
    try:
        resp = sock.getaddrinfo(domain, None, proto=sock.IPPROTO_TCP)

        ipv4 = set()
        ipv6 = set()

        for result in resp.addrinfo:
            ip = result[4][0]
            try:
                addr = ipaddress.ip_address(ip)
                if addr.version == 4:
                    ipv4.add(ip)
                elif addr.version == 6:
                    ipv6.add(ip)
            except ValueError:
                continue

        return {
            "ipv4": sorted(ipv4),
            "ipv6": sorted(ipv6),
        }
    except sock.STrace:
        return {
            "ipv4": [],
            "ipv6": [],
        }
