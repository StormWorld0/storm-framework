# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import typing
import smf
import os
import shutil
import subprocess
import data.option.session as ops

from apps.utility.colors import CC
from lib.core import handler as i
from lib.roar.plugin_api import plugin
from lib.roar.crs import net_api as api
from dataclasses import dataclass, field

IGNORED_SYSTEM_COMMANDS = {
    # Shell Built-ins
    "cd",
    "alias",
    "source",
    "exec",
    # Text Editors & Pagers
    "nano",
    "vim",
    "vi",
    "emacs",
    "neovim",
    "less",
    "more",
    "head",
    "tail",
    "cat",
    # File / Directory Operations
    "mkdir",
    "touch",
    "rm",
    "rmdir",
    "cp",
    "mv",
    "chmod",
    "chown",
    "ln",
}


# ----------------------
# Network call function
# ----------------------
class NetContext:
    """
    NetContext for all Storm Framework network operations.
    Using Singleton and Dynamic Binding patterns.
    """

    def __init__(self):
        # Looping all function names registered in __all__ in net_api.py
        for func_name in api.__all__:
            # Get the function object from net_api.py
            func_obj = getattr(api, func_name)

            # Use the function that has been called
            setattr(self, func_name, func_obj)


@dataclass
class Context:
    """
    A representation of the Framework's execution state.
    This context is what the Pipeline will carry everywhere.
    """

    current_module: typing.Any = None
    current_module_name: str = ""
    options: dict = field(default_factory=ops.default_options)
    exit: bool = False
    plugin: typing.Any = plugin
    net: NetContext = field(default_factory=NetContext)

    def __post_init__(self) -> None:
        smf.printd("CONTEXT PLUGIN", self.plugin, level="DEBUG")
        smf.printd("CONTEXT RUNTIME", self.net, level="DEBUG")

    def _execute_external(self, cmd: str, args: list[str]) -> bool:
        """Melempar perintah ke alat eksternal."""
        cmd_clean = os.path.basename(cmd).strip().lower()

        if cmd_clean in IGNORED_SYSTEM_COMMANDS:
            smf.printd(
                f"Execution ignored: '{cmd_clean}' is a system utility/built-in",
                level="INFO",
            )
            return False

        path = shutil.which(cmd_clean)
        if not path:
            smf.printd("Command execution external Not found", path, level="INFO")
            return False

        smf.printd("Monitoring execution external", path, level="INFO")
        smf.printf()
        try:
            subprocess.run([path, *args], check=True)
            return True
        except KeyboardInterrupt:
            return True
        except subprocess.CalledProcessError as e:
            smf.printd(
                f"Execution failed for {cmd_clean}, exit code: {e.returncode}",
                level="WARN",
            )
            return True
        except (subprocess.SubprocessError, OSError) as e:
            smf.printd(f"Execution failed for {cmd}", e, level="ERROR")
            return True
        except Exception as e:
            smf.printd(f"Execution failed for {cmd}", e, level="ERROR")
            return False
        finally:
            smf.printf()

    def dispatch(self, cmd: str, args: list[str]) -> None:
        """
        This method is the gateway to the handler.
        Pipeline: Input -> Core (self) -> Handler -> Commands
        """
        # Pass 'self' (this context object itself) to the handler.
        # ex.execute now does not need to return a new dict,
        handled = i.execute(cmd, args, self)

        # Log all to internal
        smf.printd("Capture cmd dispatch", cmd, level="DEBUG")
        smf.printd("Capture dispatch args", args, level="DEBUG")

        if not handled:
            success = self._execute_external(cmd, args)
            if not success:
                smf.printf(
                    f"[!]{CC.YELLOW} Unknown Command =>{CC.RESET} {cmd} {CC.YELLOW}> Run the <help> command for more details.{CC.RESET}"
                )
