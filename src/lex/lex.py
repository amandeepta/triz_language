import re
from src.Utils.tokens import *
from src.Utils.error import Error
from src.Utils.position import Position

token_specs = [
    (TT_FLOAT,    r'\d+\.\d+'),
    (TT_INT,      r'\d+'),
    (TT_IDENTIFIER, r'[A-Za-z_][A-Za-z0-9_]*'),
    (TT_EE,       r'=='),
    (TT_NE,       r'!='),
    (TT_LTE,      r'<='),
    (TT_GTE,      r'>='),
    (TT_EQ,       r'='),
    (TT_LT,       r'<'),
    (TT_GT,       r'>'),
    (TT_PLUS,     r'\+'),
    (TT_MINUS,    r'-'),
    (TT_MUL,      r'\*'),
    (TT_DIV,      r'/'),
    (TT_MOD,      r'%'),
    (TT_LPAREN,   r'\('),
    (TT_RPAREN,   r'\)'),
    (TT_LBRACE,   r'\{'),
    (TT_RBRACE,   r'\}'),
    (TT_SEMI,     r';'),
    (TT_COLON,    r':'),
    (TT_COMMA,    r','),
    ('SKIP',      r'[ \t\n\r]+'),
    ('MISMATCH',  r'.'),
]

master_pattern = '|'.join(f'(?P<{tok}>{pattern})' for tok, pattern in token_specs)
compiled_re = re.compile(master_pattern)

class RegexLexer:
    def __init__(self, text):
        self.text = text
        self.pos = Position(-1, 0, 1)

    def advance_pos(self, value):
        for char in value:
            self.pos.advance(char)

    def make_tokens(self):
        tokens = []

        for match in compiled_re.finditer(self.text):
            tok_type = match.lastgroup
            value = match.group(tok_type)
            start_pos = self.pos.copy()
            self.advance_pos(value)
            end_pos = self.pos.copy()

            if tok_type == 'SKIP':
                continue
            elif tok_type == 'MISMATCH':
                return [], Error(
                    "IllegalCharacter", 
                    f"'{value}' is not valid", 
                    start_pos.ln, 
                    start_pos.col
                )

            if tok_type == TT_IDENTIFIER:
                upper_value = value.upper()
                if upper_value in KEYWORDS:
                    tok_type = TT_KEYWORD
                    value = upper_value
                elif upper_value in ("TRUE", "FALSE"):
                    tok_type = TT_BOOL
                    value = True if upper_value=="TRUE" else False
                elif upper_value in TT_TYPES:
                    tok_type = TT_TYPE
                    value = upper_value

            if tok_type == TT_INT:
                value = int(value)
            elif tok_type == TT_FLOAT:
                value = float(value)
            elif tok_type == TT_BOOL:
                value = True if value.upper == "TRUE" else False

            tokens.append(Token(tok_type, value, start_pos, end_pos))

        tokens.append(Token(TT_EOF, pos_start=self.pos.copy(), pos_end=self.pos.copy()))
        return tokens, None


def run(text):
    lexer = RegexLexer(text)
    return lexer.make_tokens()


if __name__ == "__main__":
    test_code = """
    fn maz(a: int, b: int): int {
        b = a + b;
        return b;
    }

    fn riz(): int {
        var a;
        a = 10;
        var b;
        b = 20;
        var ab = maz(a, b);
        return ab;
    }
    """

    tokens, error = run(test_code)
    if error:
        print(error)
    else:
        print(tokens)
