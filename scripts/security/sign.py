# MIT License.
# Copyright (c) 2026 Storm Framework

# See LICENSE file in the project root for full license information.


import json
import hashlib
import base64
from rootmap import ROOT
from app.utility.spin import StormSpin
from cryptography.hazmat.primitives.asymmetric import ed25519

# logic for sha256 mathematical calculations
def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()
    
def generate_folder_manifest():
    print("[+] Get started with Storm Framework security.")

    # Load Private Key dari .env
    # .env is mandatory in every Storm installation because it is (IMPORTANT)
    # If .evn is intentionally deleted storm will not cancel the startup
    priv_key_b64 = None
    env_path = ROOT / ".env"

    if env_path.exists():
        with open(env_path, "r") as f:
            for line in f:
                if line.startswith("STORM_PRIVKEY="):
                    priv_key_b64 = line.split("=")[1].strip()
                    break

    if not priv_key_b64:
        print("[!] ERROR: STORM_PRIVKEY not found in .env. Reinstall storm!")
        return

    # Scanning Files
    # ignore names that do not need to be signed
    manifest = {}
    ignored_dirs = {
        ".git",
        "__pycache__",
        ".pytest_cache",
        ".github",
        "storm.db",
        ".gitignore",
        ".env",
        "res",
        "target"
    }

    with StormSpin():
        for path in ROOT.rglob("*"):
            if path.is_file() and path.name != "signed_manifest.json":
                if not any(part in ignored_dirs for part in path.parts):
                    relative_path = str(path.relative_to(ROOT))
                    # calculate sha256 to create hash
                    manifest[relative_path] = {
                        "sha256": calculate_sha256(path),
                        "size_bytes": path.stat().st_size,
                    }

        # Sort the manifest so that the JSON hash is always consistent (Important!)
        sorted_manifest = dict(sorted(manifest.items()))

        # Signing Process
        # Convert dict to compact JSON string for hashing
        manifest_string = json.dumps(
            sorted_manifest, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        # Load private key from Base64 DER
        try:
            priv_bytes = base64.b64decode(priv_key_b64)
            private_key = ed25519.Ed25519PrivateKey.from_private_bytes(priv_bytes[-32:])

            # Create a Signature
            signature = private_key.sign(manifest_string)
            signature_b64 = base64.b64encode(signature).decode("utf-8")
        except Exception as e:
            print(f"[!] Signing Error: {e}")
            return

        # Wrap all hashes into a valid signature
        final_data = {
            "metadata": {"version": "1.0", "signature": signature_b64},
            "files": sorted_manifest,
        }

        # save the results
        output_dir = ROOT / "lib" / "core" / "database"
        output_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = output_dir / "signed_manifest.json"

        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(final_data, f, indent=4)

    print(f"[✓] Success! Manifest signed and saved.")


if __name__ == "__main__":
    generate_folder_manifest()
