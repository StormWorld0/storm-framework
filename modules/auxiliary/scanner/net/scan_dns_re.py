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
    val = getattr(item, "value", item)

    if record_type == "TXT":
        return str(val)

    if isinstance(val, dict):
        if record_type == "MX":
            return f"{val.get('host', '')} (priority {val.get('preference', 0)})"

        elif record_type == "SOA":
            return (
                f"Primary NS : {val.get('ns', '')}, "
                f"Admin Mail : {val.get('mbox', '')}, "
                f"Serial : {val.get('serial', 0)}, "
                f"Refresh : {val.get('refresh', 0)}s, "
                f"Retry : {val.get('retry', 0)}s, "
                f"Expire : {val.get('expire', 0)}s, "
                f"Minimum TTL : {val.get('minttl', 0)}s"
            )

        elif record_type == "SSHFP":
            return (
                f"Algorithm : {val.get('algorithm')}, "
                f"Fingerprint Type : {val.get('fingerprint_type')}, "
                f"Fingerprint : {val.get('fingerprint')}"
            )

        elif record_type == "CERT":
            return (
                f"Type : {val.get('type')}, "
                f"Key Tag : {val.get('key_tag')}, "
                f"Algorithm : {val.get('algorithm')}"
            )

        elif record_type == "URI":
            return (
                f"Target : {val.get('target')} "
                f"(priority {val.get('priority')}, weight {val.get('weight')})"
            )

        elif record_type == "CAA":
            return (
                f"Flag : {val.get('flag', 0)}, "
                f"Tag : {val.get('tag', '')}, "
                f"Value : {val.get('value', '')}"
            )

        elif record_type == "DNSKEY":
            return (
                f"Flags : {val.get('flags')}, "
                f"Protocol : {val.get('protocol')}, "
                f"Algorithm : {val.get('algorithm')}, "
                f"Public Key : {val.get('publicKey')}"
            )

        elif record_type == "DS":
            return (
                f"Key Tag : {val.get('keyTag')}, "
                f"Algorithm : {val.get('algorithm')}, "
                f"Digest Type : {val.get('digestType')}, "
                f"Digest : {val.get('digest')}"
            )

        elif record_type in ("HTTPS", "SVCB"):
            lines = [
                f"Priority : {val.get('priority', 0)}",
                f"Target : {val.get('target', '')}",
            ]
            params = val.get("value", [])
            if isinstance(params, list):
                for param in params:
                    if isinstance(param, dict):
                        for k, v in param.items():
                            v_str = ", ".join(v) if isinstance(v, list) else str(v)
                            lines.append(f"{k} : {v_str}")
            return "\n     ".join(lines)

        else:
            return "\n".join(f"{k} : {v}" for k, v in val.items())

    return str(val)


REQUIRED_OPTIONS = {"DOMAIN": "example.com"}


def execute(options, net):
    target_domain = options.get("DOMAIN")
    if not target_domain:
        return

    try:
        ipaddress.ip_address(target_domain)
        return
    except ValueError:
        pass

    smf.printf(f"{C.HEADER} DNS ENUMERATION For {target_domain}")
    try:
        for record_type in DNS_RECORDS:
            resp = net.DNSL(target_domain, type=record_type, timeout=2.0, con=50)

            valid = resp.ok
            status = resp.status
            answers = resp.records

            if valid:
                if not answers:
                    continue

                smf.printf(f"{CC.CYAN} \n[{record_type} Records]:")

                for item in answers:
                    icon = SYM_SECURITY if record_type == "TXT" else SYM_INFO
                    color = CC.GREEN if record_type == "TXT" else CC.CYAN

                    smf.printf(f"{color}  {icon} {format_record(record_type, item)}")
                smf.printf()

            elif status.upper() == "TIMEOUT":
                smf.printf(f"{CC.YELLOW}[!] Timeout: {record_type} => {resp.message}")

            elif status.upper() == "ERROR":
                smf.printf(f"{CC.RED}[!] ERROR: {record_type} => {resp.message}")

    except KeyboardInterrupt:
        return
    except Exception as e:
        smf.printf(f"{CC.RED}[!] Global ERROR =>", e, file=sys.stderr, flush=True)
        smf.printd("Global error dns lookup", e, level="ERROR")
