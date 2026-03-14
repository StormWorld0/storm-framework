import importlib
import os
from app.utility.colors import C


def execute(cmd, args, context):
    """
    Central function to search for and execute command files.
    """
    cmd_path = os.path.join("lib", "core", "commands", f"{cmd}.py")
    if os.path.exists(cmd_path):
        try:
            module = importlib.import_module(f"lib.core.commands.{cmd}")

            return module.execute(args, context)
        except KeyboardInterrupt:
            return context
        except Exception as e:
            print(f"{C.ERROR}[-] ERROR => {cmd} > {e}")
            return context

    return None
