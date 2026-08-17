import inspect
import smf
import ast

from typing import Any
from pathlib import Path

from .safe import NullPlugin


def inspect_teardown(file_path: Path) -> dict:
    source = file_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(file_path))

    uses_threading = False
    uses_asyncio = False
    has_teardown = False

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "threading":
                    uses_threading = True
                elif alias.name == "asyncio":
                    uses_asyncio = True

        elif isinstance(node, ast.ImportFrom):
            if node.module == "threading" or (
                node.module and node.module.startswith("threading.")
            ):
                uses_threading = True

            elif node.module == "asyncio" or (
                node.module and node.module.startswith("asyncio.")
            ):
                uses_asyncio = True

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == "teardown":
                has_teardown = True

    requires_teardown = uses_threading or uses_asyncio
    return {"valid": not requires_teardown or has_teardown}


def extract_plugin(module: Any, plugin_name: str) -> tuple[Any, str]:
    """
    Validasi ketat arsitektur plugin.
    Jika plugin OOP cacat/gagal inisialisasi, kembalikan NullPlugin agar runtime tetap stabil.
    """
    # 1. Jika tidak ada atribut 'Plugin', 100% Fungsional
    if not hasattr(module, "Plugin"):
        return module, "FUNCTIONAL"

    # ==========================================
    # ZONA OOP: Karena ada 'Plugin', diproses sebagai OOP
    # ==========================================
    plugin_class = getattr(module, "Plugin")

    # [VALIDASI 1] Cek apakah benar Class?
    if not inspect.isclass(plugin_class):
        smf.printd(
            f"[{plugin_name}] The 'Plugin' attribute is not a Class", level="ERROR"
        )
        return NullPlugin(module), "BROKEN"

    # [VALIDASI 2] Cek entry point 'execute()'
    if not hasattr(plugin_class, "execute") or not callable(
        getattr(plugin_class, "execute")
    ):
        smf.printd(
            f"OOP Plugin [{plugin_name}] has no entry point 'execute()'", level="ERROR"
        )
        return NullPlugin(module), "BROKEN"

    if hasattr(module, "__file__"):
        teardown_info = inspect_teardown(Path(module.__file__))

        if not teardown_info["valid"]:
            smf.printd(
                f"Plugin [{plugin_name}] uses threading/asyncio",
                f"but has no teardown()",
                level="ERROR",
            )
            return NullPlugin(module), "BROKEN"

    # [STATE ALLOCATION]
    try:
        plugin_instance = plugin_class()
        return plugin_instance, "OOP"
    except Exception as e:
        smf.printd(f"Failed __init__ class Plugin on [{plugin_name}]", e, level="ERROR")
        return NullPlugin(module), "BROKEN"
