import sys
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
        print(f"[*] Error Exception Wrapper Data => {e}")
        sys.exit(1)


if __name__ == "__main__":
    data()
