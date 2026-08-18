# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author: zxelzy

import os
import smf
import signal
from typing import Set


class PIDManager:
    """Centralized PID Manager & Zombie Reaper."""

    _tracked_pids: Set[int] = set()

    @classmethod
    def register(cls, pid: int) -> None:
        """Mendaftarkan PID baru ke registry tracking."""
        if pid > 0:
            cls._tracked_pids.add(pid)

    @classmethod
    def reap_zombie(cls) -> None:
        """Non-blocking check pada seluruh PID terdaftar"""
        dead_pids = set()

        for pid in list(cls._tracked_pids):
            try:
                # os.WNOHANG: Non-blocking call
                # pid_reaped > 0 artinya proses sudah mati
                pid_reaped, _ = os.waitpid(pid, os.WNOHANG)
                if pid_reaped != 0:
                    dead_pids.add(pid)
            except ChildProcessError:
                # PID sudah bukan child process aktif
                dead_pids.add(pid)
            except Exception as e:
                smf.printd(
                    "Failed to reap zombie process throwing exception", e, level="WARN"
                )

        cls._tracked_pids -= dead_pids

    @classmethod
    def cleanup(cls) -> None:
        """Melakukan pembersihan proses yang sebelumnya di aktifkan"""
        for pid in list(cls._tracked_pids):
            try:
                # Kirim SIGTERM agar child exit secara normal
                os.kill(pid, signal.SIGTERM)
                # Reaping langsung dari Kernel
                os.waitpid(pid, 0)
            except (ProcessLookupError, ChildProcessError) as e:
                smf.printd("ProcessLookupError, ChildProcessError", e, level="WARN")
            except Exception as e:
                smf.printd(
                    "Failed to execute SIGTERM process. Fallback SIGKILL", e, level="WARN"
                )
                # Fallback SIGKILL
                try:
                    os.kill(pid, signal.SIGKILL)
                    os.waitpid(pid, 0)
                except Exception as e:
                    smf.printd("Failed to SIGKILL process", e, level="WARN")

        return cls._tracked_pids.clear()

    @classmethod
    def prepare(cls, new_pid: int) -> None:
        """Mencatat PID proses baru & Mematikan PID proses zombie"""
        cls.reap_zombie()
        cls.register(new_pid)
