import sys
import smf
import whoisdomain as whois
from apps.utility.colors import C

metadata = {
    "Name": "Searching for information",
    "Description": """
Looking for specific information on whois data to
an active domain, to get email data, servers, org, etc.
""",
    "Author": ["zxelzy"],
    "Action": [
        ["Scaner", {"Description": "Searching for data"}],
    ],
    "DefaultAction": "Scaner",
    "License": "SMF License",
    "Date": "2026-01-18",
}
REQUIRED_OPTIONS = {"DOMAIN": "(e.g., example.com)"}

def execute(options, net):
    domain = options.get("DOMAIN")
    try:
        r = net.DWhois(domain, timeout=5.0, con=20)
        if r.ok:
            smf.print(r.raw_data)
    except KeyboardInterrupt:
        return
    except Exception as e:
        smf.printf(f"{C.ERROR} ERROR: Unable to retrieve domain data.")
        smf.printf(f"{C.ERROR} Detail =>", e, file=sys.stderr, flush=True)
