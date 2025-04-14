from llvmlite import ir
from src.Parser.nodes import *
from src.Utils.tokens import *
from src.Utils.symbolTable import Environment

class Compiler:
    def __init__(self):
        self.module = ir.Module(name="my_module")
        self.builder = ir.IRBuilder()
        self.type_map = {
            'int': ir.IntType(32),
            'float': ir.FloatType(),
            'double': ir.DoubleType(),
            'bool': ir.IntType(1),
            'void': ir.VoidType()
        }
        self.env = Environment()

    def compile(self, node):
        if isinstance(node, ProgramNode):
            self.__compile_program(node)
        elif isinstance(node, ExpressionStatement):
            self.__compile_expression_statement(node)
        elif isinstance(node, BinOpNode):
            return self.__compile_bin_op(node)
        elif isinstance(node, NumberNode):
            return self.__compile_number(node)
        elif isinstance(node, VarAssignNode):
            return self.__compile_var_assign(node)
        elif isinstance(node, VarAccessNode):
            return self.__compile_var_access(node)
        else:
            raise Exception(f"Unknown node type: {type(node)}")

    def __compile_program(self, node):
        func_name = "main"
        param_type = []
        return_type = self.type_map["int"]

        fn_type = ir.FunctionType(return_type, param_type)
        func = ir.Function(self.module, fn_type, name=func_name)

        block = func.append_basic_block(f"{func_name}_entry")
        self.builder = ir.IRBuilder(block)

        for stmt in node.statements:
            self.compile(stmt)

        return_value = ir.Constant(self.type_map["int"], 0)
        self.builder.ret(return_value)

        print(self.module)
        return self.module 

    def __compile_expression_statement(self, node):
        self.compile(node.expr)

    def __compile_bin_op(self, node):
        left_value, _ = self.__resolve_value(node.left_node)
        right_value, _ = self.__resolve_value(node.right_node)

        if node.op_tok is None:
            raise Exception("Missing operator in BinOpNode")

        if node.op_tok.type == TT_PLUS:
            return self.builder.add(left_value, right_value), self.type_map["int"]
        elif node.op_tok.type == TT_MINUS:
            return self.builder.sub(left_value, right_value), self.type_map["int"]
        elif node.op_tok.type == TT_MUL:
            return self.builder.mul(left_value, right_value), self.type_map["int"]
        elif node.op_tok.type == TT_DIV:
            return self.builder.sdiv(left_value, right_value), self.type_map["int"]
        elif node.op_tok.type == TT_MOD:
            return self.builder.srem(left_value, right_value), self.type_map["int"]

        raise Exception(f"Unsupported binary operation: {node.op_tok.value}")

    def __compile_number(self, node):
        value = node.tok.value
        if isinstance(value, int):
            return ir.Constant(self.type_map["int"], value)
        elif isinstance(value, float):
            return ir.Constant(self.type_map["float"], value)
        else:
            raise Exception(f"Unsupported number type: {type(value)}")

    def __compile_var_assign(self, node):
        var_name = node.var_name_tok.value

        if node.value_node is None:
            # Default to int if no value provided
            ptr = self.builder.alloca(self.type_map["int"])
            self.env.define(var_name, ptr, self.type_map["int"], initialized=False)
        else:
            value, typ = self.__resolve_value(node.value_node)

            existing = self.env.lookup(var_name)
            if existing is None:
                # Type inferred from value
                ptr = self.builder.alloca(typ)
                self.builder.store(value, ptr)
                self.env.define(var_name, ptr, typ, initialized=True)
            else:
                ptr, existing_type, _init = existing

                if existing_type != typ:
                    raise Exception(
                        f"Type mismatch: cannot assign value of type {typ} to variable '{var_name}' of type {existing_type}"
                    )

                self.builder.store(value, ptr)
                self.env.set_initialized(var_name)

    def __compile_var_access(self, node):
        var_name = node.var_name_tok.value
        entry = self.env.lookup(var_name)
        if entry is None:
            raise Exception(f"Variable '{var_name}' not declared")

        ptr, typ, initialized = entry
        if not initialized:
            raise Exception(f"Variable '{var_name}' used before initialization")

        return self.builder.load(ptr), typ


    def __resolve_value(self, node):
        if isinstance(node, NumberNode):
            val = node.tok.value
            if isinstance(val, int):
                return ir.Constant(self.type_map["int"], val), self.type_map["int"]
            elif isinstance(val, float):
                return ir.Constant(self.type_map["float"], val), self.type_map["float"]
        elif isinstance(node, BinOpNode):
            return self.__compile_bin_op(node)
        elif isinstance(node, VarAccessNode):
            return self.__compile_var_access(node)

        raise Exception(f"Unsupported node type for value resolution: {type(node)}")
