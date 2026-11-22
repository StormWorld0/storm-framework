import smf
from apps.utility.colors import CC


class Logger:
    """Logger instances used by modules"""

    def prints(self, *args) -> None:
        if not args:
            smf.printf()
            return

        label = args[0]
        desc = " ".join(str(v) for v in args[1:])

        if not desc:
            smf.printf(f"[✓] {CC.GREEN}{label}{CC.RESET}")
        else:
            smf.printf(f"[✓] {CC.GREEN}{label}{CC.RESET}", desc)

    def printi(self, *args) -> None:
        if not args:
            smf.printf()
            return

        label = args[0]
        desc = " ".join(str(v) for v in args[1:])

        if not desc:
            smf.printf(f"[*] {CC.CYAN}{label}{CC.RESET}")
        else:
            smf.printf(f"[*] {CC.CYAN}{label}{CC.RESET}", desc)

    def printw(self, *args) -> None:
        if not args:
            smf.printf()
            return

        label = args[0]
        desc = " ".join(str(v) for v in args[1:])

        if not desc:
            smf.printf(f"[!] {CC.YELLOW}{label}{CC.RESET}")
        else:
            smf.printf(f"[!] {CC.YELLOW}{label}{CC.RESET}", desc)

    def printe(self, *args) -> None:
        if not args:
            smf.printf()
            return

        label = args[0]
        desc = " ".join(str(v) for v in args[1:])

        if not desc:
            smf.printf(f"[~] {CC.RED}{label}{CC.RESET}")
        else:
            smf.printf(f"[~] {CC.RED}{label}{CC.RESET}", desc)

    def printf(self, *args) -> None:
        if not args:
            smf.printf()
            return

        label = args[0]
        desc = " ".join(str(v) for v in args[1:])

        if not desc:
            smf.printf(f"{CC.WHITE}{label}{CC.RESET}")
        else:
            smf.printf(f"{CC.WHITE}{label}{CC.RESET}", desc)

    def printd(self, *args, **kwargs) -> None:
        if not args:
            return
        if len(kwargs) != 1:
            return
            
        level = kwargs.get("level")
        if level not in ("DEBUG", "WARN", "INFO", "ERROR"):
            return
            
        smf.printd(*args, level=level)
