from colorama import Fore, Style, init

init(autoreset=True)


# Dictionary Warna Global
class C:
    HEADER = Fore.MAGENTA + Style.BRIGHT
    MENU = Fore.CYAN
    INPUT = Fore.YELLOW + Style.BRIGHT
    SUCCESS = Fore.GREEN + Style.BRIGHT
    ERROR = Fore.RED + Style.BRIGHT
    RESET = Style.RESET_ALL
