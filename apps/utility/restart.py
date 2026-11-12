# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author: zxelzy

import os
import sys
import smf
import lib.smf.core.sf.svch as svch
from apps.utility.colors import CC
from lib.smf.core.manage import PIDManager as pid


def run_restart(options):
    # save old variables
    svch.session(options)
    # Kill the active process
    pid.cleanall(1.0)
    # Restart the storm
    executable = sys.argv[0]
    args = sys.argv
    try:
        os.execv(executable, args)
    except Exception as e:
        smf.printd("Error while restarting", e, level="ERROR")
        smf.printf(f"[!] {CC.YELLOW}Restarting failed{CC.RESET}")
        sys.exit(1)
