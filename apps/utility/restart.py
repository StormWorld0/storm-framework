# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author: zxelzy

import os
import sys
import smf
import lib.smf.core.sf.svch as svch

from lib.pid_manager import PIDManager as pid


def run_restart(options):
    # save old variables
    svch.session(options)
    # Kill the active process
    pid.cleanup()
    # Restart the storm
    executable = sys.argv[0]
    args = sys.argv
    try:
        os.execv(executable, args)
    except Exception as e:
        smf.printd("Error while restarting", e, level="ERROR")
        smf.printf(f"[!] Restart failed")
        sys.exit(1)
