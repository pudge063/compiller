class Lexer:
    def __init__(self, file, debug):
        from core.lexer.reader import Reader
        from core.lexer.helpers import Helpers
        from core.lexer.tables import vocabilary, numbers, separators, keywords

        self.debug = debug

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
    V - выход = H
    ER - ошибка

    H -> I | N2 | N8 | N10 | NF | S | H | C | ER
    I -> I | K | ER
    S -> SS | ER
    C -> S | V | ER
    N2 -> N2 | ER | N8 | N10 | NF | NEXP | N8X | N10X | N16 | N16X | N2X | V
    N8 -> N8 | ER | N10 | NF | NEXP | N10X | N16 | N16X | N8X | V
    N10 -> N10 | ER | NF | NEXP | N10X | N16 | N16X | N10X | V
    N16 -> N16 | ER | N16X | V
    N2X -> N16 | N16X | ER | V
    N8X -> ER | V
    N10X -> ER | N16 | N16X | V
    N16X -> ER | V
    NEXP -> NEXPX | N16 | N16X | ER
    NEXPX -> NEXPX | N16 | N16X | ER
    NF -> NFX | NFEXP | ER
    NFX -> NFX | ER | V
    NFEXP -> NFEXPZ | NFEXPX | ER
    NFEXPZ -> NFEXPZX | ER
    NFEXPZX -> NFEXPZX | ER | V
    """

    def gc(self) -> str:
        """
        Функция для получения одного следующего символа из файла с кодом.
        Возвращает символ с типом str.
        """
        return self.get_char()

    def nill(self):
        """
        Процедура обнуления текущего стека.
        """
        self.stack = ""

    def add(self):
        """
        Процедура добавления в стек текущего символа _.
        """
        self.stack += self._

    def write_tokens(self, tokens, numbers, identificators, errors):
        import json

        lexer_output = {
            "tokens": tokens,
            "numbers": numbers,
            "identificators": identificators,
            "errors": errors,
        }

        with open("lexer_output.json", "w", encoding="utf-8") as file:
            json.dump(lexer_output, file, indent=4, ensure_ascii=False)

    def tokenize(self):
        """
        Основная функция. Выполняет основной цикл определения токена, пока не будет прочитан весь файл.
        """
        add = self.add
        nill = self.nill

        """
        Текущее состояние автомата. В процессе определения токена состояние меняется.
        """
        q = "H"

        self.stack = ""

        """
        Листы для хранения набора токенов, идентификаторов, чисел и ошибок.
        Токены хранятся в виде (n, k), где n - номер таблицы токенов, k - номер элемента в таблице n.
        Номера таблиц:
        1 - ключевые слова
        2 - разделители
        3 - идентификаторы
        4 - переменные
        
        Идентификаторы хранятся в виде [x, y, a], где x, y, a - названия идентификаторов. 
        В таблице токенов содержится ссылка на номер элемента в листе идентификаторов.
        
        Числа хранятся в виде ("Type", x), где Type - тип Integer | Float, x - число в 10-ой системе счисления.
        Все числа переводятся в стандартный вид 10й системы счисления без э.ф..
        """
        tokens = []
        identificators = []
        numbers = []
        errors = []

        while True:
            _ = self.gc()
            self._ = _
            stack = self.stack

            if self.debug:
                print(f"stack = {stack}\t q = {q}\t char = {_}")

            if q == "ER":
                print("Error lexer.")
                return [], [], [], errors

            if q == "H":
                if _ == " " or _ == "\n":
                    continue

                add()

                if _ in self.vocabilary or _ in self.keywords:
                    q = "I"

                elif _ in self.numbers:
                    if _ in self.numbers[:2]:
                        q = "N2"
                    elif _ in self.numbers[:9]:
                        q = "N8"
                    elif _ in self.numbers:
                        q = "N10"

                elif _ == ".":
                    q = "NF"

                elif _ in ["!", "=", ">", "<", "|"]:
                    q = "SS"

                elif _ in self.separators:
                    q = "S"

                else:
                    q = "ER"

            elif q == "I":
                if _ == " ":
                    q = "H"
                    if self.stack in self.keywords:
                        tokens.append((1, self.keywords[self.stack]))

                    elif self.stack == "true":
                        tokens.append((5, 1))

                    elif self.stack == "false":
                        tokens.append((5, 0))

                    elif self.stack in self.separators:
                        tokens.append(2, self.separators[self.stack])

                    else:
                        if not self.stack in identificators:
                            identificators.append(self.stack)
                        tokens.append((3, identificators.index(self.stack)))
                    nill()

                elif _ == "\n":
                    if self.stack in self.keywords:
                        tokens.append((1, self.keywords[self.stack]))

                    elif self.stack == "true":
                        tokens.append((5, 1))

                    elif self.stack == "false":
                        tokens.append((5, 0))

                    elif self.stack in self.separators:
                        tokens.append(2, self.separators[self.stack])
                    else:
                        if not self.stack in identificators:
                            identificators.append(self.stack)
                        tokens.append((3, identificators.index(self.stack)))
                    tokens.append((2, self.separators["\n"]))
                    nill()
                    q = "H"

                elif _ in self.separators:
                    if self.stack in self.keywords:
                        tokens.append((1, self.keywords[self.stack]))

                    elif self.stack == "true":
                        tokens.append((5, 1))

                    elif self.stack == "false":
                        tokens.append((5, 0))

                    elif self.stack in self.separators:
                        tokens.append(2, self.separators[self.stack])

                    else:
                        if not self.stack in identificators:
                            identificators.append(self.stack)
                        tokens.append((3, identificators.index(self.stack)))
                    nill()
                    add()
                    q = "S"

                elif _ in self.vocabilary or _ in self.numbers:
                    add()
                    continue

                elif _ == "&":
                    add()
                    tokens.append((2, self.separators[self.stack]))
                    nill()
                    q = "H"

                elif _ in self.separators:
                    if self.stack in self.keywords:
                        tokens.append((1, self.keywords[self.stack]))
                    else:
                        if not self.stack in identificators:
                            identificators.append(self.stack)
                        tokens.append((3, identificators.index(self.stack)))
                    nill()
                    add()
                    q = "S"

                else:
                    q = "ER"

            elif q == "S":
                if _ == " " or _ == "\n":

                    if self.stack in self.separators:
                        tokens.append((2, self.separators[self.stack]))
                        nill()
                    else:
                        q = "ER"

                    if _ == "\n":
                        tokens.append((2, self.separators["\n"]))

                    q = "H"

                elif _ in ["!", "=", "<", ">", "&"]:
                    q = "SS"
                    add()

                elif _ == "*":
                    if self.stack == "(":
                        q = "C"
                    continue

                elif _ in self.separators:
                    if self.stack in self.separators:
                        tokens.append((2, self.separators[self.stack]))
                        nill()
                        add()
                    else:
                        q = "ER"
                    q = "S"

            elif q == "SS":
                if _ in ["=", "&", "|"]:
                    add()
                    if self.stack in self.separators:
                        tokens.append((2, self.separators[self.stack]))
                        nill()
                        q = "H"
                    else:
                        q = "ER"

                elif _ == " " or _ == "\n":
                    tokens.append((2, self.separators[self.stack]))
                    if _ == "\n":
                        tokens.append((2, self.separators["\n"]))
                    nill()
                    q = "H"

                else:
                    q = "ER"

            elif q == "C":
                if _ == ")" and self.stack[-1] == "*":
                    q = "H"
                    nill()
                    continue
                add()

            elif q == "N2":
                if _ in self.numbers[:2]:
                    add()

                elif _ in self.numbers[:9]:
                    add()
                    q = "N8"

                elif _ in self.numbers:
                    add()
                    q = "N10"

                elif _ == ".":
                    add()
                    q = "NF"

                elif _ in ["E", "e"]:
                    add()
                    q = "NFE"

                elif _ in ["O", "o"]:
                    add()
                    q = "N8X"

                elif _ in ["D", "d"]:
                    add()
                    q = "N10X"

                elif _ in ["a", "c", "f", "A", "C", "F"]:
                    add()
                    q = "N16"

                elif _ in ["H", "h"]:
                    add()
                    q = "N16X"

                elif _ in ["B", "b"]:
                    add()
                    q = "N2X"

                elif _ in [" ", "\n"]:
                    num = int(self.stack)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                    tokens.append((4, nid))
                    nill()

                    if _ == "\n":
                        tokens.append((2, self.separators["\n"]))

                    q = "H"

                elif _ in self.separators:
                    nid = self.in_table(self.stack, numbers)
                    if nid is False:
                        numbers.append(("Integer", self.stack))
                        nid = self.in_table(self.stack, numbers)
                    tokens.append((4, nid))
                    nill()
                    add()
                    q = "S"

                else:
                    nill()
                    q = "ER"

            elif q == "N2X":
                if (
                    _ in ["a", "b", "c", "d", "e", "f", "A", "B", "C", "D", "E", "F"]
                    or _ in self.numbers
                ):
                    add()
                    q = "N16"
                elif _ in ["H", "h"]:
                    add()
                    q = "N16X"

                elif _ in [" ", "\n"]:
                    num = int(self.stack[:-1], 2)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)

                    tokens.append((4, nid))
                    nill()

                    if _ == "\n":
                        tokens.append((2, self.separators["\n"]))

                    q = "H"

                elif _ in self.separators:
                    num = int(self.stack[:-1], 2)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                    tokens.append((4, nid))
                    nill()
                    add()
                    q = "S"

                else:
                    nill()
                    q = "ER"

            elif q == "N8":
                if _ in self.numbers[:9]:
                    add()
                    q = "N8"

                elif _ in self.numbers[:10]:
                    add()
                    q = "N10"

                elif _ == ".":
                    add()
                    q = "NF"

                elif _ in ["E", "e"]:
                    add()
                    q = "NEXP"

                elif _ in ["D", "d"]:
                    add()
                    q = "N10X"

                elif _ in ["a", "b", "c", "f", "A", "B", "C", "F"]:
                    add()
                    q = "N16"

                elif _ in ["H", "h"]:
                    add()
                    q = "N16X"

                elif _ in ["O", "o"]:
                    add()
                    q = "N8X"

                elif _ in [" ", "\n"]:
                    nid = self.in_table(self.stack, numbers)
                    if nid is False:
                        numbers.append(("Integer", self.stack))
                        nid = self.in_table(self.stack, numbers)
                    tokens.append((4, nid))

                    nill()

                    if _ == "\n":
                        tokens.append((2, self.separators["\n"]))

                    q = "H"

                elif _ in self.separators:
                    nid = self.in_table(self.stack, numbers)
                    if nid is False:
                        numbers.append(("Integer", self.stack))
                        nid = self.in_table(self.stack, numbers)
                    tokens.append((4, nid))
                    nill()
                    add()
                    q = "S"

                else:
                    nill()
                    q = "ER"

            elif q == "N8X":
                if _ in [" ", "\n"]:
                    num = int(self.stack[:-1], 8)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)

                    tokens.append((4, nid))
                    nill()

                    if _ == "\n":
                        tokens.append((2, self.separators["\n"]))

                    q = "H"

                elif _ in self.separators:
                    num = int(self.stack[:-1], 8)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                    tokens.append((4, nid))
                    nill()
                    add()
                    q = "S"

                else:
                    nill()
                    q = "ER"

            elif q == "N10":
                if _ in self.numbers[:10]:
                    add()

                elif _ == ".":
                    add()
                    q = "NF"

                elif _ in ["E", "e"]:
                    add()
                    q = "NEXP"

                elif _ in ["D", "d"]:
                    add()
                    q = "N10X"

                elif _ in ["a", "b", "c", "f", "A", "B", "C", "F"]:
                    add()
                    q = "N16"

                elif _ in ["H", "h"]:
                    add()
                    q = "N16X"

                elif _ in ["D", "d"]:
                    add()
                    q = "N10X"

                elif _ in [" ", "\n"]:
                    num = int(self.stack)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                    tokens.append((4, nid))
                    nill()

                    if _ == "\n":
                        tokens.append((2, self.separators["\n"]))

                    q = "H"

                elif _ in self.separators:
                    num = int(self.stack)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                        tokens.append((4, nid))

                    nill()
                    add()
                    q = "S"

                else:
                    nill()
                    q = "ER"

            elif q == "N10X":
                if _ in ["a", "b", "c", "d", "e", "f", "A", "B", "C", "D", "E", "F"]:
                    add()
                    q = "N16"

                elif _ in ["H", "h"]:
                    add()
                    q = "N16X"

                elif _ in [" ", "\n"]:
                    num = int(self.stack[:-1])
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                    tokens.append((4, nid))

                    nill()

                    if _ == "\n":
                        tokens.append((2, self.separators["\n"]))

                    q = "H"

                elif _ in self.separators:
                    num = int(self.stack[:-1])
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                    tokens.append((4, nid))

                    nill()
                    add()
                    q = "S"

                else:
                    nill()
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
                    add()

                elif _ in ["h", "H"]:
                    add()
                    q = "N16X"

                else:
                    nill()
                    q = "ER"

            elif q == "N16X":
                if _ in [" ", "\n"]:
                    num = int(self.stack[:-1], 16)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                    tokens.append((4, nid))

                    if _ == "\n":
                        tokens.append((2, self.separators["\n"]))

                    nill()
                    q = "H"

                elif _ in self.separators:
                    num = int(self.stack[:-1], 16)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                    tokens.append((4, nid))

                    nill()
                    add()
                    q = "S"

                else:
                    nill()
                    q = "ER"

            elif q == "NF":
                if _ in self.numbers:
                    self.add()
                    q = "NFX"

                else:
                    self.nill()
                    q = "ER"

            elif q == "NFX":
                if _ in ["E", "e"]:
                    self.add()
                    q = "NFEXP"

                elif _ in self.numbers:
                    self.add()

                elif _ in [" ", "\n"]:
                    num = float(self.stack)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Float", num))
                        nid = self.in_table(num, numbers)
                    tokens.append((4, nid))

                    if _ == "\n":
                        tokens.append((2, self.separators["\n"]))

                    nill()
                    q = "H"

                elif _ in self.separators:
                    num = float(self.stack)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Float", num))
                        nid = self.in_table(num, numbers)
                    tokens.append((4, nid))
                    nill()
                    add()
                    q = "S"

                else:
                    self.nill()
                    q = "ER"

            elif q == "NFEXP":
                add()
                if _ in ["+", "-"]:
                    q = "NFEXPZ"

                elif _ in self.numbers:
                    q = "NFEXPX"

                else:
                    nill()
                    q = "ER"

            elif q == "NFEXPZ":
                if _ in self.numbers:
                    add()
                    q = "NFEXPX"

                else:
                    nill()
                    q = "ER"

            elif q == "NFEXPX":
                if _ in self.numbers:
                    add()

                elif _ in [" ", "\n"]:
                    num = self.fexp_to_float(self.stack)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Float", num))
                    nid = self.in_table(num, numbers)

                    if _ == "\n":
                        tokens.append((2, self.separators["\n"]))

                    nill()
                    q = "H"

                elif _ in self.separators:
                    num = self.fexp_to_float(self.stack)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Float", num))
                    nid = self.in_table(num, numbers)

                    nill()
                    add()
                    q = "S"

            elif q == "NEXP":
                add()
                if _ in self.numbers:
                    q = "NEXPX"

                elif _ in ["+", "-"]:
                    q = "NEXPZ"

                elif _ in ["a", "b", "c", "d", "f", "A", "B", "C", "D", "F"]:
                    q = "N16"

                elif _ in ["H", "h"]:
                    q = "N16X"

                else:
                    nill()
                    q = "ER"

            elif q == "NEXPX":
                if _ in self.numbers:
                    add()
                    continue

                elif _ in ["a", "b", "c", "d", "f", "A", "B", "C", "D", "F"]:
                    add()
                    q = "N16"

                elif _ in ["H", "h"]:
                    add()
                    q = "N16X"

                elif _ in [" ", "\n"]:
                    num = self.fexp_to_float(self.stack)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Float", num))
                        nid = self.in_table(num, numbers)
                    tokens.append((4, nid))

                    if _ == "\n":
                        tokens.append((2, self.separators["\n"]))

                    nill()
                    q = "H"

                elif _ in self.separators:
                    num = self.fexp_to_float(self.stack)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Float", num))
                        nid = self.in_table(num, numbers)
                    tokens.append((4, nid))

                    nill()
                    add()
                    q = "S"

                else:
                    stack = ""
                    q = "ER"

            elif q == "NEXPZ":
                if _ in self.numbers:
                    add()
                    q = "NEXPZX"
                else:
                    nill()
                    q = "ER"

            elif q == "NEXPZX":
                if _ in self.numbers:
                    add()
                    continue
                elif _ in [" ", "\n"]:
                    num = self.fexp_to_float(self.stack)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                    tokens.append((4, nid))

                    if _ == "\n":
                        tokens.append((2, self.separators["\n"]))

                    nill()
                    q = "H"

                elif _ in self.separators:
                    num = self.fexp_to_float(self.stack)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                    tokens.append((4, nid))

                    nill()
                    add()
                    q = "S"

            if not _:
                break

        self.write_tokens(tokens, numbers, identificators, errors)

        return tokens, numbers, identificators, errors
