import os
import sys
import lib.smf.core.sf.svch as svch


def run_restart(context):
    # save old variables
    svch.session(context["options"])
    # Restart the storm
    executable = sys.argv[0]
    args = sys.argv
    try:
        os.execv(executable, args)
    except Exception as e:
        print(f"[-] Restart failed: {e}")
        sys.exit(1)
