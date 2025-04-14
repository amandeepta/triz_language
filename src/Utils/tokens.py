from src.Utils.position import Position

# Token types
TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_PLUS = 'PLUS'
TT_IDENTIFIER = 'IDENTIFIER'
TT_KEYWORD = 'KEYWORD'
TT_TYPE = 'TYPE'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_MOD = 'MOD'
TT_SEMI = 'SEMI'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_LBRACE = 'LBRACE'
TT_RBRACE = 'RBRACE'
TT_EQ = 'EQ'
TT_EE = 'EE'
TT_NE = 'NE'
TT_GT = 'GT'
TT_LT = 'LT'
TT_GTE = 'GTE'
TT_LTE = 'LTE'
TT_COMMA = 'COMMA'
TT_COLON = 'COLON'  # Added colon for function parameter types
TT_EOF = 'EOF'

TT_TYPES = [
    'INT',
    'FLOAT',
    'VOID'
]
# Keywords
KEYWORDS = [
    'VAR', 
    'CONST',
    'AND',
    'OR',
    'NOT',
    'FN',
    'RETURN', 
]

# Token class
class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value
        self.pos_start = pos_start.copy() if pos_start else None
        self.pos_end = pos_end.copy() if pos_end else None

        if pos_start and not pos_end:
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

    def __repr__(self):
        return f"{self.type}:{self.value}" if self.value is not None else self.type

    def matches(self, type, value):
        return self.type == type and self.value == value
