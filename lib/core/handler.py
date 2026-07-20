import importlib
import os
import smf

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lib.smf.core.console.engine import Context


def execute(cmd: str, args: list[str], ctx: "Context") -> bool:
    """
    Central function to search for and execute command files.
    Returns True if the command is found,
    and returns False if the command file does not exist.
    """
    # [Security / Sanity Check]
    # Prevent potential LFI
    safe_cmd = os.path.basename(cmd)

    cmd_path = os.path.join("lib", "core", "commands", f"{safe_cmd}.py")

    if os.path.exists(cmd_path):
        try:
            # Import modules dynamically
            cmd = importlib.import_module(f"lib.core.commands.{safe_cmd}")

            # [Context Mutation Execution]
            # Pass a `ctx` object into the command module.
            # The module will modify the properties of `ctx`
            # directly in memory (in-place modification).
            cmd.execute(args, ctx)

            return True  # Routing successfully handled
        except KeyboardInterrupt:
            return True

        except Exception as e:
            smf.printf("[!] ERROR COMMAND =>", safe_cmd)
            smf.printd("ERROR WHEN EXECUTING A COMMAND", safe_cmd, e, level="ERROR")
            return True

    return False
