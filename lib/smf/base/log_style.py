import smf
from apps.utility.colors import CC


class LoggerManager:
    """Managing style logger"""

    @staticmethod
    def success(self, label, *args) -> None:
        """Function for logger success"""
        if not label:
            return None

        if not args:
            smf.printf(f"[+] {CC.GREEN}{label}{CC.RESET}")
        else:
            smf.printf(f"[+] {CC.GREEN}{label}{CC.RESET}", *args)

    @staticmethod
    def info(self, label, *args) -> None:
        """Function for logger info"""
        if not label:
            return

        if not args:
            smf.printf(f"[*] {CC.CYAN}{label}{CC.RESET}")
        else:
            smf.printf(f"[*] {CC.CYAN}{label}{CC.RESET}", *args)

    @staticmethod
    def warning(self, label, *args) -> None:
        """Function for logger warning"""
        if not label:
            return

        if not args:
            smf.printf(f"[!] {CC.YELLOW}{label}{CC.RESET}")
        else:
            smf.printf(f"[!] {CC.YELLOW}{label}{CC.RESET}", *args)

    @staticmethod
    def error(self, label, *args) -> None:
        """Function for logger error"""
        if not label:
            return

        if not args:
            smf.printf(f"[-] {CC.RED}{label}{CC.RESET}")
        else:
            smf.printf(f"[-] {CC.RED}{label}{CC.RESET}", *args)
