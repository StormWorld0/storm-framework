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
from lib.pid_manager import PIDManager as pid


class CRS:
    """IPC (Inter-Process Communication) via Subprocess."""

    _process = None
    _lock = threading.Lock()
    _pending_requests = {}  # Format: {msg_id: threading.Event}
    _responses = {}  # Format: {msg_id: dict_response}
    _reader_thread = None

    @classmethod
    def _get_process(cls):
        if cls._process is not None:
            if cls._process.poll() is None:
                return cls._process

        binary_path = call_bin("crs_engine")
        if not os.path.exists(binary_path):
            smf.printf(f"[!]{CC.YELLOW} Binary not found =>{CC.RESET}", binary_path)
            return cls._process

        cls._process = subprocess.Popen(
            [binary_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        pid.prepare(cls._process.pid)

        # Nyalakan Background Reader untuk mendengarkan stdout Go secara terus-menerus
        if cls._reader_thread is None or not cls._reader_thread.is_alive():
            cls._reader_thread = threading.Thread(
                target=cls._background_reader, daemon=True
            )
            cls._reader_thread.start()

        return cls._process

    @classmethod
    def _background_reader(cls):
        """Thread mandiri yang membaca stdout Go secara konstan dan mendistribusikan respons."""
        proc = cls._process
        try:
            while proc and proc.poll() is None:
                try:
                    line = proc.stdout.readline()
                    if not line:
                        break

                    # Abaikan baris kosong atau log non-JSON jika ada
                    line_str = line.strip()
                    if not line_str.startswith("{"):
                        continue

                    res_dict = json.loads(line_str)
                    msg_id = res_dict.get("msg_id")

                    if msg_id:
                        with cls._lock:
                            if msg_id in cls._pending_requests:
                                cls._responses[msg_id] = res_dict
                                cls._pending_requests[msg_id].set()
                except (BrokenPipeError, OSError, ValueError):
                    break
                except Exception as e:
                    smf.printd("Error in CRS background reader", e, level="ERROR")
                    break
        finally:
            with cls._lock:
                cls._process = None
                try:
                    pid.reap_zombie()
                except Exception:
                    pass
                for event in cls._pending_requests.values():
                    event.set()

    @classmethod
    def send(cls, data: dict) -> dict:
        proc = cls._get_process()
        if not proc:
            return {"status": "ERROR", "message": "Engine binary not running"}

        msg_id = uuid.uuid4().hex
        data["msg_id"] = msg_id

        req_timeout = float(data.get("timeout", 5.0)) + 1.0

        event = threading.Event()
        with cls._lock:
            cls._pending_requests[msg_id] = event

        try:
            json_payload = json.dumps(data) + "\n"
            smf.printd("Input Json CRS", json_payload, level="DEBUG")

            # [PERBAIKAN 2]: Write dengan try-except tanpa mengunci lock terlalu lama
            try:
                proc.stdin.write(json_payload)
                proc.stdin.flush()
            except Exception as write_err:
                return {
                    "status": "ERROR",
                    "message": f"Failed to write to Go STDIN: {write_err}",
                }

            # [PERBAIKAN 3]: Gunakan req_timeout yang DINAMIS!
            if not event.wait(timeout=req_timeout):
                return {
                    "status": "ERROR",
                    "message": f"IPC Timeout waiting for engine response (exceeded {req_timeout:.1f}s)",
                }

            # Ambil respons
            with cls._lock:
                res_dict = cls._responses.pop(
                    msg_id, {"status": "ERROR", "message": "Response lost"}
                )

            smf.printd("Response Dict CRS", res_dict, level="DEBUG")
            return res_dict

        except Exception as e:
            return {"status": "ERROR", "message": str(e)}
        finally:
            with cls._lock:
                cls._pending_requests.pop(msg_id, None)
                cls._responses.pop(msg_id, None)
