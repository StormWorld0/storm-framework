# --- https://github.com/StormWorld0/storm-framework ---
# SMF License
# copyright (c) 2026
# Complete information about the License is in the root directory.
# Author: zxelzy

import os
import smf
import ctypes
import fcntl
import struct

from rootmap import ROOT
from dotenv import dotenv_values
from lib.roar.crs.net_api import Socket

# --- Struct Definition for Syscalls ---


class Statfs(ctypes.Structure):
    _fields_ = [
        ("f_type", ctypes.c_long),
        ("f_bsize", ctypes.c_long),
        ("f_blocks", ctypes.c_long),
        ("f_bfree", ctypes.c_long),
        ("f_bavail", ctypes.c_long),
        ("f_files", ctypes.c_long),
        ("f_ffree", ctypes.c_long),
        ("f_fsid", ctypes.c_long * 2),
        ("f_namelen", ctypes.c_long),
        ("f_frsize", ctypes.c_long),
        ("f_flags", ctypes.c_long),
        ("f_spare", ctypes.c_long * 4),
    ]


class Sysinfo(ctypes.Structure):
    _fields_ = [
        ("uptime", ctypes.c_long),
        ("loads", ctypes.c_ulong * 3),
        ("totalram", ctypes.c_ulong),
        ("freeram", ctypes.c_ulong),
        ("sharedram", ctypes.c_ulong),
        ("bufferram", ctypes.c_ulong),
        ("totalswap", ctypes.c_ulong),
        ("freeswap", ctypes.c_ulong),
        ("procs", ctypes.c_ushort),
        ("pad", ctypes.c_ushort),
        ("totalhigh", ctypes.c_ulong),
        ("freehigh", ctypes.c_ulong),
        ("mem_unit", ctypes.c_uint),
        (
            "_f",
            ctypes.c_char
            * (20 - ctypes.sizeof(ctypes.c_long) - ctypes.sizeof(ctypes.c_short)),
        ),
    ]


def is_docker() -> bool:
    """
    Performs heuristic validation via syscall to detect the Docker environment.
    This function is 100% unprivileged (can be run by root or a regular user).
    """
    score = 0
    threshold = 60

    smf.printd("Starting the environment validation service", level="INFO")
    try:
        libc = ctypes.CDLL("libc.so.6")
    except OSError:
        return False

    # SYSFS MAGIC NUMBER CHECK (Syscall: statfs) - Weight: 40
    # Unprivileged: All users have read-only access to '/' metadata.
    if libc:
        OVERLAYFS_SUPER_MAGIC = 0x794C7630
        AUFS_SUPER_MAGIC = 0x61756673

        statfs_buf = Statfs()
        if libc.statfs(b"/", ctypes.byref(statfs_buf)) == 0:
            if statfs_buf.f_type in (OVERLAYFS_SUPER_MAGIC, AUFS_SUPER_MAGIC):
                smf.printd("Syscall => STATF True > Score 40", level="INFO")
                smf.printf("Syscall => STATF True > Score 40")
                score += 40

    # PROCESS ENTROPY CHECK (Syscall: sysinfo) - Weight: 30
    # Unprivileged: Sysinfo is open for user-space reading.
    if libc:
        sysinfo_buf = Sysinfo()
        if libc.sysinfo(ctypes.byref(sysinfo_buf)) == 0:
            if sysinfo_buf.procs < 50:
                smf.printd("Syscall => SYSINF True > Score 30", level="INFO")
                smf.printf("Syscall => SYSINF True > Score 30")
                score += 30

    # MOUNT NAMESPACE ISOLATION CHECK (Syscall: stat on /proc/self/ns/mnt) - Weight: 30
    # Comparing this process's mount namespace inode with PID 1 (host init)
    if libc:
        self_mnt = os.stat("/proc/self/ns/mnt").st_ino
        init_mnt = os.stat("/proc/1/ns/mnt").st_ino
        if self_mnt != init_mnt:
            smf.printd(
                "Syscall => Mount Namespace Isolation True > Score 30", level="INFO"
            )
            smf.printf("Syscall => Mount Namespace Isolation True > Score 30")
            score += 30

    # MAC ADDRESS OUI CHECK (Kernel IOCTL) - Weight: 30
    # Unprivileged: Reading MAC address (SIOCGIFHWADDR) does not require CAP_NET_ADMIN,
    # just need open() access to a regular socket.
    def get_mac_address_ioctl(ifname: str) -> str:
        sock = Socket()
        s = sock.socket(sock.AF_INET, sock.SOCK_DGRAM)
        try:
            info = fcntl.ioctl(
                s.fileno, 0x8927, struct.pack("256s", bytes(ifname, "utf-8")[:15])
            )
            return ":".join("%02x" % b for b in info[18:24])
        except OSError:
            return ""
        finally:
            sock.close()

    interfaces = ["eth0"]
    matched_docker = False

    for iface in interfaces:
        mac = get_mac_address_ioctl(iface)
        if mac.startswith("02:42"):
            matched_docker = True
            smf.printd(f"Syscall => IOCTL True ({iface}) > Score 30", level="INFO")
            score += 30
            break

    return score >= threshold


def is_this_docker() -> bool:
    path = os.path.join(ROOT, ".env")
    if not os.path.isfile(path)
        return False
    
    cfg = dotenv_values(path)
    return cfg.get("DOCKER", "False").lower() == "true"
