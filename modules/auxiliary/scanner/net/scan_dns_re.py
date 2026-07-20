import ipaddress
import sys
import smf
from apps.utility.colors import C
from lib.roar.crs.dns_transport import DNSTransport

metadata = {
    "Name": "Scanning DNS Records",
    "Description": "Scan the DNS Record to find out the DNS data in it used by a website.",
    "Author": ["zxelzy"],
    "Action": [["Scanner", {"Description": "Scan DNS Records"}]],
    "DefaultAction": "Scanner",
    "License": "SMF License",
    "Date": "2025-09-22",
}

SYM_INFO = "💡"
SYM_SECURITY = "🔒"
DNS_RECORDS = [
    "A",
    "AAAA",
    "CNAME",
    "MX",
    "TXT",
    "NS",
    "SOA",
    "SRV",
    "NAPTR",
    "CAA",
    "TLSA",
    "PTR",
    "DNSKEY",
    "DS",
    "RRSIG",
    "LOC",
]

REQUIRED_OPTIONS = {"DOMAIN": ""}


def execute(options):
    """
    Eksekusi modul. Meminta 'transport' engine dari Framework Core
    untuk melakukan inspeksi paket di jaringan.
    """
    target_domain = options.get("DOMAIN")
    if not target_domain:
        return

    # Validasi input (bukan IP)
    try:
        ipaddress.ip_address(target_domain)
        return
    except ValueError:
        pass

    # Jika transport tidak di-pass dari luar, gunakan default instance (Fallback)
    if transport is None:
        transport = DNSTransport()

    smf.printf(f"{C.HEADER} DNS ENUMERATION For {target_domain}")

    # Validasi awal via Core Transport
    if not transport.is_domain_resolvable(target_domain):
        smf.printf(f"{C.ERROR}[!] ERROR: Domain not found.")
        return

    try:
        for record_type in DNS_RECORDS:
            # Modul hanya memanggil instruksi 'resolve_record' ke Core
            result = transport.resolve_record(target_domain, record_type, tcp=True)

            status = result["status"]

            if status == "SUCCESS":
                smf.printf(f"{C.MENU} \n[{record_type} Records]:")
                for item in result["data"]:
                    if record_type == "TXT":
                        smf.printf(f"{C.SUCCESS}  {SYM_SECURITY} {item}")
                    else:
                        smf.printf(f"{C.MENU}  {SYM_INFO} {item}")

            elif status == "TIMEOUT":
                smf.printf(f"{C.YELLOW}[!] Timeout:", record_type)

            elif status == "ERROR":
                smf.printf(f"{C.ERROR}[!] ERROR {record_type} => {result.get('message')}")

    except KeyboardInterrupt:
        return
    except Exception as e:
        smf.printf(f"{C.ERROR}[!] Global ERROR =>", e, file=sys.stderr, flush=True)
