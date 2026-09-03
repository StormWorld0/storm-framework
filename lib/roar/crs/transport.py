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
    """IPC (Inter-Process Communication) via Subprocess (Thread-Safe & Deadlock-Free)."""

    _process = None
    _init_lock = threading.Lock()  # Gembok khusus untuk inisialisasi / spawn
    _write_lock = threading.Lock()  # Gembok khusus untuk mencegah tabrakan Write STDIN
    _dict_lock = threading.Lock()  # Gembok khusus untuk _pending_requests & _responses

    _pending_requests = {}
    _responses = {}
    _reader_thread = None
    _stderr_thread = None

    @classmethod
    def _get_process(cls):
        # 1st Check (Fast path tanpa antre)
        if cls._process is not None and cls._process.poll() is None:
            return cls._process

        # Masuk area kritis inisialisasi
        with cls._init_lock:
            # 2nd Check (Double-checked locking pattern)
            if cls._process is not None and cls._process.poll() is None:
                return cls._process

            binary_path = call_bin("crs_engine")
            if not os.path.exists(binary_path):
                smf.printf(f"[!]{CC.YELLOW} Binary not found =>{CC.RESET}", binary_path)
                return None

            # stderr dialihkan ke DEVNULL agar tidak Deadlock (OS Buffer Full)
            cls._process = subprocess.Popen(
                [binary_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )

            pid.prepare(cls._process.pid)

            # Nyalakan Background Reader
            if cls._reader_thread is None or not cls._reader_thread.is_alive():
                cls._reader_thread = threading.Thread(
                    target=cls._background_reader,
                    args=(cls._process,),  # Passing reference secara eksplisit
                    daemon=True,
                )
                cls._reader_thread.start()

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
            # Hanya reset _process jika pointer masih sama dengan proses ini.
            # Mencegah thread reader lama membunuh pointer proses baru.
            with cls._init_lock:
                if cls._process is my_proc:
                    cls._process = None

            # Bebaskan semua thread yang sedang menunggu agar tidak infinite timeout
            with cls._dict_lock:
                for event in cls._pending_requests.values():
                    event.set()

    @classmethod
    def _stderr_reader(cls, my_proc):
        """A standalone thread to asynchronously consume and log engine stderr."""
        try:
            while my_proc and my_proc.poll() is None:
                line = my_proc.stderr.readline()
                if not line:
                    break

                line_str = line.strip()
                if line_str:
                    smf.printd("CRS Engine STDERR", line_str, level="ERROR")

        except (BrokenPipeError, OSError, ValueError):
            pass
        except Exception as e:
            smf.printd("Exception in CRS stderr reader", e, level="ERROR")

    @classmethod
    def send(cls, data: dict) -> dict:
        proc = cls._get_process()
        if not proc:
            return {"status": "ERROR", "message": "Engine binary not running"}

        msg_id = uuid.uuid4().hex
        data["msg_id"] = msg_id
        req_timeout = float(data.get("timeout", 5.0)) + 1.0
        event = threading.Event()

        with cls._dict_lock:
            cls._pending_requests[msg_id] = event

        try:
            json_payload = json.dumps(data) + "\n"
            smf.printd("Input Json CRS", json_payload, level="DEBUG")

            # Atomic Write STDIN - Cegah tabrakan JSON dari banyak thread
            try:
                with cls._write_lock:
                    proc.stdin.write(json_payload)
                    proc.stdin.flush()
            except Exception as write_err:
                pid.reap_zombie()
                return {"status": "ERROR", "message": f"Failed to write IPC: {write_err}"}

            # Tunggu balasan dari Background Reader
            if not event.wait(timeout=req_timeout):
                return {"status": "ERROR", "message": f"IPC Timeout ({req_timeout:.1f}s)"}

            # Ambil respons
            with cls._dict_lock:
                res_dict = cls._responses.pop(
                    msg_id, {"status": "ERROR", "message": "Response lost or engine died"}
                )

            smf.printd("Response Dict CRS", res_dict, level="DEBUG")
            return res_dict

        except Exception as e:
            smf.printd("Error send IPC CRS", e, level="ERROR")
            return {"status": "ERROR", "message": str(e)}
        finally:
            # Pastikan memori dictionary dibersihkan
            with cls._dict_lock:
                cls._pending_requests.pop(msg_id, None)
                cls._responses.pop(msg_id, None)
