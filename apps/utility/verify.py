import subprocess
import os
import sys
import smf

from rootmap import ROOT
from lib.roar.calling import call_bin


# Verify starting to run integrity check
def run_verif():
    # Call binary verification
    lib = call_bin("verified")

    # Check the validation of the binary file verification
    if not lib:
        smf.printd("Binary verification missing", lib, level="CRITICAL")
        smf.printf("[!] WARN => Rust binary not found in", lib)
        sys.exit(202)

    try:  # Run verification
        result = subprocess.run([lib])

        # Granular Return Code Evaluation
        if result.returncode == 203:
            # Priority 1: Pure Injection or Compound Threat (Injection + Tampering)
            smf.printf(
                "[!] Integrity detects file injection anomalies against the internal ecosystem"
            )
            smf.printd(
                "Integrity detects file Injection danger", result, level="CRITICAL"
            )
            sys.exit(result.returncode)

        elif result.returncode != 0:
            # Priority 2: Pure tampering (Modified / Missing files)
            smf.printf(
                "[!] WARNING => System refuses to boot in favor of internal integration"
            )
            smf.printd(
                "Integrity detects modified/missing files", result, level="WARNING"
            )

            # Disable boot sequence due to compromised integrity
            sys.exit(result.returncode)

        # If returncode == 0, execution continues (Safe)
        return True
    except KeyboardInterrupt:
        sys.exit(11)
    except Exception as e:
        smf.printd("INTEGRITY VERIFICATION", e, level="CRITICAL")
        smf.printf("[!] ERROR INTEGRITY CHECK =>", e, file=sys.stderr, flush=True)
        sys.exit(201)


# Check the binary integrity check file
def validate_binary_files():
    # Path to bin folder
    smf_dir = os.path.join(ROOT, "external", "source", "out", "core")
    bin_name = ["libsigned.so", "verified", "crs_engine"]

    found_map = {name: False for name in bin_name}
    failed = False

    # Loop to find binary
    for root, dirs, files in os.walk(smf_dir):
        for file in files:
            if file in found_map:
                found_map[file] = True

        if all(found_map.values()):
            break

    # Binary check loop
    for file_name, is_found in found_map.items():
        if not is_found:
            smf.printd("BINARY CORE MISSING", file_name, level="CRITICAL")
            smf.printf("[!] Binary core missing =>", file_name)
            failed = True

    return failed


# Check the Storm Framework core binary logging
def validate_binary_core():
    # Path to root folder
    bin_dir = os.path.abspath(ROOT)
    bin_names = ["smf.so"]

    found_map = {name: False for name in bin_names}
    failed = False

    # Loop to find binary
    for root, dirs, files in os.walk(bin_dir):
        for file in files:
            if file in found_map:
                found_map[file] = True

        if all(found_map.values()):
            break

    # Binary check loop
    for file_name, is_found in found_map.items():
        if not is_found:
            print(f"[!] Binary core missing => {file_name}")
            failed = True

    return failed


# Validate all core runtime files
def check_critical_files():
    error = False

    # Check binary core
    if validate_binary_core():
        error = True

    # Check binary integrity
    if validate_binary_files():
        error = True

    # Check the startup key .env file
    if not os.path.exists(".env"):
        smf.printd("FILES KEY MISSING", ".env", level="CRITICAL")
        smf.printf("STATUS: CRITICAL")
        smf.printf("MESSAGE: Integrity Key (.env) is missing!")
        smf.printf(
            "[*] Storm cannot verify the database signature without your unique keys."
        )
        smf.printf(
            "[*] Please run the installation/recovery script to regenerate your keys."
        )
        error = True

    # Stop startup if one is missing
    if error:
        sys.exit(201)
