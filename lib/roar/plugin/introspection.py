# -- https://github.com/StormWorld0/storm-framework
# -- SMF License

import sys
import inspect
import importlib
from typing import List, Any, Path, Dict, Optional, get_type_hints


class Introspection:
    """Retrieving Plugin metadata"""

    def __init__(self):
        self.func = "metadata"
        self.clas = ("Metadata", "PluginMetadata")
        self.atrb = ("metadata", "meta")
        self.index = Dict[str, Path] = {}

    def _dict_format(self, data: Dict[Any, Any]) -> Dict[str, str] | None:
        meta = {
            "name": str(data.get("name", "")),
            "description": str(data.get("description", "")),
            "action": str(data.get("action", "")),
            "author": str(data.get("author", "")),
            "version": str(data.get("version", "")),
        }
        return meta

    def _dict_format_class(self, meta_obj: Any) -> Dict[str, str] | None:
        meta = {
            "name": str(getattr(meta_obj, "name", "")),
            "description": str(getattr(meta_obj, "description", "")),
            "action": str(getattr(meta_obj, "action", "")),
            "author": str(getattr(meta_obj, "author", "")),
            "version": str(getattr(meta_obj, "version", "")),
        }
        return meta

    def _plugin_path(self, plugin: str) -> str | None:
        from .manager import PluginManager
        self.index = PluginManager()._plugin_index
        if not self.index:
            return None

        pgpath = self.index.get(plugin, "")
        if pgpath != "":
            return pgpath
        return None

    def _getfuncname(self, plugin: str) -> bool:
        fn = getattr(plugin, self.func)
        try:
            sig = inspect.signature(fn)
            hints = get_type_hints(fn)
        except Exception:
            return False

        required_kinds = (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        )
        zero_req_args = all(
            not (p.default is inspect.Parameter.empty and p.kind in required_kinds)
            for p in sig.parameters.values()
        )
        return zero_req_args and hints.get("return") == dict[str, str]

    def _parse_plugin_metadata(self, plugin: str) -> Dict[str, str] | None:
        clas = getattr(plugin, self.clas)
        is_cls = inspect.isclass(clas)
        is_fn = callable(plugin) and not is_cls

        if not is_cls and not is_fn:
            return None

        # Cek atribut `metadata` berbentuk dict
        for attr in self.atrb:
            raw_dict = getattr(plugin, attr, None)
            if isinstance(raw_dict, dict):
                parsed = self._dict_format(raw_dict)
                if parsed:
                    return parsed

        # Cek `class Metadata`
        meta_cls = getattr(plugin, self.clas, None)
        if meta_cls is not None:
            parsed = self._dict_format_class(meta_cls)
            if parsed:
                return parsed

        # Jika fungsi dengan type hint -> dict[str, str]
        if is_fn and self._getfuncname(plugin):
            runner = getattr(plugin, self.func)
            try:
                result = runner()
            except Exception:
                return None

            if isinstance(result, dict):
                parsed = self._dict_format(result)
                if parsed:
                    return parsed
        return None

    def metadata_plugin(self, plugin: Any = None) -> Dict[str, str] | None:
        if not plugin:
            return None

        if pgspec := sys.modules.get(plugin):
            return self._parse_plugin_metadata(pgspec)

        pgpath = self._plugin_path(plugin)
        spec = importlib.util.spec_from_file_location(plugin, pgpath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        return self._parse_plugin_metadata(module)
        
        
