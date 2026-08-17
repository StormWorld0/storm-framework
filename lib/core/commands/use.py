# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import smf
import apps.utility.utils as utils

from apps.utility.colors import CC


# Command use to lock or use a module that you want to use.
# here's an example as follows;
# Command => use <val>
# or
# Command => use scan
# in the input zone it will change to lock the scan so we know again
# using what module.
def execute(args, ctx):

    if not args:
        smf.printf(f"{CC.YELLOW}[!] Enter file name!{CC.RESET}")
        return

    module_name = args[0] if args else ""
    mod = utils.load_module_dynamically(module_name)

    if mod:
        ctx.current_module = mod
        ctx.current_module_name = module_name
    else:
        smf.printf(
            f"{CC.YELLOW}[!]{CC.RESET} {module_name} {CC.YELLOW}=> Not found.{CC.RESET}"
        )
