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

    smf.printf(f"{CC.CYAN}[ IP WHOIS/RDAP LOOKUP ]{CC.RESET}\n")
    try:
        r = net.IPWhois(target_ip, timeout=10.0)
        if r.ok:
            smf.printf(f"{CC.GREEN}{r.data}{CC.RESET}")
    except KeyboardInterrupt:
        return
    except Exception as e:
        smf.printf(f"{CC.RED} ERROR: Failed to retrieve IP data.")
        smf.printd("Failed to retrieve IP data", e, level="ERROR")
