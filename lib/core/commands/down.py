from app.utility.module.down_osint import install_osint_module
from app.utility.module.down_ghosint import install_ghunt_module
from app.utility.restart import run_restart
from app.utility.colors import C


# Download all OSINT modules from the repo
# The OSINT structure will be applied according to the storm logic rules.
def execute(args, context):
    cmd = args[0].lower() if args else ""
    if not cmd:
        print(f"{C.ERROR}[!] ERROR: Not module selected")
        return context
    if cmd == "osint":
        status = install_osint_module()
        if status == True:
            run_restart(context)

    elif cmd == "ghosint":
        status = install_ghunt_module()
        if status == True:
            run_restart(context)

    else:
        print(f"{C.INPUT}[-] WARN => {cmd} > Not found.")

    return context
