# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author: zxelzy

import os
import smf
import time
import signal

from typing import Set


class PIDManager:
    """Centralized PID Manager & Zombie Reaper"""

    _tracked_pids: Set[int] = set()

    @classmethod
    def register(cls, pid: int) -> None:
        """Registering new PID to registry tracking"""
        if pid > 0:
            cls._tracked_pids.add(pid)

    @classmethod
    def reap_zombie(cls) -> None:
        """Non-blocking check on all registered PID"""
        dead_pids = set()

        for pid in list(cls._tracked_pids):
            try:
                # os.WNOHANG: Non-blocking call
                # pid_reaped > 0 means the process is dead
                pid_reaped, _ = os.waitpid(pid, os.WNOHANG)
                if pid_reaped != 0:
                    dead_pids.add(pid)
            except ChildProcessError:
                # PID is no longer an active child process
                dead_pids.add(pid)
            except Exception as e:
                smf.printd(
                    "Failed to reap zombie process throwing exception", e, level="WARN"
                )

        cls._tracked_pids -= dead_pids

    @classmethod
    def cleanup(cls, timeout: float = 3.0) -> None:
        """Perform process cleanup with a non-blocking timeout mechanism"""
        for pid in list(cls._tracked_pids):
            try:
                # Send SIGTERM (graceful shutdown)
                os.kill(pid, signal.SIGTERM)

                # Non-blocking polling with time limit
                start_time = time.time()
                killed_gracefully = False

                while time.time() - start_time < timeout:
                    # os.WNOHANG prevents waitpid from blocking
                    pid_reaped, _ = os.waitpid(pid, os.WNOHANG)
                    if pid_reaped == pid:
                        killed_gracefully = True
                        break

                    time.sleep(0.1)  # Prevent CPU spin-lock

                if not killed_gracefully:
                    smf.printd(
                        f"PID {pid} ignored SIGTERM. Fallback to SIGKILL.", level="WARN"
                    )
                    os.kill(pid, signal.SIGKILL)
                    os.waitpid(pid, 0)

            except ProcessLookupError:
                pass
            except ChildProcessError:
                smf.printd(f"PID {pid} is not a child process. Skipping.", level="WARN")
            except Exception as e:
                smf.printd(f"Failed to cleanup process {pid}", e, level="ERROR")

        cls._tracked_pids.clear()

    @classmethod
    def prepare(cls, new_pid: int) -> None:
        """Recording new process PID & Killing zombie process PID"""
        cls.reap_zombie()
        cls.register(new_pid)
