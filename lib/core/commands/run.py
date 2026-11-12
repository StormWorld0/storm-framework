# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import smf
import inspect
import apps.utility.utils as utils
from apps.utility.colors import CC


def aexc(net):
    sock = net.Socket()
    http = net.HTTPR()
    return (
        sock,
        http,
    )


# Run command to run a module that we want to execute
# The workflow is as below;
#
# Command => use <module_name> or <path_module>
# Command => set <var> <val>
# Command => run
#
# After running the module will run and you just have to wait for it to finish.
def execute(args, ctx):
    current_module = ctx.current_module
    module_name = ctx.current_module_name
    options = ctx.options
    manager = ctx.plugin
    _net = ctx.net

    if not current_module:
        smf.printf(f"[!] {CC.YELLOW}No modules selected. (use <module>) first.{CC.RESET}")
        return

    # Validate options
    required_vars = getattr(current_module, "REQUIRED_OPTIONS", {})
    missing = []

    for key, description in required_vars.items():
        # Sanitize descriptions to lowercase to avoid case-sensitivity
        desc_lower = str(description).lower()

        # Keyword sanitation description key
        is_optional = (
            "(opsional)" in desc_lower
            or "(optional)" in desc_lower
            or "opsional" in desc_lower
            or "optional" in desc_lower
        )

        # Get the value entered by the user
        user_value = str(options.get(key, "")).strip()

        # If it is not optional AND the user has not filled in the value
        if not is_optional and not user_value:
            missing.append(key)

    if missing:
        smf.printf(
            f"[!]{CC.YELLOW} Failed to run. Variabel null:{CC.RESET} {', '.join(missing)}"
        )
        return

    # Path Resolution for local files
    if options.get("PASS"):
        full_path = utils.resolve_path(options["PASS"])
        if full_path:
            options["PASS"] = full_path

    # A set of custom exceptions
    # to handle forced module termination if something is detected on the network
    # The final security if the module does not use exceptions.
    sock, http = aexc(_net)

    # Execution module
    try:
        execute = current_module.execute
        sig = inspect.signature(execute)

        # Count parameters that can accept positional arguments
        valid_params = [
            p
            for p in sig.parameters.values()
            if p.kind in (p.POSITIONAL_OR_KEYWORD, p.POSITIONAL_ONLY)
        ]

        if len(valid_params) >= 2:
            execute(options, _net)
        else:
            execute(options)
    except sock.HttpException as e:
        smf.printf(f"{CC.RED}Module error =>{CC.RESET}", module_name)
        smf.printd("Module detected error", e, level="ERROR")
        return
    except sock.SocketException as e:
        smf.printf(f"{CC.RED}Module error =>{CC.RESET}", module_name)
        smf.printd("Module detected error", e, level="ERROR")
        return
    except (Exception, RuntimeError, AttributeError) as e:
        smf.printf(f"{CC.RED}Module error =>{CC.RESET}", module_name)
        smf.printd("Module detected error", e, level="ERROR")
        return
