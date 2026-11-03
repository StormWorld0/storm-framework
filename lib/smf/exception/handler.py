import sys
import smf
from .base_exc import BaseException

def exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, BaseException):
        smf.printd(f"Type: {exc_type} | Value: {exc_value}", exc_traceback, level="ERROR")
    else:
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

sys.excepthook = exception_handler
