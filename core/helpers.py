from colorama import init, Fore
from colorama import Back
from colorama import Style


class Helpers:
    init(autoreset=True)

    def print_red(self, string):
        print(Fore.RED + string)

    def print_magenta(self, string):
        print(Fore.LIGHTMAGENTA_EX + string)

    def print_cyan(self, string):
        print(Fore.CYAN + string)

    def print_yellow(self, string):
        print(Fore.LIGHTYELLOW_EX + string)

    def print_black(self, string):
        print(Fore.BLACK + string)
