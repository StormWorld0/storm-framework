# MIT License.
# Copyright (c) 2026 Storm Framework
# See LICENSE file in the project root for full license information.

from app.utility.colors import C
try:
    from script.osint.handstorm import StormOSModuleRunner
except ImportError:
    print(
        f"[*] Try running {C.SUCCESS}down osint{C.RESET} first to download the module."
    )
REQUIRED_OPTIONS = {"EMAIL": ""}


def execute(options):
    mail = options.get("EMAIL")
    runner = StormOSModuleRunner()

    try:
        if mail:
            runner.set_options(mail)
            runner.run_module()
        else:
            print(
                f"{C.ERROR}[x] ERROR: EMAIL is not set. Use 'set email <target>'{C.RESET}"
            )
    except KeyboardInterrupt:
        return 
    except Exception as e:
        return {"status": "error": "message": str(e)}

