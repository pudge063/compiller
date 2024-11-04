class Reader:
    """
    Класс Reader для чтения по символу из файла с кодом.
    Возвращает функции чтения символа и закрытия файла.
    """

    def __init__(self, file):
        self.file = file

    def char_reader(self):
        f = open(self.file, "r")

        def get_char():
            return f.read(1)

        def close_file():
            f.close()

        return get_char, close_file
