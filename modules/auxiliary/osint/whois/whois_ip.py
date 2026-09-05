import smf

from apps.utility.colors import CC

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
REQUIRED_OPTIONS = {"IP": "(ex: 1.1.1.1)"}


def execute(options, net):
    target_ip = options.get("IP")
    try:
        r = net.IPWhois(target_ip, timeout=5.0, con=20)
        if r.ok:
            if r.technical and r._categorized_contacts.get("Technical"):
                # TECHNICAL
                smf.printf(f"\n[✓] {CC.CYAN}[TECHNICAL CONTACT]{CC.RESET}")
                for contact in r.technical:
                    for k, v in contact.items():
                        smf.printf(
                            f"{CC.GREEN}    {k:<12}{CC.RESET} = {CC.YELLOW}{v}{CC.RESET}"
                        )
                    smf.printf()

            if r.admin and r._categorized_contacts.get("Administrative"):
                # ADMIN
                smf.printf(f"[✓] {CC.CYAN}[ADMINISTRATIVE CONTACT]{CC.RESET}")
                for contact in r.admin:
                    for k, v in contact.items():
                        smf.printf(
                            f"{CC.GREEN}    {k:<12}{CC.RESET} = {CC.YELLOW}{v}{CC.RESET}"
                        )
                    smf.printf()

            if r.abuse and r._categorized_contacts.get("Abuse"):
                # ABUSE
                smf.printf(f"[✓] {CC.CYAN}[ABUSE CONTACT]{CC.RESET}")
                for contact in r.abuse:
                    for k, v in contact.items():
                        smf.printf(
                            f"{CC.GREEN}    {k:<12}{CC.RESET} = {CC.YELLOW}{v}{CC.RESET}"
                        )
                    smf.printf()

            if r.registrant and r._categorized_contacts.get("Registrant"):
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
        smf.printf(f"{CC.RED} ERROR: Failed to retrieve IP data.")
        smf.printd("Failed to retrieve IP data", e, level="ERROR")
