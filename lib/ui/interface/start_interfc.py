import readline  # noqa: F401
import sys
import smf

try:
    from apps.utility.colors import *
    from lib.smf.core.console.engine import Context
except ImportError as e:
    smf.printf(f"Error import interface =>", e, file=sys.stderr)
    sys.exit(100)


def main():
    core = Context()

    while not core.exit:
        p_mod = core.current_module_name if core.current_module else "~"

        try:
            print(
                f"{CC.CYAN}┌─({CC.BLUE}storm{CC.YELLOW}<⚡>{CC.BLUE}framework{CC.CYAN}){CC.RESET}-{CC.RED}[{p_mod}]{CC.RESET}"
            )
            promp = f"{CC.CYAN}└─{CC.BLUE}➤ {CC.RESET}"
            user_input = input(promp).strip().split()
        except KeyboardInterrupt:
            smf.printf(
                f"\n[*]{CC.YELLOW} KeyboardInterrupt detected. Type 'exit' to quit.{CC.RESET}"
            )
            continue
        except EOFError:
            break

        if not user_input:
            continue

        # parsing input
        cmd = user_input[0].lower()
        args = user_input[1:]

        # Send input data to the console
        core.dispatch(cmd, args)


if __name__ == "__main__":
    main()
