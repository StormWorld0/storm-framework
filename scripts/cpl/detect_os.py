import sys

# Just to find out the name of the OS that is running
# to determine specific extensions (PyO3).
def osext():
    if sys.platform == "win32":
        return "pyd"
    else:
        return "so"
