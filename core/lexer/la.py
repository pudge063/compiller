class Lexer:
    def __init__(self, file, debug):
        from core.lexer.reader import Reader
        from core.lexer.helpers import Helpers
        from core.lexer.tables import vocabilary, numbers, separators, keywords

        self.debug = debug

        self.init_debug()

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

    def init_debug(self):
        from core.lexer.l_debug import Debug

        debugger = Debug(self.debug)

        self.change_state = debugger.change_state
        self.print_stack = debugger.print_stack
        self.add_token = debugger.add_token
        self.add_identificator = debugger.add_identificator
        self.add_number = debugger.add_number
        self.look_comment = debugger.look_comment
        self.skip_comment = debugger.skip_comment

        self.use_nill = debugger.use_nill
        self.use_add = debugger.use_add
        self.use_gc = debugger.use_gc

    def gc(self) -> str:
        self.use_gc()
        return self.get_char()

    def nill(self):
        self.use_nill()
        self.stack = ""

    def add(self):
        self.use_add()
        self.stack += self.chr

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
        add = self.add
        nill = self.nill

        q = "H"
        self.stack = ""

        tokens = []
        identificators = []
        numbers = []
        errors = []

        while True:
            chr = self.gc()
            self.chr = chr
            stack = self.stack

            ch = chr
            if chr == "\n":
                ch = "\\n"
            self.print_stack(stack, q, ch)

            if q == "ER":
                return [], [], [], errors

            if q == "H":
                if chr == " " or chr == "\n":
                    if len(tokens) > 0:
                        if chr == "\n" and tokens[-1] != (2, self.separators["\n"]):
                            tokens.append((2, self.separators["\n"]))

                            self.add_token("\\n", 2, self.separators["\n"])
                            self.add_token(self.stack, 2, self.separators["\n"])

                    else:
                        q = self.change_state(q, "H")

                    continue

                add()

                if chr in self.vocabilary or chr in self.keywords:
                    q = self.change_state(q, "I")

                elif chr in self.numbers:
                    if chr in self.numbers[:2]:
                        q = self.change_state(q, "N2")

                    elif chr in self.numbers[:9]:
                        q = self.change_state(q, "N8")

                    elif chr in self.numbers:
                        q = self.change_state(q, "N10")

                elif chr == ".":
                    q = self.change_state(q, "NF")

                elif chr in ["!=><|"]:
                    q = self.change_state(q, "SS")

                elif chr in self.separators:
                    q = self.change_state(q, "S")

            elif q == "I":
                if chr == " ":
                    q = self.change_state(q, "H")

                    if self.stack in self.keywords:
                        tokens.append((1, self.keywords[self.stack]))
                        self.add_token(self.stack, 1, self.keywords[self.stack])

                    elif self.stack == "true":
                        tokens.append((5, 1))
                        self.add_token(self.stack, 5, 1)

                    elif self.stack == "false":
                        tokens.append((5, 0))
                        self.add_token(self.stack, 5, 0)

                    elif self.stack in self.separators:
                        tokens.append(2, self.separators[self.stack])
                        self.add_token(self.stack, 2, self.separators[self.stack])

                    else:
                        if not self.stack in identificators:
                            identificators.append(self.stack)
                            self.add_identificator(self.stack, 3, self.stack)

                        tokens.append((3, identificators.index(self.stack)))
                        self.add_token(self.stack, 3, identificators.index(self.stack))

                    nill()

                elif chr == "\n":
                    if self.stack in self.keywords:
                        tokens.append((1, self.keywords[self.stack]))
                        self.add_token(self.stack, 1, self.keywords[self.stack])

                    elif self.stack == "true":
                        tokens.append((5, 1))
                        self.add_token(self.stack, 5, 1)

                    elif self.stack == "false":
                        tokens.append((5, 0))
                        self.add_token(self.stack, 5, 1)

                    elif self.stack in self.separators:
                        tokens.append(2, self.separators[self.stack])
                        self.add_token(self.stack, 2, self.separators[self.stack])

                    else:
                        if not self.stack in identificators:
                            identificators.append(self.stack)
                            self.add_identificator(self.stack, 3, self.stack)

                        tokens.append((3, identificators.index(self.stack)))
                        self.add_token(self.stack, 3, identificators.index(self.stack))

                    tokens.append((2, self.separators["\n"]))
                    self.add_token("\\n", 2, self.separators["\n"])
                    nill()

                    q = self.change_state(q, "H")

                elif chr in self.separators:
                    if self.stack in self.keywords:
                        tokens.append((1, self.keywords[self.stack]))
                        self.add_token(self.stack, 1, self.keywords[self.stack])

                    elif self.stack == "true":
                        tokens.append((5, 1))
                        self.add_token(self.stack, 5, 1)

                    elif self.stack == "false":
                        tokens.append((5, 0))
                        self.add_token(self.stack, 5, 0)

                    elif self.stack in self.separators:
                        tokens.append(2, self.separators[self.stack])
                        self.add_token(self.stack, 2, self.separators[self.stack])

                    else:
                        if not self.stack in identificators:
                            identificators.append(self.stack)
                            self.add_identificator(self.stack, 3, self.stack)

                        tokens.append((3, identificators.index(self.stack)))
                        self.add_token(self.stack, 3, identificators.index(self.stack))

                    nill()
                    add()
                    q = self.change_state(q, "S")

                elif chr in self.vocabilary or chr in self.numbers:
                    add()
                    continue

                elif chr == "&":
                    add()
                    tokens.append((2, self.separators[self.stack]))
                    self.add_token(self.stack, 2, self.separators[self.stack])

                    nill()
                    q = self.change_state(q, "H")

                elif chr in self.separators:
                    if self.stack in self.keywords:
                        tokens.append((1, self.keywords[self.stack]))
                        self.add_token(self.stack, 1, self.keywords[self.stack])

                    else:
                        if not self.stack in identificators:
                            identificators.append(self.stack)
                            self.add_identificator(self.stack, 3, self.stack)

                        tokens.append((3, identificators.index(self.stack)))
                        self.add_token(self.stack, 3, identificators.index(self.stack))

                    nill()
                    add()
                    q = self.change_state(q, "S")

                else:
                    errors.append("Unexcepted char in identificator.")
                    q = "ER"

            elif q == "S":
                if chr == " " or chr == "\n":

                    if self.stack in self.separators:
                        tokens.append((2, self.separators[self.stack]))
                        self.add_token(self.stack, 2, self.separators[self.stack])
                        nill()

                    else:
                        errors.append("Undefined separator.")
                        q = "ER"

                    if chr == "\n":
                        tokens.append((2, self.separators["\n"]))
                        self.add_token("\\n", 2, self.separators["\n"])

                    q = self.change_state(q, "H")

                elif chr in "!=<>&":
                    add()
                    q = self.change_state(q, "SS")

                elif chr == "*":
                    self.look_comment()
                    if self.stack == "(":
                        q = self.change_state(q, "C")

                elif chr in self.separators:
                    if self.stack in self.separators:
                        tokens.append((2, self.separators[self.stack]))
                        self.add_token(self.stack, 2, self.separators[self.stack])

                        nill()
                        add()
                        q = self.change_state(q, "S")

                    else:
                        errors.append(f"Undefined separator {self.stack}.")
                        q = "ER"

                else:
                    if self.stack in self.separators:
                        tokens.append((2, self.separators[self.stack]))
                        self.add_token(self.stack, 2, self.separators[self.stack])
                        nill()

            elif q == "SS":
                if chr in "=&|":
                    add()
                    if self.stack in self.separators:
                        tokens.append((2, self.separators[self.stack]))
                        self.add_token(self.stack, 2, self.separators[self.stack])

                        nill()
                        q = self.change_state(q, "H")

                    else:
                        errors.append(f"Undefined component separator {self.stack}.")
                        q = "ER"

                elif chr == " " or chr == "\n":
                    tokens.append((2, self.separators[self.stack]))
                    self.add_token(self.stack, 2, self.separators[self.stack])

                    if chr == "\n":
                        tokens.append((2, self.separators["\n"]))
                        self.add_token("\\n", 2, self.separators["\n"])

                    nill()

                    q = self.change_state(q, "H")

                else:
                    errors.append(f"Unexcepted char {chr} in component separator.")
                    q = "ER"

            elif q == "C":
                self.skip_comment()
                if chr == ")" and self.stack[-1] == "*":
                    nill()
                    q = self.change_state(q, "H")
                    continue
                add()

            elif q == "N2":
                if chr in self.numbers[:2]:
                    add()

                elif chr in self.numbers[:9]:
                    add()
                    q = self.change_state(q, "N8")

                elif chr in self.numbers:
                    add()
                    q = self.change_state(q, "N10")

                elif chr == ".":
                    add()
                    q = self.change_state(q, "NF")

                elif chr in "Ee":
                    add()
                    q = self.change_state(q, "NFEXP")

                elif chr in "Oo":
                    add()
                    q = self.change_state(q, "N8X")

                elif chr in "Dd":
                    add()
                    q = self.change_state(q, "N10X")

                elif chr in "acfACF":
                    add()
                    q = self.change_state(q, "N16")

                elif chr in "Hh":
                    add()
                    self.change_state(q, "N16X")
                    q = "N16X"

                elif chr in "Bb":
                    add()
                    q = self.change_state(q, "N2X")

                elif chr in [" ", "\n"]:
                    num = int(self.stack)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                    self.add_number(num, nid)

                    tokens.append((4, nid))
                    self.add_token(self.stack, 4, nid)

                    nill()

                    if chr == "\n":
                        tokens.append((2, self.separators["\n"]))
                        self.add_token("\\n", 2, self.separators["\n"])

                    q = self.change_state(q, "H")

                elif chr in self.separators:
                    num = int(self.stack)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                        self.add_number(num, nid)

                    tokens.append((4, nid))
                    self.add_token(num, 4, nid)

                    nill()
                    add()
                    q = self.change_state(q, "S")

                else:
                    nill()
                    errors.append(f"Unexcepted char {chr} in binary number.")
                    q = "ER"

            elif q == "N2X":
                if chr in "abcdefABCDEF" or chr in self.numbers:
                    add()
                    q = self.change_state(q, "N16")

                elif chr in "Hh":
                    add()
                    q = self.change_state(q, "N16X")

                elif chr in [" ", "\n"]:
                    num = int(self.stack[:-1], 2)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                        self.add_number(num, nid)

                    tokens.append((4, nid))
                    self.add_token(num, 4, nid)

                    nill()

                    if chr == "\n":
                        tokens.append((2, self.separators["\n"]))
                        self.add_token("\\n", 2, self.separators[self.stack])

                    q = self.change_state(q, "H")

                elif chr in self.separators:
                    num = int(self.stack[:-1], 2)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                        self.add_number(num, nid)

                    tokens.append((4, nid))
                    self.add_token(num, 4, nid)

                    nill()
                    add()
                    q = self.change_state(q, "S")

                else:
                    nill()
                    errors.append(f"Unexcepted char {chr} in binary number.")
                    q = "ER"

            elif q == "N8":
                if chr in self.numbers[:9]:
                    add()
                    q = self.change_state(q, "N8")

                elif chr in self.numbers[:10]:
                    add()
                    q = self.change_state(q, "N10")

                elif chr == ".":
                    add()
                    q = self.change_state(q, "NF")

                elif chr in "Ee":
                    add()
                    q = self.change_state(q, "NEXP")

                elif chr in "Dd":
                    add()
                    q = self.change_state(q, "N10X")

                elif chr in "abcfABCF":
                    add()
                    q = self.change_state(q, "N16")

                elif chr in "Hh":
                    add()
                    q = self.change_state(q, "N16X")

                elif chr in "Oo":
                    add()
                    q = self.change_state(q, "N8X")

                elif chr in [" ", "\n"]:
                    num = int(self.stack)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                        self.add_number(num, nid)

                    tokens.append((4, nid))
                    self.add_token(num, 4, nid)

                    nill()

                    if chr == "\n":
                        tokens.append((2, self.separators["\n"]))
                        self.add_token("\\n", 2, self.separators["\n"])

                    q = self.change_state(q, "H")

                elif chr in self.separators:
                    num = int(self.stack)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                        self.add_number(num, nid)

                    tokens.append((4, nid))
                    self.add_token(num, 4, nid)

                    nill()
                    add()
                    q = self.change_state(q, "S")

                else:
                    errors.append(f"Unexcepted char {chr} in O-number.")
                    q = "ER"

            elif q == "N8X":
                if chr in [" ", "\n"]:
                    num = int(self.stack[:-1], 8)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                        self.add_number(num, nid)

                    tokens.append((4, nid))
                    self.add_token(num, 4, nid)

                    if chr == "\n":
                        tokens.append((2, self.separators["\n"]))
                        self.add_token("\\n", 2, self.separators[self.stack])

                    nill()
                    q = self.change_state(q, "H")

                elif chr in self.separators:
                    num = int(self.stack[:-1], 8)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                        self.add_number(num, nid)

                    tokens.append((4, nid))
                    self.add_token(num, 4, nid)

                    nill()
                    add()
                    q = self.change_state(q, "S")

                else:
                    errors.append(f"Unexcepted char {chr} in binary number.")
                    q = "ER"

            elif q == "N10":
                if chr in self.numbers[:10]:
                    add()

                elif chr == ".":
                    add()
                    q = self.change_state(q, "NF")

                elif chr in "Ee":
                    add()
                    q = self.change_state(q, "NEXP")

                elif chr in "Dd":
                    add()
                    q = self.change_state(q, "N10X")

                elif chr in "abcfABCF":
                    add()
                    q = self.change_state(q, "N16")

                elif chr in "Hh":
                    add()
                    q = self.change_state(q, "N16X")

                elif chr in "Dd":
                    add()
                    q = self.change_state(q, "N10X")

                elif chr in [" ", "\n"]:
                    num = int(self.stack)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                        self.add_number(num, nid)

                    tokens.append((4, nid))
                    self.add_token(num, 4, nid)

                    if chr == "\n":
                        tokens.append((2, self.separators["\n"]))
                        self.add_token("\\n", 2, self.separators["\n"])

                    nill()
                    q = self.change_state(q, "H")

                elif chr in self.separators:
                    num = int(self.stack)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                        self.add_number(num, nid)

                    tokens.append((4, nid))
                    self.add_token(num, 4, nid)

                    nill()
                    add()
                    q = self.change_state(q, "S")

                else:
                    errors.append(f"Unexcepted char {chr} in D-number.")
                    q = "ER"

            elif q == "N10X":
                if chr in "abcdefABCDEF":
                    add()
                    q = self.change_state(q, "N16")

                elif chr in "Hh":
                    add()
                    self.change_state(q, "N16X")
                    q = "N16X"

                elif chr in [" ", "\n"]:
                    num = int(self.stack[:-1])
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                        self.add_number(num, nid)

                    tokens.append((4, nid))
                    self.add_token(num, 4, nid)

                    if chr == "\n":
                        tokens.append((2, self.separators["\n"]))
                        self.add_token("\\n", 2, self.separators[self.stack])

                    nill()
                    q = self.change_state(q, "H")

                elif chr in self.separators:
                    num = int(self.stack[:-1])
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                        self.add_number(num, nid)

                    tokens.append((4, nid))
                    self.add_token(num, 4, nid)

                    nill()
                    add()
                    q = self.change_state(q, "S")

                else:
                    errors.append(f"Unexcepted char {chr} in D-number.")
                    q = "ER"

            elif q == "N16":
                if chr in self.numbers or chr in "abcdefABCDEF":
                    add()

                elif chr in "hH":
                    add()
                    q = self.change_state(q, "N16X")

                else:
                    errors.append(f"Unexcepted char {chr} in H-number.")
                    q = "ER"

            elif q == "N16X":
                if chr in [" ", "\n"]:
                    num = int(self.stack[:-1], 16)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                        self.add_number(num, nid)

                    tokens.append((4, nid))
                    self.add_token(num, 4, nid)

                    if chr == "\n":
                        tokens.append((2, self.separators["\n"]))
                        self.add_token("\\n", 2, self.separators["\n"])

                    nill()
                    q = self.change_state(q, "H")

                elif chr in self.separators:
                    num = int(self.stack[:-1], 16)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                        self.add_number(num, nid)

                    tokens.append((4, nid))
                    self.add_token(num, 4, nid)

                    nill()
                    add()
                    q = self.change_state(q, "S")

                else:
                    errors.append(f"Unexcepted char {chr} in H-number.")
                    q = "ER"

            elif q == "NF":
                if chr in self.numbers:
                    add()
                    q = self.change_state(q, "NFX")

                else:
                    errors.append(f"Unexcepted char {chr} in float number.")
                    q = "ER"

            elif q == "NFX":
                if chr in "Ee":
                    add()
                    q = self.change_state(q, "NFEXP")

                elif chr in self.numbers:
                    add()

                elif chr in [" ", "\n"]:
                    num = float(self.stack)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Float", num))
                        nid = self.in_table(num, numbers)
                        self.add_number(num, nid)

                    tokens.append((4, nid))
                    self.add_token(num, 4, nid)

                    if chr == "\n":
                        tokens.append((2, self.separators["\n"]))
                        self.add_token("\\n", 2, self.separators[self.stack])

                    nill()
                    q = self.change_state(q, "H")

                elif chr in self.separators:
                    num = float(self.stack)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Float", num))
                        nid = self.in_table(num, numbers)
                        self.add_number(num, nid)

                    tokens.append((4, nid))
                    self.add_token(num, 4, nid)

                    nill()
                    add()
                    q = self.change_state()

                else:
                    errors.append(f"Unexcepted char {chr} in float number.")
                    q = "ER"

            elif q == "NFEXP":
                add()

                if chr in "+-":
                    q = self.change_state(q, "NFEXPZ")

                elif chr in self.numbers:
                    q = self.change_state(q, "NFEXPX")

                else:
                    errors.append(f"Unexcepted char {chr} in exp number.")
                    q = "ER"

            elif q == "NFEXPZ":
                if chr in self.numbers:
                    add()
                    q = self.change_state(q, "NFEXPX")

                else:
                    errors.append(f"Unexcepted char {chr} in exp-float number.")
                    q = "ER"

            elif q == "NFEXPX":
                if chr in self.numbers:
                    add()

                elif chr in [" ", "\n"]:
                    num = self.fexp_to_float(self.stack)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Float", num))
                        nid = self.in_table(num, numbers)
                        self.add_number(num, nid)

                    tokens.append((4, nid))
                    self.add_token(num, 4, nid)

                    if chr == "\n":
                        tokens.append((2, self.separators["\n"]))
                        self.add_token("\\n", 2, self.separators["\n"])

                    nill()
                    q = self.change_state(q, "H")

                elif chr in self.separators:
                    num = self.fexp_to_float(self.stack)
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Float", num))
                        nid = self.in_table(num, numbers)
                        self.add_number(num, nid)

                    tokens.append((4, nid))
                    self.add_token(num, 4, nid)

                    nill()
                    add()
                    q = self.change_state(q, "S")

                else:
                    errors.append(f"Unexcepted char {chr} in exp-float number.")
                    q = "ER"

            elif q == "NEXP":
                add()

                if chr in self.numbers:
                    q = self.change_state(q, "NEXPX")

                elif chr in "+-":
                    q = self.change_state(q, "NEXPZ")

                elif chr in "abcdfABCDF":
                    q = self.change_state(q, "N16")

                elif chr in "Hh":
                    q = self.change_state(q, "N16X")

                else:
                    errors.append(f"Unexcepted char {chr} in exp number.")
                    q = "ER"

            elif q == "NEXPX":
                if chr in self.numbers:
                    add()

                elif chr in "abcdfABCDF":
                    add()
                    q = self.change_state(q, "N16")

                elif chr in "Hh":
                    add()
                    q = self.change_state(q, "N16X")

                elif chr in [" ", "\n"]:
                    num = int(self.fexp_to_float(self.stack))
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                        self.add_number(num, nid)

                    tokens.append((4, nid))
                    self.add_token(num, 4, nid)

                    if chr == "\n":
                        tokens.append((2, self.separators["\n"]))
                        self.add_token("\\n", 2, self.separators[self.stack])

                    nill()
                    q = self.change_state(q, "H")

                elif chr in self.separators:
                    num = int(self.fexp_to_float(self.stack))
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                        self.add_number(num, nid)

                    tokens.append((4, nid))
                    self.add_token(num, 4, nid)

                    nill()
                    add()
                    q = self.change_state(q, "S")

                else:
                    errors.append(f"Unexcepted char {chr} in exp number.")
                    q = "ER"

            elif q == "NEXPZ":
                if chr in self.numbers:
                    add()
                    q = self.change_state(q, "NEXPZX")

                else:
                    errors.append(f"Unexcepted char {chr} in exp number.")
                    q = "ER"

            elif q == "NEXPZX":
                if chr in self.numbers:
                    add()

                elif chr in [" ", "\n"]:
                    num = int(self.fexp_to_float(self.stack))
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                        self.add_number(num, nid)

                    tokens.append((4, nid))
                    self.add_token(num, 4, nid)

                    if chr == "\n":
                        tokens.append((2, self.separators["\n"]))
                        self.add_token("\\n", 2, self.separators)

                    nill()
                    q = self.change_state(q, "H")

                elif chr in self.separators:
                    num = int(self.fexp_to_float(self.stack))
                    nid = self.in_table(num, numbers)
                    if nid is False:
                        numbers.append(("Integer", num))
                        nid = self.in_table(num, numbers)
                        self.add_number(num, nid)

                    tokens.append((4, nid))
                    self.add_token(num, 4, nid)

                    nill()
                    add()
                    q = self.change_state(q, "S")

                else:
                    errors.append(f"Unexcepted char {chr} in binary number.")
                    q = "ER"

            if not chr:
                if tokens[-1] == (2, self.separators["\n"]):
                    tokens.pop(-1)
                break

        self.write_tokens(tokens, numbers, identificators, errors)

        return tokens, numbers, identificators, errors
