import inspect
import smf

def extract_plugin(module: Any, plugin_name: str) -> tuple[Any, str]:
    """
    Validasi ketat arsitektur plugin.
    Jika plugin OOP cacat/gagal inisialisasi, kembalikan NullPlugin agar runtime tetap stabil.
    """
    # 1. Jika tidak ada atribut 'Plugin', 100% Fungsional
    if not hasattr(module, 'Plugin'):
        return module, "FUNCTIONAL"

    # ==========================================
    # ZONA OOP: Karena ada 'Plugin', diproses sebagai OOP
    # ==========================================
    plugin_class = getattr(module, 'Plugin')
    
    # [VALIDASI 1] Cek apakah benar Class?
    if not inspect.isclass(plugin_class):
        smf.printd(f"[{plugin_name}] The 'Plugin' attribute is not a Class", level="ERROR")
        return "BROKEN"

    # [VALIDASI 2] Cek entry point 'execute()' (opsional/warning)
    if not hasattr(plugin_class, 'execute') or not callable(getattr(plugin_class, 'execute')):
        smf.printd(f"OOP Plugin [{plugin_name}] has no entry point 'execute()'", level="WARN")
        return "BROKEN"

    # [STATE ALLOCATION]
    try:
        plugin_instance = plugin_class()
        return plugin_instance, "OOP"
    except Exception as e:
        smf.printd(f"Failed __init__ class Plugin on [{plugin_name}]", e, level="ERROR")
        return "BROKEN"
