import os
import smf
import json
import queue
import base64
import sqlite3
import threading

from time import monotonic
from dotenv import load_dotenv
from rootmap import ROOT
from datetime import datetime, time
from lib.roar.crs.net_api import HTTPR
from cryptography.hazmat.primitives import serialization

__autorun__ = True


class Plugin:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.api_url = os.getenv("STORM_API")
        self.db_path = os.path.join(ROOT, "lib", "sqlite", "logging", "log.db")

        self.stop_event = threading.Event()
        self.consumer_thread = None
        self.log_queue = queue.Queue()
        self.rate_limit_delay = 15.0
        self.last_timestamp = 0.0

        # Initialize Ed25519 Private Key from Base64 (PKCS#8 DER format)
        privkey_b64 = os.getenv("STORM_PRIVKEY")
        if not privkey_b64:
            raise

        try:
            # Decode Base64 to get DER bytes (ASN.1)
            pad_len = 4 - (len(privkey_b64) % 4)
            if pad_len != 4:
                privkey_b64 += "=" * pad_len

            der_bytes = base64.b64decode(privkey_b64)

            # Parse PKCS#8 DER structure into Ed25519PrivateKey object
            self.private_key = serialization.load_der_private_key(
                der_bytes, password=None
            )
        except Exception as e:
            smf.printd("Error decode b64 privkey", e, level="ERROR")
            raise

        try:
            raw_pubkey_bytes = self.private_key.public_key().public_bytes(
                encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
            )
            self.pubkey = base64.b64encode(raw_pubkey_bytes).decode("utf-8")
        except Exception as e:
            smf.printd("Error extracting pure Raw 32-byte Public Key", e, level="ERROR")
            raise

    def _sign_payload(self, data: dict) -> str:
        """Signing a data dict using Ed25519."""
        canonical_json = json.dumps(data, separators=(",", ":"), sort_keys=True)
        message_bytes = canonical_json.encode("utf")
        signature = self.private_key.sign(message_bytes)
        return base64.b64encode(signature).decode("utf-8")

    def _fetch_and_forward(self):
        """Read SQLite and send data sequentially."""
        # Calculate today's start timestamp (00:00:00)
        today_start = datetime.combine(datetime.now().date(), time.min).timestamp()
        fetch_since = max(today_start, self.last_timestamp)

        uri_path = f"file:{self.db_path}?mode=ro&nolock=1&immutable=1"
        try:
            with sqlite3.connect(uri_path, uri=True, timeout=10.0) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                query = """
                    SELECT timestamp, level, label, payload, caller, location, traceback
                    FROM system_logs 
                    WHERE level IN ('ERROR', 'CRITICAL') 
                      AND timestamp > ?
                      AND label NOT LIKE '%sendlog%'
                    ORDER BY timestamp ASC
                """
                cursor.execute(query, (fetch_since,))
                rows = cursor.fetchall()

                if not rows:
                    return

                for row in rows:
                    row_ts = float(row["timestamp"])

                    if row_ts <= self.last_timestamp and self.last_timestamp != 0.0:
                        continue

                    data_payload = {
                        "timestamp": row_ts,
                        "level": row["level"],
                        "label": row["label"],
                        "payload": row["payload"],
                        "caller": row["caller"],
                        "location": row["location"],
                        "traceback": row["traceback"],
                    }

                    signature_b64 = self._sign_payload(data_payload)
                    request_body = {
                        "pubkey": self.pubkey,
                        "signature": signature_b64,
                        "data": data_payload,
                    }

                    self.log_queue.put(request_body)
                    self.last_timestamp = row_ts
        except sqlite3.Error as e:
            smf.printd("Database error sendlog", e, level="ERROR")
        except Exception as e:
            smf.printd(
                "Unexpected error sendlog when fetching/forwarding", e, level="ERROR"
            )

    def _consumer_forward_logs(self):
        """Pop queue, send API, then enforce minimum delay of 15 seconds."""
        while not self.stop_event.is_set():
            try:
                request_body = self.log_queue.get(block=True, timeout=1.0)
            except queue.Empty:
                continue

            if not request_body:
                continue

            start_time = monotonic()

            # Perform data delivery with an internal retry mechanism if it fails.
            success = self._send_to_api(request_body)

            if not success:
                # If the HTTP request fails/times out, re-queue it.
                smf.printd("Delivery failed, requeue payload", level="WARN")
                self.log_queue.put(request_body)

            self.log_queue.task_done()

            # Enforce Throttling: Calculate execution duration
            elapsed = monotonic() - start_time
            sleep_duration = max(0.0, self.rate_limit_delay - elapsed)
            self.stop_event.wait(timeout=sleep_duration)

    def _send_to_api(self, payload: dict) -> bool:
        """Handle HTTP POST requests."""
        headers = {
            "User-Agent": "storm-framework/3.0 (sendlog)",
            "Content-Type": "application/json",
        }
        try:
            http = HTTPR()
            res = (
                http.post(self.api_url, payload, headers)
                .timeout(5.0)
                .concurrency(1)
                .run()
            )
            res_data = res.json()
            if res.status_code == 200:
                try:
                    status = res_data.get("status")
                    message = res_data.get("message")
                    smf.printd(
                        f"CODE: {res.status_code} : {status} =>", message, level="INFO"
                    )
                except Exception:
                    smf.printd(f"CODE: {res.status_code}", level="INFO")

            elif res.status_code >= 400:
                try:
                    status = res_data.get("status")
                    message = res_data.get("message")
                    smf.printd(
                        f"CODE: {res.status_code} : {status} =>", message, level="WARN"
                    )
                    return False
                except Exception:
                    smf.printd(f"CODE: {res.status_code}", level="ERROR")
                    return False

            smf.printd(
                f"Sendlog successfully. Timestamp:",
                payload["data"]["timestamp"],
                level="INFO",
            )
            return True
        except http.Timeout:
            smf.printd("Request timeout sendlog", level="WARN")
            return False
        except http.HTrace as e:
            smf.printd("API sendlog request failed", e, level="ERROR")
            return False

    def teardown(self):
        """SUICIDE FUNCTION"""
        # Sends a signal to ALL threads to exit the loop
        self.stop_event.set()

        # Wait for the consumer thread to completely finish
        if self.consumer_thread and self.consumer_thread.is_alive():
            self.consumer_thread.join(timeout=2.0)

        smf.printd("Sendlog service stopped.", level="INFO")

    def execute(self):
        """Entry point daemon"""
        smf.printd("Starting the sendlog service", level="INFO")

        # Start Consumer Thread
        self.consumer_thread = threading.Thread(
            target=self._consumer_forward_logs, daemon=True
        )
        self.consumer_thread.start()

        while not self.stop_event.is_set():
            self._fetch_and_forward()
            self.stop_event.wait(timeout=60)
