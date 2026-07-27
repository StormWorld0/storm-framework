# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
import json
import subprocess
import os
import smf
import base64

from ..calling import call_bin
from apps.utility.colors import *


class CRS:
    """IPC (Inter-Process Communication) via Subprocess."""

    _process = None

    @classmethod
    def _get_process(cls):
        if cls._process is None or cls._process.poll() is not None:
            # Nanti path ini tinggal kamu arahin ke biner Go kamu
            binary_path = call_bin("crs_engine")

            # Kalau biner belum ada, Jembatan akan langsung lapor error
            if not os.path.exists(binary_path):
                smf.printf(f"[!]{CC.YELLOW} Binary not found =>{CC.RESET}", binary_path)

            cls._process = subprocess.Popen(
                [binary_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
        return cls._process

    @classmethod
    def send(cls, data: dict) -> dict:
        try:
            proc = cls._get_process()

            # 1. Ubah Dict ke JSON (1 baris)
            json_payload = json.dumps(data) + "\n"
            smf.printd(
                "Process input data from CRS Engine", json.dumps(data), level="DEBUG"
            )

            # 2. Lempar ke engine via Stdin
            proc.stdin.write(json_payload)
            proc.stdin.flush()

            # 3. Baca 1 baris balasan JSON dari Stdout
            response_line = proc.stdout.readline()

            if not response_line:
                smf.printd("CRS Engine suddenly stopped", response_line, level="WARN")
                return {"status": "ERROR", "message": "Engine suddenly dies"}

            # 4. Ubah balik JSON ke Dict
            res_dict = json.loads(response_line)

            if isinstance(res_dict, dict) and isinstance(res_dict.get("data"), dict):
                raw_b64 = res_dict["data"].get("raw_bytes")
                if isinstance(raw_b64, str):
                    try:
                        res_dict["data"]["raw_bytes"] = base64.b64decode(raw_b64)
                    except Exception as b64_err:
                        # Fallback jika gagal decode base64
                        res_dict["data"]["raw_bytes"] = b""
                        smf.printd("Base64 decode failed", str(b64_err), level="ERROR")

            smf.printd("CRS Process Output dict format", res_dict, level="DEBUG")
            return res_dict
        except Exception as e:
            smf.printd("Error CRS send", e, level="ERROR")
            return {"status": "ERROR", "message": str(e)}
