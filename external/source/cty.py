import smf
from apps.utility.colors import *

def ctyp()
    try:
        import ctypes
        crypto = ctypes.CDLL("libcrypto.so.3")
        return crypto
    except Exception as e:
        smf.printf(f"[*] {CC.YELLOW}Android environment does not support this module{CC.RESET}")
        smf.printd("Error calling libcrypto to Linux", e, level="INFO")
        return None
