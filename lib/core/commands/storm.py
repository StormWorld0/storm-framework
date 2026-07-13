# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import smf

from apps.utility.colors import *
from apps.utility.update import run_update as update
from apps.utility.restart import run_restart as restart


# This command storm is used for several specific command values.
# for example give this;
#
# Command => storm update > to update the Storm Framework.
#
def execute(args, ctx):
    cmd = args[0].lower() if args else ""
    options = ctx.options

    if not cmd:
        smf.printf(
            f"[!]{CC.YELLOW} Incorrect input, Run (help) for complete information.{CC.RESET}"
        )
        return

    # I don't understand this update command, which sometimes happens when there is a big and sensitive update.
    # then sometimes integrity detects a missing file, which indicates that there is an identity but the file is missing on the disk
    # but I still recommend reinstalling for security and stability
    if cmd == "update":
        status = update()
        if status == True:
            restart(options)

    # Fallback not found
    else:
        smf.printf(f"[!]{CC.YELLOW} {cmd} => Not found.{CC.RESET}")
