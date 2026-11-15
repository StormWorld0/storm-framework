import smf
from apps.utility.colors import CC


class Logger:
    """Logger instances used by modules"""

    def prints(self, *args) -> None:
        if not args:
            smf.printf()
            return

        label = args[:1]
        arg = args[1:]

        if not arg:
            smf.printf(f"[+] {CC.GREEN}{*label}{CC.RESET}")
        else:
            smf.printf(f"[+] {CC.GREEN}{*label}{CC.RESET}", *arg)

    def printi(self, *args) -> None:
        if not args:
            smf.printf()
            return

        label = args[:1]
        arg = args[1:]

        if not arg:
            smf.printf(f"[*] {CC.CYAN}{*label}{CC.RESET}")
        else:
            smf.printf(f"[*] {CC.CYAN}{*label}{CC.RESET}", *arg)

    def printw(self, *args) -> None:
        if not args:
            smf.printf()
            return

        label = args[:1]
        arg = args[1:]

        if not arg:
            smf.printf(f"[!] {CC.YELLOW}{*label}{CC.RESET}")
        else:
            smf.printf(f"[!] {CC.YELLOW}{*label}{CC.RESET}", *arg)

    def printe(self, *args) -> None:
        if not args:
            smf.printf()
            return

        label = args[:1]
        arg = args[1:]

        if not args:
            smf.printf(f"[-] {CC.RED}{*label}{CC.RESET}")
        else:
            smf.printf(f"[-] {CC.RED}{*label}{CC.RESET}", *arg)
