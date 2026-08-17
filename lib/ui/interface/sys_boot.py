# --- https://github.com/StormWorld0/storm-framework ---
# SMF License
# copyright (c) 2026
# Complete information about the License is in the root directory.
# Author: zxelzy

import readline  # noqa: F401
import sys
import smf

try:
    from lib.smf.core.booting.boot import boot as sysb
    from ..banner import banner as style_ui
    from .start_interfc import main
except ImportError as e:
    smf.printf(f"Error import interface =>", e, file=sys.stderr)
    sys.exit(100)


# Perform step by step initialization starting before entering the interface
# Booting to run the initial steps and determine security and stability
# Loading banner for style framework
# call main to activate (Read Eval Print Loop) interface
def system_booting():
    sysb()
    style_ui()
    main()
