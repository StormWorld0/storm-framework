import base64
import urllib.parse
import smf


class Plugin:
    def __init__(self):
        self.name = "Advanced Dynamic Multi-Decoder"
        self.version = "1.0.0"

        # Register function decode machine
        self._dispatch_table = {
            "Base64": self._decode_base64,
            "URL": self._decode_url,
            "Hex": self._decode_hex,
        }

    def execute(self, *args, **kwargs) -> dict:
        """
        Entry point baru yang sinkron dengan SmartOptions / RuntimeContext.
        Menerima 'payload' tunggal (string) lalu mentransformasikannya.
        """
        payload = kwargs.get("payload", "")
        metadata = kwargs.get("metadata", {})

        # 1. Validasi keberadaan node Transforms
        transforms = metadata.get("Transforms", {})
        if not transforms or not payload:
            return {"handled": False}

        current_payload = payload

        # 2. Iterasi pipeline decoder secara sekuensial (berantai)
        for transform_key, decoder_func in self._dispatch_table.items():
            if transforms.get(transform_key) is True:
                # Lakukan decode pada payload saat ini
                decoded_result = decoder_func(current_payload)

                # Jika ada perubahan, perbarui payload untuk iterasi decoder selanjutnya
                if decoded_result != current_payload:
                    current_payload = decoded_result

        # 3. Jika payload berhasil bermutasi, kirim balik ke engine
        if current_payload != payload:
            smf.printd(f"[{self.name}] Payload successfully transformed.", level="DEBUG")
            return {"mutated_payload": current_payload}

        return {"handled": False}

    # ==========================================
    # PRIVATE DECODER STRATEGIES (Tidak Berubah)
    # ==========================================

    def _decode_base64(self, data: str) -> str:
        try:
            padded_data = data + "=" * (-len(data) % 4)
            decoded_bytes = base64.b64decode(padded_data, validate=True)
            return decoded_bytes.decode("utf-8", errors="ignore")
        except Exception:
            return data

    def _decode_url(self, data: str) -> str:
        try:
            return urllib.parse.unquote(data)
        except Exception:
            return data

    def _decode_hex(self, data: str) -> str:
        try:
            clean_hex = data.replace("0x", "").replace("\\x", "")
            decoded_bytes = bytes.fromhex(clean_hex)
            return decoded_bytes.decode("utf-8", errors="ignore")
        except Exception:
            return data
