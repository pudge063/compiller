class Parser:
    """
    Функция синтаксического анализатора. Вход: файл лексем,
    выход - заключение о правильности грамматики или сообщения об ошибках.

    <программа>::= begin var <описание> {; <оператор>} end
    <оператор>::= <составной> | <присваивания> | <условный> | <фиксированного_цикла> | <условного_цикла> | <ввода> | <вывода>
    <описание>::= dim <идентификатор> {, <идентификатор> } <тип>
    <тип>::=# | @ | &
    <составной>::=«[» <оператор> { ( : | перевод строки) <оператор>} «]»
    <присваивания>::= <идентификатор> assign <выражение>
    <условный>::= if <выражение> then <оператор> [else <оператор>] end
    <фиксированного_цикла>::= for <присваивания> val <выражение> do <оператор>
    <условного_цикла>::= while <выражение> do <оператор>next
    <ввода>::= enter <идентификатор> {пробел <идентификатор> }
    <вывода>::= displ <выражение> {, <выражение> }
    """

    def __init__(self, debug):

        self.init_tokens()
        self.init_tables()
        self.init_colors()
        self.debug = debug

        self.current_index = 0

    def init_tokens(self):
        import json

        with open("lexer_output.json", "r", encoding="utf-8") as file:
            lexer_output = json.load(file)

        self.tokens = lexer_output["tokens"]
        self.numbers = lexer_output["numbers"]
        self.identificators = lexer_output["identificators"]
        self.errors = lexer_output["errors"]

    def init_tables(self):
        from core.parser.tables import keywords, separators

        self.keywords = keywords
        self.separators = separators

    def init_colors(self):
        from core.helpers import Helpers

        helper = Helpers()

        self.print_red = helper.print_red
        self.print_cyan = helper.print_cyan
        self.print_magenta = helper.print_magenta
        self.print_yellow = helper.print_yellow
        self.print_black = helper.print_black

    def current_token(self):
        ct = (
            self.tokens[self.current_index]
            if self.current_index < len(self.tokens)
            else None
        )
        if self.debug:
            print("Current token: ", ct)

        return ct

    def next_token(self):
        if self.debug:
            self.print_black("Next token.")

        self.current_index += 1
        return self.current_token()

    def is_identificator(self):
        if self.current_token()[0] == 3:
            return True
        return False

    def skip_enter(self):
        if self.debug:
            self.print_black("Skip enter.")

        if self.current_token() == [2, self.separators["\n"]]:
            self.next_token()

    def parse_begin(self):
        if self.debug:
            self.print_yellow("Parse 'begin'.")

        if not self.current_token() == [1, self.keywords["begin"]]:
            raise SyntaxError("Excepted 'begin'.")

    def parse_end(self):
        if self.debug:
            self.print_yellow("Parse 'end'.")

        if self.current_token() == [1, self.keywords["end"]]:
            self.next_token()
            self.skip_enter()
            if self.current_token():
                raise SyntaxError("Unexcepted token after 'end'.")
            else:
                self.print_cyan("\nEnd syntax analyzer.\n")
        else:
            raise SyntaxError("Excepted 'end'.")

    def parse_var(self):
        if self.debug:
            self.print_yellow("Parse 'var'.")

        self.next_token()
        self.skip_enter()
        if self.current_token() == [1, self.keywords["var"]]:
            self.next_token()
            if self.current_token() == [1, self.keywords["dim"]]:
                self.next_token()
                if not self.is_identificator():
                    raise SyntaxError("Excepted identificator.")
                self.next_token()
                self.parse_identificator()
            else:
                raise SyntaxError("Excepted 'dim'.")
        else:
            raise SyntaxError("Excepted 'var'.")

    def parse_identificator(self):
        if self.debug:
            self.print_yellow("Parse identificator.")

        while True:
            if self.current_token() == [2, self.separators[","]]:
                self.next_token()
                if self.is_identificator():
                    self.next_token()
                else:
                    raise SyntaxError("Excepted next identificator.")
            elif self.current_token()[0] == 1 and (
                self.current_token()[1] == self.keywords["#"]
                or self.current_token()[1] == self.keywords["@"]
                or self.current_token()[1] == self.keywords["&"]
            ):
                self.next_token()
                break
            else:
                raise SyntaxError("Excepted identificator type.")

    def parse_operator(self):
        if self.debug:
            self.print_yellow(f"Parse operator. {self.current_token()}")

        if self.current_token() == [2, self.separators["["]]:
            self.next_token()
            self.parse_component_operator()

        elif self.is_identificator():
            self.next_token()
            self.parse_assign_operator()

        else:
            raise SyntaxError("Excepted operator.")

    def parse_component_operator(self):
        if self.debug:
            self.print_yellow("Parse component operator.")

        self.parse_operator()

        while True:
            if self.current_token() == [2, self.separators["]"]]:
                if self.debug:
                    print("].")

                self.next_token()
                break

            elif self.current_token() == [
                2,
                self.separators[":"],
            ] or self.current_token() == [2, self.separators["\n"]]:
                if self.debug:
                    print(": or \\n.")

                self.next_token()
                self.parse_operator()

            else:
                raise SyntaxError("Excepted ']' in component operator.")

    def parse_assign_operator(self):
        if self.debug:
            self.print_yellow(f"Parse assign operator. {self.current_token()}")

        if self.current_token() == [1, self.keywords["assign"]]:
            self.next_token()
            if self.current_token()[0] == 4:
                self.next_token()
            else:
                raise SyntaxError("Excepted value to assign.")
        else:
            raise SyntaxError("Excepted assign operator.")

    def parse_program(self):
        if self.debug:
            self.print_cyan("Start syntax analyzer.\n")

        self.parse_begin()

        self.parse_var()

        while True:
            if self.current_token() == [2, self.separators[";"]]:
                self.next_token()
                self.skip_enter()
                self.parse_operator()
            else:
                self.skip_enter()
                break

        self.parse_end()
