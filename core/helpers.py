from colorama import init, Fore
from colorama import Back
from colorama import Style


class Helpers:
    init(autoreset=True)

    def print_red(self, string):
        print(Fore.RED + string)
        Style.RESET_ALL

    def print_magenta(self, string):
        print(Fore.LIGHTMAGENTA_EX + string)
        Style.RESET_ALL

    def print_cyan(self, string):
        print(Fore.CYAN + string)
        Style.RESET_ALL

    def print_yellow(self, string):
        print(Fore.LIGHTYELLOW_EX + string)
        Style.RESET_ALL

    def print_black(self, string):
        print(Fore.BLACK + string)
        Style.RESET_ALL
