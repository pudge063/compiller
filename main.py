import sys
from core.analyze_manager import Manager
from core.helpers import Helpers

manager = Manager()
helper = Helpers()

if __name__ == "__main__":
    args = sys.argv
    arg_dict = {"-f": None, "debug": False}
    part_of_arg, tmp_arg = False, None

    try:
        for arg in args:
            if arg[0] == "-":
                part_of_arg = True
                if not arg in arg_dict:
                    raise Exception(f"Undefined arg {arg}.")
                tmp_arg = arg
            elif part_of_arg:
                arg_dict[tmp_arg] = arg
                part_of_arg = False
            else:
                arg_dict[arg] = True

        if part_of_arg:
            raise Exception(f"Excepted part of {tmp_arg} arg.")

        f = arg_dict["-f"] if arg_dict["-f"] else "test1.txt"
        d = True if arg_dict["debug"] else False

        if manager.start_compile(f, d):
            if manager.start_parser(d):
                pass

        if d:
            helper.print_magenta(f"Compiler args: {arg_dict}\n")

    except Exception as e:
        print(e)

    finally:
        print("Program ended...")
