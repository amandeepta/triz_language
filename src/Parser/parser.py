from src.Utils.tokens import *
from src.Utils.error import *
from src.Parser.nodes import *

PRECEDENCE = {
    TT_PLUS: 1,
    TT_MINUS: 1,
    TT_MUL: 2,
    TT_DIV: 2,
    TT_MOD: 2
}

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.pos_start = None
        self.pos_end = None

    def register(self, res):
        if isinstance(res, ParseResult):
            if res.error:
                self.error = res.error
            return res.node
        return res

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        self.error = error
        return self

    def set_pos(self, token):
        # Helper method to pass position info from token
        if token:
            self.pos_start = token.pos_start
            self.pos_end = token.pos_end

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.current_tok = None
        self.advance()

    def __is_at_end(self):
        return self.tok_idx >= len(self.tokens)

    def advance(self):
        self.tok_idx += 1
        if not self.__is_at_end():
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    def parse(self):
        res = ParseResult()
        program_node = ProgramNode([])

        while self.current_tok.type != TT_EOF:
            if self.current_tok.type == TT_RBRACE:
                break

            stmt = res.register(self.statement())
            if res.error:
                return res
            program_node.statements.append(stmt)

            if isinstance(stmt, (ExpressionStatement, VarAssignNode, ReturnNode)):
                if self.current_tok.type == TT_SEMI:
                    self.advance()
                # Allow optional semicolon
                elif self.current_tok.type != TT_EOF and self.current_tok.type != TT_RBRACE:
                    return res.failure(InvalidSyntaxError(
                        getattr(self.current_tok, 'pos_start', None),
                        getattr(self.current_tok, 'pos_end', None),
                        "Expected ';' after statement"
                    ))

        return res.success(program_node)

    def statement(self):
        res = ParseResult()

        if self.current_tok.matches(TT_KEYWORD, "FN"):
            return res.success(res.register(self.func_def()))

        if self.current_tok.matches(TT_KEYWORD, "RETURN"):
            return_stmt = self.return_stmt()
            if return_stmt.error:
                res.set_pos(self.current_tok)
                return res.failure(return_stmt.error)
            return res.success(return_stmt.node)

        expr = res.register(self.expr())
        if res.error:
            return res
        return res.success(ExpressionStatement(expr))

    def return_stmt(self):
        res = ParseResult()
        self.advance()

        if self.current_tok.type == TT_SEMI:
            self.advance()
            return res.success(ReturnNode(None))

        return_value = res.register(self.expr())
        if res.error:
            return res
        
        return res.success(ReturnNode(return_value))

    def expr(self):
        res = ParseResult()

        if self.current_tok.matches(TT_KEYWORD, 'VAR'):
            self.advance()
            if self.current_tok.type != TT_IDENTIFIER:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected identifier"
                ))
            var_name = self.current_tok
            self.advance()

            if self.current_tok.type != TT_EQ:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected '=' for variable assignment"
                ))
            self.advance()

            value = res.register(self.expr())
            if res.error:
                return res
            return res.success(VarAssignNode(var_name, value))

        return self.bin_op(self.atom, 0)

    def bin_op(self, func, min_precedence):
        res = ParseResult()
        left = res.register(func())
        if res.error:
            return res

        while self.current_tok.type in PRECEDENCE and PRECEDENCE[self.current_tok.type] >= min_precedence:
            op_tok = self.current_tok
            precedence = PRECEDENCE[op_tok.type]
            self.advance()
            right = res.register(self.bin_op(func, precedence + 1))
            if res.error:
                return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)

    def func_def(self):
        res = ParseResult()
        self.advance()
        if self.current_tok.type != TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start,
                self.current_tok.pos_end,
                "Expected function name"
            ))
        func_name = self.current_tok
        self.advance()

        if self.current_tok.type != TT_LPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start,
                self.current_tok.pos_end,
                "Expected '(' for parameters"
            ))
        self.advance()

        param_toks = []
        if self.current_tok.type == TT_IDENTIFIER:
            param_toks.append(self.current_tok)
            self.advance()
            while self.current_tok.type == TT_COMMA:
                self.advance()
                if self.current_tok.type != TT_IDENTIFIER:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "Expected identifier for parameter"
                    ))
                param_toks.append(self.current_tok)
                self.advance()

        if self.current_tok.type != TT_RPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start,
                self.current_tok.pos_end,
                "Expected closing parenthesis ')'"
            ))
        self.advance()

        if self.current_tok.type != TT_LBRACE:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start,
                self.current_tok.pos_end,
                "Expected opening brace '{' for function body"
            ))
        self.advance()

        body = []
        while self.current_tok.type != TT_RBRACE and self.current_tok.type != TT_EOF:
            stmt = res.register(self.statement())
            if res.error:
                return res
            body.append(stmt)
            
            if isinstance(stmt, (ExpressionStatement, VarAssignNode, ReturnNode)):
                if self.current_tok.type == TT_SEMI:
                    self.advance()

        if self.current_tok.type != TT_RBRACE:
            
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start,
                self.current_tok.pos_end,
                "Expected closing brace '}' for function body"
            ))
        self.advance()

        block_node = BlockNode(body)
        return res.success(FunctionNode(func_name, param_toks, block_node))

    def atom(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_PLUS, TT_MINUS):
            op_tok = tok
            self.advance()
            factor = res.register(self.atom())
            if res.error:
                return res
            return res.success(UnaryOpNode(op_tok, factor))
        elif tok.type in (TT_INT, TT_FLOAT):
            self.advance()
            return res.success(NumberNode(tok))
        elif tok.type == TT_IDENTIFIER:
            self.advance()
            return res.success(VarAccessNode(tok))
        elif tok.type == TT_LPAREN:
            self.advance()
            expr = res.register(self.expr())
            if res.error:
                return res
            if self.current_tok.type == TT_RPAREN:
                self.advance()
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected ')'"
                ))
        return res.failure(InvalidSyntaxError(
            tok.pos_start,
            tok.pos_end,
            "Expected int, float, '+', '-', identifier, or '('"
        ))
