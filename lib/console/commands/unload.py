# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import smf

from apps.utility.colors import *


# This command is used to turn off the plugin life cycle.
# active, in the following way;
#
# Command => unload <plugin_name>
#
# It will directly disable the active plugin.
def execute(args, ctx):

    # Input validation
    if not args:
        smf.printf(f"{CC.YELLOW}[!] Use the command =>{CC.RESET} unload <plugin_name>")
        return

    # Get plugin name command
    cmd = args[0].lower()

    # Unload plugin name
    ctx.plugin.unload(cmd)
