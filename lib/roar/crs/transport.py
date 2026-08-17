# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author: zxelzy

import json
import subprocess
import os
import smf
import base64
import atexit

from ..calling import call_bin
from apps.utility.colors import *


class CRS:
    """IPC (Inter-Process Communication) via Subprocess."""

    _process = None

    @classmethod
    def _get_process(cls):
        if cls._process is not None:
            if cls._process.poll() is None:
                return cls._process

            cls._process.wait()
            cls._process = None

        binary_path = call_bin("crs_engine")

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

        atexit.register(cls._cleanup)
        return cls._process

    @classmethod
    def _cleanup(cls):
        """Universal cleanup handler when parent exit is normal/graceful."""
        if cls._process is not None:
            try:
                # Menutup stdin mengirimkan EOF
                # ke child process di OS manapun
                if cls._process.stdin:
                    cls._process.stdin.close()
                cls._process.terminate()
                cls._process.wait(timeout=1)
            except Exception:
                pass
            finally:
                cls._process = None

    @classmethod
    def send(cls, data: dict) -> dict:
        try:
            proc = cls._get_process()

            # Convert Dict to JSON (1 line)
            json_payload = json.dumps(data) + "\n"
            smf.printd(
                "Process input data from CRS Engine", json.dumps(data), level="DEBUG"
            )

            # Throw to binary via Stdin
            proc.stdin.write(json_payload)
            proc.stdin.flush()

            # Read 1 line of JSON response from Stdout
            response_line = proc.stdout.readline()

            if not response_line:
                smf.printd("CRS Engine suddenly stopped", response_line, level="WARN")
                return {"status": "ERROR", "message": "Engine suddenly dies"}

            # Convert JSON back to Dict
            res_dict = json.loads(response_line)

            if isinstance(res_dict, dict) and isinstance(res_dict.get("data"), dict):
                raw_b64 = res_dict["data"].get("raw_bytes")
                if isinstance(raw_b64, str):
                    try:
                        res_dict["data"]["raw_bytes"] = base64.b64decode(raw_b64)
                    except Exception as b64_err:
                        # Fallback if base64 decode fails
                        res_dict["data"]["raw_bytes"] = b""
                        smf.printd("Base64 decode failed", b64_err, level="ERROR")

            smf.printd("CRS Process Output dict format", res_dict, level="DEBUG")
            return res_dict
        except Exception as e:
            smf.printd("Error CRS send", e, level="ERROR")
            return {"status": "ERROR", "message": str(e)}
