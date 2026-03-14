import os
import subprocess
import sys
from rootmap import ROOT


def install_osint_module():
    repo_url = "https://github.com/StormWorld0/OSINT.git"
    target_dir = os.path.join(ROOT, "script", "osint")
    # 1. Clone Repo
    if os.path.exists(os.path.join(target_dir, ".git")):
        print("[!] Module found. Updating...")

        try:
            # 1. Get the latest info without changing the locale first
            subprocess.run(
                ["git", "-C", target_dir, "fetch", "--all"], stdout=subprocess.DEVNULL
            )
            # 2. CHECK CHANGES: Compare local (HEAD) with server (origin/main)
            check_diff = subprocess.run(
                ["git", "-C", target_dir, "diff", "--name-only", "HEAD", "origin/main"],
                capture_output=True,
                text=True,
            )
            # 3. Reset Execution (Update file to the latest version)
            process = subprocess.run(
                ["git", "-C", target_dir, "reset", "--hard", "origin/main"],
                stdout=subprocess.PIPE,
                text=True,
            )
            if process.returncode == 0:
                print(f"[✓] update success.")

        except Exception as e:
            print(f"[-] Update failed: {e}")
    else:
        print("[*] Downloading OSINT Module...")
        subprocess.run(["git", "clone", repo_url, target_dir], check=True)

    # 2. Installation via setup.py
    setup_file = os.path.join(target_dir, "setup.py")
    if os.path.exists(setup_file):
        print("[*] Detected setup.py. Installing module in editable mode...")
        extra = (
            []
            if "com.termux" in os.environ.get("PREFIX", "")
            else ["--break-system-packages"]
        )
        # multi environment, this is good for users testing on termux or standard linux
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "."] + extra,
            cwd=target_dir,
            check=True,
        )

        print("[✓] OSINT Package installed successfully.")
    try:
        from scripts.security.sign import generate_folder_manifest

        generate_folder_manifest()
        return True
    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    install_osint_module()
