# MIT License.
# Copyright (c) 2026 Storm Framework
# See LICENSE file in the project root for full license information.


import subprocess
import os

from rootmap import ROOT

REQUIRED_OPTIONS = {
    "INTERFACE": "example: eth0",
}


def execute(options):
    iface = options.get("INTERFACE")
    bin_path = os.path.join(ROOT, "external", "source", "binary", "dpi_netspy")
    if not os.path.isfile(bin_path):
        print(f"[!] ERROR: Binary not found {bin_path}.")
        return False
    print(f"[*] Run Go-Sniffer on interface: {iface}")

    try:
        # Calling a Go binary with interface arguments
        proc = subprocess.Popen(
            [bin_path, iface],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        while True:
            line = proc.stdout.readline()
            if not line:
                break
            print(line.strip())

    except KeyboardInterrupt:
        print("\n[*] Stop Sniffer...")
        proc.terminate()
    except Exception as e:
        print(f"[!] ERROR: {e}")

    return True
