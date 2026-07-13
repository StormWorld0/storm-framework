# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import smf
from apps.utility.colors import *


# This command is to delete data in the specified global variable.
# The command consists of two different mechanisms, namely;
#
# Command => unset <var>
# or
# Command => unset all
#
# unset <var> =>> To delete data in a specific variable.
# unset all =>> To delete data in all variables.
def execute(args, ctx):
    options = ctx.options

    # Validate at least 1 argument
    if len(args) >= 1:
        var_name = args[0].upper()

        # Validate the existence of keys in dictionary options
        if var_name not in options:
            smf.printf(
                f"[!]{CC.YELLOW} WARN =>{CC.RESET} {var_name} {CC.YELLOW}> is not a valid options!{CC.RESET}"
            )
            return

        # Reset the variable value to an empty string
        if var_name == "ALL":
            # Remove values from all variables
            for key in options.keys():
                options[key] = ""
            smf.printf(f"{CC.YELLOW}[*] All options have been unset.{CC.RESET}")
        else:
            # Delete value in specific variables
            options[var_name] = ""
            smf.printf(f"{CC.YELLOW}{var_name} => unset{CC.RESET}")
    else:
        # Displays command usage help if no arguments are given.
        smf.printf(f"[!]{CC.YELLOW} Use the command =>{CC.RESET} unset <VAR>")
