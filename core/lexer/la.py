class Lexer:
    def __init__(self, file, debug):
        from core.lexer.reader import Reader
        from core.lexer.helpers import Helpers
        from core.lexer.tables import vocabilary, numbers, separators, keywords

        self.init_colors()

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

    def init_colors(self):
        from core.helpers import Helpers

        helper = Helpers()
        self.print_black = helper.print_black
        self.print_cyan = helper.print_cyan
        self.print_red = helper.print_red
        self.print_magenta = helper.print_magenta
        self.print_yellow = helper.print_yellow

    def gc(self) -> str:
        """
        Функция для получения одного следующего символа из файла с кодом.
        Возвращает символ с типом str.
        """

        if self.debug:
            self.print_black("Call gc().")

        return self.get_char()

    def nill(self):
        """
        Процедура обнуления текущего стека.
        """

        if self.debug:
            self.print_black("Call nill().")

        self.stack = ""

    def add(self):
        """
        Процедура добавления в стек текущего символа _.
        """

        if self.debug:
            self.print_black("Call add().")

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
                ch = _
                if _ == "\n":
                    ch = "\\n"
                self.print_black(f"stack: {stack}# q: {q} char: {ch}")

            if q == "ER":
                return [], [], [], errors

            if q == "H":
                if _ == " " or _ == "\n":
                    if _ == "\n" and tokens[-1] != (2, self.separators["\n"]):
                        tokens.append((2, self.separators["\n"]))
                        if self.debug:
                            self.print_yellow(f"token '\\n' -> (2, {self.separators["\n"]})")
                            
                        if self.debug:
                            self.print_yellow(
                                f"token '{self.stack}' -> (2, {self.separators[self.stack]})"
                            )
                    continue
                add()

                if _ in self.vocabilary or _ in self.keywords:
                    if self.debug:
                        self.print_yellow(f"q: {q} -> I")
                    q = "I"

                elif _ in self.numbers:
                    if _ in self.numbers[:2]:
                        if self.debug:
                            self.print_yellow(f"q: {q} -> N2")
                        q = "N2"

                    elif _ in self.numbers[:9]:
                        if self.debug:
                            self.print_yellow(f"q: {q} -> N8")
                        q = "N8"

                    elif _ in self.numbers:
                        if self.debug:
                            self.print_yellow(f"q: {q} -> N10")
                        q = "N10"

                elif _ == ".":
                    if self.debug:
                        self.print_yellow(f"q: {q} -> NF")
                    q = "NF"

                elif _ in ["!", "=", ">", "<", "|"]:
                    if self.debug:
                        self.print_yellow(f"q: {q} -> SS")
                    q = "SS"

                elif _ in self.separators:
                    if self.debug:
                        self.print_yellow(f"q: {q} -> S")
                    q = "S"

            elif q == "I":
                if _ == " ":
                    if self.debug:
                        self.print_yellow(f"q: {q} -> H")
                    q = "H"

                    if self.stack in self.keywords:
                        tokens.append((1, self.keywords[self.stack]))
                        if self.debug:
                            self.print_yellow(
                                f"token '{self.stack}' -> (1, {self.keywords[self.stack]})"
                            )

                    elif self.stack == "true":
                        tokens.append((5, 1))
                        if self.debug:
                            self.print_yellow(f"token '{self.stack}' -> (5, 1)")

                    elif self.stack == "false":
                        tokens.append((5, 0))
                        if self.debug:
                            self.print_yellow(f"token '{self.stack}' -> (5, 0)")

                    elif self.stack in self.separators:
                        tokens.append(2, self.separators[self.stack])
                        if self.debug:
                            self.print_yellow(
                                f"token '{self.stack}' -> (2, {self.separators[self.stack]})"
                            )

                    else:
                        if not self.stack in identificators:
                            identificators.append(self.stack)
                            if self.debug:
                                self.print_yellow(
                                    f"identificator '{self.stack}' -> (3, {self.stack})"
                                )
                        tokens.append((3, identificators.index(self.stack)))
                        if self.debug:
                            self.print_yellow(
                                f"token '{self.stack}' -> (3, {self.stack})"
                            )
                    nill()

                elif _ == "\n":
                    if self.stack in self.keywords:
                        tokens.append((1, self.keywords[self.stack]))
                        if self.debug:
                            self.print_yellow(
                                f"token '{self.stack}' -> (1, {self.keywords[self.stack]})"
                            )

                    elif self.stack == "true":
                        tokens.append((5, 1))
                        if self.debug:
                            self.print_yellow(f"token '{self.stack}' -> (5, 1)")

                    elif self.stack == "false":
                        tokens.append((5, 0))
                        if self.debug:
                            self.print_yellow(f"token '{self.stack}' -> (5, 0)")

                    elif self.stack in self.separators:
                        tokens.append(2, self.separators[self.stack])
                        if self.debug:
                            self.print_yellow(
                                f"token '{self.stack}' -> (2, {self.separators[self.stack]})"
                            )
                    else:
                        if not self.stack in identificators:
                            identificators.append(self.stack)
                            if self.debug:
                                self.print_yellow(
                                    f"identificator '{self.stack}' -> (3, {self.stack})"
                                )

                        tokens.append((3, identificators.index(self.stack)))
                        if self.debug:
                            self.print_yellow(
                                f"token '{self.stack}' -> (3, {self.stack})"
                            )

                    tokens.append((2, self.separators["\n"]))
                    nill()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> H")
                    q = "H"

                elif _ in self.separators:
                    if self.stack in self.keywords:
                        tokens.append((1, self.keywords[self.stack]))
                        if self.debug:
                            self.print_yellow(
                                f"token '{self.stack}' -> (1, {self.keywords[self.stack]})"
                            )

                    elif self.stack == "true":
                        tokens.append((5, 1))
                        if self.debug:
                            self.print_yellow(f"token '{self.stack}' -> (5, 1)")

                    elif self.stack == "false":
                        tokens.append((5, 0))
                        if self.debug:
                            self.print_yellow(f"token '{self.stack}' -> (5, 0)")

                    elif self.stack in self.separators:
                        tokens.append(2, self.separators[self.stack])
                        if self.debug:
                            self.print_yellow(
                                f"token '{self.stack}' -> (2, {self.separators[self.stack]})"
                            )

                    else:
                        if not self.stack in identificators:
                            identificators.append(self.stack)
                            if self.debug:
                                self.print_yellow(
                                    f"identificator '{self.stack}' -> (3, {self.stack})"
                                )
                        tokens.append((3, identificators.index(self.stack)))
                        if self.debug:
                            self.print_yellow(
                                f"token '{self.stack}' -> (3, {self.stack})"
                            )
                    nill()
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> S")
                    q = "S"

                elif _ in self.vocabilary or _ in self.numbers:
                    add()
                    continue

                elif _ == "&":
                    add()
                    tokens.append((2, self.separators[self.stack]))
                    if self.debug:
                        self.print_yellow(
                            f"token '{self.stack}' -> (2, {self.separators[self.stack]})"
                        )

                    nill()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> H")
                    q = "H"

                elif _ in self.separators:
                    if self.stack in self.keywords:
                        tokens.append((1, self.keywords[self.stack]))
                        if self.debug:
                            self.print_yellow(
                                f"token '{self.stack}' -> (1, {self.keywords[self.stack]})"
                            )
                    else:
                        if not self.stack in identificators:
                            identificators.append(self.stack)
                            if self.debug:
                                self.print_yellow(
                                    f"identificator '{self.stack}' -> (3, {self.stack})"
                                )
                        tokens.append((3, identificators.index(self.stack)))
                        if self.debug:
                            self.print_yellow(
                                f"token '{self.stack}' -> (3, {self.stack})"
                            )

                    nill()
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> S")
                    q = "S"

                else:
                    errors.append("Unexcepted char in identificator.")
                    q = "ER"

            elif q == "S":
                if _ == " " or _ == "\n":

                    if self.stack in self.separators:
                        tokens.append((2, self.separators[self.stack]))
                        if self.debug:
                            self.print_yellow(
                                f"token '{self.stack}' -> (2, {self.separators[self.stack]})"
                            )
                        nill()

                    else:
                        errors.append("Undefined separator.")
                        q = "ER"

                    if _ == "\n":
                        tokens.append((2, self.separators["\n"]))
                        if self.debug:
                            self.print_yellow(
                                f"token '\\n' -> (2, {self.separators["\n"]})"
                            )

                    if self.debug:
                        self.print_yellow(f"q: {q} -> H")
                    q = "H"

                elif _ in ["!", "=", "<", ">", "&"]:
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> SS")
                    q = "SS"

                elif _ == "*":
                    if self.debug:
                        self.print_yellow("Look comment...")

                    if self.stack == "(":
                        if self.debug:
                            self.print_yellow(f"q: {q} -> C")
                        q = "C"
                    continue

                elif _ in self.separators:
                    if self.stack in self.separators:
                        tokens.append((2, self.separators[self.stack]))
                        if self.debug:
                            self.print_yellow(
                                f"token '{self.stack}' -> (2, {self.separators[self.stack]})"
                            )

                        nill()
                        add()
                    else:
                        errors.append(f"Undefined separator {self.stack}.")
                        q = "ER"

                    if self.debug:
                        self.print_yellow(f"q: {q} -> S")
                    q = "S"

            elif q == "SS":
                if _ in ["=", "&", "|"]:
                    add()
                    if self.stack in self.separators:
                        tokens.append((2, self.separators[self.stack]))
                        if self.debug:
                            self.print_yellow(
                                f"token '{self.stack}' -> (2, {self.separators[self.stack]})"
                            )

                        nill()

                        if self.debug:
                            self.print_yellow(f"q: {q} -> H")
                        q = "H"
                    else:
                        errors.append(f"Undefined component separator {self.stack}.")
                        q = "ER"

                elif _ == " " or _ == "\n":
                    tokens.append((2, self.separators[self.stack]))
                    if self.debug:
                        self.print_yellow(
                            f"token '{self.stack}' -> (2, {self.separators[self.stack]})"
                        )

                    if _ == "\n":
                        tokens.append((2, self.separators["\n"]))
                        if self.debug:
                            self.print_yellow(
                                f"token '\\n' -> (2, {self.separators["\n"]})"
                            )

                    nill()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> H")
                    q = "H"

                else:
                    errors.append(f"Unexcepted char {_} in component separator.")
                    q = "ER"

            elif q == "C":
                if self.debug:
                    self.print_yellow("... comment ...")

                if _ == ")" and self.stack[-1] == "*":
                    nill()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> H")
                    q = "H"

                    continue

                add()

            elif q == "N2":
                if _ in self.numbers[:2]:
                    add()

                elif _ in self.numbers[:9]:
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> N8")
                    q = "N8"

                elif _ in self.numbers:
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> N10")
                    q = "N10"

                elif _ == ".":
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> NF")
                    q = "NF"

                elif _ in ["E", "e"]:
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> NFEXP")
                    q = "NFEXP"

                elif _ in ["O", "o"]:
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> N8X")
                    q = "N8X"

                elif _ in ["D", "d"]:
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> N10X")
                    q = "N10X"

                elif _ in ["a", "c", "f", "A", "C", "F"]:
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> N16")
                    q = "N16"

                elif _ in ["H", "h"]:
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> N16X")
                    q = "N16X"

                elif _ in ["B", "b"]:
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> N2X")
                    q = "N2X"

                elif _ in [" ", "\n"]:
                    num = int(self.stack)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                    if self.debug:
                        self.print_yellow(f"numbers '{num}' -> (4, {nid})")

                    tokens.append((4, nid))
                    if self.debug:
                        self.print_yellow(f"token '{self.stack}' -> (4, {nid})")

                    nill()

                    if _ == "\n":
                        tokens.append((2, self.separators["\n"]))
                        if self.debug:
                            self.print_yellow(
                                f"token '\\n' -> (2, {self.separators["\n"]})"
                            )

                    if self.debug:
                        self.print_yellow(f"q: {q} -> H")
                    q = "H"

                elif _ in self.separators:
                    num = int(self.stack)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                        if self.debug:
                            self.print_yellow(f"numbers '{num}' -> (4, {nid})")

                    tokens.append((4, nid))
                    if self.debug:
                        self.print_yellow(f"tokens '{num}' -> (4, {nid})")

                    nill()
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> S")
                    q = "S"

                else:
                    nill()
                    errors.append(f"Unexcepted char {_} in binary number.")
                    q = "ER"

            elif q == "N2X":
                if (
                    _ in ["a", "b", "c", "d", "e", "f", "A", "B", "C", "D", "E", "F"]
                    or _ in self.numbers
                ):
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> N16")
                    q = "N16"

                elif _ in ["H", "h"]:
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> N16X")
                    q = "N16X"

                elif _ in [" ", "\n"]:
                    num = int(self.stack[:-1], 2)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                        if self.debug:
                            self.print_yellow(f"numbers '{num}' -> (4, {nid})")

                    tokens.append((4, nid))
                    if self.debug:
                        self.print_yellow(f"tokens '{num}' -> (4, {nid})")

                    nill()

                    if _ == "\n":
                        tokens.append((2, self.separators["\n"]))
                        if self.debug:
                            self.print_yellow(
                                f"tokens '\\n' -> (2, {self.separators["\n"]})"
                            )

                    if self.debug:
                        self.print_yellow(f"q: {q} -> H")
                    q = "H"

                elif _ in self.separators:
                    num = int(self.stack[:-1], 2)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                        if self.debug:
                            self.print_yellow(f"numbers '{num}' -> (4, {nid})")

                    tokens.append((4, nid))
                    if self.debug:
                        self.print_yellow(f"tokens '{num}' -> (4, {nid})")

                    nill()
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> S")
                    q = "S"

                else:
                    nill()
                    errors.append(f"Unexcepted char {_} in binary number.")
                    q = "ER"

            elif q == "N8":
                if _ in self.numbers[:9]:
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> N8")
                    q = "N8"

                elif _ in self.numbers[:10]:
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> N10")
                    q = "N10"

                elif _ == ".":
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> NF")
                    q = "NF"

                elif _ in ["E", "e"]:
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> NEXP")
                    q = "NEXP"

                elif _ in ["D", "d"]:
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> N10x")
                    q = "N10X"

                elif _ in ["a", "b", "c", "f", "A", "B", "C", "F"]:
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> N16")
                    q = "N16"

                elif _ in ["H", "h"]:
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> N16X")
                    q = "N16X"

                elif _ in ["O", "o"]:
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> N8X")
                    q = "N8X"

                elif _ in [" ", "\n"]:
                    num = int(self.stack)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                        if self.debug:
                            self.print_yellow(f"numbers '{num}' -> (4, {nid})")

                    tokens.append((4, nid))
                    if self.debug:
                        self.print_yellow(f"tokens '{num}' -> (4, {nid})")

                    nill()

                    if _ == "\n":
                        tokens.append((2, self.separators["\n"]))
                        if self.debug:
                            self.print_yellow(
                                f"tokens '\\n' -> (2, {self.separators["\n"]})"
                            )

                    if self.debug:
                        self.print_yellow(f"q: {q} -> H")
                    q = "H"

                elif _ in self.separators:
                    num = int(self.stack)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                        if self.debug:
                            self.print_yellow(f"numbers '{num}' -> (4, {nid})")

                    tokens.append((4, nid))
                    if self.debug:
                        self.print_yellow(f"numbers '{num}' -> (4, {nid})")

                    nill()
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> S")
                    q = "S"

                else:
                    nill()
                    errors.append(f"Unexcepted char {_} in O-number.")
                    q = "ER"

            elif q == "N8X":
                if _ in [" ", "\n"]:
                    num = int(self.stack[:-1], 8)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                        if self.debug:
                            self.print_yellow(f"number '{num}' -> (4, {nid})")

                    tokens.append((4, nid))
                    if self.debug:
                        self.print_yellow(f"token '{num}' -> (4, {nid})")

                    nill()

                    if _ == "\n":
                        tokens.append((2, self.separators["\n"]))
                        if self.debug:
                            self.print_yellow(
                                f"token '\\n' -> (2, {self.separators["\n"]})"
                            )

                    if self.debug:
                        self.print_yellow(f"q: {q} -> H")
                    q = "H"

                elif _ in self.separators:
                    num = int(self.stack[:-1], 8)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                        if self.debug:
                            self.print_yellow(f"number '{num}' -> (4, {nid})")

                    tokens.append((4, nid))
                    if self.debug:
                        self.print_yellow(f"token '{num}' -> (4, {nid})")

                    nill()
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> S")
                    q = "S"

                else:
                    nill()
                    errors.append(f"Unexcepted char {_} in binary number.")
                    q = "ER"

            elif q == "N10":
                if _ in self.numbers[:10]:
                    add()

                elif _ == ".":
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> NF")
                    q = "NF"

                elif _ in ["E", "e"]:
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> NEXP")
                    q = "NEXP"

                elif _ in ["D", "d"]:
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> N10X")
                    q = "N10X"

                elif _ in ["a", "b", "c", "f", "A", "B", "C", "F"]:
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> N16")
                    q = "N16"

                elif _ in ["H", "h"]:
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> N16X")
                    q = "N16X"

                elif _ in ["D", "d"]:
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> N10X")
                    q = "N10X"

                elif _ in [" ", "\n"]:
                    num = int(self.stack)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                        if self.debug:
                            self.print_yellow(f"number '{num}' -> (4, {nid})")

                    tokens.append((4, nid))
                    if self.debug:
                        self.print_yellow(f"token '{num}' -> (4, {nid})")

                    nill()

                    if _ == "\n":
                        tokens.append((2, self.separators["\n"]))
                        if self.debug:
                            self.print_yellow(
                                f"token '\\n' -> (2, {self.separators["\n"]})"
                            )

                    if self.debug:
                        self.print_yellow(f"q: {q} -> H")
                    q = "H"

                elif _ in self.separators:
                    num = int(self.stack)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                        if self.debug:
                            self.print_yellow(f"number '{num}' -> (4, {nid})")

                    tokens.append((4, nid))
                    if self.debug:
                        self.print_yellow(f"token '{num}' -> (4, {nid})")

                    nill()
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> S")
                    q = "S"

                else:
                    nill()
                    errors.append(f"Unexcepted char {_} in D-number.")
                    q = "ER"

            elif q == "N10X":
                if _ in ["a", "b", "c", "d", "e", "f", "A", "B", "C", "D", "E", "F"]:
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> N16")
                    q = "N16"

                elif _ in ["H", "h"]:
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> N16X")
                    q = "N16X"

                elif _ in [" ", "\n"]:
                    num = int(self.stack[:-1])
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                        if self.debug:
                            self.print_yellow(f"number '{num}' -> (4, {nid})")

                    tokens.append((4, nid))
                    if self.debug:
                        self.print_yellow(f"token '{num}' -> (4, {nid})")

                    nill()

                    if _ == "\n":
                        tokens.append((2, self.separators["\n"]))
                        if self.debug:
                            self.print_yellow(
                                f"token '\\n' -> (2, {self.separators["\n"]})"
                            )

                    if self.debug:
                        self.print_yellow(f"q: {q} -> H")
                    q = "H"

                elif _ in self.separators:
                    num = int(self.stack[:-1])
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                        if self.debug:
                            self.print_yellow(f"number '{num}' -> (4, {nid})")

                    tokens.append((4, nid))
                    if self.debug:
                        self.print_yellow(f"token '{num}' -> (4, {nid})")

                    nill()
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> S")
                    q = "S"

                else:
                    nill()
                    errors.append(f"Unexcepted char {_} in D-number.")
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

                    if self.debug:
                        self.print_yellow(f"q: {q} -> N16X")
                    q = "N16X"

                else:
                    nill()
                    errors.append(f"Unexcepted char {_} in H-number.")
                    q = "ER"

            elif q == "N16X":
                if _ in [" ", "\n"]:
                    num = int(self.stack[:-1], 16)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                        if self.debug:
                            self.print_yellow(f"number '{num}' -> (4, {nid})")
                    tokens.append((4, nid))
                    if self.debug:
                        self.print_yellow(f"token '{num}' -> (4, {nid})")

                    if _ == "\n":
                        tokens.append((2, self.separators["\n"]))
                        if self.debug:
                            self.print_yellow(
                                f"token '\\n' -> (2, {self.separators["\n"]})"
                            )

                    nill()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> H")
                    q = "H"

                elif _ in self.separators:
                    num = int(self.stack[:-1], 16)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                        if self.debug:
                            self.print_yellow(f"number '{num}' -> (4, {nid})")

                    tokens.append((4, nid))
                    if self.debug:
                        self.print_yellow(f"token '{num}' -> (4, {nid})")

                    nill()
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> S")
                    q = "S"

                else:
                    nill()
                    errors.append(f"Unexcepted char {_} in H-number.")
                    q = "ER"

            elif q == "NF":
                if _ in self.numbers:
                    self.add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> NFX")
                    q = "NFX"

                else:
                    self.nill()
                    errors.append(f"Unexcepted char {_} in float number.")
                    q = "ER"

            elif q == "NFX":
                if _ in ["E", "e"]:
                    self.add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> NFEXP")
                    q = "NFEXP"

                elif _ in self.numbers:
                    self.add()

                elif _ in [" ", "\n"]:
                    num = float(self.stack)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Float", num))
                        nid = self.in_table(num, numbers)
                        if self.debug:
                            self.print_yellow(f"number '{num}' -> (4, {nid})")

                    tokens.append((4, nid))
                    if self.debug:
                        self.print_yellow(f"token '{num}' -> (4, {nid})")

                    if _ == "\n":
                        tokens.append((2, self.separators["\n"]))
                        if self.debug:
                            self.print_yellow(
                                f"token '\\n' -> (2, {self.separators["\n"]})"
                            )

                    nill()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> H")
                    q = "H"

                elif _ in self.separators:
                    num = float(self.stack)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Float", num))
                        nid = self.in_table(num, numbers)
                        if self.debug:
                            self.print_yellow(f"number '{num}' -> (4, {nid})")

                    tokens.append((4, nid))
                    if self.debug:
                        self.print_yellow(f"token '{num}' -> (4, {nid})")

                    nill()
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> S")
                    q = "S"

                else:
                    self.nill()
                    errors.append(f"Unexcepted char {_} in float number.")
                    q = "ER"

            elif q == "NFEXP":
                add()

                if _ in ["+", "-"]:
                    if self.debug:
                        self.print_yellow(f"q: {q} -> NFEXPZ")
                    q = "NFEXPZ"

                elif _ in self.numbers:
                    if self.debug:
                        self.print_yellow(f"q: {q} -> NFEXPX")
                    q = "NFEXPX"

                else:
                    nill()
                    errors.append(f"Unexcepted char {_} in exp number.")
                    q = "ER"

            elif q == "NFEXPZ":
                if _ in self.numbers:
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> NFXPX")
                    q = "NFEXPX"

                else:
                    nill()
                    errors.append(f"Unexcepted char {_} in exp-float number.")
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
                        if self.debug:
                            self.print_yellow(f"number '{num}' -> (4, {nid})")

                    tokens.append((4, nid))
                    if self.debug:
                        self.print_yellow(f"token '{num}' -> (4, {nid})")

                    if _ == "\n":
                        tokens.append((2, self.separators["\n"]))
                        if self.debug:
                            self.print_yellow(
                                f"token '\\n' -> (2, {self.separators["\n"]})"
                            )

                    nill()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> H")
                    q = "H"

                elif _ in self.separators:
                    num = self.fexp_to_float(self.stack)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Float", num))
                        nid = self.in_table(num, numbers)
                        if self.debug:
                            self.print_yellow(f"number '{num}' -> (4, {nid})")

                    tokens.append((4, nid))
                    if self.debug:
                        self.print_yellow(f"token '{num}' -> (4, {nid})")

                    nill()
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> S")
                    q = "S"

                else:
                    nill()
                    errors.append(f"Unexcepted char {_} in exp-float number.")
                    q = "ER"

            elif q == "NEXP":
                add()

                if _ in self.numbers:
                    if self.debug:
                        self.print_yellow(f"q: {q} -> NEXPX")
                    q = "NEXPX"

                elif _ in ["+", "-"]:
                    if self.debug:
                        self.print_yellow(f"q: {q} -> NEXPZ")
                    q = "NEXPZ"

                elif _ in ["a", "b", "c", "d", "f", "A", "B", "C", "D", "F"]:
                    if self.debug:
                        self.print_yellow(f"q: {q} -> N16")
                    q = "N16"

                elif _ in ["H", "h"]:
                    if self.debug:
                        self.print_yellow(f"q: {q} -> N16X")
                    q = "N16X"

                else:
                    nill()
                    errors.append(f"Unexcepted char {_} in exp number.")
                    q = "ER"

            elif q == "NEXPX":
                if _ in self.numbers:
                    add()
                    continue

                elif _ in ["a", "b", "c", "d", "f", "A", "B", "C", "D", "F"]:
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> N16")
                    q = "N16"

                elif _ in ["H", "h"]:
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> N16X")
                    q = "N16X"

                elif _ in [" ", "\n"]:
                    num = int(self.fexp_to_float(self.stack))
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                        if self.debug:
                            self.print_yellow(f"number '{num}' -> (4, {nid})")

                    tokens.append((4, nid))
                    if self.debug:
                        self.print_yellow(f"token '{num}' -> (4, {nid})")

                    if _ == "\n":
                        tokens.append((2, self.separators["\n"]))
                        if self.debug:
                            self.print_yellow(
                                f"token '\\n' -> (2, {self.separators["\n"]})"
                            )

                    nill()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> H")
                    q = "H"

                elif _ in self.separators:
                    num = int(self.fexp_to_float(self.stack))
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                        if self.debug:
                            self.print_yellow(f"number '{num}' -> (4, {nid})")

                    tokens.append((4, nid))
                    if self.debug:
                        self.print_yellow(f"token '{num}' -> (4, {nid})")

                    nill()
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> S")
                    q = "S"

                else:
                    stack = ""
                    errors.append(f"Unexcepted char {_} in exp number.")
                    q = "ER"

            elif q == "NEXPZ":
                if _ in self.numbers:
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> NEXPZX")
                    q = "NEXPZX"

                else:
                    nill()
                    errors.append(f"Unexcepted char {_} in exp number.")
                    q = "ER"

            elif q == "NEXPZX":
                if _ in self.numbers:
                    add()
                    continue

                elif _ in [" ", "\n"]:
                    num = int(self.fexp_to_float(self.stack))
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                        if self.debug:
                            self.print_yellow(f"number '{num}' -> (4, {nid})")

                    tokens.append((4, nid))
                    if self.debug:
                        self.print_yellow(f"token '{num}' -> (4, {nid})")

                    if _ == "\n":
                        tokens.append((2, self.separators["\n"]))
                        if self.debug:
                            self.print_yellow(
                                f"token '\\n' -> (2, {self.separators["\n"]})"
                            )

                    nill()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> H")
                    q = "H"

                elif _ in self.separators:
                    num = int(self.fexp_to_float(self.stack))
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                        if self.debug:
                            self.print_yellow(f"number '{num}' -> (4, {nid})")

                    tokens.append((4, nid))
                    if self.debug:
                        self.print_yellow(f"token '{num}' -> (4, {nid})")

                    nill()
                    add()

                    if self.debug:
                        self.print_yellow(f"q: {q} -> S")
                    q = "S"

                else:
                    nill()
                    errors.append(f"Unexcepted char {_} in binary number.")
                    q = "ER"

            if not _:
                if tokens[-1] == (2, self.separators["\n"]):
                    tokens.pop(-1)
                break

        self.write_tokens(tokens, numbers, identificators, errors)

        return tokens, numbers, identificators, errors
