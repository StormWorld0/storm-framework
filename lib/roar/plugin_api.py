# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import smf

from typing import Any, List, Dict

from .plugin import manager
from .plugin import monitoring
from .plugin import introspection


class StormAPI:
    """Plugin API Mechanism"""

    @staticmethod
    def boot() -> None:
        """Registering Plugin to database"""
        return manager.boot()

    @staticmethod
    def load(plugin_name: str) -> bool:
        """Registering Plugins and Execution"""
        return manager.load(plugin_name)

    @staticmethod
    def unload(plugin_name: str) -> bool:
        """Removing Plugins from Register"""
        return manager.unload(plugin_name)

    @staticmethod
    def broadcast(event_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Calling a Plugin without knowing the Plugin name"""
        return manager.broadcast(event_name, *args, **kwargs)

    @staticmethod
    def monitor() -> List[dict]:
        """
        REPL command: `show plugin`
        Connecting managers to monitoring.
        """
        # API mengambil 'State/Data' dari Manager
        pluginpath = manager.PLUGIN_DIR
        data = manager.REGISTRY

        # Menyuntikkan data tersebut ke fungsi Monitoring.
        # Monitoring akan memprosesnya dan mengembalikan laporan.
        laporan = monitoring.get_status_map(pluginpath, data)

        return laporan

    @staticmethod
    def inspect(plugin_name: str) -> List[dict]:
        """
        REPL command: `info <plugin_name>`
        Connecting managers to introspection.
        """
        # API meminta spesifik 1 plugin dari Manager
        target_plugin = manager.get_plugin(plugin_name)

        # Membedah metadata Plugin
        manifest = introspection.get_plugin_manifest(target_plugin)

        return manifest

    @staticmethod
    def execute(plugin_name: str, payload: Any = None) -> Any:
        """Single execution of the plugin."""
        plugin = manager.get_plugin(plugin_name)
        if not plugin or isinstance(plugin, manager.NullPlugin):
            smf.printd(f"Plugin '{plugin_name}' could not be executed.", level="ERROR")
            return

        action = getattr(plugin, "execute", None)
        if callable(action):
            return action(payload)

        smf.printd(f"Plugin {plugin_name}", "Has no function 'execute()'", level="ERROR")
        return


# Expose instance
plugin = StormAPI()
