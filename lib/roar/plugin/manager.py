# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import importlib.util
import sys
import threading
import smf
import gc

from rootmap import ROOT
from pathlib import Path

from typing import Dict, Set, Optional, Any
from .storage import PluginStateStore
from .safe import SafePluginProxy, NullPlugin
from .inspection import extract_plugin

# ==========================================
# STATE MEMORY (Module-Level Singleton)
# Menggantikan peran `self`
# ==========================================
PLUGIN_DIR: Path = Path(ROOT) / "plugin"
PLUGIN_DIR.mkdir(parents=True, exist_ok=True)

_store = PluginStateStore()
_lock = threading.RLock()
_plugin_index: Dict[str, Path] = {}

REGISTRY: Dict[str, Any] = {}
ACTIVE_PLUGINS: Set[str] = _store.load_active_plugins()


# ==========================================
# CORE LOGIC (Pure Functions)
# ==========================================
def build_index() -> None:
    """O(N) executed ONLY ONCE. Membangun Hash Map menggunakan Shallow Scan."""
    _plugin_index.clear()

    for child in PLUGIN_DIR.iterdir():
        if child.name.startswith(".") or child.name.startswith("__"):
            continue

        if child.is_dir():
            init_file = child / "__init__.py"
            if init_file.exists():
                _plugin_index[child.name] = init_file
        elif child.is_file() and child.suffix == ".py":
            _plugin_index[child.stem] = child


def resolve_plugin_path(plugin_name: str) -> Optional[Path]:
    """O(1) Directory Traversal via Hash Map."""
    return _plugin_index.get(plugin_name)


def purge_module_from_memory(plugin_name: str) -> None:
    """Hard Cleanup: Removes the main module AND all its submodules."""
    keys_to_remove = [
        k for k in sys.modules if k == plugin_name or k.startswith(f"{plugin_name}.")
    ]
    for k in keys_to_remove:
        del sys.modules[k]
    importlib.invalidate_caches()


# DI PANGGIL OLEH API
def get_plugin(plugin_name: str) -> Any:
    """Mengambil proxy plugin dari RAM."""
    plugin = REGISTRY.get(plugin_name)
    if plugin is None:
        smf.printd("Caller requested inactive/missing plugin", plugin_name, level="WARN")
        return NullPlugin(plugin_name)
    return plugin



def load_module(plugin_name: str) -> bool:
    """Fungsi kompilasi AST & Memory Allocation tingkat rendah."""
    with _lock:
        plugin_path = resolve_plugin_path(plugin_name)
        if not plugin_path or not plugin_path.exists():
            smf.printf("[!] Plugin not found on disk =>", plugin_name)
            return False

        try:
            smf.printd("Resolving module path", plugin_name, level="INFO")

            spec = importlib.util.spec_from_file_location(plugin_name, str(plugin_path))
            if spec is None or spec.loader is None:
                smf.printd(f"Cannot create module spec for {plugin_path}")
                return False

            module = importlib.util.module_from_spec(spec)
            sys.modules[plugin_name] = module
            spec.loader.exec_module(module)

            # Validasi dan ekstrak instance OOP atau modul biasa
            plugin_obj, plugin_type = extract_plugin(module, plugin_name)

            if plugin_type == "BROKEN":
                purge_module_from_memory(plugin_name)
                smf.printd(
                    "Plugin does not pass OOP/FUNC validation", plugin_type, level="WARN"
                )
                return False

            # Wrap with SafePluginProxy
            safe_instance = SafePluginProxy(plugin_name, plugin_obj)
            REGISTRY[plugin_name] = safe_instance

            # --- WRAPPER DAEMON UNTUK ISOLASI CRASH ---
            def daemon_runner(target_func, p_name):
                """Wrapper thread untuk menangkap runtime exception & melakukan teardown."""
                try:
                    target_func()
                except Exception as e:
                    smf.printd(
                        f"FATAL Plugin Daemon CRASHED => {p_name}", e, level="ERROR"
                    )
                    # Menggunakan global lock saat memodifikasi state manager dari thread anak
                    with _lock:
                        REGISTRY[p_name] = NullPlugin(p_name)
                        purge_module_from_memory(p_name)
                        smf.printd(
                            f"Cleanup complete for crashed plugin: {p_name}", level="INFO"
                        )

            # --- ENTRY POINT LOGIC ---
            if plugin_type == "OOP" and hasattr(plugin_obj, "execute"):
                smf.printd(f"Starting OOP Daemon for => {plugin_name}", level="INFO")

                runner = threading.Thread(
                    target=daemon_runner,
                    args=(plugin_obj.execute, plugin_name),  # Passing target ke wrapper
                    name=f"Daemon-{plugin_name}",
                    daemon=True,
                )
                runner.start()

            elif plugin_type == "FUNCTIONAL" and getattr(module, "__autorun__", False):
                start_routine = getattr(module, "execute", None)
                if start_routine:
                    smf.printd(
                        f"Spawning background thread for autorun plugin =>",
                        plugin_name,
                        level="INFO",
                    )

                    runner = threading.Thread(
                        target=daemon_runner,
                        args=(start_routine, plugin_name),  # Passing target ke wrapper
                        name=f"Daemon-{plugin_name}",
                        daemon=True,
                    )
                    runner.start()

            smf.printd("Plugin loaded successfully", plugin_name, level="INFO")
            return True
        except Exception as e:
            smf.printf(f"Failed to load plugin =>", plugin_name)
            smf.printd(f"Failed to load plugin [{plugin_name}]", e, level="ERROR")

            # Delete from Memory (existing or not) on validation error
            REGISTRY[plugin_name] = NullPlugin(plugin_name)
            purge_module_from_memory(plugin_name)
            _store.remove_plugin(plugin_name)
            return False


def load(plugin_name: str) -> bool:
    with _lock:
        build_index()
        success = load_module(plugin_name)
        if success:
            ACTIVE_PLUGINS.add(plugin_name)
            _store.add_plugin(plugin_name)
            smf.printf("[✓] Plugin loaded successfully =>", plugin_name)
        return success


def unload(plugin_name: str) -> bool:
    with _lock:
        if plugin_name not in REGISTRY:
            return False
        try:
            plugin_instance = REGISTRY[plugin_name]
            # Search function (teardown)
            if hasattr(plugin_instance, "teardown") and callable(plugin_instance.teardown):
                try:
                    # Execute (teardown) the plugin's properties
                    plugin_instance.teardown()
                except Exception as e:
                    smf.printd(f"Error during {plugin_name} teardown", e, level="ERROR")

            # Remove from Register
            del REGISTRY[plugin_name]
            # Remove from load plugin
            ACTIVE_PLUGINS.discard(plugin_name)
            # Delete from cache
            _store.remove_plugin(plugin_name)
            # Remove from sys.modules
            purge_module_from_memory(plugin_name)
            # Call the Garbage Collector
            gc.collect()
            
            smf.printf("[✓] Plugin unloaded completely =>", plugin_name)
            return True
        except Exception as e:
            smf.printd(f"Failed to unload plugin {plugin_name}", e, level="CRITICAL")
            return False


def boot() -> None:
    for p_name in tuple(ACTIVE_PLUGINS):
        load_module(p_name)


def broadcast(event_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
    """
    Mengirimkan event ke semua plugin yang terdaftar di REGISTRY secara dinamis.

    Returns:
        Dict[str, Any]: Mapping antara nama plugin dan hasil return dari plugin tersebut.
                        Contoh: {"decode_plugin": {"handled": True}}
    """
    results: Dict[str, Any] = {}

    with _lock:
        # Gunakan list(REGISTRY.items()) untuk menghindari RuntimeError
        current_registry = list(REGISTRY.items())

    for plugin_name, safe_proxy in current_registry:
        #    Deteksi hook fungsi secara dinamis pada module/proxy.
        #    Mendukung format 'pre_execute' langsung sebagai nama fungsi di dalam modul plugin.
        event_hook = getattr(safe_proxy, event_name, None)

        if event_hook and callable(event_hook):
            try:
                # Eksekusi hook dan simpan hasilnya
                res = event_hook(*args, **kwargs)

                # Kita hanya mencatat plugin yang mengembalikan data (bukan None)
                if res is not None:
                    results[plugin_name] = res

            except Exception as e:
                smf.printd(
                    f"Broadcast event [{event_name}] failed in plugin [{plugin_name}]",
                    e,
                    level="ERROR",
                )
                results[plugin_name] = {"handled": False, "error": str(e)}

    return results


# ==========================================
# AUTO-EXECUTION (Siklus Hidup Awal)
# ==========================================
# Membangun indeks otomatis saat `import manager` dipanggil pertama kali
build_index()
