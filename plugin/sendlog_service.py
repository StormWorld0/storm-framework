import os
import smf
import json
import queue
import base64
import sqlite3
import requests
import threading

from time import sleep, monotonic
from dotenv import load_dotenv
from rootmap import ROOT
from datetime import datetime, time
from cryptography.hazmat.primitives import serialization

__autorun__ = True


class Plugin:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.api_url = os.getenv("STORM_TLG")
        self.db_path = os.path.join(ROOT, "lib", "sqlite", "logging", "log.db")

        self.log_queue = queue.Queue()
        self.rate_limit_delay = 10.0
        self.last_timestamp = 0.0

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
            smf.printd("Error decode b64 privkey", e, level="ERROR")
            return

        try:
            # Derive murni Raw Ed25519 Public Key (32 bytes -> 44 char Base64)
            raw_pubkey_bytes = self.private_key.public_key().public_bytes(
                encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
            )
            # Override self.pubkey dengan format Raw 32-byte yang disukai Web Crypto Worker
            self.pubkey = base64.b64encode(raw_pubkey_bytes).decode("utf-8")
        except Exception as e:
            smf.printd("Error extracting pure Raw 32-byte Public Key", e, level="ERROR")
            return

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
        # Hitung timestamp awal hari ini (00:00:00)
        today_start = datetime.combine(datetime.now().date(), time.min).timestamp()
        fetch_since = max(today_start, self.last_timestamp)

        uri_path = f"file:{self.db_path}?mode=ro&nolock=1&immutable=1"
        smf.printd("Read uri sendlog service", uri_path, level="DEBUG")
        try:
            with sqlite3.connect(uri_path, uri=True, timeout=10.0) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                query = """
                    SELECT timestamp, level, label, payload, traceback, caller_info 
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
                        "traceback": row["traceback"],
                        "caller_info": row["caller_info"],
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
            smf.printd("Database error", e, level="ERROR")
        except Exception as e:
            smf.printd("Unexpected error saat fetching/forwarding", e, level="ERROR")

    def _consumer_forward_logs(self):
        """Pop queue, kirim API, lalu enforce delay minimal 10 detik."""
        while True:
            try:
                # Blocking fetch dengan timeout agar thread bisa gracefully exit jika needed
                request_body = self.log_queue.get(block=True, timeout=1.0)
            except queue.Empty:
                continue

            start_time = monotonic()

            # Melakukan pengiriman data dengan mekanisme retry internal jika gagal
            success = self._send_to_api(request_body)

            if not success:
                # Jika HTTP request gagal/timeout, masukkan kembali ke antrean depan (re-queue)
                # Catatan: Pada queue standard, re-queue ditaruh di belakang. Untuk requeue ke depan
                # bisa menggunakan queue.Deque / collections.deque jika prioritas mutlak.
                smf.printd("Delivery failed, requeue payload", level="WARN")
                self.log_queue.put(request_body)

            self.log_queue.task_done()

            # Enforce Throttling: Hitung durasi execution & pastikan interval minimum >= 10s
            elapsed = monotonic() - start_time
            sleep_duration = max(0.0, self.rate_limit_delay - elapsed)
            sleep(sleep_duration)

    def _send_to_api(self, payload: dict) -> bool:
        """Handle HTTP POST requests."""
        headers = {
            "User-Agent": "storm-framework/3.0 (Linux/x86_64)",
            "Content-Type": "application/json",
        }
        try:
            res = requests.post(self.api_url, json=payload, headers=headers, timeout=5.0)
            if res.status_code == 200:
                try:
                    res_data = res.json()
                    status = res_data.get("status")
                    message = res_data.get("message")
                    smf.printd(
                        f"CODE: {res.status_code} : {status} =>", message, level="INFO"
                    )
                except Exception:
                    smf.printd(f"CODE: 200 OK", level="INFO")

            res.raise_for_status()
            smf.printd(
                f"Log forwarded successfully. Timestamp:",
                payload["data"]["timestamp"],
                level="INFO",
            )
            return True
        except requests.exceptions.Timeout:
            smf.printd("Request timeout", level="WARN")
            return False
        except requests.exceptions.HTTPError as e:
            smf.printd("HTTP error", e, level="ERROR")
            return False
        except requests.exceptions.RequestException as e:
            smf.printd("API request failed", e, level="ERROR")
            return False

    def execute(self):
        """Entry point daemon."""
        smf.printd("Starting the Secure Log Forwarder service...", level="INFO")

        # Start Consumer Thread
        consumer_thread = threading.Thread(
            target=self._consumer_forward_logs, daemon=True
        )
        consumer_thread.start()

        while True:
            self._fetch_and_forward()
            sleep(60)
