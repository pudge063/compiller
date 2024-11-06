class Manager:
    def start_compile(self, file: str = "test1.txt", debug: str = False):
        from core.lexer.la import Lexer
        from core.helpers import Helpers

        lexer = Lexer(file, debug)
        helpers = Helpers()

        helpers.print_cyan("Start lexer analyzer.\n")

        tokens, numbers, identificators, errors = lexer.tokenize()

        if len(errors) == 0:
            helpers.print_cyan("\nTokens:")
            print(tokens, "\n")

            helpers.print_cyan("Numbers:")
            print(numbers, "\n")

            helpers.print_cyan("Identificators:")
            print(identificators, "\n")

            helpers.print_cyan("End lexer analyzer.\n")

            helpers.print_magenta("Lexer OK!\n")

            return True

        else:
            helpers.print_red(f"Error in lexer: {errors[0]}\n")

        return False

    def start_parser(self, debug: str = False):
        from core.parser.syntax import Parser
        from core.helpers import Helpers

        helpers = Helpers()

        parser = Parser(debug)

        try:
            parser.parse_program()
            helpers.print_magenta("Syntax analyzer OK!\n")
            return True
        except Exception as e:
            helpers.print_red(f"Syntax error: {e}\n")

        return False

    def start_semantic_analyzer(self):
        pass
