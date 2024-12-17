from core.lexer.tables import separators
from core.semant.semant import SemanticAnalyzer


# from core.semant.semant import SemanticAnalyzer


class Parser:
    """
    Функция синтаксического анализатора. Вход: файл лексем,
    выход - заключение о правильности грамматики или сообщения об ошибках.

    <программа>::= begin var <описание> {; <оператор>} end
    <оператор>::= <составной> | <присваивания> | <условный>
    |<фиксированного_цикла> | <условного_цикла> | <ввода> | <вывода>
    <описание>::= dim <идентификатор> {, <идентификатор> } <тип>
    <тип>::= # | @ | &
    <составной>::= «[» <оператор> { ( : | перевод строки) <оператор>} «]»
    <присваивания>::= <идентификатор> assign <выражение>
    <условный>::= if <выражение> then <оператор> [else <оператор>] end
    <фиксированного_цикла>::= for <присваивания> val <выражение> do <оператор>
    <условного_цикла>::= while <выражение> do <оператор>next
    <ввода>::= enter <идентификатор> {пробел <идентификатор> }
    <вывода>::= displ <выражение> {, <выражение> }
    """

    def __init__(self, debug):
        self.current_var = None
        self.declare_var_list = {}
        self.symbol_table = {}
        self.semantic = SemanticAnalyzer()
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
        # self.print_black = helper.print_black
        self.print_black = helper.print_yellow

    def current_token(self):
        ct = (
            self.tokens[self.current_index]
            if self.current_index < len(self.tokens)
            else None
        )

        if self.debug:
            readable = self.get_readable_token(ct)  # Преобразуем в читаемый формат
            self.print_cyan(f"Current token ({ct, readable}")

        return ct

    def get_readable_token(self, token):
        if not token:
            return "EOF"  # End of File

        token_type, token_value = token

        if token_type == 1:  # Ключевые слова
            for k, v in self.keywords.items():
                if v == token_value:
                    return k

        elif token_type == 2:  # Разделители
            for k, v in self.separators.items():
                if v == token_value:
                    return k

        elif token_type == 3:  # Идентификаторы
            return self.identificators[token_value]

        elif token_type == 4:  # Числа
            return self.numbers[token_value]

        elif token_type == 5:  # Логические значения
            return token_value

        return f"UNKNOWN({token})"

    def next_token(self):
        if self.debug:
            self.print_black("Next token")

        self.current_index += 1
        while self.current_token() == [2, self.separators["\n"]]:
            self.skip_enter()
        return self.current_token()

    def is_identificator(self):
        if self.current_token()[0] == 3:
            return True
        return False

    def is_bool(self):
        if self.current_token()[0] == 5:
            return True
        return False

    def is_number(self):
        if self.current_token()[0] == 4:
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
        self.next_token()

    def get_separator_by_value(self, value):
        for key, val in separators.items():
            if val == value:
                return key
        return None  # Если значение не найдено

    def parse_end(self):
        if self.debug:
            self.print_yellow("Parse 'end'.")

        number = self.current_token()[1]

        if self.current_token() == [1, self.keywords["end"]]:
            self.next_token()
            self.skip_enter()
            if self.current_token():
                raise SyntaxError("Unexcepted token after 'end'.")
            else:
                self.print_cyan("\nEnd syntax analyzer.\n")
        else:
            raise SyntaxError("Excepted 'end'.")

    # < описание >: := dim < идентификатор > {, < идентификатор >} < тип >
    def parse_var(self):
        if self.debug:
            self.print_yellow("Parsing 'var'...")

        if not self.current_token() == [1, self.keywords["var"]]:  # Проверка ключевого слова 'var'
            raise SyntaxError("Expected 'var'.")
        self.next_token()

        if not self.current_token() == [1, self.keywords["dim"]]:  # Проверка ключевого слова 'dim'
            raise SyntaxError("Expected 'dim'.")
        self.next_token()

        var_name = self.identificators[self.current_token()[1]]
        if not self.is_identificator():  # Первый идентификатор
            raise SyntaxError("Expected identifier.")
        self.semantic.add_variable(var_name)
        self.next_token()
        self.parse_identificator()  # Разбор списка идентификаторов
        # Следующий токен должен быть тип (например, #, @, &)
        if (self.current_token() and self.current_token()[0] == 1
                and self.current_token()[1] in [
                    self.keywords["#"],
                    self.keywords["@"],
                    self.keywords["&"]
                ]):
            ct = (
                self.tokens[self.current_index]
                if self.current_index < len(self.tokens)
                else None
            )
            value = self.get_readable_token(ct)
            varies = self.semantic.variables
            for var in varies:
                self.semantic.set_variable_type(var,value)
            self.next_token()
        else:
            raise SyntaxError("Expected identifier's type (#, @, &).")

    # < выражение >: := < операнд > { < операции_группы_отношения > < операнд >}
    def parse_expression(self):
        if self.debug:
            self.print_yellow(f"Parse expression: {self.current_token()}")

        self.parse_operand()  # Разбираем первый операнд

        while self.current_token() and self.current_token()[0] == 2:  # Операторы отношений
            op = self.current_token()[1]
            if op in [self.separators["<"], self.separators["="], self.separators[">"],
                      self.separators["<="], self.separators["!="],self.separators[">="]]:
                self.next_token()
                self.parse_operand()  # Разбираем следующий операнд
            else:
                break

    # < операнд >: := < слагаемое > { < операции_группы_сложения > < слагаемое >}
    def parse_operand(self):
        if self.debug:
            self.print_yellow(f"Parse operand: {self.current_token()}")

        self.parse_summand()  # Разбираем первое слагаемое

        while self.current_token() and self.current_token()[0] == 2:  # Операции сложения
            op = self.current_token()[1]
            if op in [self.separators["+"], self.separators["-"]]:
                self.next_token()
                self.parse_summand()  # Разбираем следующее слагаемое
            else:
                break

    # <слагаемое> ::= <множитель> {<операции_группы_умножения> <множитель>}
    def parse_summand(self):
        if self.debug:
            self.print_yellow(f"Parse summand: {self.current_token()}")

        self.parse_factor()  # Разбираем первый множитель

        while self.current_token() and self.current_token()[0] == 2:  # Операции умножения/деления
            op = self.current_token()[1]
            if op in [self.separators["*"], self.separators["/"]]:
                self.next_token()
                self.parse_factor()  # Разбираем следующий множитель
            else:
                break

    # < множитель >: := < идентификатор > | < число > | < логическая_константа >
    # | < унарная_операция > < множитель > | (< выражение >)
    def parse_factor(self):
        if self.debug:
            self.print_yellow(f"Parse factor: {self.current_token()}")
        ct = (
            self.tokens[self.current_index]
            if self.current_index < len(self.tokens)
            else None
        )
        value = self.get_readable_token(ct)
        # varies = self.semantic.variables

        if self.is_identificator():  # Идентификатор
            self.semantic.initialize_variable(self.current_var,value)
            self.next_token()

        elif self.is_number():  # Число
            self.next_token()

        elif self.is_bool():
            self.next_token()

        elif self.current_token() and self.current_token()[1] == self.separators["!"]:  # Унарная операция "!"
            self.next_token()
            self.parse_factor()  # Разбираем операнд унарного оператора

        elif self.current_token() and self.current_token()[1] == self.separators["-"]:  # Унарная операция "-"
            self.next_token()
            self.parse_factor()

        elif self.current_token() and self.current_token()[1] == self.separators["("]:  # Скобки вокруг выражения
            self.next_token()
            self.parse_expression()  # Разбираем внутреннее выражение
            if not self.current_token() or self.current_token()[1] != self.separators[")"]:
                raise SyntaxError("Expected closing ')'")
            self.next_token()  # Пропускаем ')'

        else:  # Если ничего не подходит
            raise SyntaxError("Expected factor.")

    # < идентификатор >: := < буква > { < буква > | < цифра >}
    def parse_identificator(self):
        if self.debug:
            self.print_yellow("Parsing identifiers...")

        while True:
            if self.current_token() == [2, self.separators[","]]:  # Запятая
                self.next_token()
                var_name = self.identificators[self.current_token()[1]]
                if self.is_identificator():
                    # self.semantic.is_declared(var_name)
                    # self.semantic.add_variable(var_name)
                    self.next_token()
                else:
                    raise SyntaxError("Expected identifier after ','.")
            else:
                break
    # <оператор>::= <составной> | <присваивания> | <условный> |
    #           <фиксированного_цикла> | <условного_цикла> | <ввода> | <вывода>
    def parse_operator(self):
        if self.debug:
            self.print_yellow(f"Parse operator. {self.current_token()}")
        ct = (
            self.tokens[self.current_index]
            if self.current_index < len(self.tokens)
            else None
            )
        value = self.get_readable_token(ct)
        # varies = self.semantic.variables
        if self.current_token() == [2, self.separators["["]]:
            self.next_token()
            self.parse_component_operator()
        elif self.is_identificator():
            self.current_var = value

            self.next_token()
            print("operator:")
            print(self.tokens[self.current_index])

            if self.tokens[self.current_index] == [1, self.keywords["assign"]]: #ЗДЕСЬ
                self.parse_assign_operator()
            else:self.parse_summand()
        elif self.current_token() == [1, self.keywords["if"]]:
            self.parse_conditional_operator()
        elif self.current_token() == [1, self.keywords["for"]]:
            self.parse_for_loop()
        elif self.current_token() == [1, self.keywords["while"]]:
            self.parse_while_loop()
        elif self.current_token() == [1, self.keywords["enter"]]:
            self.parse_input_operator()
        elif self.current_token() == [1, self.keywords["displ"]]:
            self.parse_output_operator()
        else:
            raise SyntaxError("Expected operator.")

    # <условный>::= if <выражение> then <оператор> [else <оператор>] end
    def parse_conditional_operator(self):
        if self.debug:
            self.print_yellow(f"Parse conditional operator. {self.current_token()}")
        if self.current_token() == [1, self.keywords["if"]]:
            self.next_token()
            self.parse_expression()  # Разбор условия
            if self.current_token() != [1, self.keywords["then"]]:
                raise SyntaxError("Expected 'then' after 'if'.")
            self.next_token()
            self.parse_operator()  # Разбор оператора в блоке `then`
            if self.current_token() == [1, self.keywords["else"]]:  # Проверка наличия `else`
                self.next_token()
                self.parse_operator()  # Разбор оператора в блоке `else`
            if self.current_token() != [1, self.keywords["end"]]:
                raise SyntaxError("Expected 'end' to close conditional block.")
            self.next_token()
        else:
            raise SyntaxError("Expected 'if'.")

    # <фиксированного_цикла>::= for <присваивания> val <выражение> do <оператор>
    def parse_for_loop(self):
        if self.debug:
            self.print_yellow(f"Parse for loop. {self.current_token()}")
        if self.current_token() == [1, self.keywords["for"]]:
            self.next_token()
            self.parse_operator()
            self.parse_assign_operator()  # Разбор присваивания начального значения
            if self.current_token() != [1, self.keywords["val"]]:
                raise SyntaxError("Expected 'val' in 'for' loop.")
            self.next_token()
            self.parse_expression()  # Разбор конечного значения
            if self.current_token() != [1, self.keywords["do"]]:
                raise SyntaxError("Expected 'do' in 'for' loop.")
            self.next_token()
            self.parse_operator()  # Разбор тела цикла
        else:
            raise SyntaxError("Expected 'for'.")

    # < условного_цикла >: := while < выражение > do < оператор > next
    def parse_while_loop(self):
        if self.debug:
            self.print_yellow(f"Parse while loop. {self.current_token()}")
        if self.current_token() == [1, self.keywords["while"]]:
            self.next_token()
            self.parse_expression()  # Разбор условия
            if self.current_token() != [1, self.keywords["do"]]:
                raise SyntaxError("Expected 'do' in 'while' loop.")
            self.next_token()
            self.parse_operator()  # Разбор тела цикла
            if self.current_token() != [1, self.keywords["next"]]:
                raise SyntaxError("Expected 'next' to close 'while' loop.")
            self.next_token()
        else:
            raise SyntaxError("Expected 'while'.")

    # <ввода>::= enter <идентификатор> { пробел <идентификатор> }
    def parse_input_operator(self):
        if self.debug:
            self.print_yellow(f"Parse input operator. {self.current_token()}")
        if self.current_token() == [1, self.keywords["enter"]]:
            self.next_token()
            if not self.is_identificator():
                raise SyntaxError("Expected identifier after 'enter'.")
            while self.is_identificator():  # Поддержка нескольких идентификаторов
                self.next_token()
                if self.current_token() == [2, " "]:  # Разделение пробелами
                    self.next_token()
        else:
            raise SyntaxError("Expected 'enter'.")

    # <вывода>::= displ <выражение> {, <выражение>}
    def parse_output_operator(self):
        if self.debug:
            self.print_yellow(f"Parse output operator. {self.current_token()}")
        if self.current_token() == [1, self.keywords["displ"]]:
            self.next_token()
            self.parse_expression()  # Разбор первого выражения
            while self.current_token() == [2, self.separators[","]]:  # Поддержка нескольких выражений через запятую
                self.next_token()
                self.parse_expression()
        else:
            raise SyntaxError("Expected 'displ'.")

    # <составной>::= «[» <оператор> { ( : | перевод строки) <оператор>} «]»
    def parse_component_operator(self):
        if self.debug:
            self.print_yellow("Parse component operator.")

        self.parse_operator()

        while True:
            if self.current_token() == [2, self.separators["]"]]:
                if self.debug:
                    print("[.")

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

    # < присваивания >: := < идентификатор > assign < выражение >
    def parse_assign_operator(self):
        if self.debug:
            self.print_yellow("Parse component assign operator.")

        if self.current_token() == [1, self.keywords["assign"]]:
            self.next_token()
            self.parse_factor()

        else:
            raise SyntaxError("Excepted assign operator.")

    # <слагаемое>::= <множитель> {<операции_группы_умножения> <множитель>}
    def parse_term(self):
        self.parse_factor()
        self.next_token()
        if self.current_token()[0] == 2 and (self.current_token()[1] in ["*", "/"]):
            self.parse_factor()

    # <программа>::= begin var <описание> {; <оператор>} end
    def parse_program(self):
        if self.debug:
            self.print_cyan("Start syntax analyzer.\n")

        self.parse_begin()
        self.parse_var()

        # print(self.current_token(),[1,self.keywords["end"]])
        while self.current_token() and self.current_token() != [1, self.keywords["end"]]:
            if self.current_token() == [2, self.separators[";"]]:
                self.next_token()
                self.skip_enter()
            else:
                self.parse_operator()

        self.parse_end()
