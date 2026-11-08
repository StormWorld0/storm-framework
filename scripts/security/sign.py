import sys


def run_sign():
    try:
        from lib.roar.calling import call_so

        bin = call_so("libsigned")
        bin.storm_sign()
        return True
    except (Exception, ImportError) as e:
        print(f"[*] Error => {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    run_sign()
