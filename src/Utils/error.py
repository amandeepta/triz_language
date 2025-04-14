# Error class
class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def __str__(self):
        result  = f'{self.error_name}: {self.details}\n'
        result += f'line {self.pos_start}'
        return result

class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)

class InvalidSyntaxError:
    def __init__(self, pos_start, pos_end, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.details = details

    def as_string(self):
        return f"Invalid Syntax: {self.details} at position {self.pos_start}-{self.pos_end}"


class RTError(Error):
    def __init__(self, pos_start, pos_end, details, context):
        super().__init__(pos_start, pos_end, 'Runtime Error', details)
        self.context = context

    def __str__(self):
        return f'Runtime Error: {self.details} Context : {self.context}'
