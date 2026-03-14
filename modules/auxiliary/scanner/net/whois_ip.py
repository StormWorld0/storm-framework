from ipwhois import IPWhois
from app.utility.colors import C

REQUIRED_OPTIONS = {"IP": "(ex: x.x.x.x)"}


def execute(options):
    target_ip = options.get("IP")
    if not target_ip:
        print(f"{C.ERROR} ERROR: IP variable content 'set ip x.x.x.x'!")
        return
    print(f"{C.HEADER}[ IP WHOIS/RDAP LOOKUP ] -> {target_ip}")
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
        print(f"{C.MENU} ASN:            {C.RESET}{results.get('asn')}")
        print(f"{C.MENU} CIDR:           {C.RESET}{results.get('asn_cidr')}")
        print(f"{C.MENU} Country:        {C.RESET}{results.get('asn_country_code')}")
        print(f"{C.MENU} ASN Description:{C.RESET}{results.get('asn_description')}")
        print(
            f"{C.MENU} Network Name:   {C.RESET}{results.get('network', {}).get('name')}"
        )
        print(f"{C.MENU} Abuse Emails:   {C.RESET}{unique_emails}")

    except KeyboardInterrupt:
        return
    except Exception as e:
        print(f"{C.ERROR} ERROR: Failed to retrieve IP data.")
        print(f"{C.ERROR} Detail: {e}")
