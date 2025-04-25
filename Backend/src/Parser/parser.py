from src.Utils.tokens import *
from src.Utils.error import *
from src.Parser.nodes import *

PRECEDENCE = {
    TT_PLUS: 1,
    TT_MINUS: 1,
    TT_MUL: 2,
    TT_DIV: 2,
    TT_MOD: 2, 
    TT_EE: 0,
    TT_EQ : 0,
    TT_EE : 0,
    TT_NE : 0,
    TT_GT : 0,
    TT_LT : 0,
    TT_GTE : 0,
    TT_LTE : 0,
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
        self.pos_start = node.pos_start if node else None
        self.pos_end = node.pos_end if node else None
        return self

    def failure(self, error):
        self.error = error
        self.pos_start = error.pos_start
        self.pos_end = error.pos_end
        return self

    def set_pos(self, token):
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

    def peek(self):
        if self.tok_idx + 1 < len(self.tokens):
            return self.tokens[self.tok_idx + 1]
        return None

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

            if isinstance(stmt, (ExpressionStatement, VarAssignNode, VarReAssignNode, ReturnNode)):
                if self.current_tok.type == TT_SEMI:
                    self.advance()
                elif self.current_tok.type != TT_EOF and self.current_tok.type != TT_RBRACE:
                    return res.failure(InvalidSyntaxError(
                        getattr(self.current_tok, 'pos_start', None),
                        getattr(self.current_tok, 'pos_end', None),
                        "Expected ';' after statement"
                    ))

        return res.success(program_node)

    def statement(self, inside_loop = False):
        res = ParseResult()
        var_name = self.current_tok
        next_tok = self.peek()
        print(f"{var_name}, {next_tok} :: {inside_loop}")

        # Handle while statements
        if self.current_tok.matches(TT_KEYWORD, "WHILE"):
            print(f"enter while")
            return res.success(res.register(self.while_block()))
        
        if self.current_tok.matches(TT_KEYWORD, "FOR"):
            print(f"enter for :: ")
            return self.for_block()



        # Handle print statement
        if self.current_tok.matches(TT_KEYWORD, "PRINT"):
            self.advance()

            # Ensure there's a '(' after PRINT keyword
            if self.current_tok.type != TT_LPAREN:
                return res.failure(InvalidSyntaxError(
                    getattr(self.current_tok, 'pos_start', None),
                    getattr(self.current_tok, 'pos_end', None),
                    "Expected '(' after 'PRINT'"
                ))
            self.advance()
            
            # Collect arguments inside the parentheses
            args = []
            while self.current_tok.type != TT_RPAREN:
                # Parse the expression for each argument
                expr = res.register(self.expr())
                if res.error:
                    return res

                args.append(expr)
                
                # Check for a comma separating arguments
                if self.current_tok.type == TT_COMMA:
                    self.advance()
                    continue
                # If we encounter a closing parenthesis or anything else, stop
                if self.current_tok.type == TT_RPAREN:
                    break
                else:
                    return res.failure(InvalidSyntaxError(
                        getattr(self.current_tok, 'pos_start', None),
                        getattr(self.current_tok, 'pos_end', None),
                        "Expected ',' or ')' after argument"
                    ))

            # Ensure the closing parenthesis
            if self.current_tok.type != TT_RPAREN:
                return res.failure(InvalidSyntaxError(
                    getattr(self.current_tok, 'pos_start', None),
                    getattr(self.current_tok, 'pos_end', None),
                    "Expected ')' after arguments"
                ))
            self.advance()
            if self.current_tok.type != TT_SEMI:
                return res.failure(InvalidSyntaxError(
                    getattr(self.current_tok, 'pos_start', None),
                    getattr(self.current_tok, 'pos_end', None),
                    "Expected ';' after print statement"
                ))
            self.advance()
            # Return the PrintNode with arguments
            return res.success(PrintNode(args))


        # Handle function definitions
        if self.current_tok.matches(TT_KEYWORD, "FN"):
            return res.success(res.register(self.func_def()))
        
        # Handle break statement
        if self.current_tok.matches(TT_KEYWORD, "BREAK"):
            if not inside_loop:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "'break' statements can only be used inside loops"
                ))
            pos_start = self.current_tok.pos_start
            pos_end = self.current_tok.pos_end
            self.advance()

            if self.current_tok.type != TT_SEMI:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected ';' after 'break'"
                ))
            self.advance()
            return res.success(BreakNode(pos_start, pos_end))

        if self.current_tok.matches(TT_KEYWORD, "CONTINUE"):
            if not inside_loop:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "'cintinue' statements can only be used inside loops"
                ))
            pos_start = self.current_tok.pos_start
            pos_end = self.current_tok.pos_end
            self.advance()

            if self.current_tok.type != TT_SEMI:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected ';' after 'continue'"
                ))
            self.advance()
            return res.success(ContinueNode(pos_start, pos_end))

        # Handle return statements
        if self.current_tok.matches(TT_KEYWORD, "RETURN"):
            return_stmt = self.return_stmt()
            if return_stmt.error:
                res.set_pos(self.current_tok)
                return res.failure(return_stmt.error)
            return res.success(return_stmt.node)
        
        if self.current_tok.matches(TT_KEYWORD, "IF"):
            print(f"enter if  :: :: : " )
            return res.success(res.register(self.if_block(inside_loop=inside_loop)))

        # Default case: Parse expressions
        expr = res.register(self.expr())
        if res.error:
            return res
        return res.success(ExpressionStatement(expr))
    

    #handle for block
    def for_block(self):
        res = ParseResult()

        self.advance()  # consume 'for'

        # Expect '(' after 'for'
        if self.current_tok.type != TT_LPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '(' after 'for'"
            ))
        self.advance()


        # Parse initialization using expr() as it handles the 'var' keyword and assignment.
        init = res.register(self.expr())
        if res.error:
            return res

        # Parse loop condition
        condition = res.register(self.expr())
        if res.error:
            return res

        # Expect ';' after condition
        if self.current_tok.type != TT_SEMI:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected ';' after condition"
            ))
        self.advance()

        # Parse step expression
        step_value = res.register(self.expr())
        if res.error:
            return res

        # Expect ')' to close loop control section
        if self.current_tok.type != TT_RPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected ')' after step value"
            ))
        self.advance()

        # Expect '{' to begin block
        if self.current_tok.type != TT_LBRACE:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '{' to start for-loop body"
            ))
        self.advance()

        # Parse the body block
        body = res.register(self.block(inside_loop=True))
        if res.error:
            return res

        # Successfully parsed a for-loop
        return res.success(ForNode(init.var_name_tok, init.value_node, condition, step_value, body))
    
    def while_block(self):
        res = ParseResult()
        self.advance() #consume while

        if self.current_tok.type != TT_LPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start,
                self.current_tok.pos_end,
                "Expected '(' after WHILE",
            ))
        
        self.advance() # consume '('

        condition = res.register(self.bool_exp())
        if res.error:
            return res
    
        if self.current_tok.type != TT_RPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start,
                self.current_tok.pos_end,
                "Expected ')' after condition ends"
            ))
        self.advance()   #consume ')'


        if self.current_tok.type != TT_LBRACE:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start,
                self.current_tok.pos_end,
                "Expected '{' after defining condition for WHILE",
            ))
        self.advance()

        body = res.register(self.block(inside_loop = True))
        if res.error:
            return res
        
        return res.success(WhileNode(condition, body))



    #Handle if statements
    def if_block(self, inside_loop = False):
        res = ParseResult()
        self.advance()  #consume 'if'

        if self.current_tok.type != TT_LPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start,
                self.current_tok.pos_end,
                "Expected '(' after IF",
            ))
        self.advance()  #consume '('

        #parse condition
        condition = res.register(self.bool_exp())

        if res.error:
            return res
        
        
        
        if self.current_tok.type != TT_RPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start,
                self.current_tok.pos_end,
                "Expected ')' after condition"
            ))
        self.advance()
        
        if self.current_tok.type != TT_LBRACE:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start,
                self.current_tok.pos_end,
                "Expected '{' after IF",
            ))
        self.advance()

        then_block = res.register(self.block(inside_loop=inside_loop))
        if res.error:
            return res
        
        else_block = None
        if self.current_tok.matches(TT_KEYWORD, "ELSE"):
            self.advance()

            if self.current_tok.matches(TT_KEYWORD, "IF"):
                else_block = res.register(self.if_block(inside_loop=inside_loop))
                if res.error:
                    return res
            
            else:
                if self.current_tok.type != TT_LBRACE:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "Expected '{' after ELSE",
                    ))
                self.advance()
                else_block = res.register(self.block(inside_loop=inside_loop))
                if res.error:
                    return res
                
        return res.success(IfNode(condition, then_block, else_block))
    

    def block(self, inside_loop = False):
        res = ParseResult()

        statements = []

        while self.current_tok.type != TT_RBRACE and self.current_tok.type != TT_EOF:
            stmt = res.register(self.statement(inside_loop=inside_loop))
            if res.error:
                return res
            statements.append(stmt)
            if self.current_tok.type == TT_SEMI:
                self.advance()

        if self.current_tok.type != TT_RBRACE:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start,
                self.current_tok.pos_end,
                "Expected '}' at end of block"
            ))
        self.advance()  
        
        return BlockNode(statements)


        


    def return_stmt(self):
        res = ParseResult()
        self.advance()

        if self.current_tok.type == TT_SEMI:
            self.advance()
            return res.success(ReturnNode(None))

        return_value = res.register(self.expr())
        if res.error:
            return res

        if self.current_tok.type != TT_SEMI:
            return res.failure(InvalidSyntaxError(
                getattr(self.current_tok, 'pos_start', None),
                getattr(self.current_tok, 'pos_end', None),
                "Expected ';' after return statement"
            ))
        self.advance()

        return res.success(ReturnNode(return_value))

    def expr(self):
        res = ParseResult()
        var_name = self.current_tok
        next_tok = self.peek()

        # Handle variable assignment or reassignment
        if self.current_tok.type == TT_IDENTIFIER:
            if next_tok and next_tok.type == TT_EQ:
                return self.var_reassign(var_name)

        if self.current_tok.matches(TT_KEYWORD, 'VAR'):
            return self.var_assign()
        
        return self.bin_op(self.atom, 0)
    
    def var_assign(self):
        res = ParseResult()

        self.advance() #consume var
        if self.current_tok.type != TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start,
                self.current_tok.pos_end,
                "Expected identifier"
            ))
        var_name = self.current_tok
        self.advance()

        if self.current_tok.type == TT_SEMI:
            self.advance()
            return res.success(VarAssignNode(var_name, None))

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
        if self.current_tok.type != TT_SEMI:
            return res.failure(InvalidSyntaxError(
                getattr(self.current_tok, 'pos_start', None),
                getattr(self.current_tok, 'pos_end', None),
                "Expected ';' after variable assignment"
            ))
        self.advance()
        return res.success(VarAssignNode(var_name, value))
    
    def var_reassign(self, var_name):
        res = ParseResult()

        self.advance()  # Skip the identifier
        self.advance()  # Skip the '='

        value = res.register(self.expr())
        if res.error:
            return res.failure(res.error)

        if self.current_tok.type != TT_SEMI:
            return res.failure(InvalidSyntaxError(
                getattr(self.current_tok, 'pos_start', None),
                getattr(self.current_tok, 'pos_end', None),
                "Expected ';' after assignment"
            ))
        self.advance()

        return res.success(VarReAssignNode(var_name, value))



    def bool_exp(self):
        return self.bin_op(self.comp_expr, 0)

    def comp_expr(self):
        res = ParseResult()

        if self.current_tok.matches(TT_KEYWORD, 'NOT'):
            op_tok = self.current_tok
            res.register(self.advance())  # consume 'NOT'
            node = res.register(self.comp_expr())
            if res.error:
                return res
            return res.success(UnaryOpNode(op_tok, node))

        left = res.register(self.arith_expr())
        if res.error:
            return res

        if self.current_tok.type in (TT_EQ, TT_NE, TT_LT, TT_LTE, TT_GT, TT_GTE):
            op_tok = self.current_tok
            res.register(self.advance())  # consume the operator
            right = res.register(self.arith_expr())
            if res.error:
                return res
            return res.success(BinOpNode(left, op_tok, right))

        return res.success(left)
    
    def arith_expr(self):
        return self.bin_op(self.term, 1)

    def term(self):
        return self.bin_op(self.factor, 2)

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_PLUS, TT_MINUS):
            # Handle unary plus and minus
            op_tok = tok
            self.advance()
            factor = res.register(self.factor())
            if res.error:
                return res
            return res.success(UnaryOpNode(op_tok, factor))
        
        # Handle numbers (integers or floats)
        elif tok.type in (TT_INT, TT_FLOAT):
            self.advance()
            return res.success(NumberNode(tok))
        
        elif tok.matches(TT_KEYWORD, "TRUE"):
            self.advance()
            return res.success(BooleanNode(tok))
        elif tok.matches(TT_KEYWORD, "FALSE"):
            self.advance()
            return res.success(BooleanNode(tok))
        elif tok.matches(TT_KEYWORD, "NOT"):
            self.advance()
            expr = res.register(self.atom())
            if res.error:
                return res
            return res.success(UnaryOpNode(tok, expr))
        
        # Handle variables (identifiers)
        elif tok.type == TT_IDENTIFIER:
            self.advance()
            return res.success(VarAccessNode(tok))
        
        # Handle parentheses (subexpressions)
        elif tok.type == TT_LPAREN:
            self.advance()
            expr = res.register(self.expr())  # Parse inner expression
            if res.error:
                return res
            if self.current_tok.type != TT_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected closing parenthesis ')'"
                ))
            self.advance()
            return res.success(expr)

        return res.failure(InvalidSyntaxError(
            tok.pos_start,
            tok.pos_end,
            "Expected a number, variable, or opening parenthesis"
        ))
    
    

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
        while self.current_tok.type == TT_IDENTIFIER:
            param_name = self.current_tok
            self.advance()
            if self.current_tok.type != TT_COLON:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected ':' after parameter name"
                ))
            self.advance()

            if self.current_tok.type not in TT_TYPE:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected parameter type (INT or FLOAT)"
                ))
            param_type = self.current_tok
            param_toks.append((param_name, param_type))
            self.advance()

            if self.current_tok.type == TT_COMMA:
                self.advance()

        if self.current_tok.type != TT_RPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start,
                self.current_tok.pos_end,
                "Expected closing parenthesis ')' for function parameters"
            ))
        self.advance()

        if self.current_tok.type != TT_COLON:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start,
                self.current_tok.pos_end,
                "Expected ':' after function parameters"
            ))
        self.advance()

        if self.current_tok.type not in TT_TYPE:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start,
                self.current_tok.pos_end,
                "Expected return type (INT or FLOAT)"
            ))
        return_type = self.current_tok
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

            if isinstance(stmt, (ExpressionStatement, VarAssignNode, VarReAssignNode, ReturnNode)):
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
        return res.success(FunctionNode(func_name, param_toks, return_type, block_node))

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
        elif tok.matches(TT_KEYWORD, "TRUE" ):
            self.advance()
            return res.success(BooleanNode(True))
        elif tok.matches(TT_KEYWORD, "FALSE"):
            self.advance()
            return res.success(BooleanNode(False))
        elif tok.matches(TT_KEYWORD, "NOT"):
            self.advance()
            expr = res.register(self.atom())
            if res.error:
                return res
            return res.success(UnaryOpNode(tok, expr))
        elif tok.type == TT_STR:
            self.advance()
            return res.success(StringNode(tok))
        elif tok.type == TT_IDENTIFIER:
            self.advance()

            if self.current_tok.type == TT_LPAREN:
                self.advance()
                arg_nodes = []

                if self.current_tok.type != TT_RPAREN:
                    arg_nodes.append(res.register(self.expr()))
                    if res.error:
                        return res

                    while self.current_tok.type == TT_COMMA:
                        self.advance()
                        arg_nodes.append(res.register(self.expr()))
                        if res.error:
                            return res

                if self.current_tok.type != TT_RPAREN:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "Expected closing parenthesis ')'"
                    ))

                self.advance()

                return res.success(FunctionCallNode(tok, arg_nodes))

            return res.success(VarAccessNode(tok))
        elif tok.type == TT_LPAREN:
            self.advance()
            expr = res.register(self.expr())
            if res.error:
                return res
            if self.current_tok.type != TT_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected closing parenthesis ')'"
                ))
            self.advance()
            return res.success(expr)

        return res.failure(InvalidSyntaxError(
            tok.pos_start,
            tok.pos_end,
            f"Expected an expression"
        ))
