import requests
import subprocess
from app.utility.colors import C


def run_update():
    url = (
        "https://raw.githubusercontent.com/StormWorld0/storm-framework/main/version.txt"
    )
    try:
        response = requests.get(url, timeout=5)
        latest_version = response.text.strip()
    except:
        pass
    # 1. Get the latest info without changing the locale first
    subprocess.run(["git", "fetch", "--all"], stdout=subprocess.DEVNULL)

    # 2. CHECK CHANGES: Compare local (HEAD) with server (origin/main)
    check_diff = subprocess.run(
        ["git", "diff", "--name-only", "HEAD", "origin/main"],
        capture_output=True,
        text=True,
    )

    # 3. Reset Execution (Update file to the latest version)
    process = subprocess.run(
        ["git", "reset", "--hard", "origin/main"], stdout=subprocess.PIPE, text=True
    )

    if process.returncode == 0:
        print(f"{C.SUCCESS}\n[✓] System updated to version: {latest_version}{C.RESET}")

    # 4. Trigger Compiler ONLY IF needed
    try:
        from scripts.security.sign import generate_folder_manifest

        generate_folder_manifest()
        return True
    except Exception as e:
        print(f"ERROR: {e}")
