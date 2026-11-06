import sys
import smf
from .base_exc import StormBaseException


def exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, StormBaseException):
        smf.printd(f"Type: {exc_type} | Value: {exc_value}", exc_traceback, level="WARN")
    else:
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
