class Helpers:
    def in_number_table(self, num, table: list[tuple]):
        for i in range(len(table)):
            if table[i][1] == num:
                return i
        return False
