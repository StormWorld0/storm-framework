from .log_style import LoggerManager as lm


class Logger:
    """Logger instances used by modules"""

    def prints(self, label, *args) -> None:
        lm.success(label, *args)

    def printi(self, label, *args) -> None:
        lm.info(label, *args)

    def printw(self, label, *args) -> None:
        lm.warning(label, *args)

    def printe(self, label, *args) -> None:
        lm.error(label, *args)
