import smf
from apps.utility.colors import CC


class LoggerManager:
    """Managing style logger"""

    def success(self, label, *args) -> None | bool:
        """Function for logger success"""
        if not label:
            return None

        if not args:
            smf.printf(f"[+] {CC.GREEN}{label}{CC.RESET}")
            return True
        else:
            smf.printf(f"[+] {CC.GREEN}{label}{CC.RESET}", args)
            return True
        return False

    def info(self, label, *args) -> None | bool:
        """Function for logger info"""
        if not label:
            return None

        if not args:
            smf.printf(f"[*] {CC.CYAN}{label}{CC.RESET}")
            return True
        else:
            smf.printf(f"[*] {CC.CYAN}{label}{CC.RESET}", args)
            return True
        return False

    def warning(self, label, *args) -> None | bool:
        """Function for logger warning"""
        if not label:
            return None

        if not args:
            smf.printf(f"[!] {CC.YELLOW}{label}{CC.RESET}")
            return True
        else:
            smf.printf(f"[!] {CC.YELLOW}{label}{CC.RESET}", args)
            return True
        return False

    def error(self, label, *args) -> None | bool:
        """Function for logger error"""
        if not label:
            return None

        if not args:
            smf.printf(f"[-] {CC.RED}{label}{CC.RESET}")
            return True
        else:
            smf.printf(f"[-] {CC.RED}{label}{CC.RESET}", args)
            return True
        return False
