# MIT License.
# Copyright (c) 2026 Storm Framework
# See LICENSE file in the project root for full license information.
import requests
from app.utility.colors import C
from app.utility.spin import StormSpin

SUBDOMAINS = [
    "www",
    "dev",
    "api",
    "mail",
    "blog",
    "test",
    "staging",
    "admin",
    "ftp",
    "vpn",
    "server",
    "cms",
    "cdn",
    "static",
    "app",
    "auth",
    "assets",
    "img",
    "images",
    "media",
    "beta",
    "demo",
    "panel",
    "dashboard",
    "internal",
    "intranet",
    "ssh",
    "git",
    "gitlab",
    "repo",
    "status",
    "cpanel",
    "webmail",
    "cpcalendars",
]


REQUIRED_OPTIONS = {"DOMAIN": ""}


def execute(options):
    """Searching for active subdomains"""
    target_domain = options.get("DOMAIN")

    target_domain = (
        target_domain.replace("http://", "").replace("https://", "").strip("/")
    )
    print(f"{C.HEADER} SUBDOMAIN ENUMERATION for {target_domain}")

    found_count = 0
    PROTOCOLS = ["http", "https"]
    with StormSpin():
        for subdomain in SUBDOMAINS:
            for proto in PROTOCOLS:
                url = f"{proto}://{subdomain}.{target_domain}"
                try:
                    response = requests.head(url, timeout=3, allow_redirects=True)
                    status_code = response.status_code
                    if status_code < 400 or status_code == 403:
                        print(
                            f"{C.SUCCESS}[✓] Subdomain Found: {url} - Status: {status_code}"
                        )
                        found_count += 1

                except KeyboardInterrupt:
                    return
                except requests.exceptions.RequestException:
                    pass
                except Exception as e:
                    print(f"{C.ERROR}[!] ERROR on {url}: {e}{C.RESET}")
                    continue

    print(f"{C.SUCCESS}\n[✓] Subdomain active: {found_count}")

    if found_count == 0:
        print(f"{C.ERROR} No active subdomains found with list: {found_count}")
