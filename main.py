import sys
from core.lexer.la import Lexer
from core.parser.syntax_analyzer import Parser
import json


def compile(file: str = "test1.txt"):
    lexer = Lexer(file)

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
    arg_dict = {}
    if len(args) % 2:
        for i in range(1, len(args), 2):
            param_name = args[i]
            param_value = args[i + 1]
            arg_dict[param_name] = param_value

        if "-f" in arg_dict:
            compile(arg_dict["-f"])
        else:
            raise Exception("Undefined argument.")
    else:
        compile()

    print(arg_dict)
