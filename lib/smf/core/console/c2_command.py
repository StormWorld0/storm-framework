import readline  # noqa: F401

from apps.utility.colors import *
from .central import dispatch


def command(callback):
    while True:
        try:
            print(
                f"{CC.CYAN}┌─({CC.BLUE}storm{CC.YELLOW}<⚡>{CC.BLUE}c2{CC.CYAN}){CC.RESET}"
            )
            promp = f"{CC.CYAN}└─{CC.BLUE}➤ {CC.RESET}"
            user_input = input(promp).strip().split()
        except KeyboardInterrupt: return
        except EOFError: break

        # validation
        if not user_input:
            continue

        # exit loop
        if user_input.lower() == "exit":
            break

        # send input
        dispatch(cmd, callback)


if __name__ == "__main__":
    command(callback)
