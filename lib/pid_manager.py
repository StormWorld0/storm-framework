# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author: zxelzy

import os
import smf
import time
import signal
import threading

from typing import Set

class PIDManager:
    """Centralized PID Manager & Zombie Reaper (Thread-Safe & Concurrent)"""
    _tracked_pids: Set[int] = set()
    _lock = threading.Lock() # 🟢 THE MAIN KEY TO PREVENTING RACE CONDITION

    @classmethod
    def register(cls, pid: int) -> None:
        """Registering a new process PID"""
        if pid > 0:
            with cls._lock:
                cls._tracked_pids.add(pid)

    @classmethod
    def reap_zombie(cls) -> None:
        """Cleaning up dead processes"""
        with cls._lock:
            dead_pids = set()
            for pid in list(cls._tracked_pids):
                try:
                    pid_reaped, _ = os.waitpid(pid, os.WNOHANG)
                    if pid_reaped != 0:
                        dead_pids.add(pid)
                except ChildProcessError:
                    dead_pids.add(pid)
                except Exception as e:
                    smf.printd(f"Failed to reap zombie PID {pid}", e, level="WARN")

            # Sekarang operasi ini aman dari tabrakan antar thread
            cls._tracked_pids -= dead_pids

    @classmethod
    def cleanup(cls, timeout: float = 3.0) -> None:
        """Perform parallel process cleanup with broadcast mechanism"""
        with cls._lock:
            if not cls._tracked_pids:
                return
            
            pids_to_kill = list(cls._tracked_pids)
            
        # 1. BROADCAST SIGTERM KE SEMUA PROSES SEKALIGUS (Tidak pakai nunggu)
        for pid in pids_to_kill:
            try:
                os.kill(pid, signal.SIGTERM)
            except OSError:
                pass

        # 2. TUNGGU HASILNYA SECARA BERSAMAAN (Paralel Polling)
        start_time = time.time()
        alive_pids = set(pids_to_kill)

        # Maksimal fungsi ini hanya makan waktu {timeout} detik untuk SEMUA proses
        while alive_pids and (time.time() - start_time < timeout):
            for pid in list(alive_pids):
                try:
                    pid_reaped, _ = os.waitpid(pid, os.WNOHANG)
                    if pid_reaped == pid:
                        alive_pids.remove(pid)
                except ChildProcessError:
                    alive_pids.remove(pid)
            
            time.sleep(0.1) # Prevent CPU spin-lock

        # 3. SAPU BERSIH SISANYA (SIGKILL)
        for pid in alive_pids:
            try:
                smf.printd(f"PID {pid} ignored SIGTERM. Fallback to SIGKILL.", level="WARN")
                os.kill(pid, signal.SIGKILL)
                os.waitpid(pid, 0)
            except OSError:
                pass

        with cls._lock:
            cls._tracked_pids.clear()

    @classmethod
    def prepare(cls, new_pid: int) -> None:
        """Note the PID of the process being run"""
        cls.reap_zombie()
        cls.register(new_pid)
