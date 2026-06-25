# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import smf
import inspect
import apps.utility.utils as utils

from apps.utility.colors import *


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
    options = ctx.options
    plugin = ctx.plugin

    if not current_module:
        smf.printf(f"{CC.YELLOW}[!] No modules selected. (use <module>) first.{CC.RESET}")
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
            f"{CC.YELLOW}[!] Failed to run. Variabel null: {', '.join(missing)}{CC.RESET}"
        )
        return

    metadata = getattr(current_module, "metadata", {})

    # Path Resolution for local files
    if options.get("PASS"):
        full_path = utils.resolve_path(options["PASS"])
        if full_path:
            options["PASS"] = full_path

    # Runtime
    module_runtime = ctx.runtime(metadata=metadata, plugin_manager=plugin)

    # Execution module
    try:
        execute_func = current_module.execute
        sig = inspect.signature(execute_func)

        # Hitung parameter yang bisa menerima argumen posisi
        valid_params = [
            p
            for p in sig.parameters.values()
            if p.kind in (p.POSITIONAL_OR_KEYWORD, p.POSITIONAL_ONLY)
        ]

        if len(valid_params) >= 2:
            execute_func(options, module_runtime)
        else:
            execute_func(options)

    except AttributeError as e:
        smf.printd("ATTRIBUTE ERROR COMMAND RUN", e, level="ERROR")
        smf.printf(f"{CC.RED}[!] RUN ATTRIBUTE ERROR{CC.RESET}")

    except Exception as e:
        smf.printd("ERROR COMMAND RUN EXCEPTION", e, level="ERROR")
        smf.printf(f"{CC.RED}[!] ERROR DURING EXECUTION{CC.RESET}")
