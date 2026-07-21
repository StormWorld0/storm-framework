import ipaddress
import sys
import smf
from apps.utility.colors import C

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
    "SSHFP",  # Fingerprint SSH
    "CERT",  # Certificate
    "URI",  # URI record
    "SVCB",  # Service Binding (modern)
    "HTTPS",  # HTTPS Service Binding (RFC 9460)
]


def format_record(record_type, item):
    if record_type == "TXT":
        return item

    if record_type == "MX":
        return f"{item['host']} (priority {item['preference']})"

    if record_type == "SOA":
        return (
            f"Primary NS : {item['ns']}, "
            f"Admin Mail : {item['mbox']}, "
            f"Serial : {item['serial']}, "
            f"Refresh : {item['refresh']}s, "
            f"Retry : {item['retry']}s, "
            f"Expire : {item['expire']}s, "
            f"Minimum TTL : {item['minttl']}s"
        )

    if record_type == "SSHFP":
        return (
            f"Algorithm : {item['algorithm']}, "
            f"Fingerprint Type : {item['fingerprint_type']}, "
            f"Fingerprint : {item['fingerprint']}"
        )

    if record_type == "CERT":
        return (
            f"Type : {item['type']}, "
            f"Key Tag : {item['key_tag']}, "
            f"Algorithm : {item['algorithm']}"
        )

    if record_type == "URI":
        return (
            f"Target : {item['target']} "
            f"(priority {item['priority']}, weight {item['weight']})"
        )

    if record_type in ("HTTPS", "SVCB"):
        lines = [
            f"Priority : {item['priority']}",
            f"Target : {item['target']}",
        ]

        for param in item["value"]:
            for key, value in param.items():
                if isinstance(value, list):
                    value = ", ".join(value)
                lines.append(f"{key} : {value}")

        return "\n    ".join(lines)

    return str(item)

REQUIRED_OPTIONS = {"DOMAIN": "", "PROTOCOL": "Default TCP"}


def execute(options, net):
    """
    Eksekusi modul. Meminta 'transport' engine dari Framework Core
    untuk melakukan inspeksi paket di jaringan.
    """
    target_domain = options.get("DOMAIN")
    protocol = options.get("PROTOCOL")
    if not target_domain:
        return

    if not protocol:
        protocol = "tcp"

    # Validasi input (bukan IP)
    try:
        ipaddress.ip_address(target_domain)
        return
    except ValueError:
        pass

    smf.printf(f"{C.HEADER} DNS ENUMERATION For {target_domain}")
    try:
        for record_type in DNS_RECORDS:
            result = net.dns_request(
                target_domain, type=record_type, protocol=protocol, timeout=2.0
            )

            status = result["status"]
            answers = result["data"]["answers"]

            if status == "SUCCESS":
                if not answers:
                    continue

                smf.printf(f"{C.MENU} \n[{record_type} Records]:")

                for item in answers:
                    icon = SYM_SECURITY if record_type == "TXT" else SYM_INFO
                    color = C.SUCCESS if record_type == "TXT" else C.MENU

                    smf.printf(f"{color}  {icon} {format_record(record_type, item)}")

            elif status == "TIMEOUT":
                smf.printf(f"{C.YELLOW}[!] Timeout:", record_type)

            elif status == "ERROR":
                smf.printf(f"{C.ERROR}[!] ERROR {record_type} => {result.get('message')}")

    except KeyboardInterrupt:
        return
    except Exception as e:
        smf.printf(f"{C.ERROR}[!] Global ERROR =>", e, file=sys.stderr, flush=True)
        smf.printd("Global error dns lookup", e, level="ERROR")
