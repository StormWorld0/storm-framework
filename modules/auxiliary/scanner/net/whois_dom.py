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


def get_clean_data(data):
    """Tidy up the date or list format to make it easier to read."""
    if not data:
        return "N/A"
    if isinstance(data, list):
        return str(data[0]).split()[0]
    return str(data).split()[0]


def execute(options):
    target = options.get("DOMAIN")
    if not target:
        smf.printf(
            f"{C.ERROR} ERROR: Fill in the DOMAIN variable 'set domain example.com'!"
        )
        return

    clean_domain = (
        target.replace("http://", "").replace("https://", "").split("/")[0].strip()
    )

    smf.printf(f"{C.HEADER}[ DOMAIN WHOIS LOOKUP ] -> {clean_domain}")
    try:
        w = whois.query(clean_domain)

        if not w:
            smf.printf(f"{C.ERROR} ERROR: Domain not found or blocked by provider.")
            return

        # Show Information
        smf.printf(f"{C.MENU} Registrar:      {C.RESET}{getattr(w, 'registrar', 'N/A')}")
        smf.printf(
            f"{C.MENU} Created Date:   {C.RESET}{get_clean_data(getattr(w, 'creation_date', None))}"
        )
        smf.printf(
            f"{C.MENU} Expiry Date:    {C.RESET}{get_clean_data(getattr(w, 'expiration_date', None))}"
        )
        smf.printf(
            f"{C.MENU} Organization:   {C.RESET}{getattr(w, 'private_registrant', 'N/A') if not getattr(w, 'org', None) else w.org}"
        )

        # Email handling
        emails = getattr(w, "emails", "N/A")
        smf.printf(
            f"{C.MENU} Emails:         {C.RESET}{', '.join(emails) if isinstance(emails, list) else emails}"
        )

        # Name Servers
        ns = getattr(w, "name_servers", [])
        smf.printf(
            f"{C.MENU} Name Servers:   {C.RESET}{', '.join(list(ns)[:2]) if ns else 'N/A'}"
        )

    except KeyboardInterrupt:
        return
    except Exception as e:
        smf.printf(f"{C.ERROR} ERROR: Unable to retrieve domain data.")
        smf.printf(f"{C.ERROR} Detail =>", e, file=sys.stderr, flush=True)
