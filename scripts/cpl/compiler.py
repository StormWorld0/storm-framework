import os
import subprocess
import tempfile

from rootmap import ROOT
from apps.utility.spin import StormSpin

from .advcore import safe_mode
from .detect_os_ext import osext


def start_build():
    os.chdir(ROOT)

    # Cache is saved
    tmp_dir = tempfile.gettempdir()
    rust_cache = os.path.join(tmp_dir, "smf-build")
    os.makedirs(rust_cache, exist_ok=True)

    # Binary output is saved
    bin_path = os.path.abspath(os.path.join(ROOT, "external/source/out"))
    os.makedirs(bin_path, exist_ok=True)

    # Binary output root
    root_path = os.path.abspath(ROOT)

    # context to Makefile
    os.environ["CARGO_TARGET_DIR"] = rust_cache
    os.environ["OUT_DIR"] = bin_path
    os.environ["OUT_ROOT"] = root_path
    os.environ["EXT"] = osext()

    # Ignore folder list
    ignore_dirs = {".git", "__pycache__", "node_modules", "cache", "vendor"}

    print("[*] Run binary compilation.")

    cores = safe_mode()
    failed_binary = []
    build_failed = False
    try:
        # Setup loading
        with StormSpin():
            # running loop
            for root, dirs, files in os.walk("."):
                dirs[:] = [d for d in dirs if d not in ignore_dirs]
                if "Makefile" in files:
                    if os.path.abspath(root) == os.path.abspath(ROOT):
                        continue
                    try:  # Running make
                        cmd = ["make", "-C", root, f"-j{cores}"]
                        subprocess.run(cmd, check=True, capture_output=True)
                    except subprocess.CalledProcessError as e:
                        build_failed = True
                        module = os.path.basename(root)
                        failed_binary.append(module)
                        print(f"[!] Build failed in {module} => {e.stderr.decode()}")
                    except FileNotFoundError as e:
                        build_failed = True
                        module = os.path.basename(root)
                        failed_binary.append(module)
                        print(f"[!] Make => {e}")
                        break

        if build_failed:
            print("[!] Compilation finished with errors.")
            print("[*] List failed binary:")
            for module in failed_binary:
                print(f"      - {module}")
        else:
            print("[✓] Compilation successful.")
    except KeyboardInterrupt:
        print("Compiler Stop. Reinstall to continue.")
    except Exception as e:
        print(f"ERROR COMPILER => {e}")
        return


if __name__ == "__main__":
    start_build()
