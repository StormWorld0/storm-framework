from .log_style import LoggerManager as lm


class Logger:
    """Logger instances used by modules"""

    def prints(self, label, *args) -> None:
        if not label:
            smf.printf()
            return

        lm.success(label, *args)

    def printi(self, label, *args) -> None:
        if not label:
            smf.printf()
            return

        lm.info(label, *args)

    def printw(self, label, *args) -> None:
        if not label:
            smf.printf()
            return

        lm.warning(label, *args)

    def printe(self, label, *args) -> None:
        if not label:
            smf.printf()
            return

        lm.error(label, *args)
