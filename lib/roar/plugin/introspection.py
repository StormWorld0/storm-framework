# -- https://github.com/StormWorld0/storm-framework
# -- SMF License

import inspect
from typing import List, Any, TypedDict, Optional, Type
from .safe import NullPlugin


class PluginMethodManifest(TypedDict):
    """Kontrak struktur data hasil introspeksi."""

    action: str
    parameters: str
    description: Optional[str]


def get_plugin_manifest(
    plugin_instance: Any,
    require_class: bool = False,
    expected_class_name: str = "Plugin"
) -> List[PluginMethodManifest]:
    """
    Mengekstrak manifest dari plugin.
    
    :param plugin_instance: Modul atau instance plugin (akan menembus proxy).
    :param require_class: Flag untuk memvalidasi apakah target HARUS berupa Class/Instance.
    :param expected_class_name: Nama class yang diharapkan jika require_class=True.
    """
    # 1. Early Exit: Proteksi null object
    if isinstance(plugin_instance, NullPlugin) or not plugin_instance:
        return []

    # 2. Proxy Unwrapping
    actual_target = getattr(plugin_instance, "_instance", plugin_instance)

    # 3. Validasi Structure (Class/Instance vs Module)
    target_to_scan = actual_target

    if require_class:
        # Pengecekan A: Apakah target ini adalah Class Uninstantiated atau Instance dari sebuah Class?
        is_class_obj = inspect.isclass(actual_target)
        is_instance_obj = hasattr(actual_target, "__class__") and not inspect.ismodule(actual_target)

        if not (is_class_obj or is_instance_obj):
            # Target bukan class maupun instance (misal: murni modul Python)
            return []

        # Pengecekan B: Validasi Nama Class
        class_name = actual_target.__name__ if is_class_obj else actual_target.__class__.__name__
        if class_name != expected_class_name:
            # Nama class tidak sesuai spesifikasi (bukan "Plugin")
            return []

        target_to_scan = actual_target

    # 4. Scanning (Mendukung 'isfunction' untuk Modul & 'ismethod/isfunction' untuk Class)
    manifest: List[PluginMethodManifest] = []

    for name, member in inspect.getmembers(target_to_scan):
        # Abaikan private/protected/dunder
        if name.startswith("_"):
            continue

        # Memastikan member adalah callable function atau method
        if not (inspect.isfunction(member) or inspect.ismethod(member)):
            continue

        # 5. Resolusi Signature
        try:
            sig = inspect.signature(member)
            
            # Jika memindai Uninstantiated Class, hapus parameter 'self' dari signature
            # agar output manifest tetap bersih bagi caller.
            params = list(sig.parameters.values())
            if params and params[0].name == "self":
                sig = sig.replace(parameters=params[1:])
                
            clean_params = str(sig)
        except (ValueError, TypeError):
            clean_params = "(...)"

        # 6. Ekstraksi Metadata
        manifest.append(
            {
                "action": name,
                "parameters": clean_params,
                "description": inspect.getdoc(member),
            }
        )

    return manifest
    
