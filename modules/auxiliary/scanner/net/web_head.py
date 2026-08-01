import requests
import re
import sys
import smf
from apps.utility.colors import *

metadata = {
    "Name": "Searching for website header",
    "Description": """
Send a request to get the headers of an active website
and look for weaknesses or unintentionally specific versions
public or look for other loopholes to exploit weaknesses.
""",
    "Author": ["zxelzy"],
    "Action": [
        ["Scanner", {"Description": "Looking for vulnerabilities"}],
    ],
    "DefaultAction": "Scanner",
    "License": "SMF License",
    "Date": "2025-11-04",
}
REQUIRED_OPTIONS = {"URL": ""}


def execute(options, net):
    """Checking the security header of a URL."""
    url = options.get("URL")

    if not url.startswith(("https://", "http://")):
        url = "https://" + url

    smf.printf()
    smf.printf(f"{CC.CYAN} CHECKING THE HEADER =>{CC.RESET}", url)
    try:
        headers = {"User-Agent": "Storm-Framework/3.11 (X11; Linux x86_64)"}
        r = net.http_requests(
            "get", url, header=headers, timeout=5, verify=False, redirect=False
        )
        for header, value in r.header.items():
            smf.printf(f"  {CC.YELLOW}{header}:{C.RESET} {value}")

        # Cek status
        if r.ok:
            smf.printf(f"{CC.CYAN} \n--- HEADER SECURITY ANALYSIS ---{CC.RESET}\n")

            # Cek server
            server = r.get_header("Server")
            if server:
                if re.search(r"\d+\.\d+", server):
                    smf.printf(f"[!]{C.ERROR} Server Version Exposed:{C.RESET}", server)
                else:
                    smf.printf(
                        f"[✓]{C.SUCCESS} Server identified without version disclosure:{C.RESET}",
                        server,
                    )
            else:
                smf.printf(f"[✓]{C.SUCCESS} Server header not found or hidden.{C.RESET}")

            # Check X-Powered-By to find out the backend server
            xpb = r.get_header("X-Powered-By")
            if xpb:
                smf.printf(f"[!]{C.ERROR} Backend Technology Exposed:{C.RESET}", xpb)
            else:
                smf.printf(f"[✓]{C.SUCCESS} X-Powered-By header not present.{C.RESET}")

            # Check X-Frame-Options Security Header (Clickjacking Prevention)
            xfo = r.get_header("X-Frame-Options")
            if "X-Frame-Options" not in r.header:
                smf.printf(
                    f"[!]{C.ERROR} X-Frame-Options header is MISSING. Potential for Clickjacking.{C.RESET}"
                )
            else:
                smf.printf(f"[✓]{C.SUCCESS} X-Frame-Options:{C.RESET}", xfo)

            # Strict-Transport-Security (Downgrade Prevention)
            hsts = r.get_header("Strict-Transport-Security")
            if "Strict-Transport-Security" not in r.header and url.startswith("https://"):
                smf.printf(
                    f"[!]{C.ERROR} The Strict-Transport-Security header is MISSING. HTTP Downgrade Risks.{C.RESET}"
                )
            else:
                smf.printf(f"[✓]{C.SUCCESS} Strict-Transport-Security:{C.RESET}", hsts)

            # 1. Check Content-Security-Policy (XSS Prevention)
            csp = r.get_header("Content-Security-Policy")
            if "Content-Security-Policy" not in r.header:
                smf.printf(
                    f"[!]{C.ERROR} CSP Header MISSING. Risk of Cross-Site Scripting (XSS).{C.RESET}"
                )
            else:
                smf.printf(f"[✓]{C.SUCCESS} Content-Security-Policy:{C.RESET}", csp)

            # 2. Cek X-Content-Type-Options (Pencegahan MIME Sniffing)
            if r.get_header("X-Content-Type-Options") != "nosniff":
                smf.printf(
                    f"[!]{C.ERROR} X-Content-Type-Options is MISSING or misconfigured. Risk of MIME Sniffing.{C.RESET}"
                )
            else:
                smf.printf(f"[✓]{C.SUCCESS} X-Content-Type-Options:{C.RESET} nosnif")

            # 3. Cek Referrer-Policy (Pencegahan Kebocoran Data URL)
            rp = r.get_header("Referrer-Policy")
            if "Referrer-Policy" not in r.header:
                smf.printf(
                    f"[!]{C.ERROR} Referrer-Policy header MISSING. Potential data leakage via Referrer header.{C.RESET}"
                )
            else:
                smf.printf(f"[✓]{C.SUCCESS} Referrer-Policy:{C.RESET}", rp)

            set_cookie = r.get_header("Set-Cookie")
            if set_cookie:
                cookie_lower = set_cookie.lower()

                if "httponly" not in cookie_lower:
                    smf.printf(f"[!]{C.ERROR} Cookie missing 'HttpOnly' flag.{C.RESET}")

                if url.startswith("https://") and "secure" not in cookie_lower:
                    smf.printf(f"[!]{C.ERROR} Cookie missing 'Secure' flag.{C.RESET}")

                if "samesite" not in cookie_lower:
                    smf.printf(f"[!]{C.ERROR} Cookie missing 'SameSite' flag.{C.RESET}")
            smf.printf()
        else:
            smf.printf(f"[!] {CC.YELLOW}Error Response =>{CC.RESET}", r.status_code)
            smf.printf(f"[!] {CC.RED}{r.status} =>{CC.RESET}{CC.YELLOW}", r.message)
            smf.printf()

    except KeyboardInterrupt:
        return
    except requests.exceptions.RequestException as e:
        smf.printf(
            f"{C.ERROR}[x] ERROR WHILE CONNECTING TO {url} =>",
            e,
            file=sys.stderr,
            flush=True,
        )
        smf.printf()
