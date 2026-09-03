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
            result = r.data
            smf.printf()
            smf.printf(f"{CC.CYAN}{result}{CC.RESET}")
            smf.printf()
    except KeyboardInterrupt:
        return
    except Exception as e:
        smf.printf(f"{CC.RED} ERROR: Failed to retrieve IP data.")
        smf.printd("Failed to retrieve IP data", e, level="ERROR")
