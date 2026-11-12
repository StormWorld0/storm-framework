import os
import smf
import time
import signal
import threading
from typing import Dict


class PIDManager:
    """Centralized PID Manager & Zombie Reaper (Thread-Safe & Concurrent)"""

    # Mapping structure: {"id": pid}
    _tracked_processes: Dict[str, int] = {}
    _lock = threading.Lock()

    @classmethod
    def _kill_process_safely(cls, pid: int) -> None:
        """Internal helper to kill a specific PID with a grace period."""
        try:
            os.kill(pid, signal.SIGTERM)

            # Give yourself a moment to exit gracefully
            start_time = time.time()
            while time.time() - start_time < 2.0:
                reaped, _ = os.waitpid(pid, os.WNOHANG)
                if reaped == pid:
                    return
                time.sleep(0.1)

            # Fallback to SIGKILL if ignoring SIGTERM
            os.kill(pid, signal.SIGKILL)
            os.waitpid(pid, 0)
        except (ChildProcessError, OSError):
            pass

    @classmethod
    def reap_zombie(cls) -> None:
        """Cleaning up dead processes"""
        with cls._lock:
            dead_ids = []
            for id, pid in cls._tracked_processes.items():
                try:
                    pid_reaped, _ = os.waitpid(pid, os.WNOHANG)
                    if pid_reaped != 0:
                        dead_ids.append(id)
                except ChildProcessError:
                    dead_ids.append(id)
                except Exception as e:
                    smf.printd(f"Failed to reap zombie PID {pid}", e, level="WARN")

            for id in dead_ids:
                cls._tracked_processes.pop(id, None)

    @classmethod
    def cleanall(cls, timeout: float = 3.0) -> None:
        """Perform parallel process cleanup with broadcast mechanism"""
        with cls._lock:
            if not cls._tracked_pids:
                return

            pids_to_kill = list(cls._tracked_processes.values())

        # Throws SIGTERM to all processes
        for pid in pids_to_kill:
            try:
                os.kill(pid, signal.SIGTERM)
            except OSError:
                pass

        # Wait for the results together (Paralel Polling)
        start_time = time.time()
        alive_pids = set(pids_to_kill)

        while alive_pids and (time.time() - start_time < timeout):
            for pid in list(alive_pids):
                try:
                    pid_reaped, _ = os.waitpid(pid, os.WNOHANG)
                    if pid_reaped == pid:
                        alive_pids.remove(pid)
                except ChildProcessError:
                    alive_pids.remove(pid)
            time.sleep(0.1)  # Prevent CPU spin-lock

        # Fallback to SIGKILL
        for pid in alive_pids:
            try:
                smf.printd(
                    f"PID {pid} ignored SIGTERM. Fallback to SIGKILL.", level="WARN"
                )
                os.kill(pid, signal.SIGKILL)
                os.waitpid(pid, 0)
            except OSError:
                pass

        with cls._lock:
            cls._tracked_pids.clear()

    @classmethod
    def prepare(cls, id: str, pid: int) -> None:
        """
        Register or replace processes based on custom id
        If custom_id has already been registered, the old process will be killed
        automatically first (preventing orphan/double spawn).
        """
        if pid <= 0:
            return

        with cls._lock:
            # If the ID already exists, clear the old process.
            if custom_id in cls._tracked_processes:
                old_pid = cls._tracked_processes[id]
                smf.printd(
                    f"Process '{id}' already exists (PID {old_pid}). Replacing with new PID {pid}.",
                    level="WARN",
                )
                cls._kill_process_safely(old_pid)

            # Note the new PID
            cls._tracked_processes[id] = pid

    @classmethod
    def kill_id(cls, id: str) -> bool:
        """Kills specific processes based on custom id."""
        with cls._lock:
            pid = cls._tracked_processes.pop(id, None)

        if pid:
            smf.printd(f"Terminating target process '{id}' (PID {pid})", level="INFO")
            cls._kill_process_safely(pid)
            return True

        smf.printd(f"Process ID '{id}' not found in registry.", level="DEBUG")
        return False
