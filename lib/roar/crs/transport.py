# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author: zxelzy

import json
import subprocess
import threading
import uuid
import os
import smf

from ..calling import call_bin
from apps.utility.colors import CC
from lib.smf.core.manage import PIDManager as pid


class CRSD:
    """IPC (Inter-Process Communication) via Subprocess (Thread-Safe & Deadlock-Free)."""

    _process = None
    _init_lock = threading.Lock()  # Special lock for initialization/spawn
    _write_lock = threading.Lock()  # Special lock to prevent Write STDIN collisions
    _dict_lock = (
        threading.Lock()
    )  # Special lock for _pending_requests & _responses & _resp_stderr

    _pending_requests = {}
    _pending_stderr = {}
    _responses = {}
    _reader_thread = None
    _stderr_thread = None

    @classmethod
    def _turn_on_process(cls):
        # 1st Check (Fast path tanpa antre)
        if cls._process is not None and cls._process.poll() is None:
            return cls._process

        # Entering the critical initialization area
        with cls._init_lock:
            # 2nd Check (Double-checked locking pattern)
            if cls._process is not None and cls._process.poll() is None:
                return cls._process

            binary_path = call_bin("crs_engine")
            if not os.path.exists(binary_path):
                smf.printf(f"[!]{CC.YELLOW} Binary not found =>{CC.RESET}", binary_path)
                smf.printd("Binary does not exist", binary_path, level="WARN")
                return None

            # Running IPC process
            # Taking all the responses that are there
            cls._process = subprocess.Popen(
                [binary_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
            pid.prepare(cls._process.pid)

            # Turn on Background Reader
            if cls._reader_thread is None or not cls._reader_thread.is_alive():
                cls._reader_thread = threading.Thread(
                    target=cls._background_reader,
                    args=(cls._process,),
                    daemon=True,
                )
                cls._reader_thread.start()

            # Turn on Background stderr
            if cls._stderr_thread is None or not cls._stderr_thread.is_alive():
                cls._stderr_thread = threading.Thread(
                    target=cls._stderr_reader,
                    args=(cls._process,),
                    daemon=True,
                )
                cls._stderr_thread.start()

            return cls._process

    @classmethod
    def _background_reader(cls, my_proc):
        """A standalone thread that constantly reads Go stdout."""
        try:
            while my_proc and my_proc.poll() is None:
                try:
                    line = my_proc.stdout.readline()
                    if not line:
                        break

                    line_str = line.strip()
                    if not line_str.startswith("{"):
                        continue

                    res_dict = json.loads(line_str)
                    msg_id = res_dict.get("msg_id")

                    if msg_id:
                        with cls._dict_lock:
                            if msg_id in cls._pending_requests:
                                cls._responses[msg_id] = res_dict
                                cls._pending_requests[msg_id].set()

                except (BrokenPipeError, OSError, ValueError):
                    break
                except Exception as e:
                    smf.printd("Error in CRS background reader", e, level="ERROR")
                    break
        finally:
            # Only reset _process if the pointer is still the same as this process.
            # Prevents old reader threads from killing new process pointers.
            with cls._init_lock:
                if cls._process is my_proc:
                    cls._process = None

            # Free all waiting threads to avoid infinite timeout
            with cls._dict_lock:
                for event in cls._pending_requests.values():
                    event.set()

    @classmethod
    def _stderr_reader(cls, my_proc):
        """A standalone thread to consume stderr and broadcast lines to all active requests."""
        try:
            while my_proc and my_proc.poll() is None:
                try:
                    line = my_proc.stderr.readline()
                    if not line:
                        break

                    line_str = line.strip()
                    if line_str:
                        smf.printd("CRS Engine STDERR", line_str, level="CRITICAL")
                        with cls._dict_lock:
                            # Broadcast stderr to all active/pending requests
                            for err_list in cls._pending_stderr.values():
                                err_list.append(line_str)

                except (BrokenPipeError, OSError, ValueError):
                    break
                except Exception as e:
                    smf.printd("Exception in CRS stderr reader", e, level="ERROR")
                    break
        finally:
            with cls._init_lock:
                if cls._process is my_proc:
                    cls._process = None

    @classmethod
    def send_data(cls, data: dict) -> dict:
        proc = cls._turn_on_process()
        if not proc:
            return {"status": "ERROR", "message": "Engine binary not running"}, {}

        msg_id = uuid.uuid4().hex
        data["msg_id"] = msg_id
        timeout = float(data.get("timeout", 5.0))
        event = threading.Event()

        with cls._dict_lock:
            cls._pending_requests[msg_id] = event
            cls._pending_stderr[msg_id] = []

        try:
            json_payload = json.dumps(data) + "\n"
            smf.printd("Input Json CRS", json_payload, level="DEBUG")

            # Atomic Write STDIN - Prevent JSON collisions from multiple threads
            try:
                with cls._write_lock:
                    proc.stdin.write(json_payload)
                    proc.stdin.flush()
            except (BrokenPipeError, OSError):
                pid.reap_zombie()
                return {
                    "status": "BROKEN",
                    "message": "Write IPC experienced BrokenPipe",
                }, {}
            except Exception as write_err:
                pid.reap_zombie()
                return {
                    "status": "ERROR",
                    "message": f"Failed to write IPC: {write_err}",
                }, {}

            if timeout == 0.0:
                req_timeout = None
            else:
                req_timeout = timeout + 1.0

            wait_interval = 0.5  # Check pulse (0.5 seconds)
            elapsed = 0.0

            if req_timeout is None:
                while cls._process and cls._process.poll() is None:
                    if event.wait(timeout=wait_interval):
                        break
                else:
                    return {
                        "status": "ERROR",
                        "message": "Engine crashed while waiting for infinite response",
                    }, {}
            else:
                while elapsed < req_timeout:
                    if event.wait(timeout=wait_interval):
                        break  # Event set by Reader (Success or Initial Cleanup)

                    # If wait() is longer than 0.5s, check if the reader is still alive/acknowledged the process.
                    if cls._process is not proc or proc.poll() is not None:
                        return {
                            "status": "ERROR",
                            "message": "Engine crashed while waiting for response",
                        }, {}
                    elapsed += wait_interval
                else:
                    # Loop completes without break => Timeout
                    return {
                        "status": "ERROR",
                        "message": f"IPC Timeout ({req_timeout:.1f}s)",
                    }, {}

            # Take a response stdout
            with cls._dict_lock:
                res_dict = cls._responses.pop(
                    msg_id, {"status": "ERROR", "message": "Response lost or engine died"}
                )
                stderr_lines = cls._pending_stderr.pop(msg_id, [])

            res_err = {}
            if stderr_lines:
                res_err = {
                    "status": "CRITICAL",
                    "message": " | ".join(stderr_lines),
                }

            smf.printd("Response Dict CRS", res_dict, level="DEBUG")
            return res_dict, res_err
        except KeyboardInterrupt:
            try:
                if proc and proc.stdin:
                    proc.stdin.close()
            except Exception:
                pass
            return {"status": "INTER", "message": "KeyboardInterrupt detected"}, {}
        except (BrokenPipeError, OSError):
            return {
                "status": "BROKEN",
                "message": "(CRS.send) experienced BrokenPipe",
            }, {}
        except Exception as e:
            smf.printd("Error send IPC CRS", e, level="ERROR")
            return {"status": "ERROR", "message": str(e)}, {}
        finally:
            # Make sure the dictionary memory is cleared
            with cls._dict_lock:
                cls._pending_requests.pop(msg_id, None)
                cls._pending_stderr.pop(msg_id, None)
                cls._responses.pop(msg_id, None)
