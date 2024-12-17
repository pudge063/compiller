# from core.semant.semant import SemanticAnalyzer
from core.helpers import Helpers




class Manager:
    def __init__(self):
        self.tokens = {}
        self.numbers = {}
        self.ident = {}

    def start_compile(self, file: str = "test1.txt", debug: str = False):
        from core.lexer.la import Lexer

        lexer = Lexer(file, debug)
        helpers = Helpers()

        helpers.print_cyan("Start lexer analyzer.\n")

        self.tokens, self.numbers, self.ident, self.errors = lexer.tokenize()

        if len(self.errors) == 0:
            # helpers.print_cyan("\nTokens:")
            Helpers.print_cyan(self, "\nTokens new:")
            print(self.tokens, "\n")

            helpers.print_cyan("Numbers:")
            print(self.numbers, "\n")

            helpers.print_cyan("Identificators:")
            print(self.ident, "\n")

            helpers.print_cyan("End lexer analyzer.\n")

            helpers.print_magenta("Lexer OK!\n")

            return True

        else:
            helpers.print_red(f"Error in lexer: {self.errors[0]}\n")

        return False



    def start_parser(self, debug: str = False):
        from core.parser.syntax import Parser
    
        helpers = Helpers()
    
        parser = Parser(debug)
        parser.init_tables()
        try:
            parser.parse_program()
            helpers.print_magenta("Syntax analyzer OK!\n")
            return True
        except Exception as e:
            helpers.print_red(f"Syntax error: {e}\n")
    
        return False

    def start_semantic_analyzer(self):
        helpers = Helpers()
        semantic_analyzer = SemanticAnalyzer()
    
        try:
            semantic_analyzer.analyze(self.tokens)
            helpers.print_magenta("Semantic analyzer OK!\n")
            return True
        except Exception as e:
            helpers.print_red(f"Semantic error: {e}\n")
    
        return False
