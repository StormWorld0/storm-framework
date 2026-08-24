import subprocess
import smf
import sys

from apps.utility.colors import *
from lib.roar.calling import call_bin

metadata = {
    "Name": "OSINT for subdomains",
    "Description": """
Perform a scan on the specified subdomain
to search and find subdomains that allow for
exploited.
""",
    "Author": ["zxelzy"],
    "Action": [
        ["Sub Enumeration", {"Description": "Searching for valid subdomains"}],
        ["Scanner", {"Description": "Searching for sensitive subdomains"}],
    ],
    "DefaultAction": "Scanner",
    "License": "SMF License",
    "Date": "2026-04-20",
}
REQUIRED_OPTIONS = {
    "DOMAIN": "ex: google.com",
    "WORD": "Path to wordlist subdomain",
    "THREAD": "default 1",
}


def output_stream(line: str) -> str:
    """Color log stdout"""
    if "STATUS" in line:
        return f"\n[*] {CC.YELLOW}INFO => {line}{CC.RESET}\n"

    if "FOUND =>" in line:
        return f"[✓] {CC.GREEN}{line}{CC.RESET}"

    if "Enumeration" in line:
        return f"\n[✓] {CC.YELLOW}{line}{CC.RESET}"

    if "Error" in line:
        return f"[!] {CC.RED}{line}{CC.RESET}"

    return line


def render_progress_bar(percent: int, current: int, total: int, width: int = 30) -> str:
    """Menggambar visualisasi progress bar kustom"""
    pos = int((percent * width) / 100)
    bar = "■" * pos + " " * (width - pos)
    return f"\r\033[K{CC.YELLOW}Progress =>{CC.RESET} [ {CC.CYAN}{bar}{CC.RESET} ] {CC.WHITE}{percent}% ({current}/{total}){CC.RESET}"


def execute(options):
    target_domain = options.get("DOMAIN")
    wordlist_path = options.get("WORD")
    threads = str(options.get("THREAD"))

    binary = call_bin("dns_sub_enum")

    if not binary:
        smf.printf(f"[!] {CC.YELLOW}WARN => Binary not found at >{CC.RESET}", binary)
        return

    smf.printf(
        f"\n[*] {CC.YELLOW}Starting SUBDOMAIN ENUMERATION for =>{CC.RESET}",
        target_domain,
    )

    cmd = [binary, "-d", target_domain, "-w", wordlist_path, "-c", threads]

    process = None
    current_bar = ""  # Menyimpan state visual progress bar saat ini

    try:
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
        )

        for line in iter(process.stdout.readline, ""):
            cleaned_line = line.rstrip("\r\n")
            if not cleaned_line:
                continue

            # DEFENSIVE INTERCEPT: Handle jika log PROGRESS nempel di ujung log FOUND
            log_to_print = cleaned_line
            if "PROGRESS =>" in cleaned_line:
                try:
                    # Pecah baris menjadi: [log_normal, angka_progress]
                    parts = cleaned_line.split("PROGRESS =>")

                    log_to_print = parts[0].strip()
                    data_part = parts[1].strip()
                    values = [v.strip() for v in data_part.split("|")]

                    if len(values) == 3:
                        pct, crt, tot = map(int, values)
                        current_bar = render_progress_bar(pct, crt, tot)

                        # Cetak progress bar ke baris paling bawah
                        sys.stdout.write(current_bar)
                        sys.stdout.flush()
                except (ValueError, IndexError):
                    pass

                # Jika baris ini murni sinyal PROGRESS (sisi kiri kosong), skip log normal
                if not log_to_print:
                    continue

            # JIKA ADA LOG NORMAL YANG HARUS DICETAK (FOUND / STATUS / DLL)
            stream_line = output_stream(log_to_print)

            # Hapus progress bar yang sedang menggantung di bawah
            if current_bar:
                sys.stdout.write("\r\033[K")
                sys.stdout.flush()

            # Cetak log normal hasil parsing output_stream
            smf.printf(stream_line)

            # Cetak ulang progress bar tepat di bawah log yang baru saja muncul
            if current_bar:
                sys.stdout.write(current_bar)
                sys.stdout.flush()

        process.stdout.close()
        process.wait()

    except KeyboardInterrupt:
        if current_bar:
            sys.stdout.write("\r\033[K")  # Bersihkan bar saat di-stop agar prompt bersih
        smf.printf("\n[✓] Sub Enumeration is stopped")

    except Exception as e:
        if current_bar:
            sys.stdout.write("\r\033[K")
        smf.printf(f"[!] {CC.RED}An IPC module error occurred{CC.RESET}")
        smf.printd("Subenum IPC error", e, level="ERROR")

    finally:
        if process and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()

        if current_bar:
            sys.stdout.write("\r\033[K")

        smf.printf(
            f"[✓] {CC.GREEN}SubDomain Enumeration daemon successfully stopped and cleaned up.{CC.RESET}"
        )
