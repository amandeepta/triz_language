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
            "VOID": ir.VoidType()
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
        elif isinstance(node, VarReAssignNode):
            return self.__compile_var_reassign(node)
        elif isinstance(node, VarAccessNode):
            return self.__compile_var_access(node)
        elif isinstance(node, FunctionNode):
            return self.__compile_function(node)
        elif isinstance(node, FunctionCallNode):
            return self.__compile_function_call(node)
        elif isinstance(node, ReturnNode):  # Handle ReturnNode
            self.__compile_return(node)
        else:
            raise Exception(f"Unknown node type: {type(node)}")
        
    def __compile_function(self, node):
        func_name = node.func_name_tok.value
        print(f"Compiling function: {func_name}")

        param_types = [self.type_map[param_type_tok.value] for (_, param_type_tok) in node.param_toks]
        print(f"[DEBUG] Parameter types for function '{func_name}': {param_types}")


        print(type(node.return_type))
        return_type = self.type_map[node.return_type.value]

        print(f"Function return type: {return_type}")

        fn_type = ir.FunctionType(return_type, param_types)

        func = ir.Function(self.module, fn_type, name=func_name)
        print(f"LLVM Function created: {func}")

        block = func.append_basic_block(f"{func_name}_entry")
        self.builder = ir.IRBuilder(block)

        self.env = Environment(parent=self.env)

        for i, (param_name_tok, param_type_tok) in enumerate(node.param_toks):
            llvm_type = self.type_map[param_type_tok.value]
            ptr = self.builder.alloca(llvm_type, name=param_name_tok.value)
            self.builder.store(func.args[i], ptr)
            self.env.define(param_name_tok.value, ptr, llvm_type, initialized=True)
            print(f"[DEBUG] Allocated variable '{param_name_tok.value}' of type {llvm_type}")

        for stmt in node.body_node.statements:
            print(f"[DEBUG] Compiling statement: {stmt}")
            if isinstance(stmt, ReturnNode):
                print("[DEBUG] Found return statement")
                return_value, inferred_type = self.__resolve_value(stmt.return_val)
                print(f"[DEBUG] Inferred return type: {inferred_type}, Expected: {return_type}")
                if inferred_type != return_type:
                    raise Exception(f"Return type mismatch: Expected {return_type} but got {inferred_type}")
            
            self.compile(stmt)

        if not self.builder.block.is_terminated:
            print(f"[DEBUG] Function '{func_name}' not explicitly terminated")
            if return_type == self.type_map["void"]:
                self.builder.ret_void()
                print("[DEBUG] Returned void")
            else:
                default_ret = ir.Constant(return_type, 0)
                self.builder.ret(default_ret)
                print("[DEBUG] Returned default value 0")

        self.env = self.env.parent
        print(f"[INFO] Function '{func_name}' compiled successfully\n")

    def __compile_function_call(self, node):
        func_name = node.func_name_tok.value
        func = self.module.get_global(func_name)
        
        if func is None:
            raise Exception(f"Function '{func_name}' not declared")
        
        args = [self.__resolve_value(arg)[0] for arg in node.arg_nodes]

        if len(args) != len(func.args):
            raise Exception(f"Function '{func_name}' expects {len(func.args)} arguments, but {len(args)} were provided")
   

        self.builder.call(func, args)



    def __compile_block(self, node):
        for stmt in node.statements:
            self.compile(stmt)

    def __compile_return(self, node):
        return_value, _ = self.__resolve_value(node.return_val)  # Resolve return value

        # Add return instruction to the builder
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
        # Ensure the block is not already terminated before adding a return
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

    def __compile_var_reassign(self, node):
        var_name = node.var_name_tok.value

        value, type = self.__resolve_value(node.value_node)

        existing = self.env.lookup(var_name)

        if not existing:
            raise Exception(f"variable '{var_name}' is not declared before reassignment")
        
        ptr, existing_type, initialized = existing

        if existing_type != type:
            raise Exception(f"Type mismatch can not assign value of type {type} to variable '{var_name} of type {existing_type}'")
        
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
