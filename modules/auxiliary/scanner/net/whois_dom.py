import sys
import smf

from apps.utility.colors import CC

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
            # TECHNICAL
            smf.printf(f"\n[✓] {CC.CYAN}[TECHNICAL CONTACT]{CC.RESET}")
            for contact in r.technical:
                for k, v in contact.items():
                    smf.printf(
                        f"{CC.GREEN}    {k:<12}{CC.RESET} = {CC.YELLOW}{v}{CC.RESET}"
                    )
                smf.printf()

            # ADMIN
            smf.printf(f"[✓] {CC.CYAN}[ADMINISTRATIVE CONTACT]{CC.RESET}")
            for contact in r.admin:
                for k, v in contact.items():
                    smf.printf(
                        f"{CC.GREEN}    {k:<12}{CC.RESET} = {CC.YELLOW}{v}{CC.RESET}"
                    )
                smf.printf()

            # ABUSE
            smf.printf(f"[✓] {CC.CYAN}[ABUSE CONTACT]{CC.RESET}")
            for contact in r.abuse:
                for k, v in contact.items():
                    smf.printf(
                        f"{CC.GREEN}    {k:<12}{CC.RESET} = {CC.YELLOW}{v}{CC.RESET}"
                    )
                smf.printf()

            # REGISTRANT
            smf.printf(f"[✓] {CC.CYAN}[REGISTRANT CONTACT]{CC.RESET}")
            for contact in r.registrant:
                for k, v in contact.items():
                    smf.printf(
                        f"{CC.GREEN}    {k:<12}{CC.RESET} = {CC.YELLOW}{v}{CC.RESET}"
                    )
                smf.printf()
        else:
            smf.printf(f"[!] {CC.CYAN}Invalid WhoisIP:{CC.RESET}")
            smf.printf(f"   {CC.YELLOW}   Status      => {r.status}")
            smf.printf(f"   {CC.YELLOW}   Status Code => {r.status_code}")
            smf.printf(f"   {CC.YELLOW}   Message     => {r.message}")
    except KeyboardInterrupt:
        return
    except Exception as e:
        smf.printf(f"{CC.RED} ERROR: Unable to retrieve domain data.")
        smf.printf(f"Whois Domain Exception", e, level="ERROR")
