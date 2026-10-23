# --- https://github.com/StormWorld0/storm-framework ---
# SMF License
# copyright (c) 2026
# Complete information about the License is in the root directory.
# Author: zxelzy

import sys
import smf

try:
    from lib.smf.core.booting.free_boot import systemd as sysd
    from .control_ifc import systemctl as sysctl
    from ..banner import banner as style
except ImportError as e:
    smf.printf(f"Error import interface =>", e, file=sys.stderr)
    sys.exit(100)


# Perform step by step initialization starting before entering the interface
# Booting to run the initial steps and determine security and stability
# Loading banner for style framework
# call main to activate (Read Eval Print Loop) interface
def systemb():
    sysd()     # Running the boot system
    style()    # Displays the UI/UX style of the REPL session
    sysctl()   # Run the main control system
