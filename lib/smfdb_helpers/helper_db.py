import sys
import smf
from .log_utils import extract_logs


def log_export():
    level = "debug"
    try:
        if "--data" in sys.argv:
            index = sys.argv.index("--log")
            if index + 1 < len(sys.argv):
                level = sys.argv[index + 1]

        levup = level.upper()
        outfile = f"log_{level}.txt"

        valid_levels = {"ALL", "DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"}
        if levup not in valid_levels:
            smf.printf(
                f"[!] Unknown log level => {levup} >> Allowed => {', '.join(valid_levels)}"
            )
            # Monitor user typos
            smf.printd("Invalid log extraction attempt", levup, level="WARN")
            return

        extract_logs(levup, outfile)
    except Exception as e:
        smf.printf(f"[*] Error Exception Wrapper Data => {e}")
        sys.exit(1)

if __name__ == "__main__":
    log_export()
