# -- https://github.com/StormWorld0/storm-framework
# -- SMF License

import sys
import inspect
import importlib.util
from pathlib import Path
from typing import Tuple, Any, Dict, get_type_hints


class Introspection:
    """Retrieving Plugin metadata"""

    def __init__(self, plugin_index: Dict[str, Path] | None = None) -> None:
        self.func = "metadata"
        self.clas = ("Metadata", "PluginMetadata")
        self.atrb = ("metadata", "meta")
        self.index: Dict[str, Path] = plugin_index if plugin_index is not None else {}

    def _dict_format(self, data: Dict[Any, Any]) -> Dict[str, str]:
        return {
            "name": str(data.get("name", "")),
            "description": str(data.get("description", "")),
            "action": str(data.get("action", "")),
            "author": str(data.get("author", "")),
            "version": str(data.get("version", "")),
        }

    def _dict_format_class(self, meta_obj: Any) -> Dict[str, str]:
        return {
            "name": str(getattr(meta_obj, "name", "")),
            "description": str(getattr(meta_obj, "description", "")),
            "action": str(getattr(meta_obj, "action", "")),
            "author": str(getattr(meta_obj, "author", "")),
            "version": str(getattr(meta_obj, "version", "")),
        }

    def _is_valid_meta(self, meta: Dict[str, str]) -> bool:
        return bool(meta["name"].strip() and meta["action"].strip())

    def _index_plugin(self) -> Dict[str, Path] | None:
        try:
            from . import manager
            lp = getattr(manager, "LP", None)
            pm = getattr(lp, "pm", None) if lp is not None else None
            idx = getattr(pm, "_plugin_index", None) if pm is not None else None

            if idx and isinstance(idx, dict):
                self.index = idx
                return self.index
        except Exception:
            pass
        return None
            
    def _plugin_path(self, plugin: str) -> Path | None:
        if not self._index_plugin():
            return None
        
        pgpath = self.index.get(plugin)
        if pgpath:
            return Path(pgpath)
        return None

    def _can_call_meta_func(self, obj: Any) -> Tuple[bool, Any]:
        # Check whether obj itself is a function with the hint dict[str, str],
        # or has a method/attr self.func
        candidates = []
        if inspect.isfunction(obj) or (callable(obj) and not inspect.isclass(obj) and not inspect.ismodule(obj)):
            candidates.append(obj)

        attr_fn = getattr(obj, self.func, None)
        if callable(attr_fn) and not inspect.isclass(attr_fn):
            candidates.append(attr_fn)

        req_kinds = (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        )

        for fn in candidates:
            try:
                sig = inspect.signature(fn)
                hints = get_type_hints(fn)
            except Exception:
                continue

            zero_req = all(
                not (p.default is inspect.Parameter.empty and p.kind in req_kinds)
                for p in sig.parameters.values()
            )
            if zero_req and hints.get("return") == dict[str, str]:
                return True, fn

        return False, None

    def _find_meta_class(self, obj: Any) -> Any:
        if inspect.isclass(obj) and obj.__name__ in self.clas:
            return obj
        for cls_name in self.clas:
            found = getattr(obj, cls_name, None)
            if found is not None:
                return found
        return None

    def _parse_plugin_metadata(self, target: Any) -> Dict[str, str] | None:
        if target is None:
            return None

        # Check the `metadata` / `meta` attribute in dict form (in module, class, or function)
        for attr in self.atrb:
            raw_dict = getattr(target, attr, None)
            if isinstance(raw_dict, dict):
                parsed = self._dict_format(raw_dict)
                if self._is_valid_meta(parsed):
                    return parsed

        # Check `Metadata` / `PluginMetadata`
        meta_cls = self._find_meta_class(target)
        if meta_cls is not None:
            parsed = self._dict_format_class(meta_cls)
            if self._is_valid_meta(parsed):
                return parsed

        # Check function with type hint -> dict[str, str] and no required arguments
        can_call, runner = self._can_call_meta_func(target)
        if can_call and callable(runner):
            try:
                result = runner()
            except Exception:
                return None

            if isinstance(result, dict):
                parsed = self._dict_format(result)
                if self._is_valid_meta(parsed):
                    return parsed

        return None

    def metadata_plugin(self, plugin: str | None = None) -> Dict[str, str] | None:
        if not plugin:
            return None

        # Get `plugin` in sys.modules if it exists
        if mod := sys.modules.get(plugin):
            parsed = self._parse_plugin_metadata(mod)
            if parsed:
                return parsed

        # Find path from index (`Dict[str, Path]`)
        pgpath = self._plugin_path(plugin)
        if pgpath is None or not pgpath.exists():
            return None

        spec = importlib.util.spec_from_file_location(plugin, str(pgpath))
        if spec is None or spec.loader is None:
            return None

        module = importlib.util.module_from_spec(spec)
        sys.modules[plugin] = module
        spec.loader.exec_module(module)

        return self._parse_plugin_metadata(module)
