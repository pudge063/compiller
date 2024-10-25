from core.la import Lexer

lexer = Lexer("test.txt")

tokens, numbers, identificators = lexer.tokenize()

print(tokens)
print(numbers)
print(identificators)
