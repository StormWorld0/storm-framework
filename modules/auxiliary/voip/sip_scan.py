import subprocess
import threading
import os
import smf

from lib.roar.calling import call_bin

metadata = {
    "Name": "Session Initiation Protocol Scanning",
    "Description": """
Monitor SIP systems before conducting DoS attacks on 
VoIP traffic. Uses multiple dynamic protocols as needed 
(UDP, TCP, TLS) to handle different protocols in the 
target SIP system.
""",
    "Author": ["zxelzy"],
    "Action": [
        ["Scanner", {"Description": "VoIP system scanning"}],
        ["SIP", {"Description": "Signaling control protocol"}],
    ],
    "DefaultAction": "Scanner",
    "License": "SMF License",
    "Date": "2025-08-07",
}

REQUIRED_OPTIONS = {
    "IP": "",
    "PORT": "standar port 5060/5061",
    "PROTOCOL": "example (udp, tls, tcp)",
    "THREAD": "example: 50",
}


def execute(options):
    """
    Eksekusi modul scanner VoIP dengan mendelegasikan I/O intensif ke binary Go.
    """
    # 1. Ekstraksi dan sanitasi parameter
    ip_target = options.get("IP")
    port = str(options.get("PORT"))
    protocol = str(options.get("PROTOCOL")).lower()
    threads = str(options.get("THREAD"))

    # Resolusi path absolut ke binary
    binary = call_bin("sip_scan")

    if not binary:
        smf.printf(f"[!] Binary not found =>", binary)
        return

    # 2. Konstruksi argumen Command-Line
    cmd = [binary, "-p", port, "-proto", protocol, "-c", threads]

    smf.printf(f"[*] External process initialization: {' '.join(cmd)}")

    try:
        # 3. Spawning Child Process via PIPE
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        # 4. Injeksi Data Dinamis (Single IP, CIDR, atau File)
        if ip_target:
            if os.path.isfile(ip_target):
                # Eksekusi stream I/O jika target berupa file (Skala Besar)
                smf.printf(
                    f"[*] Streaming targets from file {ip_target} to the scanner..."
                )
                with open(ip_target, "r") as f:
                    for line in f:
                        clean_line = line.strip()
                        if clean_line:
                            process.stdin.write(f"{clean_line}\n")
            else:
                # Eksekusi single target
                smf.printf(f"[*] Sending target {ip_target} to the scanner...")
                process.stdin.write(f"{ip_target}\n")

        # EOF trigger untuk binary Go agar wait group dapat ditutup
        process.stdin.close()

        # 5. Threaded Async Output Reader
        def read_output(pipe, prefix=""):
            for line in iter(pipe.readline, ""):
                if line:
                    smf.printf(f"{prefix} {line.strip()}")
            pipe.close()

        stdout_thread = threading.Thread(
            target=read_output, args=(process.stdout, "[GO]")
        )
        stderr_thread = threading.Thread(target=read_output, args=(process.stderr, "[!]"))

        stdout_thread.start()
        stderr_thread.start()

        # Sinkronisasi proses sebelum mengembalikan state ke REPL
        process.wait()
        stdout_thread.join()
        stderr_thread.join()

        smf.printf("[*] The scanner module has finished executing.")

    except Exception as e:
        smf.printf("[!] An IPC error occurred")
        smf.printd("A VOIP IPC error occurred", e, level="ERROR")
