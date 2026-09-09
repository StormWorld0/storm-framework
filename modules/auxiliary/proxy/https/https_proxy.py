import subprocess
import smf
import os

from rootmap import ROOT
from apps.utility.colors import CC
from lib.roar.calling import call_bin

metadata = {
    "Name": "Forward proxy https",
    "Description": """
Performing MITM on network traffic
using the Deep Packet Inspection (DPI) mechanism
to disassemble the body and read it in plaintext.

Using proxy logic to capture specific traffic
in the network and can be implemented more dynamically.
""",
    "Author": ["zxelzy"],
    "Action": [
        ["Proxy", {"Description": "Reading headers and bodies"}],
        ["DPI", {"Description": "Perform inspection in body header"}],
        ["MITM", {"Description": "Perform network packet reconnaissance"}],
    ],
    "DefaultAction": "Proxy",
    "License": "SMF License",
    "Date": "2025-04-16",
}
REQUIRED_OPTIONS = {"IP": "ip address standar = 0.0.0.0", "PORT": "standar port = 6443"}


def output_stream(line: str) -> str:
    """
    Inspects each line of stdout and injects ANSI color codes
    based on the log pattern (keyword).
    """
    if "[ERROR]" in line or "[FATAL]" in line:
        return f"\n{CC.RED}{line}{CC.RESET}"
    elif "[WARN]" in line or "[WARNING]" in line:
        return f"{CC.YELLOW}{line}{CC.RESET}"
    elif "[START]" in line:
        return f"{CC.GREEN}{line}{CC.RESET}\n"
    elif "[INIT]" in line:
        return f"{CC.GREEN}{line}{CC.RESET}"
    elif "[DPI-REQ]" in line:
        return f"\n{CC.CYAN}{line}{CC.RESET}"
    elif "[DPI-RES]" in line:
        return f"\n{CC.CYAN}{line}{CC.RESET}"
    elif "[DPI-BYPASS]" in line:
        return f"{CC.WHITE}{line}{CC.RESET}"
    elif "[DPI-INFO]" in line or "INFO" in line or "[DPI-REQ-INFO]" in line:
        return f"{CC.YELLOW}{line}{CC.RESET}"
    elif "==========" in line or "====================" in line:
        return f"{CC.YELLOW}{line}{CC.RESET}"

    return line  # return line = Standard output


def execute(options):

    # Take input
    ip = options.get("IP")
    port = options.get("PORT")

    # Binary path
    bin_path = call_bin("https_proxy")

    # Binary validation
    if not bin_path:
        smf.printf(f"{CC.RED}[!] Binary not found.{CC.RESET}", bin_path)
        return

    # Storm Framework internal CA Root Path
    ca_cert_path = os.path.join(ROOT, "config", "smf_ca.crt")
    ca_key_path = os.path.join(ROOT, "config", "smf_ca.key")

    # Enter the required data
    cmd = [
        bin_path,
        "-cert",
        ca_cert_path,
        "-key",
        ca_key_path,
        "-ip",
        ip,
        "-port",
        port,
    ]

    # bufsize=1 (Line buffered) ensures every \n is sent directly to Python's stdout
    # without waiting for the OS memory buffer to fill up.
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
    )

    try:  # Loop of output stream
        for line in process.stdout:
            stream_line = output_stream(line)
            smf.printf(stream_line, end="", flush=True)

    # Monitor CTRL + C
    except KeyboardInterrupt:
        smf.printf(f"\n{CC.YELLOW}[*] Proxy stopped.{CC.RESET}")

    # Catch error exception
    except Exception as e:
        smf.printf(f"\n{CC.RED}[!] Error https_proxy =>{CC.RESET}", e)
        smf.printd(f"Exception https_proxy", e, level="ERROR")

    # Stop the binary process
    finally:
        if process.poll() is None:  # Check the process in the background
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()

        smf.printf(
            f"{CC.GREEN}[*] Proxy daemon successfully stopped and cleaned up.{CC.RESET}"
        )
