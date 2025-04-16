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


class BooleanNode:
    def __init__(self, tok):
        self.tok = tok
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'BooleanNode({repr(self.tok)})'

    def json(self):
        return {
            "type": "BooleanLiteral",
            "value": self.tok.value
        }

        pass

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
    
class VarReAssignNode:
    def __init__(self, var_name_tok, value_node):
        self.var_name_tok = var_name_tok
        self.value_node = value_node
        self.value = value_node
        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = value_node.pos_end if value_node else var_name_tok.pos_end

    def __repr__(self):
        return f'VarReAssignNode({repr(self.var_name_tok)}, {repr(self.value_node)})'

    def json(self):
        return {
            "type": "VarReAssign",
            "name": self.var_name_tok.value,
            "value": self.value_node.json()
        }
    



class ReturnNode:
    def __init__(self, return_val_node):
        self.return_val = return_val_node
        if return_val_node is None:
            self.pos_start = None
            self.pos_end = None
        else:
            self.pos_start = self.return_val.pos_start
            self.pos_end = self.return_val.pos_end

    def __repr__(self):
        return f'ReturnNode({repr(self.return_val)})'

    def json(self):
        return {
            "type": "Return",
            "value": self.return_val.json() if self.return_val else None,
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
    def __init__(self, func_name_tok, param_toks,return_type, body_node):
        self.func_name_tok = func_name_tok
        self.param_toks = param_toks
        self.body_node = body_node
        self.return_type = return_type
        self.pos_start = self.func_name_tok.pos_start
        self.pos_end = self.body_node.pos_end

    def __repr__(self):
        return f"FunctionNode({repr(self.func_name_tok)}, {repr(self.param_toks)}, {repr(self.body_node)})"

    def json(self):
        return {
            "type": "FunctionStatement",
            "name": self.func_name_tok.value,
            "return_type" : self.return_type,
            "parameters": [{
                "type": "FunctionParameter",
                "name": param.value,
                "value_type": param.type  # Assuming it's always int for simplicity, adjust as needed
            } for param in self.param_toks],
            
            "body": self.body_node.json(),
        }

class StringNode:
    def __init__(self, tok):
        self.token = tok
        self.pos_start = tok.pos_start
        self.pos_end = tok.pos_end
        self.type = "StringLiteral"

    def __repr__(self):
        return f'StringNode("{self.token.value}")'

    def json(self):
        return {
            "type": self.type,
            "value": self.token.value
        }


class FunctionCallNode:
    def __init__(self, func_name_tok, arg_nodes):
        self.func_name_tok = func_name_tok
        self.arg_nodes = arg_nodes

        self.pos_start = self.func_name_tok.pos_start
        self.pos_end = self.arg_nodes[-1].pos_end if self.arg_nodes else self.func_name_tok.pos_end

    def __repr__(self):
        return f"FunctionCallNode({repr(self.func_name_tok)}, {repr(self.arg_nodes)})"

    def json(self):
        return {
            "type": "FunctionCall",
            "name": self.func_name_tok.value,
            "arguments": [arg.json() for arg in self.arg_nodes]
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
        return f"(Program: {repr(self.statements)})"

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
        return f'BlockNode({repr(self.statements)})'

    def json(self):
        return {
            "type": "Block",
            "statements": [stmt.json() for stmt in self.statements]
        }

class IfNode:
    def __init__(self, condition_node, then_node, else_node = None):
        self.condition_node = condition_node
        self.then_node = then_node
        self.else_node = else_node

        self.pos_start = self.condition_node.pos_start
        self.pos_end = self.else_node.pos_end if self.else_node else self.then_node.pos_end

    def __repr__(self):
        if self.else_node:
            return f"IfNode: {self.condition_node}, {self.then_node}, {self.else_node}"
        else:
            return f"IfNode: {self.condition_node}, {self.then_node}"
        
    def json(self):
        return {
            "type" : "IfStatement",
            "condition" : self.condition_node.json(),
            "then" : self.then_node.json(),
            "else" : self.else_node.json() if self.else_node else None,
        }

class PrintNode:
    def __init__(self, expr_nodes):
        # expr_nodes is now a list of expression nodes
        self.expr_nodes = expr_nodes
        # The position information should be derived from the first and last expressions
        self.pos_start = self.expr_nodes[0].pos_start
        self.pos_end = self.expr_nodes[-1].pos_end

    def __repr__(self):
        # Update repr to represent multiple expressions
        return f'PrintNode({repr(self.expr_nodes)})'

    def json(self):
        # Update json method to output the list of expressions
        return {
            "type": "PrintStatement",
            "exprs": [expr_node.json() for expr_node in self.expr_nodes]
        }

class WhileNode:
    def __init__(self, condition_node, body_node):
        self.condition_node = condition_node
        self.body_node = body_node

        self.pos_start = condition_node.pos_start
        self.pos_end = body_node.pos_end

    def __repr__(self):
        return f"WhileNode: {self.condition_node}, {self.body_node}"
        
    def json(self):
        return {
            "type" : "WhileStatement",
            "condition" : self.condition_node.json(),
            "then" : self.body_node.json(),
        }
    
class ForNode:
    def __init__(self, var_name, start_value_node, condition_node, step_value_node, body_node):
        self.var_name = var_name                  # A token containing the variable's name.
        self.start_value_node = start_value_node  # AST node for the starting value.
        self.condition_node = condition_node      # AST node for the loop condition.
        self.step_value_node = step_value_node    # AST node for the step (update) expression.
        self.body_node = body_node                # AST node for the block of statements.

        self.pos_start = var_name.pos_start
        self.pos_end = body_node.pos_end

    def __repr__(self):
        return f"ForNode: ({self.var_name.value} , {self.start_value_node}; {self.condition_node}; {self.step_value_node}) {self.body_node}"

    def json(self):
        return {
            "type": "ForStatement",
            "var": self.var_name_tok.value,
            "start": self.start_value_node.json(),
            "end": self.end_value_node.json(),
            "step": self.step_value_node.json() if self.step_value_node else None,
            "body": self.body_node.json()
        }
    
class BreakNode:
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.type = "BreakStatement"

    def __repr__(self):
        return f"(break)"

    def json(self):
        return {
            "type": "BreakStatement"
        }

class ContinueNode:
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.type = "ContinueStatement"

    def __repr__(self):
        return f"(continue)"

    def json(self):
        return {
            "type": "ContinueStatement"
        }
