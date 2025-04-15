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
            'void': ir.VoidType(),
            "INT": ir.IntType(32),
            "FLOAT": ir.FloatType(),
            "VOID": ir.VoidType(),
            "STRING": ir.IntType(8).as_pointer(),
            "string": ir.IntType(8).as_pointer(),
            "STR" : ir.IntType(8).as_pointer(),
            "str" : ir.IntType(8).as_pointer(),
        }
        self.env = Environment()

    def compile(self, node):
        try:
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
            elif isinstance(node, VarReAssignNode):
                return self.__compile_var_reassign(node)
            elif isinstance(node, VarAccessNode):
                return self.__compile_var_access(node)
            elif isinstance(node, FunctionNode):
                return self.__compile_function(node)
            elif isinstance(node, FunctionCallNode):
                return self.__compile_function_call(node)
            elif isinstance(node, PrintNode):
                return self.__compile_print(node)

            elif isinstance(node, ReturnNode):
                self.__compile_return(node)
            elif isinstance(node, IfNode):
                self.__compile_if(node)
            else:
                raise Exception(f"Unknown node type: {type(node)}")
        except Exception as e:
            print(f"[ERROR] Compilation failed: {str(e)}")
            raise e
        
    def __compile_if(self, node):
        condition_value, condition_type = self.__resolve_value(node.condition_node)

        if condition_type != self.type_map["bool"]:
            raise Exception("Condition in 'if' statement must be of tyoe bool")
        
        then_block = self.builder.append_basic_block("if_then")
        else_block = self.builder.append_basic_block("if_else") if node.else_node else None
        merge_block = self.builder.append_basic_block("if_merge")

        if else_block:
            self.builder.cbranch(condition_value, then_block, else_block)
        else:
            self.builder.cbranch(condition_value, then_block, merge_block)

        self.builder.position_at_end(then_block)
        self.__compile_block(node.then_node)
        if not self.builder.block.is_terminated:
            self.builder.branch(merge_block)

        if else_block:
            self.builder.position_at_end(else_block)
            self.__compile_block(node.else_node)
            if not self.builder.block.is_terminated:
                self.builder.branch(merge_block)

        self.builder.position_at_end(merge_block)


    

    def __compile_function(self, node):
        func_name = node.func_name_tok.value
        param_types = [self.type_map[param_type_tok.value] for (_, param_type_tok) in node.param_toks]
        return_type = self.type_map.get(node.return_type.value if node.return_type else "int", self.type_map["int"])

        fn_type = ir.FunctionType(return_type, param_types)
        func = ir.Function(self.module, fn_type, name=func_name)
        block = func.append_basic_block(f"{func_name}_entry")
        self.builder = ir.IRBuilder(block)
        self.env = Environment(parent=self.env)

        for i, (param_name_tok, param_type_tok) in enumerate(node.param_toks):
            llvm_type = self.type_map[param_type_tok.value] if param_type_tok.value != "string" else ir.IntType(8).as_pointer()
            ptr = self.builder.alloca(llvm_type, name=param_name_tok.value)
            self.builder.store(func.args[i], ptr)
            self.env.define(param_name_tok.value, ptr, llvm_type, initialized=True)

        for stmt in node.body_node.statements:
            if isinstance(stmt, ReturnNode):
                return_value, inferred_type = self.__resolve_value(stmt.return_val)
                if inferred_type != return_type:
                    raise Exception(f"Return type mismatch: Expected {return_type} but got {inferred_type}")
                self.builder.ret(return_value)
                continue
            self.compile(stmt)

        if not self.builder.block.is_terminated:
            if return_type == self.type_map["void"]:
                self.builder.ret_void()
            else:
                default_ret = ir.Constant(return_type, 0)
                self.builder.ret(default_ret)

        self.env = self.env.parent
        
    def __compile_print(self, node):
        value, typ = self.__resolve_value(node.expr_node)

        printf = self.module.globals.get('printf')
        if printf is None:
            voidptr_ty = ir.IntType(8).as_pointer()
            printf_ty = ir.FunctionType(ir.IntType(32), [voidptr_ty], var_arg=True)
            printf = ir.Function(self.module, printf_ty, name="printf")

        fmt_str = None

        if typ == self.type_map["string"]:
            fmt_str = "%s\n\0"
            args = [value]
        elif typ == self.type_map["int"]:
            fmt_str = "%d\n\0"
            args = [value]
        elif typ == self.type_map["float"]:
            fmt_str = "%f\n\0"
            args = [value]
        elif typ == self.type_map["bool"]:
            int_val = self.builder.zext(value, ir.IntType(32))
            fmt_str = "%d\n\0"
            args = [int_val]
        else:
            raise Exception(f"Print does not support type: {typ}")

        fmt_bytes = bytearray(fmt_str.encode("utf8"))
        const_fmt = ir.Constant(ir.ArrayType(ir.IntType(8), len(fmt_bytes)), fmt_bytes)
        global_fmt = ir.GlobalVariable(self.module, const_fmt.type, name=f"print_fmt_{typ}")
        global_fmt.linkage = 'internal'
        global_fmt.global_constant = True
        global_fmt.initializer = const_fmt

        fmt_ptr = self.builder.bitcast(global_fmt, ir.IntType(8).as_pointer())
        self.builder.call(printf, [fmt_ptr] + args)



    def __compile_function_call(self, node):
        func_name = node.func_name_tok.value
        func = self.module.get_global(func_name)

        if func is None:
            raise Exception(f"Function '{func_name}' not declared")

        args = [self.__resolve_value(arg)[0] for arg in node.arg_nodes]

        if len(args) != len(func.args):
            raise Exception(f"Function '{func_name}' expects {len(func.args)} arguments, but {len(args)} were provided")

        call_result = self.builder.call(func, args)

        return_type = func.function_type.return_type

        return call_result, return_type

    def __compile_block(self, node):
        for stmt in node.statements:
            self.compile(stmt)

    def __compile_return(self, node):
        return_value, _ = self.__resolve_value(node.return_val)
        self.builder.ret(return_value)

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
        if not self.builder.block.is_terminated:
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
        elif node.op_tok.type == TT_GT:
            return self.builder.icmp_signed('>', left_value, right_value), self.type_map["bool"]
        elif node.op_tok.type == TT_LT:
            return self.builder.icmp_signed('<', left_value, right_value), self.type_map["bool"]
        elif node.op_tok.type == TT_EE:
            return self.builder.icmp_signed('==', left_value, right_value), self.type_map["bool"]
        elif node.op_tok.type == TT_NE:
            return self.builder.icmp_signed('!=', left_value, right_value), self.type_map["bool"]
        elif op == '>=':
            return self.builder.icmp_signed('>=', left_value, right_value), self.type_map["bool"]
        elif op == '<=':
            return self.builder.icmp_signed('<=', left_value, right_value), self.type_map["bool"]

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
            ptr = self.builder.alloca(self.type_map["int"])
            self.env.define(var_name, ptr, self.type_map["int"], initialized=False)
        else:
            value, typ = self.__resolve_value(node.value_node)

            existing = self.env.lookup(var_name)
            if existing is None:
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

    def __compile_var_reassign(self, node):
        var_name = node.var_name_tok.value

        value, type = self.__resolve_value(node.value_node)

        existing = self.env.lookup(var_name)

        if not existing:
            raise Exception(f"variable '{var_name}' is not declared before reassignment")
        
        ptr, existing_type, initialized = existing

        if existing_type != type:
            raise Exception(f"Type mismatch cannot assign value of type {type} to variable '{var_name}' of type {existing_type}")
        
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

    def __compile_string(self, node):
        string_val = node.token.value
        byte_array = bytearray(string_val.encode("utf8")) + b'\00'
        const_array = ir.Constant(ir.ArrayType(ir.IntType(8), len(byte_array)), byte_array)

        unique_name = f".str_{len(self.module.global_values)}"
        global_str = ir.GlobalVariable(self.module, const_array.type, name=unique_name)
        global_str.linkage = 'internal'
        global_str.global_constant = True
        global_str.initializer = const_array

        ptr = self.builder.bitcast(global_str, ir.IntType(8).as_pointer())
        return ptr, self.type_map["string"]


    def __resolve_value(self, node):
        if isinstance(node, NumberNode):
            val = node.tok.value
            if isinstance(val, int):
                return ir.Constant(self.type_map["int"], val), self.type_map["int"]
            elif isinstance(val, float):
                return ir.Constant(self.type_map["float"], val), self.type_map["float"]
        elif isinstance(node, BooleanNode):
            val = node.tok.value
            return ir.Constant(self.type_map["bool"], 1 if val else 0), self.type_map["bool"]
        elif isinstance(node, BinOpNode):
            return self.__compile_bin_op(node)
        elif isinstance(node, StringNode):
            return self.__compile_string(node)
        elif isinstance(node, VarAccessNode):
            return self.__compile_var_access(node)
        elif isinstance(node, FunctionCallNode):
            return self.__compile_function_call(node)

        raise Exception(f"Unsupported node type for value resolution: {type(node)}")
