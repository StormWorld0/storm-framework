import os
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
    def reap_zombies(cls) -> None:
        """Non-blocking check pada seluruh PID terdaftar"""
        dead_pids = set()

        for pid in list(cls._tracked_pids):
            try:
                # os.WNOHANG: Non-blocking call
                # pid_reaped > 0 artinya proses sudah mati & berhasil di-reap dari OS
                pid_reaped, _ = os.waitpid(pid, os.WNOHANG)
                if pid_reaped != 0:
                    dead_pids.add(pid)
            except ChildProcessError:
                # PID sudah bukan child process aktif / sudah di-reap oleh OS
                dead_pids.add(pid)
            except Exception:
                pass

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
            except (ProcessLookupError, ChildProcessError):
                pass
            except Exception:
                # Jika SIGTERM gagal, paksa dengan SIGKILL
                try:
                    os.kill(pid, signal.SIGKILL)
                    os.waitpid(pid, 0)
                except Exception:
                    pass

        cls._tracked_pids.clear()

    @classmethod
    def prepare(cls, new_pid: int) -> None:
        """Mencatat PID proses baru & Mematikan PID proses zombie"""
        cls.reap_zombies()
        cls.register(new_pid)
