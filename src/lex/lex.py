from src.Utils.tokens import *
from src.Utils.error import *
from src.Utils.position import *

import string

DIGITS = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = Position(-1, 0, 1)
        self.current = None
        self.next()

    def next(self):
        self.pos.advance(self.current)
        self.current = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def make_tokens(self):
        tokens = []

        while self.current is not None:
            if self.current in ' \t':
                self.next()
            elif self.current == '\n':
                self.next()
            elif self.current in DIGITS:
                tokens.append(self.make_number())
            elif self.current in LETTERS:
                tokens.append(self.make_identifiers())
            elif self.current == '+':
                tokens.append(self.make_simple_token(TT_PLUS))
            elif self.current == '-':
                tokens.append(self.make_simple_token(TT_MINUS))
            elif self.current == '*':
                tokens.append(self.make_simple_token(TT_MUL))
            elif self.current == '/':
                tokens.append(self.make_simple_token(TT_DIV))
            elif self.current == '%':
                tokens.append(self.make_simple_token(TT_MOD))
            elif self.current == '(':
                tokens.append(self.make_simple_token(TT_LPAREN))
            elif self.current == ')':
                tokens.append(self.make_simple_token(TT_RPAREN))
            elif self.current == '{':
                tokens.append(self.make_simple_token(TT_LBRACE))
            elif self.current == '}':
                tokens.append(self.make_simple_token(TT_RBRACE))
            elif self.current == ',':
                tokens.append(self.make_simple_token(TT_COMMA))
            elif self.current == ':':
                tokens.append(self.make_simple_token(TT_COLON))
            elif self.current == '=':
                token, error = self.make_equals(TT_EQ)
                if error: return [], error
                tokens.append(token)
            elif self.current == '!':
                token, error = self.make_not_equals()
                if error: return [], error
                tokens.append(token)
            elif self.current == '<':
                token, error = self.make_less_than()
                if error: return [], error
                tokens.append(token)
            elif self.current == '>':
                token, error = self.make_greater_than()
                if error: return [], error
                tokens.append(token)
            elif self.current == ';':
                tokens.append(self.make_simple_token(TT_SEMI))
            else:
                err = Error("IllegalCharacter", f"'{self.current}' is not valid", self.pos.ln, self.pos.col)
                return [], err

        tokens.append(Token(TT_EOF))
        return tokens, None

    def make_simple_token(self, type_):
        pos_start = self.pos.copy()
        self.next()
        pos_end = self.pos.copy()
        return Token(type_, pos_start=pos_start, pos_end=pos_end)

    def make_number(self):
        num_str = ''
        has_dot = False
        pos_start = self.pos.copy()

        while self.current is not None and (self.current in DIGITS or self.current == '.'):
            if self.current == '.':
                if has_dot:
                    break
                has_dot = True
            num_str += self.current
            self.next()

        value = float(num_str) if has_dot else int(num_str)
        tok_type = TT_FLOAT if has_dot else TT_INT
        pos_end = self.pos.copy()
        return Token(tok_type, value, pos_start, pos_end)

    def make_identifiers(self):
        id_str = ""
        pos_start = self.pos.copy()

        while self.current is not None and self.current in LETTERS_DIGITS + '_':
            id_str += self.current
            self.next()

        pos_end = self.pos.copy()
        if id_str.upper() in KEYWORDS:  # Check if the identifier is a keyword
            token_type = TT_KEYWORD
            value = id_str.upper()
        elif id_str.upper() in TT_TYPES :
            token_type = TT_TYPE
            value = id_str.upper()
        else:
            token_type = TT_IDENTIFIER
            value = id_str
        return Token(token_type, value, pos_start, pos_end)

    def make_not_equals(self):
        pos_start = self.pos.copy()
        self.next()
        if self.current == '=':
            self.next()
            return Token(TT_NE, pos_start=pos_start, pos_end=self.pos.copy()), None
        return None, Error("IllegalCharacter", "'=' expected after '!'", self.pos.line, self.pos.col)

    def make_equals(self, type_):
        pos_start = self.pos.copy()
        self.next()
        if self.current == '=':
            self.next()
            return Token(TT_EE, pos_start=pos_start, pos_end=self.pos.copy()), None
        return Token(type_, pos_start=pos_start, pos_end=self.pos.copy()), None

    def make_less_than(self):
        pos_start = self.pos.copy()
        self.next()
        if self.current == '=':
            self.next()
            return Token(TT_LTE, pos_start=pos_start, pos_end=self.pos.copy()), None
        return Token(TT_LT, pos_start=pos_start, pos_end=self.pos.copy()), None

    def make_greater_than(self):
        pos_start = self.pos.copy()
        self.next()
        if self.current == '=':
            self.next()
            return Token(TT_GTE, pos_start=pos_start, pos_end=self.pos.copy()), None
        return Token(TT_GT, pos_start=pos_start, pos_end=self.pos.copy()), None

def run(text):
    lexer = Lexer(text)
    return lexer.make_tokens()

def main():
    text = "fn mi(a: int, b: float): int { var a = 10; return a; }"
    tokens, error = run(text)

    if error:
        print(error)
    else:
        print(tokens)

if __name__ == "__main__":
    main()
