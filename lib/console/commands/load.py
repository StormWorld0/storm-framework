# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import smf

from apps.utility.colors import *


# This command is used to activate the plugin.
# by loading it into memory manually
# so that it can be immediately activated and used by the machine.
#
# Command => load <plugin_name>
#
# It will automatically load the plugin into memory.
def execute(args, ctx):

    # Input validation
    if not args:
        smf.printf(f"{CC.YELLOW}[!] Use the command > load <plugin_name>{CC.RESET}")
        return

    # Get plugin name from input
    cmd = args[0].lower()
    # Load plugin into memory
    ctx.plugin.load(cmd)
