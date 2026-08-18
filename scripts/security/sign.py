import sys

try:
    import smf
except ImportError:
    print("[!] Error import smf")


def run_sign():
    try:
        from lib.roar.calling import call_so

        bin = call_so("libsigned")

        bin.storm_sign()
        return True
    except ImportError as e:
        smf.print(
            "[!] Critical => Binary not found.",
            file=sys.stderr,
            flush=True,
        )
        smf.printd("Import error libsigned binary not found", e, level="CRITICAL")
        return False
    except Exception as e:
        smf.printf("[*] Error Exception in signed", e, flush=True)
        smf.printd("Error exception in libsigned", e, level="CRITICAL")
        return False


if __name__ == "__main__":
    run_sign()
