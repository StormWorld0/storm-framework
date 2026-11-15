import smf
from apps.utility.colors import CC


class Logger:
    """Logger instances used by modules"""

    def prints(self, label: str = "", *args) -> None:
        if not label:
            smf.printf()
            return

        if not args:
            smf.printf(f"[✓] {CC.GREEN}{label}{CC.RESET}")
        else:
            smf.printf(f"[✓] {CC.GREEN}{label}{CC.RESET}", *args)

    def printi(self, label: str = "", *args) -> None:
        if not label:
            smf.printf()
            return

        if not args:
            smf.printf(f"[*] {CC.CYAN}{label}{CC.RESET}")
        else:
            smf.printf(f"[*] {CC.CYAN}{label}{CC.RESET}", *args)

    def printw(self, label: str = "", *args) -> None:
        if not label:
            smf.printf()
            return

        if not args:
            smf.printf(f"[!] {CC.YELLOW}{label}{CC.RESET}")
        else:
            smf.printf(f"[!] {CC.YELLOW}{label}{CC.RESET}", *args)

    def printe(self, label: str = "", *args) -> None:
        if not label:
            smf.printf()
            return

        if not args:
            smf.printf(f"[~] {CC.RED}{label}{CC.RESET}")
        else:
            smf.printf(f"[~] {CC.RED}{label}{CC.RESET}", *args)
