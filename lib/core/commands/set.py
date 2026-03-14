import app.utility.utils as utils
from app.utility.colors import C


def execute(args, context):
    options = context["options"]
    if len(args) >= 2:
        var_name = args[0].upper()
        var_value = args[1]
        if "PASS" in var_name:
            found_path = utils.resolve_path(var_value)
            if found_path:
                options[var_name] = found_path
                print(f"{var_name} => {found_path}")
            else:
                print(f"{C.INPUT}[-] WARN => {var_value} > not found!")
        else:
            options[var_name] = var_value
            print(f"{var_name} => {var_value}")
    else:
        print(f"{C.INPUT}[!] Try: set <VARIABLE> <VALUE>")

    context["options"] = options
    return context
