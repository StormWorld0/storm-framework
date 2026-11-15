import smf
from .log_style import LoggerManager as lm


class Logger:
    """Logger instances used by modules"""

    def prints(self, *args) -> None:
        if not args:
            smf.printf()
            return

        label = args[:1]
        lm.success(label, *args)

    def printi(self, *args) -> None:
        if not args:
            smf.printf()
            return

        label = args[:1]
        lm.info(label, *args)

    def printw(self, *args) -> None:
        if not args:
            smf.printf()
            return

        label = args[:1]
        lm.warning(label, *args)

    def printe(self, *args) -> None:
        if not args:
            smf.printf()
            return

        label = args[:1]
        lm.error(label, *args)
