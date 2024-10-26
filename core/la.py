class Lexer:
    def __init__(self, file):
        from core.reader import Reader
        from core.helpers import Helpers
        from core.tables import vocabilary, numbers, separators, keywords

        reader = Reader(file)
        get_char, close_file = reader.char_reader()
        self.get_char = get_char
        self.close_file = close_file

        helpers = Helpers()
        self.in_table = helpers.in_number_table
        self.fexp_to_float = helpers.fexp_to_float

        self.vocabilary = vocabilary
        self.numbers = numbers
        self.separators = separators
        self.keywords = keywords

    """
    Описание состояний:
    H - начальное состояние
    I - идентификатор
    N - число
    C - комментарий
    S - разделитель
    K - ключевое слово
    V - выход
    ER - ошибка

    H -> I | N | S | H
    I -> I | K | ER
    N -> N2
    S -> C | S | ER
    C -> V | ER
    N2 -> N2 | ER | N8 | N10 | NF | NEXP | N8X | N10X | N16 | N16X | N2X | V
    N8 -> N8 | ER | N10 | NF | NEXP | N10X | N16 | N16X | N8X | V
    N10 -> N10 | ER | NF | NEXP | N10X | N16 | N16X | N10X | V
    N16 -> N16 | ER | N16X | V
    N2X -> N16 | N16X | ER | V
    N8X -> ER | V
    N10X -> ER | N16 | N16X | V
    N16X -> ER
    NEXP -> NEXP | N16 | N16X | ER
    NF -> NF | NEXPX | ER | V
    NEXPX -> NEXPX | ER | V
    """

    def gc(self):
        return self.get_char()

    def tokenize(self):
        stack = ""
        q = "H"
        tokens = []
        identificators = []
        numbers = []

        while True:
            _ = self.gc()
            print(f"stack = {stack}, q = {q}, char = {_}")

            if q == "ER":
                print("Error.")
                return [], [], []

            if q == "H":
                if _ == " " or _ == "\n":
                    continue
                stack += _
                if _ in self.vocabilary or _ in self.keywords:
                    q = "I"
                    continue
                elif _ in self.numbers:
                    if _ in self.numbers[:2]:
                        q = "N2"
                    elif _ in self.numbers[:9]:
                        q = "N8"
                    elif _ in self.numbers[:10]:
                        q = "N10"
                    continue

                elif _ == ".":
                    q = "NF"
                    continue

                elif _ in ["!", "=", ">", "<", "|"]:
                    q = "SS"
                    continue
                elif _ in self.separators:
                    q = "S"
                    continue
                else:
                    q = "ER"

            elif q == "I":
                if _ == " " or _ == "\n":
                    q = "H"
                    if stack in self.keywords:
                        tokens.append((1, self.keywords[stack]))
                        stack = ""
                    else:
                        if not stack in identificators:
                            identificators.append(stack)
                        tokens.append((3, identificators.index(stack)))
                        stack = ""
                elif _ in self.vocabilary or _ in self.numbers:
                    stack += _
                    continue

                elif _ == "&":
                    stack += _
                    tokens.append((2, self.separators[stack]))
                    stack = ""
                    q = "H"
                    continue

                elif _ in self.separators:
                    q = "S"
                    if stack in self.keywords:
                        tokens.append((1, self.keywords[stack]))
                        stack = ""
                    else:
                        if not stack in identificators:
                            identificators.append(stack)
                        tokens.append((3, identificators.index(stack)))
                        stack = ""
                    stack = _
                    continue

                else:
                    q = "ER"
                    continue

            elif q == "S":
                if _ == " " or _ == "\n":
                    q = "H"
                    if stack in self.separators:
                        tokens.append((2, self.separators[stack]))
                        stack = ""
                    else:
                        q = "ER"

                elif _ in ["!", "=", "<", ">", "&"]:
                    q = "SS"
                    stack += _

                elif _ == "*":
                    if stack == "(":
                        q = "C"
                    continue

            elif q == "SS":
                if _ in ["=", "&", "|"]:
                    stack += _
                    if stack in self.separators:
                        tokens.append((2, self.separators[stack]))
                        stack = ""
                        q = "H"
                        continue
                    else:
                        q = "ER"
                        continue
                elif _ == " " or _ == "\n":
                    if stack in self.separators:
                        tokens.append((2, self.separators[stack]))
                        stack = ""
                        q = "H"
                    else:
                        q = "ER"
                        stack = ""
                    continue

            elif q == "C":
                if _ == ")" and stack[-1] == "*":
                    q = "H"
                    stack = ""
                    continue
                stack += _

            elif q == "N2":
                if _ in self.numbers[:2]:
                    stack += _
                    continue

                elif _ in self.numbers[:9]:
                    stack += _
                    q = "N8"

                elif _ in self.numbers:
                    stack += _
                    q = "N10"

                elif _ == ".":
                    stack += _
                    q = "NF"

                elif _ in ["E", "e"]:
                    stack += "E"
                    q = "NFE"

                elif _ in ["O", "o"]:
                    stack += _
                    q = "N8X"

                elif _ in ["D", "d"]:
                    stack += _
                    q = "N10X"

                elif _ in ["a", "c", "f", "A", "C", "F"]:
                    stack += _
                    q = "N16"

                elif _ in ["H", "h"]:
                    stack += _
                    q = "N16X"

                elif _ in ["B", "b"]:
                    stack += _
                    q = "N2X"

                elif _ in [" ", "\n"]:
                    nid = self.in_table(stack, numbers)
                    if nid is False:
                        numbers.append(("Integer", stack))
                        nid = self.in_table(stack, numbers)
                    tokens.append((4, nid))
                    stack = ""
                    q = "H"

                elif _ in self.separators:
                    nid = self.in_table(stack, numbers)
                    if nid is False:
                        numbers.append(("Integer", stack))
                        nid = self.in_table(stack, numbers)
                    tokens.append((4, nid))
                    stack = _
                    q = "S"

                else:
                    stack = ""
                    q = "ER"

            elif q == "N2X":
                if _ in ["a", "c", "d", "e", "f", "A", "C", "D", "E", "F"]:
                    stack += _
                    q = "N16"
                elif _ in ["H", "h"]:
                    stack += _
                    q = "N16X"

                elif _ in [" ", "\n"]:
                    num = int(stack[:-1], 2)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)

                    tokens.append((4, nid))
                    stack = ""
                    q = "H"

                elif _ in self.separators:
                    num = int(stack[:-1], 2)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                    tokens.append((4, nid))
                    stack = _
                    q = "S"

                else:
                    stack = ""
                    q = "ER"

            elif q == "N8":
                if _ in self.numbers[:9]:
                    stack += _
                    q = "N8"

                elif _ in self.numbers[:10]:
                    stack += _
                    q = "N10"

                elif _ == ".":
                    stack += _
                    q = "NF"

                elif _ in ["E", "e"]:
                    stack += _
                    q = "NEXP"

                elif _ in ["D", "d"]:
                    stack += _
                    q = "N10X"

                elif _ in ["a", "b", "c", "f", "A", "B", "C", "F"]:
                    stack += _
                    q = "N16"

                elif _ in ["H", "h"]:
                    stack += _
                    q = "N16X"

                elif _ in ["O", "o"]:
                    stack += _
                    q = "N8X"

                elif _ in [" ", "\n"]:
                    nid = self.in_table(stack, numbers)
                    if nid is False:
                        numbers.append(("Integer", stack))
                        nid = self.in_table(stack, numbers)
                    tokens.append((4, nid))

                    stack = ""
                    q = "H"

                elif _ in self.separators:
                    nid = self.in_table(stack, numbers)
                    if nid is False:
                        numbers.append(("Integer", stack))
                        nid = self.in_table(stack, numbers)
                    tokens.append((4, nid))
                    stack = _
                    q = "S"

                else:
                    stack = ""
                    q = "ER"

            elif q == "N8X":
                if _ in [" ", "\n"]:
                    num = int(stack[:-1], 8)
                    nid = self.in_table(num, numbers)
                    if nid is False:

                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                    tokens.append((4, nid))
                    stack = ""
                    q = "H"

                elif _ in self.separators:
                    num = int(stack[:-1], 8)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                    tokens.append((4, nid))
                    stack = _
                    q = "S"

                else:
                    stack = ""
                    q = "ER"

            elif q == "N10":
                if _ in self.numbers[:10]:
                    stack += _

                elif _ == ".":
                    stack += _
                    q = "NF"

                elif _ in ["E", "e"]:
                    stack += _
                    q = "NEXP"

                elif _ in ["D", "d"]:
                    stack += _
                    q = "N10X"

                elif _ in ["a", "b", "c", "f", "A", "B", "C", "F"]:
                    stack += _
                    q = "N16"

                elif _ in ["H", "h"]:
                    stack += _
                    q = "N16X"

                elif _ in ["D", "d"]:
                    stack += _
                    q = "N10X"

                elif _ in [" ", "\n"]:
                    nid = self.in_table(stack, numbers)
                    if nid is False:
                        numbers.append(("Integer", stack))
                        nid = self.in_table(stack, numbers)
                    tokens.append((4, nid))
                    stack = ""
                    q = "H"

                elif _ in self.separators:
                    nid = self.in_table(stack, numbers)
                    if nid is False:
                        numbers.append(("Integer", stack))
                        nid = self.in_table(stack, numbers)
                        tokens.append((4, nid))

                    stack = _
                    q = "S"

                else:
                    stack = ""
                    q = "ER"

            elif q == "N10X":
                if _ in ["a", "b", "c", "d", "e", "f", "A", "B", "C", "D", "E", "F"]:
                    stack += _
                    q = "N16"

                elif _ in ["H", "h"]:
                    stack += _
                    q = "N16X"

                elif _ in [" ", "\n"]:
                    num = stack[:-1]
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                    tokens.append((4, nid))

                    stack = ""
                    q = "H"

                elif _ in self.separators:
                    num = stack[:-1]
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                    tokens.append((4, nid))

                    stack = _
                    q = "S"

                else:
                    stack = ""
                    q = "ER"

            elif q == "N16":
                if _ in self.numbers or _ in [
                    "a",
                    "b",
                    "c",
                    "d",
                    "e",
                    "f",
                    "A",
                    "B",
                    "C",
                    "D",
                    "E",
                    "F",
                ]:
                    stack += _

                elif _ in ["h", "H"]:
                    stack += _
                    q = "N16X"

                else:
                    stack = ""
                    q = "ER"

            elif q == "N16X":
                if _ in [" ", "\n"]:
                    num = int(stack[:-1], 16)
                    nid = self.in_table(stack, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                    tokens.append((4, nid))
                    stack = ""
                    q = "H"

                elif _ in self.separators:
                    num = int(stack[:-1], 16)
                    nid = self.in_table(stack, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                    tokens.append((4, nid))
                    stack = _
                    q = "S"

                else:
                    stack = ""
                    q = "ER"

            elif q == "NF":
                if _ in self.numbers:
                    stack += _
                    q = "NFX"

                else:
                    stack = ""
                    q = "ER"

            elif q == "NFX":
                if _ in ["E", "e"]:
                    stack += _
                    q = "NFEXP"
                    continue

                elif _ in self.numbers:
                    stack += _
                    continue

                elif _ in [" ", "\n"]:
                    nid = self.in_table(stack, numbers)
                    if nid is False:
                        numbers.append(("Float", stack))
                        nid = self.in_table(stack, numbers)
                    tokens.append((4, nid))

                    stack = ""
                    q = "H"

                elif _ in self.separators:
                    nid = self.in_table(stack, numbers)
                    if nid is False:
                        numbers.append(("Float", stack))
                        nid = self.in_table(stack, numbers)
                    tokens.append((4, nid))

                    stack = _
                    q = "S"

                else:
                    stack = ""
                    q = "ER"

            elif q == "NFEXP":
                if _ in ["+", "-"]:
                    stack += _
                    q = "NFEXPZ"

                elif _ in self.numbers:
                    stack += _
                    q = "NFEXPX"

                else:
                    stack = ""
                    q = "ER"

            elif q == "NFEXPZ":
                if _ in self.numbers:
                    stack += _
                    q = "NFEXPX"

                else:
                    stack = ""
                    q = "ER"

            elif q == "NFEXPX":
                if _ in self.numbers:
                    stack += _
                    continue

                elif _ in [" ", "\n"]:
                    num = self.fexp_to_float(stack)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Float", num))
                    nid = self.in_table(num, numbers)

                    stack = ""
                    q = "H"

                elif _ in self.separators:
                    num = self.fexp_to_float(stack)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Float", num))
                    nid = self.in_table(num, numbers)

                    stack = _
                    q = "S"

            elif q == "NEXP":
                if _ in self.numbers:
                    stack += _
                    q = "NEXPX"

                elif _ in ["+", "-"]:
                    stack += _
                    q = "NEXPZ"

                elif _ in ["a", "b", "c", "d", "f", "A", "B", "C", "D", "F"]:
                    stack += _
                    q = "N16"

                elif _ in ["H", "h"]:
                    stack += _
                    q = "N16X"

                else:
                    stack = ""
                    q = "ER"

            elif q == "NEXPX":
                if _ in self.numbers:
                    stack += _
                    continue

                elif _ in ["a", "b", "c", "d", "f", "A", "B", "C", "D", "F"]:
                    stack += _
                    q = "N16"

                elif _ in ["H", "h"]:
                    stack += _
                    q = "N16X"

                elif _ in [" ", "\n"]:
                    num = self.fexp_to_float(stack)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Float", num))
                        nid = self.in_table(num, numbers)
                    tokens.append((4, nid))

                    stack = ""
                    q = "H"

                elif _ in self.separators:
                    num = self.fexp_to_float(stack)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Float", num))
                        nid = self.in_table(num, numbers)
                    tokens.append((4, nid))

                    stack = _
                    q = "S"

                else:
                    stack = ""
                    q = "ER"

            if not _:
                break

        return tokens, numbers, identificators
