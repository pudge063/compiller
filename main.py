from core.la import Lexer
import json

lexer = Lexer("test.txt")

tokens, numbers, identificators = lexer.tokenize()

print(tokens)
print(numbers)
print(identificators)

with open("lexer_out.txt", "w") as fw:
    json.dump(tokens, fw)
    json.dump(numbers, fw)
    json.dump(identificators, fw)
