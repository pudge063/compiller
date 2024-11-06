from colorama import init, Fore
from colorama import Back
from colorama import Style


class Helpers:
    def print_red(self, string):
        init(autoreset=True)
        print(Fore.RED + string)
        Style.RESET_ALL

    def print_magenta(self, string):
        init(autoreset=True)
        print(Fore.LIGHTMAGENTA_EX + string)
        Style.RESET_ALL
        
    def print_cyan(self, string):
        init(autoreset=True)
        print(Fore.CYAN + string)
        Style.RESET_ALL
