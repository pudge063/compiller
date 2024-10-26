from core.la import Lexer
import json

lexer = Lexer("test.txt")

tokens, numbers, identificators, errors = lexer.tokenize()

print(tokens)
print(numbers)
print(identificators)
print(errors)

with open("lexer_out.txt", "w") as fw:
    json.dump(tokens, fw)
    json.dump(numbers, fw)
    json.dump(identificators, fw)
