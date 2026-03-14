import os
import subprocess
import sys

from pathlib import Path
from rootmap import ROOT
from scripts.security.sign import generate_folder_manifest


def install_ghunt_module():
    repo_url = "https://github.com/StormWorld0/GhOSINT.git"
    target_dir = Path(ROOT) / "script" / "ghunt"

    # Clone Repo or Update
    if os.path.exists(os.path.join(target_dir, ".git")):
        print("[!] Module found. Updating...")

        try:
            subprocess.run(
                ["git", "-C", str(target_dir), "fetch", "--all"],
                stdout=subprocess.DEVNULL,
            )
            check_diff = subprocess.run(
                [
                    "git",
                    "-C",
                    str(target_dir),
                    "diff",
                    "--name-only",
                    "HEAD",
                    "origin/main",
                ],
                capture_output=True,
                text=True,
            )
            process = subprocess.run(
                ["git", "-C", str(target_dir), "reset", "--hard", "origin/main"],
                stdout=subprocess.PIPE,
                text=True,
            )
            if process.returncode == 0:
                print(f"[✓] update success.")

        except Exception as e:
            print(f"[-] Update failed: {e}")
    else:
        print("[*] Downloading GhOSINT Module...")
        subprocess.run(["git", "clone", repo_url, str(target_dir)], check=True)

    # setup after installation/update is complete
    # and register the new file identity
    venv_dir = target_dir / "venv"
    python_exe = venv_dir / "bin" / "python"
    pip_exe = venv_dir / "bin" / "pip"

    try:
        if not venv_dir.exists():
            subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
        else:
            pass

        subprocess.run(
            [
                str(pip_exe),
                "install",
                "ghunt",
            ],
            check=True,
        )
        subprocess.run(
            [str(python_exe), "-m", "playwright", "install", "chromium"], check=True
        )
        print("[✓] GhOSINT Package installed successfully.")

        # New file hash and signature
        generate_folder_manifest()
        return True
    except Exception as e:
        print(f"\n[-] Installation Failed: {e}")
        return False
