#
class SemanticError(Exception):
    pass

class SemanticAnalyzer:
    def __init__(self):
        self.variables = {}  # Таблица символов: {имя: тип}

    def declare_variable(self, name, var_type):
        if name in self.variables:
            raise SemanticError(f"Переменная {name} уже объявлена")
        self.variables[name] = var_type

    def check_variable(self, name):
        if name not in self.variables:
            raise SemanticError(f"Переменная {name} не объявлена")

    def check_type(self, name, expected_type):
        actual_type = self.variables.get(name)
        if actual_type != expected_type:
            raise SemanticError(
                f"Несоответствие типов: {name} имеет тип {actual_type}, ожидался {expected_type}"
            )

    def check_operation(self, left_type, operator, right_type):
        if (operator in {"==", "!=", "<", "<=", ">", ">=", "+", "-", "||", "*", "/", "&&"}
                and left_type != right_type):
            raise SemanticError(
                f"Операция {operator} недопустима между типами {left_type} и {right_type}"
            )

    def add_variable(self, name):
        if name in self.variables:
            raise SemanticError(f"Переменная {name} уже объявлена")

    def is_declared(self, var_name):
        if var_name not in self.variables:
            raise SemanticError(f"Переменная {var_name} не объявлена")

    # def is_initialized(self, var_name):
    #     if var_name not in self.variables:
    #         raise SemanticError(f"Переменная {var_name} не объявлена")
    #     if
    def initialize_variable(self, current_var, value):
        pass