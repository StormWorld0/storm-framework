import subprocess
from lib.roar.crs.net_api import HTTPR


def run_update():
    url = "https://raw.githubusercontent.com/StormWorld0/storm-framework/main/data/data.json"
    try:
        http = HTTPR()
        http.get(url)
        resp = http.run()
        latest_version = resp.json()["version"]
    except Exception as e:
        print(f"ERROR VERSION UPDATE => {e}")

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
        print(f"\n[✓] System updated to version => {latest_version}")

    # 4. Trigger Compiler ONLY IF needed
    try:
        from scripts.cpl import compiler

        compiler.start_build()
    except ImportError as e:
        print(f"Error import compiler => {e}")
        return
    except Exception as e:
        print(f"Error when running the compiler => {e}")
        return

    # 5. Trigger Signed to all file
    try:
        from scripts.security.sign import run_sign

        run_sign()
        return True
    except ImportError as e:
        print(f"Error import => {e}")
        return False
    except Exception as e:
        print(f"Error executing signature => {e}")
        return False


if __name__ == "__main__":
    run_update()
