import sys
import smf

from .gen_wrapper import generate

def data():
    wrapper = None
    try:
        if "--data" in sys.argv:
            index = sys.argv.index("--data")

            if index + 1 < len(sys.argv):
                wrapper = sys.argv[index + 1]

        generate(wrapper)
    except Exception as e:
        smf.printf("[*] Error Exception Wrapper Data =>", e)
        sys.exit(100)
