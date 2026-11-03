# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import os
import sys
import smf
import lib.smf.core.sf.svch as svch
from apps.utility.colors import CC
from lib.smf.core.manage import PIDManager as pid


# This is to restart and save the variables that were set before restarting and then restore them.
# This is good if we experience a bug or error failure when we are ready to execute.
# by storing old variable data, it is very profitable and speeds up the time
def execute(args, ctx):
    options = ctx.options
    # save old variables
    svch.session(options)
    # Kill the active process
    pid.cleanup(timeout=1.0)
    # Restart the storm
    executable = sys.argv[0]
    args = sys.argv
    try:
        os.execv(executable, args)
    except Exception as e:
        smf.printf(f"[!] {CC.YELLOW}Restarting failed{CC.RESET}", file=sys.stderr)
        smf.printd("Error while restarting", e, level="ERROR")
        sys.exit(1)
