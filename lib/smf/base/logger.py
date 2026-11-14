import smf
from .logger_manager import LoggerManager as lm


class Logger:
    """Logger instances used by modules"""

    def print_success(self, label, *args) -> None:
        lm.success(label, *args)

    def print_info(self, label, *args) -> None:
        lm.info(label, *args)

    def print_warn(self, label, *args) -> None:
        lm.warning(label, *args)

    def print_error(self, label, *args) -> None:
        lm.error(label, *args)
        
