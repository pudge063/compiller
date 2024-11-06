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

    def __init__(self):
        self.init_tokens()
        self.init_tables()

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

    current_index = 0

    def current_token(self):
        return (
            self.tokens[self.current_index]
            if self.current_index < len(self.tokens)
            else None
        )

    def next_token(self):
        global current_index
        self.current_index += 1
        return self.current_token()

    def is_identificator(self):
        if self.current_token()[0] == 3:
            return True
        return False

    def skip_enter(self):
        if self.current_token() == [2, self.separators["\n"]]:
            self.next_token()

    def parse_program(self):
        """
        Основная функция парсера, запускает парсинг программы.
        Сначала проверяется первый токен begin, затем запускается парсинг тела программы.
        Потом проверяется последний токен на end.
        Выводятся ошибки, если токены не соответствуют ожидаемым значениям.

        <программа>::= begin var <описание> {; <оператор>} end
        """
        # parsing begin
        if self.current_token() == [1, self.keywords["begin"]]:
            self.next_token()
            if self.current_token() == [2, self.separators["\n"]]:
                self.next_token()
            else:
                raise SyntaxError("Excepted \\n after 'begin'.")

            # parsing var
            if self.current_token() == [1, self.keywords["var"]]:
                self.next_token()
                self.parse_initialization()
            else:
                raise SyntaxError("Excepted initialization variables.")

            self.skip_enter()

            if self.current_token() == [1, self.keywords["end"]]:
                if self.next_token():
                    if self.next_token() == [2, self.separators["\n"]]:
                        self.next_token()
                    if self.current_token():
                        raise SyntaxError("Unexcepted token after 'end'.")
                else:
                    print("Program parsed successfully.")
            else:
                raise SyntaxError("Expected 'end'.")
        else:
            raise SyntaxError("Excepted 'begin'.")

    def parse_initialization(self):
        """
        Инициализация переменных для правила:
        <описание>::= dim <идентификатор> {, <идентификатор> } <тип>
        """

        if self.current_token() == [1, self.keywords["dim"]]:
            self.next_token()
            self.parse_initialization_identificators()
        else:
            raise SyntaxError("Excepted dim.")

    def parse_initialization_identificators(self):

        if self.is_identificator():

            self.next_token()

            if self.current_token() == [2, self.separators[","]]:
                self.next_token()
                self.parse_initialization_identificators()

            elif self.current_token()[0] == 1 and (
                self.current_token()[1] == self.keywords["&"]
                or self.current_token()[1] == self.keywords["@"]
                or self.current_token()[1] == self.keywords["#"]
            ):
                self.next_token()
                if self.current_token() == [2, self.separators[";"]]:
                    self.parse_operator()
            else:
                raise SyntaxError("Excepted variable type.")
        else:
            raise SyntaxError("Excepted identificator.")

    def parse_operator(self):
        self.next_token()
        self.skip_enter()
        print("Parse operator", self.current_token())

        if self.current_token() == [2, self.separators["["]]:
            self.parse_component_operator()

        elif self.current_token() == [2, self.separators["\n"]]:
            pass

        elif self.current_token() == [2, self.separators["]"]]:
            pass

        elif self.current_token()[0] == 3:
            self.parse_assign()

        elif self.current_token() == [1, self.keywords["if"]]:
            pass

        elif self.current_token() == [1, self.keywords["for"]]:
            pass

        elif self.current_token() == [1, self.keywords["while"]]:
            pass

        elif self.current_token() == [1, self.keywords["enter"]]:
            pass

        elif self.current_token() == [1, self.keywords["displ"]]:
            pass

        else:
            raise SyntaxError("Excepted operator.")

    def parse_component_operator(self):
        self.skip_enter()
        print("Parse component operator", self.current_token())
        self.parse_operator()

        while True:
            self.next_token()
            print(self.current_token())

            if self.current_token() == [2, self.separators["]"]]:
                break

            elif self.current_token()[0] == 2 and (
                self.current_token()[1] in [self.separators[":"], self.separators["\n"]]
            ):
                self.parse_operator()

    def parse_assign(self):
        print("Parse assign operator", self.current_token())
        self.next_token()
        if self.current_token() == [1, self.keywords["assign"]]:
            self.next_token()
            if not self.current_token()[0] == 4:
                raise SyntaxError("Excepted value.")
        else:
            raise SyntaxError("Excepted assign keyword.")
