import os
import subprocess
import sys

from rootmap import ROOT

def down_ghunt():
    repo_url = "https://github.com/storm-os/GhOSINT.git"
    target_dir = os.path.join(ROOT, "script", "ghunt")

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


    
    venv_dir = base_path / "venv"
    python_exe = venv_dir / "bin" / "python"
    pip_exe = venv_dir / "bin" / "pip"

    try:
        # 1. Buat Virtual Environment
        if not venv_dir.exists():
            print("[+] Creating Virtual Environment...")
            subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
        else:
            print("[!] Venv already exists. Skipping creation.")

        # Kita install langsung 'ghunt' dari PyPI atau dari folder jika ada requirements.txt
        subprocess.run([str(pip_exe), "install", "--upgrade", "pip"], check=True)
        subprocess.run([str(pip_exe), "install", "ghunt"], check=True)

        # 3. Install Playwright (Wajib untuk GHunt login/scraping)
        subprocess.run(
            [str(python_exe), "-m", "playwright", "install", "chromium"], check=True
        )

        print("\n[✔] GHunt Installation Complete!")
        return True
    except Exception as e:
        print(f"\n[-] Installation Failed: {e}")
        return False


