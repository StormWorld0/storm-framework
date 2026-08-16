# File: plugin/demo_plug.py
import smf

__autorun__ = True


class Plugin:
    def __init__(self):
        # Dipanggil otomatis saat modul di-load oleh manager
        smf.printd("DemoPlugin", "Plugin instance allocated in memory.", level="DEBUG")
        self.status = "Active"

    def execute(self, data):
        """Fungsi normal yang berjalan dengan baik."""
        return f"Data '{data}' has been processed by DemoPlugin."

    def trigger_crash(self):
        """Fungsi cacat untuk menguji ketahanan framework (Fault Tolerance)."""
        smf.printd("DemoPlugin", "Executing dangerous operation...", level="WARN")
        # Ini akan memicu ZeroDivisionError
        result = 100 / 0
        return result
