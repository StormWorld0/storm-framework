import ctypes
import smf
from apps.utility.colors import *


def libcrp():
    try:
        crypto = ctypes.CDLL("libcrypto.so.3")

        class AES_KEY(ctypes.Structure):
            _fields_ = [("rd_key", ctypes.c_uint * 60), ("rounds", ctypes.c_int)]

        crypto.AES_set_decrypt_key.argtypes = [
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.POINTER(AES_KEY),
        ]
        crypto.AES_decrypt.argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.POINTER(AES_KEY),
        ]

        return crypto
    except OSError as e:
        smf.printf(
            f"[*] {CC.YELLOW}This module is not supported on this platform.{CC.RESET}"
        )
        smf.printd("Failed to load libcrypto.so.3", e, level="INFO")
        return None


def libc():
    try:
        return ctypes.CDLL("libc.so.6", use_errno=True)
    except OSError as e:
        smf.printf(f"{CC.YELLOW}This module is not supported on this platform.{CC.RESET}")
        smf.printd("Failed to load libc.so.6", e, level="INFO")
        return None
