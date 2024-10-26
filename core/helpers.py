class Helpers:
    def in_number_table(self, num, table: list[tuple]):
        print(table)
        if len(table) > 0:
            for i in range(len(table)):
                if table[i][1] == num:
                    return i
        return False

    def fexp_to_float(self, num):
        return ("{:.10f}".format(float(num))).rstrip("0").rstrip(".")
