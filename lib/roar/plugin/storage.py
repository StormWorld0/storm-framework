# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import json
import smf

from rootmap import ROOT
from pathlib import Path
from typing import Set, Dict, Any


class PluginStateStore:
    def __init__(self) -> None:
        self.cachepath: Path = (
            Path(ROOT) / "lib" / "smf" / "core" / "sf" / "cache" / "plugin-session"
        )
        self.filepath: Path = self.cachepath / "plugin_cache.json"
        self.cachepath.mkdir(parents=True, exist_ok=True)

    def load_active_plugins(self) -> Set[str]:
        """Memuat daftar plugin aktif dari disk."""
        if not self.filepath.exists():
            return set()

        try:
            data_text = self.filepath.read_text(encoding="utf-8")
            data: Dict[str, Any] = json.loads(data_text)
            return set(data.get("active_plugins", []))
        except json.JSONDecodeError as e:
            smf.printd("State Storage JSON Corrupted", e, level="ERROR")
            return set()
        except Exception as e:
            smf.printd("State Storage Error", e, level="CRITICAL")
            return set()

    def save_active_plugins(self, active_plugins_set: Set[str]) -> None:
        """Menyimpan state plugin ke disk secara Atomic Replace."""
        temp_filepath = self.filepath.with_suffix(".tmp")
        try:
            payload = {"active_plugins": list(active_plugins_set)}
            temp_filepath.write_text(json.dumps(payload, indent=4), encoding="utf-8")
            temp_filepath.replace(self.filepath)
        except Exception as e:
            smf.printd("State Storage Save Error", e, level="ERROR")
        finally:
            if temp_filepath.exists():
                temp_filepath.unlink(missing_ok=True)

    def add_plugin(self, plugin_name: str) -> None:
        """
        Menambahkan plugin ke daftar aktif jika belum ada.
        Jika sudah ada, Set secara otomatis menjamin kekhasan (no duplicate).
        """
        current_plugins = self.load_active_plugins()
        if plugin_name not in current_plugins:
            current_plugins.add(plugin_name)
            self.save_active_plugins(current_plugins)

    def remove_plugin(self, plugin_name: str) -> None:
        """
        Menghapus plugin spesifik dari daftar aktif.
        Item lain dalam file JSON tetap dipertahankan.
        """
        current_plugins = self.load_active_plugins()
        if plugin_name in current_plugins:
            current_plugins.remove(plugin_name)
            self.save_active_plugins(current_plugins)
