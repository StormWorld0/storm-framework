import smf
import sys
import asyncio

from apps.utility.colors import CC
from lib.roar.calling import call_bin

metadata = {
    "Name": "OSINT for subdomains",
    "Description": """
Perform a scan on the specified subdomain
to search and find subdomains that allow for
exploited.
""",
    "Author": ["zxelzy"],
    "Action": [
        ["Sub Enumeration", {"Description": "Searching for valid subdomains"}],
        ["Scanner", {"Description": "Searching for sensitive subdomains"}],
    ],
    "DefaultAction": "Scanner",
    "License": "SMF License",
    "Date": "2026-04-20",
}
REQUIRED_OPTIONS = {
    "DOMAIN": "ex: google.com",
    "WORD": "Path to wordlist subdomain",
    "THREAD": "default 1",
}

def code_color(state):
    code = state.status_code
    if code == 200:
        cd_color = f"{CC.GREEN}{code}{CC.RESET}"
    elif 201 <= code <= 399:
        cd_color = f"{CC.CYAN}{code}{CC.RESET}"
    elif code => 400:
        cd_color = f"{CC.YELLOW}{code}{CC.RESET}"
    else:
        return code
    return cd_color

def execute(options, net):
    target_domain = options.get("DOMAIN")
    wordlist = options.get("WORD")
    threads = str(options.get("THREAD"))

    smf.printf(
        f"\n[*] {CC.YELLOW}Starting SUBDOMAIN ENUMERATION for =>{CC.RESET}",
        target_domain,
    )

    try:
        resp = net.DNSD(domain, wordlist, con=threads, timeout=3.0)
        if resp.ok:
            code = code_color(resp)
            act = resp.url_active
            serv = resp.get_headers("server")
            ct = resp.get_headers("Content-Type")
        
            smf.printf(f"\n[*] {CC.YELLOW}INFO => STATUS | URL | SERVER | Content-Type\n{CC.RESET}")
            for url in resp.url:
                smf.printf(f"[*] {CC.GREEN}FOUND =>{CC.RESET} {code} | {CC.GREEN}{url:<40}{CC.RESET} | {CC.YELLOW}{serv:<20}{CC.RESET} | {CC.CYAN}{ct}{CC.RESET}")

        smf.printf(f"\n[✓]{CC.YELLOW} Enumeration complete. Found {act} active subdomain.{CC.RESET}")
    except KeyboardInterrupt:
        smf.printf("\n[✓] Sub Enumeration is stopped")
    except Exception as e:
        smf.printf(f"[!] {CC.RED}An IPC module error occurred{CC.RESET}")
        smf.printd("Subenum IPC error", e, level="ERROR")
    finally:
        smf.printf(
            f"[✓] {CC.GREEN}SubDomain Enumeration daemon successfully stopped and cleaned up.{CC.RESET}"
)
