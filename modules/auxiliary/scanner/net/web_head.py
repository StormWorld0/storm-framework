import requests
import re
from app.utility.colors import C

REQUIRED_OPTIONS = {"URL": ""}


def execute(options):
    """Checking the security header of a URL."""
    target_url = options.get("URL")

    if not target_url.startswith(("https://", "http://")):
        target_url = "https://" + target_url
    print(f"{C.HEADER} CHECKING THE HEADER: {target_url}")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        }
        response = requests.get(target_url, headers=headers, timeout=5)
        for header, value in response.headers.items():
            print(f"  {C.HEADER}{header}:{C.RESET} {value}")

        print(f"{C.HEADER} \n--- HEADER SECURITY ANALYSIS ---\n")

        # check server
        server = response.headers.get("Server")
        if server:
            if re.search(r"\d+\.\d+", server):
                print(f"{C.ERROR}[!] Server Version Exposed: {server}{C.RESET}")
            else:
                print(
                    f"{C.SUCCESS}[✓] Server identified without version disclosure: {server}{C.RESET}"
                )
        else:
            print(f"{C.SUCCESS}[✓] Server header not found or hidden.{C.RESET}")

        # Check X-Powered-By to find out the backend server
        xpb = response.headers.get("X-Powered-By")
        if xpb:
            print(f"{C.ERROR}[!] Backend Technology Exposed: {xpb}{C.RESET}")
        else:
            print(f"{C.SUCCESS}[✓] X-Powered-By header not present.{C.RESET}")

        # Check X-Frame-Options Security Header (Clickjacking Prevention)
        xfo = response.headers.get("X-Frame-Options")
        if "X-Frame-Options" not in response.headers:
            print(
                f"{C.ERROR}[!] X-Frame-Options header is MISSING. Potential for Clickjacking.{C.RESET}"
            )
        else:
            print(f"{C.SUCCESS}[✓] X-Frame-Options: {xfo}.{C.RESET}")

        # Strict-Transport-Security (Downgrade Prevention)
        hsts = response.headers.get("Strict-Transport-Security")
        if (
            "Strict-Transport-Security" not in response.headers
            and target_url.startswith("https://")
        ):
            print(
                f"{C.ERROR}[!] The Strict-Transport-Security header is MISSING. HTTP Downgrade Risks.{C.RESET}"
            )
        else:
            print(f"{C.SUCCESS}[✓] Strict-Transport-Security: {hsts}.{C.RESET}")

        # 1. Check Content-Security-Policy (XSS Prevention)
        csp = response.headers.get("Content-Security-Policy")
        if "Content-Security-Policy" not in response.headers:
            print(
                f"{C.ERROR}[!] CSP Header MISSING. Risk of Cross-Site Scripting (XSS).{C.RESET}"
            )
        else:
            print(f"{C.SUCCESS}[✓] Content-Security-Policy: {csp}.{C.RESET}")

        # 2. Cek X-Content-Type-Options (Pencegahan MIME Sniffing)
        if response.headers.get("X-Content-Type-Options") != "nosniff":
            print(
                f"{C.ERROR}[!] X-Content-Type-Options is MISSING or misconfigured. Risk of MIME Sniffing.{C.RESET}"
            )
        else:
            print(f"{C.SUCCESS}[✓] X-Content-Type-Options: nosniff.{C.RESET}")

        # 3. Cek Referrer-Policy (Pencegahan Kebocoran Data URL)
        rp = response.headers.get("Referrer-Policy")
        if "Referrer-Policy" not in response.headers:
            print(
                f"{C.ERROR}[!] Referrer-Policy header MISSING. Potential data leakage via Referrer header.{C.RESET}"
            )
        else:
            print(f"{C.SUCCESS}[✓] Referrer-Policy: {rp}.{C.RESET}")

        set_cookie = response.headers.get("Set-Cookie")
        if set_cookie:
            cookie_lower = set_cookie.lower()

            if "httponly" not in cookie_lower:
                print(f"{C.ERROR}[!] Cookie missing 'HttpOnly' flag.{C.RESET}")

            if target_url.startswith("https://") and "secure" not in cookie_lower:
                print(f"{C.ERROR}[!] Cookie missing 'Secure' flag.{C.RESET}")

            if "samesite" not in cookie_lower:
                print(f"{C.ERROR}[!] Cookie missing 'SameSite' flag.{C.RESET}")

    except KeyboardInterrupt:
        return
    except requests.exceptions.RequestException as e:
        print(f"{C.ERROR}[x] ERROR WHILE CONNECTING TO {target_url}: {e}{C.RESET}\n")

    print(f"{C.HEADER} ---------------------------------------")
