class NumberNode:
    def __init__(self, tok):
        self.tok = tok
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'NumberNode({repr(self.tok)})'

    def json(self):
        return {
            "type": "IntegerLiteral" if self.tok.type == "INT" else "FloatLiteral",
            "value": self.tok.value
        }


class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node
        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        return f'BinOpNode({repr(self.left_node)}, {repr(self.op_tok)}, {repr(self.right_node)})'

    def json(self):
        return {
            "type": "InfixExpression",
            "left": self.left_node.json(),
            "operator": self.op_tok.value if self.op_tok.value is not None else self.op_tok.type,
            "right": self.right_node.json()
        }


class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node
        self.pos_start = self.op_tok.pos_start
        self.pos_end = node.pos_end

    def __repr__(self):
        return f'UnaryOpNode({repr(self.op_tok)}, {repr(self.node)})'

    def json(self):
        return {
            "type": "UnaryExpression",
            "operator": self.op_tok.value,
            "operand": self.node.json()
        }


class VarAssignNode:
    def __init__(self, var_name_tok, value_node):
        self.var_name_tok = var_name_tok
        self.value_node = value_node
        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = value_node.pos_end if value_node else var_name_tok.pos_end

    def __repr__(self):
        return f'VarAssignNode({repr(self.var_name_tok)}, {repr(self.value_node)})'

    def json(self):
        return {
            "type": "VarAssign",
            "name": self.var_name_tok.value,
            "value": self.value_node.json()
        }

class ReturnNode:
    def __init__(self, return_val_node):
        self.return_val = return_val_node
        self.pos_start = self.return_val.pos_start
        self.pos_end = self.return_val.pos_end

    def __repr__(self):
        return f'ReturnNode({repr(self.func_name)}, {repr(self.return_value)})'
    
    def json(self):
        return {
            "type": "Return",
            "value": self.return_val.json(),
        }
    

class VarAccessNode:
    def __init__(self, var_name_tok):
        self.var_name_tok = var_name_tok
        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end

    def __repr__(self):
        return f'VarAccessNode({repr(self.var_name_tok)})'

    def json(self):
        return {
            "type": "VarAccess",
            "name": self.var_name_tok.value
        }


class ExpressionStatement:
    def __init__(self, expr):
        self.expr = expr
        self.pos_start = expr.pos_start
        self.pos_end = expr.pos_end

    def __repr__(self):
        return f'ExpressionStatement({repr(self.expr)})'

    def json(self):
        return {
            "type": "ExpressionStatement",
            "expr": self.expr.json()
        }

class FunctionNode:
    def __init__(self, func_name_tok, param_toks, body_node):
        self.func_name_tok = func_name_tok
        self.param_toks = param_toks
        self.body_node = body_node

        self.pos_start = self.func_name_tok.pos_start
        self.pos_end = self.body_node.pos_end

    def __repr__(self):
        return f"FunctionNode({repr(self.func_name_tok)}, {repr(self.param_toks)}, {repr(self.body_node)})"
    
    def json(self):
        return {
            "type": "Function",
            "name": self.func_name_tok.value,
            "parameters": [param.value for param in self.param_toks],
            "body": self.body_node.json(),
        }
    

class NumberNode:
    def __init__(self, tok):
        self.tok = tok
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'NumberNode({repr(self.tok)})'

    def json(self):
        return {
            "type": "IntegerLiteral" if self.tok.type == "INT" else "FloatLiteral",
            "value": self.tok.value
        }


class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node
        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        return f'BinOpNode({repr(self.left_node)}, {repr(self.op_tok)}, {repr(self.right_node)})'

    def json(self):
        return {
            "type": "InfixExpression",
            "left": self.left_node.json(),
            "operator": self.op_tok.value if self.op_tok.value is not None else self.op_tok.type,
            "right": self.right_node.json()
        }


class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node
        self.pos_start = self.op_tok.pos_start
        self.pos_end = node.pos_end

    def __repr__(self):
        return f'UnaryOpNode({repr(self.op_tok)}, {repr(self.node)})'

    def json(self):
        return {
            "type": "UnaryExpression",
            "operator": self.op_tok.value,
            "operand": self.node.json()
        }


class VarAssignNode:
    def __init__(self, var_name_tok, value_node):
        self.var_name_tok = var_name_tok
        self.value_node = value_node
        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = value_node.pos_end if value_node else var_name_tok.pos_end

    def __repr__(self):
        return f'VarAssignNode({repr(self.var_name_tok)}, {repr(self.value_node)})'

    def json(self):
        return {
            "type": "VarAssign",
            "name": self.var_name_tok.value,
            "value": self.value_node.json()
        }


class ReturnNode:
    def __init__(self, return_val_node):
        self.return_val = return_val_node
        if return_val_node is None :
            self.pos_start = None
            self.pos_end = None
        else :
            self.pos_start = self.return_val.pos_start
            self.pos_end = self.return_val.pos_end

    def __repr__(self):
        return f'ReturnNode({repr(self.return_val)})'

    def json(self):
        return {
            "type": "Return",
            "value": self.return_val.json(),
        }


class VarAccessNode:
    def __init__(self, var_name_tok):
        self.var_name_tok = var_name_tok
        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end

    def __repr__(self):
        return f'VarAccessNode({repr(self.var_name_tok)})'

    def json(self):
        return {
            "type": "VarAccess",
            "name": self.var_name_tok.value
        }


class ExpressionStatement:
    def __init__(self, expr):
        self.expr = expr
        self.pos_start = expr.pos_start
        self.pos_end = expr.pos_end

    def __repr__(self):
        return f'ExpressionStatement({repr(self.expr)})'

    def json(self):
        return {
            "type": "ExpressionStatement",
            "expr": self.expr.json()
        }


class FunctionNode:
    def __init__(self, func_name_tok, param_toks, body_node):
        self.func_name_tok = func_name_tok
        self.param_toks = param_toks
        self.body_node = body_node

        self.pos_start = self.func_name_tok.pos_start
        self.pos_end = self.body_node.pos_end

    def __repr__(self):
        return f"FunctionNode({repr(self.func_name_tok)}, {self.param_toks}, {repr(self.body_node)})"

    def json(self):
        return {
            "type": "FunctionStatement",
            "name": self.func_name_tok.value,
            "parameters": [{
                "type": "FunctionParameter",
                "name": param.value,
                "value_type": "int"  # Assuming it's always int for simplicity, adjust as needed
            } for param in self.param_toks],
            "body": self.body_node.json(),
        }


class ProgramNode:
    def __init__(self, statements=None):
        self.statements = statements or []

        if self.statements:
            self.pos_start = self.statements[0].pos_start
            self.pos_end = self.statements[-1].pos_end
        else:
            self.pos_start = None
            self.pos_end = None

    def add_statement(self, stmt):
        self.statements.append(stmt)
        if self.pos_start is None:
            self.pos_start = stmt.pos_start
        self.pos_end = stmt.pos_end

    def __repr__(self):
        return f"(Program: {self.statements})"

    def json(self):
        return {
            "type": "Program",
            "statements": [stmt.json() for stmt in self.statements]
        }

    
class BlockNode:
    def __init__(self, statements):
        self.statements = statements or []

        if self.statements:
            self.pos_start = self.statements[0].pos_start
            self.pos_end = self.statements[-1].pos_end
        else:
            self.pos_start = None
            self.pos_end = None

    def __repr__(self):
        return f'BlockNode({self.statements})'

    def json(self):
        return {
            "type": "Block",
            "statements": [stmt.json() for stmt in self.statements]
        }
