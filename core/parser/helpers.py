class ParserHelpers:
    def is_identificator(self):
        if self.current_token()[0] == 3:
            return True
        return False
