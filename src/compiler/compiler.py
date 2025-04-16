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
        self.break_targets = []
        self.continue_targets = []

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
            elif isinstance(node, WhileNode):
                self.__compile_while(node)
            elif isinstance(node, ForNode):
                self.__compile_for(node)
            
            else:
                raise Exception(f"Unknown node type: {type(node)}")
        except Exception as e:
            print(f"[ERROR] Compilation failed: {str(e)}")
            raise e
        return self.module
        
    def __compile_for(self, node):
        # --- Initialization ---
        # Evaluate the starting value (e.g., for "var i = 0", compile 0)
        init_value, init_type = self.__resolve_value(node.start_value_node)
        var_name = node.var_name.value

        # Allocate space for the loop variable and store the initial value.
        var_ptr = self.builder.alloca(init_type, name=var_name)
        self.builder.store(init_value, var_ptr)
        self.env.define(var_name, var_ptr, init_type, initialized=True)
        
        # --- Create Basic Blocks ---
        # Create blocks for the condition check, loop body, update (step), and after the loop.
        cond_block = self.builder.append_basic_block("for_cond")
        body_block = self.builder.append_basic_block("for_body")
        update_block = self.builder.append_basic_block("for_update")
        end_block = self.builder.append_basic_block("for_end")

        self.break_targets.append(end_block)  # Add the exit block for break
        self.continue_targets.append(cond_block)  # Add the condition block for continue
        
        # Jump to the condition block
        self.builder.branch(cond_block)
        
        # --- Condition Block ---
        self.builder.position_at_end(cond_block)
        # Evaluate the loop condition; must be boolean.
        condition_value, cond_type = self.__resolve_value(node.condition_node)
        if cond_type != self.type_map["bool"]:
            raise Exception("For loop condition must be of type 'bool'")
        self.builder.cbranch(condition_value, body_block, end_block)
        
        # --- Loop Body Block ---
        self.builder.position_at_end(body_block)
        # Compile the loop body.
        self.__compile_block(node.body_node)
        

        # When the body finishes (and if not terminated by a return), go to the update block.
        if not self.builder.block.is_terminated:
            self.builder.branch(update_block)
        
        # --- Update Block ---
        self.builder.position_at_end(update_block)
        # Evaluate the step expression (e.g., for "i = i + 1").
        step_value, step_type = self.__resolve_value(node.step_value_node)
        if step_type != init_type:
            raise Exception("For loop step expression must match the type of the loop variable")
        # Update the loop variable.
        self.builder.store(step_value, var_ptr)
        # Go back to the condition check.
        self.builder.branch(cond_block)
        
        # --- End Block ---
        self.builder.position_at_end(end_block)
        # --- Pop break and continue targets ---
        self.break_targets.pop()  # Pop the break target after loop ends
        self.continue_targets.pop()  # Pop the continue target after loop ends
        
    def __compile_while(self, node):
        cond_block = self.builder.append_basic_block("while_cond")
        body_block = self.builder.append_basic_block("while_body")
        while_end = self.builder.append_basic_block("while_end")
        self.break_targets.append(while_end)
        self.continue_targets.append(cond_block)
        
        self.builder.branch(cond_block)
        self.builder.position_at_end(cond_block)

        # Resolve condition
        condition_value, condition_type = self.__resolve_value(node.condition_node)

        if condition_type != self.type_map["bool"]:
            raise Exception("Condition in WHILE statement must be of type 'bool'")

        # Conditional branch
        self.builder.cbranch(condition_value, body_block, while_end)

        # Set up the body block
        self.builder.position_at_end(body_block)
        
        # Compile the block inside the while loop
        self.__compile_block(node.body_node)

        # Check if a break needs to be handled
        if not self.builder.block.is_terminated:
            self.builder.branch(cond_block)

        # Pop break and continue targets
        self.builder.position_at_end(while_end)



        
    def __compile_if(self, node):
        condition_value, condition_type = self.__resolve_value(node.condition_node)

        if condition_type != self.type_map["bool"]:
            raise Exception("Condition in IF statement must be of type 'bool'")

        then_block = self.builder.append_basic_block("if_then")
        else_block = self.builder.append_basic_block("if_else") if node.else_node else None
        merge_block = self.builder.append_basic_block("if_merge")

        if else_block:
            self.builder.cbranch(condition_value, then_block, else_block)
        else:
            self.builder.cbranch(condition_value, then_block, merge_block)

        # Compile then block
        self.builder.position_at_end(then_block)
        self.__compile_block(node.then_node)
        if not self.builder.block.is_terminated:
            self.builder.branch(merge_block)

        # Compile else block (if it exists)
        if else_block:
            self.builder.position_at_end(else_block)
            self.__compile_block(node.else_node)
            if not self.builder.block.is_terminated:
                self.builder.branch(merge_block)

        # Merge block
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
        
    def __compile_print(self, node: PrintNode):
        printf = self.module.globals.get('printf')
        if printf is None:
            voidptr_ty = ir.IntType(8).as_pointer()
            printf_ty = ir.FunctionType(ir.IntType(32), [voidptr_ty], var_arg=True)
            printf = ir.Function(self.module, printf_ty, name="printf")

        format_parts = []
        args = []

        for expr in node.expr_nodes:
            value, typ = self.__resolve_value(expr)

            if typ == self.type_map["string"]:
                format_parts.append("%s")
                if isinstance(value.type, ir.PointerType) and isinstance(value.type.pointee, ir.PointerType):
                    loaded = self.builder.load(value)
                    casted = self.builder.bitcast(loaded, ir.IntType(8).as_pointer())
                    args.append(casted)
                else:
                    casted = self.builder.bitcast(value, ir.IntType(8).as_pointer())
                    args.append(casted)

            elif typ == self.type_map["int"]:
                format_parts.append("%d")
                args.append(value)

            elif typ == self.type_map["float"]:
                format_parts.append("%f")
                args.append(value)

            elif typ == self.type_map["bool"]:
                format_parts.append("%d")
                casted = self.builder.zext(value, ir.IntType(32))
                args.append(casted)

            else:
                raise Exception(f"Print does not support type: {typ}")

        fmt_str = " ".join(format_parts) + "\n\0"
        fmt_name = f"print_fmt_{len(format_parts)}"

        fmt_bytes = bytearray(fmt_str.encode("utf8"))
        const_fmt = ir.Constant(ir.ArrayType(ir.IntType(8), len(fmt_bytes)), fmt_bytes)

        if fmt_name not in self.module.globals:
            global_fmt = ir.GlobalVariable(self.module, const_fmt.type, name=fmt_name)
            global_fmt.linkage = 'internal'
            global_fmt.global_constant = True
            global_fmt.initializer = const_fmt
        else:
            global_fmt = self.module.get_global(fmt_name)

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
            if isinstance(stmt, BreakNode):
                # If it's a break statement, jump to the break target (exit point of the loop)
                self.builder.branch(self.break_targets[-1])  # Jump to the while_end block
            elif isinstance(stmt, ContinueNode):
                # If it's a continue statement, jump to the continue target (loop condition)
                self.builder.branch(self.continue_targets[-1])  # Jump to the loop's condition check
            else :
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
        elif node.op_tok.type == TT_GTE:
            return self.builder.icmp_signed('>=', left_value, right_value), self.type_map["bool"]
        elif node.op_tok.type == TT_LTE:
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
            # Don't allocate memory or assign a type yet — just declare it in the environment
            self.env.define(var_name, None, None, initialized=False)
        else:
            value, typ = self.__resolve_value(node.value_node)

            existing = self.env.lookup(var_name)
            if existing is None or existing[0] is None:
                # Allocate now since this is the first assignment with known type
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
        
        #different for varreaassign
        elif isinstance(node, VarReAssignNode):
            
            var_name = node.var_name_tok.value
            existing = self.env.lookup(var_name)
             
            if not existing:
                raise Exception(f"Variable '{var_name}' not declared.")

            ptr, existing_type, _ = existing
            new_value, value_type = self.__resolve_value(node.value_node)
            return new_value, existing_type

        raise Exception(f"Unsupported node type for value resolution: {type(node)}")
