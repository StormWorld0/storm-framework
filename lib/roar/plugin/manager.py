# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import importlib.util
import sys
import threading
import smf
import gc

from apps.utility.colors import CC
from rootmap import ROOT
from pathlib import Path
from typing import Dict, Set, Optional, Any

from .storage import PluginStateStore
from .safe import SafePluginProxy, NullPlugin
from .inspection import extract_plugin
from .result import PluginResult


class PluginManager:
    """STATE MEMORY (Module-Level Singleton)"""

    def __init__(self):
        self._PLUGIN_DIR: Path = Path(ROOT) / "plugin"

        self._store = PluginStateStore()
        self._lock = threading.RLock()
        self._plugin_index: Dict[str, Path] = {}

        self._REGISTRY: Dict[str, Any] = {}
        self._ACTIVE_PLUGINS: Set[str] = self._store.load_active_plugins()

    # ==========================================
    # CORE LOGIC OBJECT
    # ==========================================
    def build_index(self) -> None:
        """O(N) executed ONLY ONCE. Membangun Hash Map menggunakan Shallow Scan."""
        self._plugin_index.clear()

        for child in self._PLUGIN_DIR.iterdir():
            if child.name.startswith(".") or child.name.startswith("__"):
                continue

            if child.is_dir():
                init_file = child / "__init__.py"
                if init_file.exists():
                    self._plugin_index[child.name] = init_file
            elif child.is_file() and child.suffix == ".py":
                self._plugin_index[child.stem] = child

    def resolve_plugin_path(self, plugin_name: str) -> Optional[Path]:
        """O(1) Directory Traversal via Hash Map."""
        return self._plugin_index.get(plugin_name)

    def purge_module_from_memory(self, plugin_name: str) -> None:
        """Hard Cleanup: Removes the main module AND all its submodules."""
        keys_to_remove = [
            k for k in sys.modules if k == plugin_name or k.startswith(f"{plugin_name}.")
        ]
        for k in keys_to_remove:
            del sys.modules[k]

        importlib.invalidate_caches()

    def load_module(self, plugin_name: str) -> bool:
        """Fungsi kompilasi AST & Memory Allocation tingkat rendah."""
        with self._lock:
            plugin_path = self.resolve_plugin_path(plugin_name)
            if not plugin_path or not plugin_path.exists():
                smf.printf(
                    f"[!]{CC.YELLOW} Plugin not found on disk =>{CC.RESET}", plugin_name
                )
                return False

            try:
                smf.printd("Resolving module path", plugin_name, level="INFO")

                spec = importlib.util.spec_from_file_location(
                    plugin_name, str(plugin_path)
                )
                if spec is None or spec.loader is None:
                    smf.printd(f"Cannot create module spec for {plugin_path}")
                    return False

                module = importlib.util.module_from_spec(spec)
                sys.modules[plugin_name] = module
                spec.loader.exec_module(module)

                # Validasi dan ekstrak instance OOP atau modul biasa
                plugin_obj, plugin_type = extract_plugin(module, plugin_name)

                if plugin_type == "BROKEN":
                    self.purge_module_from_memory(plugin_name)
                    smf.printd(
                        "Plugin does not pass OOP/FUNC validation",
                        plugin_type,
                        level="ERROR",
                    )
                    return False

                # Wrap with SafePluginProxy
                safe_instance = SafePluginProxy(plugin_name, plugin_obj)
                self._REGISTRY[plugin_name] = safe_instance

                # --- WRAPPER DAEMON UNTUK ISOLASI CRASH ---
                def daemon_runner(self, target_func, p_name):
                    """Wrapper thread untuk menangkap runtime exception & melakukan teardown."""
                    try:
                        target_func()
                    except Exception as e:
                        smf.printd(
                            f"FATAL Plugin Daemon CRASHED => {p_name}", e, level="ERROR"
                        )
                        # Menggunakan global lock saat memodifikasi state manager dari thread anak
                        with self._lock:
                            self._REGISTRY[p_name] = NullPlugin(p_name)
                            self._store.remove_plugin(p_name)

                        # menjalankan di luar supaya tidak deadlock
                        self.purge_module_from_memory(p_name)
                        smf.printd(
                            f"Cleanup complete for crashed plugin: {p_name}", level="INFO"
                        )

                # --- ENTRY POINT LOGIC ---
                if plugin_type == "OOP" and getattr(module, "__autorun__", False):
                    smf.printd(f"Starting OOP Daemon for =>", plugin_name, level="INFO")

                    runner = threading.Thread(
                        target=daemon_runner,
                        args=(
                            plugin_obj.execute,
                            plugin_name,
                        ),  # Passing target ke wrapper
                        name=f"Daemon-{plugin_name}",
                        daemon=True,
                    )
                    runner.start()

                elif plugin_type == "FUNCTIONAL" and getattr(
                    module, "__autorun__", False
                ):
                    start_routine = getattr(module, "execute", None)
                    if start_routine:
                        smf.printd(
                            "Starting FUCNTIONAL Daemon for =>", plugin_name, level="INFO"
                        )

                        runner = threading.Thread(
                            target=daemon_runner,
                            args=(
                                start_routine,
                                plugin_name,
                            ),  # Passing target ke wrapper
                            name=f"Daemon-{plugin_name}",
                            daemon=True,
                        )
                        runner.start()

                smf.printd("Plugin loaded successfully", plugin_name, level="INFO")
                return True
            except Exception as e:
                smf.printf(
                    f"[!]{CC.YELLOW} Failed to load plugin =>{CC.RESET}", plugin_name
                )
                smf.printd(f"Failed to load plugin [{plugin_name}]", e, level="ERROR")

                # Delete from Memory (existing or not) on validation error
                self._REGISTRY[plugin_name] = NullPlugin(plugin_name)
                self.purge_module_from_memory(plugin_name)
                self._store.remove_plugin(plugin_name)
                return False


class LoadPlugin:
    """Called by API"""

    def __init__(self):
        self.pm = PluginManager()
        self._PLUGIN_DIR = self.pm._PLUGIN_DIR
        self._REGISTRY = self.pm._REGISTRY
        self._ACTIVE_PLUGINS = self.pm._ACTIVE_PLUGINS
        self._store = self.pm._store

        self._lock = threading.RLock()

    def load(self, plugin_name: str) -> bool:
        with self._lock:
            self.pm.build_index()
            success = self.pm.load_module(plugin_name)
            if success:
                self._ACTIVE_PLUGINS.add(plugin_name)
                self._store.add_plugin(plugin_name)
                smf.printf(
                    f"[✓]{CC.GREEN} Plugin loaded successfully =>{CC.RESET}", plugin_name
                )
            return success

    def unload(self, plugin_name: str) -> bool:
        with self._lock:
            if plugin_name not in self._REGISTRY:
                return False
            try:
                plugin_instance = self._REGISTRY[plugin_name]
                # Search function (teardown)
                if hasattr(plugin_instance, "teardown") and callable(
                    plugin_instance.teardown
                ):
                    try:
                        # Execute (teardown) the plugin's properties
                        plugin_instance.teardown()
                    except Exception as e:
                        smf.printd(
                            f"Error during {plugin_name} teardown", e, level="ERROR"
                        )

                # Remove from Register
                del self._REGISTRY[plugin_name]
                # Remove from load plugin
                self._ACTIVE_PLUGINS.discard(plugin_name)
                # Delete from cache
                self._store.remove_plugin(plugin_name)
                # Remove from sys.modules
                self.pm.purge_module_from_memory(plugin_name)
                # Call the Garbage Collector
                gc.collect()
                smf.printf(
                    f"[✓]{CC.GREEN} Plugin unloaded completely =>{CC.RESET}", plugin_name
                )
                return True
            except Exception as e:
                smf.printd(f"Failed to unload plugin {plugin_name}", e, level="ERROR")
                return False

    def boot(self) -> bool | None:
        smf.printd("Plugin service is running", level="INFO")
        try:
            for p_name in tuple(self._ACTIVE_PLUGINS):
                self.pm.load_module(p_name)
            return True
        except Exception:
            return None

    def get_plugin(self, plugin_name: str) -> Any:
        """Mengambil proxy plugin dari RAM."""
        plugin = self._REGISTRY.get(plugin_name)
        if plugin is None:
            smf.printd(
                "Caller requested inactive/missing plugin", plugin_name, level="WARN"
            )
            return NullPlugin(plugin_name)
        return plugin

    def broadcast(
        self, event_name: str, *args: Any, **kwargs: Any
    ) -> Dict[str, PluginResult]:
        """Sends events to all active and compatible Plugins"""

        results: Dict[str, PluginResult] = {}
        with self._lock:
            current_registry = list(self._REGISTRY.items())

        for plugin_name, safe_proxy in current_registry:
            event_hook = getattr(safe_proxy, event_name, None)
            if event_hook and callable(event_hook):
                try:
                    # Execute the hook and save the result
                    res = event_hook(*args, **kwargs)
                    if isinstance(res, PluginResult):
                        results[plugin_name] = res
                    else:
                        results[plugin_name] = PluginResult.ok(res)
                except Exception as e:
                    smf.printd(
                        f"Broadcast event [{event_name}] failed in plugin [{plugin_name}]",
                        e,
                        level="ERROR",
                    )
                    results[plugin_name] = PluginResult.fail(e)
        return results


# ==========================================
# AUTO-EXECUTION (Early Life Cycle)
# ==========================================
PluginManager().build_index()
LP = LoadPlugin()
