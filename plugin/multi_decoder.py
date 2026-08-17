import base64
import urllib.parse
import smf

__autorun__ = False

class Plugin:
    def __init__(self):
        self.name = "Advanced Dynamic Multi-Decoder"
        self.version = "1.0.0"

        # Register function decode machine
        self._dispatch_table = {
            "b64": self._decode_base64,
            "url": self._decode_url,
            "hex": self._decode_hex,
        }

    def execute(self, *args, **kwargs) -> dict:
                """Entry Point"""
        payload = kwargs.get("payload", "")
        metadata = kwargs.get("metadata", {})

        # Validasi keberadaan node Transforms
        transforms = metadata.get("Transforms", {})
        if not transforms or not payload:
            return {"handled": False}

        current_payload = payload

        # Iterasi pipeline decoder secara sekuensial
        for transform_key, decoder_func in self._dispatch_table.items():
            if transforms.get(transform_key).lower is True:
                decoded_result = decoder_func(current_payload)
                
                if decoded_result != current_payload:
                    current_payload = decoded_result

        if current_payload != payload:
            smf.printd(f"[{self.name}] Payload successfully transformed.", level="INFO")
            return {"payload": current_payload}

        return {"handled": False}

    
    # ==========================================
    #    --- PRIVATE DECODER STRATEGIES ---
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
