import sys
from core.lexer.la import Lexer
from core.parser.syntax import Parser
import json
from core.helpers import Helpers


def start_compile(file: str = "test1.txt", debug: str = False):
    lexer = Lexer(file, debug)
    helpers = Helpers()

    helpers.print_cyan("Start lexer analyzer.\n")

    tokens, numbers, identificators, errors = lexer.tokenize()

    if errors.count == 0:
        helpers.print_cyan("Tokens:")
        print(tokens, "\n")

        helpers.print_cyan("Numbers:")
        print(numbers, "\n")

        helpers.print_cyan("Identificators:")
        print(identificators, "\n")

        helpers.print_magenta("Lexer OK!\n")

        start_parser(debug)

    else:
        helpers.print_red(f"Error in lexer: {errors[0]}\n")


def start_parser(debug):
    helpers = Helpers()

    parser = Parser(debug)

    try:
        parser.parse_program()
    except Exception as e:
        helpers.print_red(f"Syntax error: {e}\n")


if __name__ == "__main__":
    args = sys.argv
    arg_dict = {"-f": None, "debug": False}
    part_of_arg, tmp_arg = False, None
    try:
        for arg in args:
            if arg[0] == "-":
                part_of_arg = True
                if not arg in arg_dict:
                    raise Exception(f"Undefined arg {arg}.")
                tmp_arg = arg
            elif part_of_arg:
                arg_dict[tmp_arg] = arg
                part_of_arg = False
            else:
                arg_dict[arg] = True

        if part_of_arg:
            raise Exception(f"Excepted part of {tmp_arg} arg.")

        f = arg_dict["-f"] if arg_dict["-f"] else "test1.txt"
        d = True if arg_dict["debug"] else False

        start_compile(f, d)

        if d:
            print(arg_dict)

    except Exception as e:
        print(e)

    finally:
        print("Compiler end.")
