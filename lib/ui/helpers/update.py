# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import requests
import subprocess
import sys


def update():
    url = "https://raw.githubusercontent.com/StormWorld0/storm-framework/main/data/data.json"
    try:
        latest_version = requests.get(url).json()["version"]
    except Exception as e:
        print(f"ERROR VERSION UPDATE => {e}")

    # Get the latest info without changing the locale first
    subprocess.run(["git", "fetch", "--all"], stdout=subprocess.DEVNULL)

    # CHECK CHANGES: Compare local (HEAD) with server (origin/main)
    check_diff = subprocess.run(
        ["git", "diff", "--name-only", "HEAD", "origin/main"],
        capture_output=True,
        text=True,
    )

    # Reset Execution (Update file to the latest version)
    process = subprocess.run(
        ["git", "reset", "--hard", "origin/main"], stdout=subprocess.PIPE, text=True
    )

    if process.returncode == 0:
        print(f"\n[✓] System updated to version => {latest_version}")

    # Trigger Compiler ONLY IF needed
    try:
        from scripts.cpl import compiler

        compiler.start_build()
    except ImportError as e:
        print(f"Error import compiler => {e}")
        sys.exit(100)
    except Exception as e:
        print(f"Error when running the compiler => {e}")
        sys.exit(100)

    try:
        from scripts.security.sign import run_sign

        run_sign()
    except ImportError as e:
        print(f"Error import => {e}")
        sys.exit(100)
    except Exception as e:
        print(f"Error executing signature => {e}")
        sys.exit(100)


if __name__ == "__main__":
    update()
