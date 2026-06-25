# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
from pathlib import Path
from typing import List, Dict, Any, TypedDict, Literal
from .safe import NullPlugin

# 1. Strict Typing untuk Status
PluginStatus = Literal["ACTIVE", "INACTIVE", "CRASHED", "ORPHANED"]


class PluginStatusReport(TypedDict):
    """Kontrak struktur data metrik plugin."""

    name: str
    status: PluginStatus
    is_package: bool


# ==========================================
# ALAT BEDAH MONITORING (Pure Functions)
# ==========================================


def list_available_on_disk(plugin_dir: Path) -> Dict[str, bool]:
    """
    Shallow Scan: Memindai anak langsung dari folder plugin.
    [Dependency Injection]: Path disuntikkan secara eksplisit.
    """
    available: Dict[str, bool] = {}

    # Validasi input (Fail-safe)
    if not plugin_dir or not plugin_dir.exists():
        return available

    # Eksekusi O(1) depth scan menggunakan iterdir()
    for child in plugin_dir.iterdir():

        # Filter 1: Abaikan dunder dan file hidden
        if child.name.startswith(".") or child.name.startswith("__"):
            continue

        # Arsitektur 1: Package Based
        if child.is_dir():
            init_file = child / "__init__.py"
            if init_file.exists():
                available[child.name] = True

        # Arsitektur 2: Single File
        elif child.is_file() and child.suffix == ".py":
            plugin_name = child.stem
            if plugin_name not in available:
                available[plugin_name] = False

    return available


def get_status_map(
    plugin_dir: Path, registry: Dict[str, Any]
) -> List[PluginStatusReport]:
    """
    Melakukan rekonsiliasi state antara Memory (RAM) vs Physical Disk.
    [Dependency Injection]: Manager harus memberikan Path dan Registry miliknya.
    """
    disk_plugins = list_available_on_disk(plugin_dir)
    status_report: List[PluginStatusReport] = []

    # Fase 1: Pemetaan dari sudut pandang Physical Disk
    for p_name, is_package in disk_plugins.items():
        status: PluginStatus = "INACTIVE"

        if p_name in registry:
            # Cek apakah object-nya NullPlugin (Crashing at Load)
            if isinstance(registry[p_name], NullPlugin):
                status = "CRASHED"
            else:
                status = "ACTIVE"

        status_report.append({"name": p_name, "status": status, "is_package": is_package})

    # Fase 2: Deteksi "Orphaned / Zombie Plugins"
    for p_name, instance in registry.items():
        if p_name not in disk_plugins:
            status: PluginStatus = "ORPHANED"

            # Walaupun orphaned, bisa jadi dia memang sudah crash
            if isinstance(instance, NullPlugin):
                status = "CRASHED"

            status_report.append(
                {
                    "name": p_name,
                    "status": status,
                    "is_package": False,  # Unknown karena file fisik hilang
                }
            )

    return status_report
