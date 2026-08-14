import os
import smf
import time
import json
import base64
import sqlite3
import logging
import requests

from rootmap import ROOT
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization

__autorun__ = True


class SMFHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_emitting = False  # Guard flag terhadap re-entrancy

    def emit(self, record):
        if self._is_emitting:
            return

        self._is_emitting = True
        try:
            # Gunakan self.format(record) agar terintegrasi dengan Formatter standar
            log_entry = self.format(record)
            smf.printd("Plugin sendlog service", log_entry, level=record.levelname)
        except Exception:
            self.handleError(record)
        finally:
            self._is_emitting = False


# Standard logging configuration
logging.basicConfig(level=logging.INFO, handlers=[SMFHandler()], force=True)


class Plugin:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

        # Load environment variables
        load_dotenv()
        self.pubkey = os.getenv("STORM_PUBKEY")
        self.api_url = os.getenv("API_TLG")
        self.db_path = os.path.join(ROOT, "lib", "sqlite", "logging", "log.db")

        # Inisialisasi Ed25519 Private Key dari Base64 (PKCS#8 DER format)
        privkey_b64 = os.getenv("STORM_PRIVKEY")
        if not privkey_b64:
            raise ValueError("STORM_PRIVKEY not found.")

        try:
            # Decode Base64 untuk mendapatkan byte DER (ASN.1)
            # Menambahkan logic padding = (opsional di Python, b64decode biasanya mentolerir,
            # tapi kita pastikan paddingnya tepat jika environment strict)
            pad_len = 4 - (len(privkey_b64) % 4)
            if pad_len != 4:
                privkey_b64 += "=" * pad_len

            der_bytes = base64.b64decode(privkey_b64)

            # Parsing struktur PKCS#8 DER menjadi objek Ed25519PrivateKey
            self.private_key = serialization.load_der_private_key(
                der_bytes, password=None
            )
        except Exception as e:
            smf.printd("Error decode b64 plugin sendlog", e, level="ERROR")
            raise ValueError(f"Failed to load DER private key: {e}")

        # State management (Watermark)
        self.last_timestamp = 0.0

    def _sign_payload(self, data: dict) -> str:
        """Signing a data dict using Ed25519."""
        # Canonical JSON serialization untuk deterministic byte array
        canonical_json = json.dumps(data, separators=(",", ":"), sort_keys=True)
        message_bytes = canonical_json.encode("utf-8")

        # Sign data & encode signature ke Base64
        signature = self.private_key.sign(message_bytes)
        return base64.b64encode(signature).decode("utf-8")

    def _fetch_and_forward(self):
        """Read SQLite and send data sequentially."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                query = """
                    SELECT timestamp, level, label, payload, traceback, caller_info 
                    FROM system_logs 
                    WHERE level IN ('ERROR', 'CRITICAL') 
                      AND timestamp > ?
                    ORDER BY timestamp ASC
                """
                cursor.execute(query, (self.last_timestamp,))
                rows = cursor.fetchall()

                if not rows:
                    return

                for row in rows:
                    data_payload = {
                        "timestamp": row["timestamp"],
                        "level": row["level"],
                        "label": row["label"],
                        "payload": row["payload"],
                        "traceback": row["traceback"],
                        "caller_info": row["caller_info"],
                    }

                    signature_b64 = self._sign_payload(data_payload)

                    request_body = {
                        "pubkey": self.pubkey,
                        "signature": signature_b64,
                        "data": data_payload,
                    }

                    self._send_to_api(request_body)
                    self.last_timestamp = row["timestamp"]

        except sqlite3.Error as db_err:
            self.logger.error(f"Database error: {db_err}")
        except Exception as e:
            self.logger.error(f"Unexpected error saat fetching/forwarding: {e}")

    def _send_to_api(self, payload: dict):
        """Handle HTTP POST requests."""
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(
                self.api_url, json=payload, headers=headers, timeout=5.0
            )
            response.raise_for_status()
            self.logger.info(
                f"Log forwarded successfully. Timestamp: {payload['data']['timestamp']}"
            )
        except requests.exceptions.RequestException as req_err:
            self.logger.error(f"API request failed: {req_err}")
            raise

    def execute(self):
        """Entry point daemon."""
        interval_seconds = 10
        self.logger.info("Starting the Secure Log Forwarder service...")
        while True:
            self._fetch_and_forward()
            time.sleep(interval_seconds)
