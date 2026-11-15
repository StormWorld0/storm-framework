import smf
from apps.utility.colors import CC


class LoggerManager:
    """Managing style logger"""

    @staticmethod
    def success(label, *args) -> None:
        """Function for logger success"""
        if not args:
            smf.printf(f"[+] {CC.GREEN}{label}{CC.RESET}")
        else:
            smf.printf(f"[+] {CC.GREEN}{label}{CC.RESET}", *args)

    @staticmethod
    def info(label, *args) -> None:
        """Function for logger info"""
        if not args:
            smf.printf(f"[*] {CC.CYAN}{label}{CC.RESET}")
        else:
            smf.printf(f"[*] {CC.CYAN}{label}{CC.RESET}", *args)

    @staticmethod
    def warning(label, *args) -> None:
        """Function for logger warning"""
        if not args:
            smf.printf(f"[!] {CC.YELLOW}{label}{CC.RESET}")
        else:
            smf.printf(f"[!] {CC.YELLOW}{label}{CC.RESET}", *args)

    @staticmethod
    def error(label, *args) -> None:
        """Function for logger error"""
        if not args:
            smf.printf(f"[-] {CC.RED}{label}{CC.RESET}")
        else:
            smf.printf(f"[-] {CC.RED}{label}{CC.RESET}", *args)
