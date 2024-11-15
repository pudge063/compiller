class Debug:
    def __init__(self, debug_state=False):
        self.debug_state = debug_state
        self.init_colors()

    def init_colors(self):
        from core.helpers import Helpers

        helper = Helpers()
        self.print_black = helper.print_black
        self.print_cyan = helper.print_cyan
        self.print_red = helper.print_red
        self.print_magenta = helper.print_magenta
        self.print_yellow = helper.print_yellow

    def change_state(self, prev_q, next_q):
        if self.debug_state:
            self.print_yellow(f"change_state: {prev_q} => {next_q}")
        return next_q

    def print_stack(self, stack, q, ch):
        if self.debug_state:
            self.print_black(f"stack: {stack}# q: {q} ch: {ch}")

    def add_token(self, stack, table_id, token_id):
        if self.debug_state:
            self.print_yellow(f"token {stack} => ({table_id}, {token_id})")

    def add_identificator(self, stack, table_id, token_id):
        if self.debug_state:
            self.print_yellow(f"identificator {stack} => ({table_id}, {token_id})")

    def add_number(self, stack, token_id):
        if self.debug_state:
            self.print_yellow(f"numbers {stack} => (4, {token_id})")
