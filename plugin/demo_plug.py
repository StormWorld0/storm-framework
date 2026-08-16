import smf
import traceback

__autorun__ = True


class Plugin:
    def __init__(self):
        self.status = "error"

    def _trigger_crash(self):
        smf.printd(
            "DemoPlugin",
            "Executing dangerous operation...",
            level="WARN"
        )

        # Deliberately crash
        return self.status + 100

    def execute(self, data):
        try:
            return self._trigger_crash()
        except Exception as e:
            smf.printd("", e, level="ERROR")
            raise
