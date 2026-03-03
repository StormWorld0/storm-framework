# MIT License.
# Copyright (c) 2026 Storm Framework
# See LICENSE file in the project root for full license information.


import subprocess
import os
import sys
from app.utility.colors import C


def run_verif():
    bin_p = "external/source/binary/check"
    if not os.path.exists(bin_p):
        print(f"[-] ERROR: Rust binary not found in {bin_p}")
        sys.exit(1)
    print(f"[*] [INTEGRITY] Launching Storm Engine")
    try:
        result = subprocess.run([bin_p])

        if result.returncode != 0:
            print(f"\n[-] CRITICAL: Reinstall Storm for security.)")
            sys.exit(result.returncode)

        return True

    except Exception as e:
        print(f"[-] ERROR during execution: {e}")
        sys.exit(1)


def check_critical_files():
    if not os.path.exists(".env"):
        print(f"{C.ERROR}[!] CRITICAL: Integrity Key (.env) is missing!{C.RESET}")
        print(
            f"[*] Storm cannot verify the database signature without your unique keys."
        )
        print(
            f"[*] Please run the installation/recovery script to regenerate your keys."
        )
        sys.exit(1)
