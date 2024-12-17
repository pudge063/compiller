

class VariableInfo:
    def __init__(self, name: str, is_initialized: bool, value: object):
        self.name = name
        self.is_initialized = is_initialized
        self.value = value

    def get_name(self) -> str:
        return self.name

    def set_name(self, new_name: str) -> None:
        self.name = new_name

    def get_is_initialized(self) -> bool:
        return self.is_initialized

    def set_is_initialized(self, is_initialized: bool) -> None:
        self.is_initialized = is_initialized

    def get_value(self) -> object:
        return self.value

    def set_value(self, new_value: object) -> None:
        self.value = new_value
