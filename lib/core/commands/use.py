# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import smf
import importlib
import apps.utility.load_db as db
from apps.utility.colors import CC


def load_module_dynamically(module_name):
    # Returns module_path or module_name from DB
    actual_path = db.resolve_module_path(module_name)

    if not actual_path:
        return None

    # Direct transformation to dot notation for Python import
    module_dots = f"modules.{actual_path.replace('/', '.')}"

    try:
        return importlib.import_module(module_dots)
    except Exception as e:
        smf.printd("Dynamic import error", f"{module_dots} -> {repr(e)}", level="ERROR")
        return None


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
    mod = load_module_dynamically(module_name)

    if mod:
        ctx.current_module = mod
        ctx.current_module_name = module_name
    else:
        smf.printf(
            f"{CC.YELLOW}[!]{CC.RESET} {module_name} {CC.YELLOW}=> Not found.{CC.RESET}"
        )
