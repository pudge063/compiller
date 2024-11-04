import sys
from core.lexer.la import Lexer
from core.parser.syntax_analyzer import Parser
import json


def start_compile(file: str = "test1.txt", debug: str = False):
    lexer = Lexer(file, debug)

    tokens, numbers, identificators, errors = lexer.tokenize()

    print(tokens)
    print(numbers)
    print(identificators)
    print(errors)

    """
    Парсинг программы (синтаксический анализ).
    """
    # parser = Parser()
    # try:
    #     parser.parse_program()
    # except SyntaxError as e:
    #     print(f"Syntax error: {e}")


if __name__ == "__main__":
    args = sys.argv
    arg_dict = {"-f": None, "debug": False}
    part_of_arg, tmp_arg = False, None
    for arg in args:
        if arg[0] == "-":
            part_of_arg = True
            tmp_arg = arg
        elif part_of_arg:
            arg_dict[tmp_arg] = arg
            part_of_arg = False
        else:
            arg_dict[arg] = True
    try:
        if part_of_arg:
            raise Exception(f"Excepted part of {tmp_arg} arg.")
        f = arg_dict["-f"] if arg_dict["-f"] else "test1.txt"
        d = True if arg_dict["debug"] else False
        start_compile(f, d)
        if d:
            print(arg_dict)
    except Exception as e:
        print(e)
