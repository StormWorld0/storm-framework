# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import smf

from typing import Any, List, Dict, Callable, Optional

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
        # API retrieves 'State/Data' from Manager
        pluginpath = manager.PLUGIN_DIR
        data = manager.REGISTRY

        # Inject the data into the Monitoring function.
        # Monitoring will process it and return a report.
        laporan = monitoring.get_status_map(pluginpath, data)
        # Returning data report
        return laporan

    @staticmethod
    def inspect(plugin_name: str) -> List[dict]:
        """
        REPL command: `info <plugin_name>`
        Connecting managers to introspection.
        """
        # API requests specific 1 plugin from Manager
        target_plugin = manager.get_plugin(plugin_name)
        # Dissecting Plugin metadata
        manifest = introspection.get_plugin_manifest(target_plugin)
        return manifest

    @staticmethod
    def get_plugin(plugin_name: str) -> Optional[Callable[[Any], Any]]:
        """Retrieve a callable handler for the specified plugin."""

        # Calling the plugin from the register, to find out if the plugin exists
        plugin = manager.get_plugin(plugin_name)
        if not plugin or isinstance(plugin, manager.NullPlugin):
            smf.printd(
                f"Plugin '{plugin_name}' could not be found or initialized.",
                level="ERROR",
            )
            return None

        # Inspection to find entry points
        action = getattr(plugin, "execute", None)
        if not callable(action):
            smf.printd(
                f"Plugin '{plugin_name}' has no callable 'execute()' method", level="WARN"
            )
            return None

        # Return closure
        def runner(data: Any = None) -> Any:
            try:
                return action(data)
            except Exception as e:
                smf.printd(f"Error executing plugin: {plugin_name}", e, level="ERROR")
                return None

        return runner


# Expose instance
plugin = StormAPI()
