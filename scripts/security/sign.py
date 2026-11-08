import sys


def run_sign():
    try:
        from lib.roar.calling import call_so

        bin = call_so("libsigned")
        bin.storm_sign()
        return True
    except ImportError as e:
        print("[!] Critical => Binary not found.", file=sys.stderr)
        return False
    except Exception as e:
        smf.printf(f"[*] Error Exception in signed => {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    run_sign()
