import sys
import smf
from ipwhois import IPWhois
from apps.utility.colors import C

metadata = {
    "Name": "Searching for information",
    "Description": """
Finding information behind an IP Address using Whois
allows to find ASN, Country, CIDR, etc. data.
""",
    "Author": ["zxelzy"],
    "Action": [
        ["Scanner", {"Description": "Searching for data"}],
    ],
    "DefaultAction": "Scanner",
    "License": "SMF License",
    "Date": "2026-01-06",
}
REQUIRED_OPTIONS = {"IP": "(ex: x.x.x.x)"}


def execute(options):
    target_ip = options.get("IP")
    if not target_ip:
        smf.printf(f"{C.ERROR} ERROR: IP variable content 'set ip x.x.x.x'!")
        return
    smf.printf(f"{C.HEADER}[ IP WHOIS/RDAP LOOKUP ]")
    try:
        obj = IPWhois(target_ip)
        results = obj.lookup_rdap()
        emails = []
        if "objects" in results:
            for handle, info in results["objects"].items():
                contact = info.get("contact", {})
                if contact.get("email"):
                    for email_entry in contact["email"]:
                        emails.append(email_entry["value"])
        unique_emails = ", ".join(list(set(emails))) if emails else "N/A"

        # Show Information
        smf.printf(f"{C.MENU} ASN:            {C.RESET}{results.get('asn')}")
        smf.printf(f"{C.MENU} CIDR:           {C.RESET}{results.get('asn_cidr')}")
        smf.printf(f"{C.MENU} Country:        {C.RESET}{results.get('asn_country_code')}")
        smf.printf(f"{C.MENU} ASN Description:{C.RESET}{results.get('asn_description')}")
        smf.printf(
            f"{C.MENU} Network Name:   {C.RESET}{results.get('network', {}).get('name')}"
        )
        smf.printf(f"{C.MENU} Abuse Emails:   {C.RESET}{unique_emails}")

    except KeyboardInterrupt:
        return
    except Exception as e:
        smf.printf(f"{C.ERROR} ERROR: Failed to retrieve IP data.")
        smf.printf(f"{C.ERROR} Detail =>", e, file=sys.stderr, flush=True)
