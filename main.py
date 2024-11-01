from core.lexer.la import Lexer
from core.parser.syntax_analyzer import Parser
import json

lexer = Lexer("test3.txt")

tokens, numbers, identificators, errors = lexer.tokenize()

print(tokens)
print(numbers)
print(identificators)
print(errors)

"""
Парсинг программы (синтаксический анализ).
"""
parser = Parser()
try:
    parser.parse_program()
except SyntaxError as e:
    print(f"Syntax error: {e}")
