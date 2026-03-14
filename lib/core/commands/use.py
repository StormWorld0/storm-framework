import app.utility.utils as utils
from app.utility.colors import C


# No comment while it's still stable
def execute(args, context):
    module_name = args[0].lower() if args else ""
    mod = utils.load_module_dynamically(module_name)

    if mod:
        context["current_module"] = mod
        context["current_module_name"] = module_name
    else:
        print(f"{C.INPUT}[-] WARN => {module_name} > Not found.")

    return context
