import ctypes
import smf
from apps.utility.colors import CC

def libc():
    try:
        return ctypes.CDLL("libcrypto.so.3")
    except OSError as e:
        smf.printf(f"[*] {CC.YELLOW}This module is not supported on this platform.{CC.RESET}")
        smf.printd("Failed to load libcrypto.so.3", e, level="INFO")
        return None
