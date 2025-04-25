from src.lex.lex import run
from src.Parser.parser import Parser
from src.compiler.compiler import Compiler
from llvmlite import binding as llvm
import ctypes

def exec(text):
    tokens, error = run(text)
    if error:
        print("Lexer Error:", error)
        return None

    print("Tokens:", tokens)

    parser = Parser(tokens)
    ast = parser.parse()

    if ast.error:
        print("Parser Error:", ast.error)
        return None

    return ast.node

def llvm_to_ctypes(llvm_type):
    typename = str(llvm_type)

    if typename == 'i1':
        return ctypes.c_bool
    elif typename == 'i8':
        return ctypes.c_int8
    elif typename == 'i16':
        return ctypes.c_int16
    elif typename == 'i32':
        return ctypes.c_int32
    elif typename == 'i64':
        return ctypes.c_int64
    elif typename == 'float':
        return ctypes.c_float
    elif typename == 'double':
        return ctypes.c_double
    elif typename == 'i8*':
        return ctypes.c_char_p  
    elif typename == 'void':
        return None
    else:
        return None

def compile_ast(ast_node, output_filename="program.l"):
    compiler = Compiler()

    try:
        mod_ir, mod_text = compiler.compile(ast_node)

        with open(output_filename, "w") as f:
            f.write(mod_text)
        print(f"[\u2713] LLVM IR saved to '{output_filename}'")

        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()

        mod = llvm.parse_assembly(mod_text)
        mod.verify()

        target = llvm.Target.from_default_triple()
        target_machine = target.create_target_machine()
        engine = llvm.create_mcjit_compiler(mod, target_machine)
        engine.finalize_object()
        engine.run_static_constructors()

        for func in mod_ir.functions:
            if func.is_declaration:
                continue

            print(f"Found function: {func.name}")
            func_ptr = engine.get_function_address(func.name)

            ret_type = func.function_type.return_type
            param_types = func.function_type.args

            c_ret_type = llvm_to_ctypes(ret_type)
            c_param_types = [llvm_to_ctypes(p) for p in param_types]
            print("return type is ", c_ret_type)
            if c_ret_type is None and any(t is None for t in c_param_types):
                print(f"[!] Skipping function '{func.name}' due to unsupported types.")
                continue

            cfunc_type = ctypes.CFUNCTYPE(c_ret_type if c_ret_type else None, *c_param_types)
            cfunc = cfunc_type(func_ptr)

            # Generate the appropriate arguments for the function
            dummy_args = []
            for ctype in c_param_types:
                # Assign dummy values based on the expected type
                if ctype == ctypes.c_void_p:
                    dummy_args.append(ctypes.c_void_p())  # Example void pointer
                elif ctype == ctypes.c_char_p:
                    dummy_args.append(ctypes.c_char_p(b"example"))  # Example string
                elif ctype == ctypes.c_int32:
                    dummy_args.append(ctypes.c_int32(42))  # Example integer value
                elif ctype == ctypes.c_int64:
                    dummy_args.append(ctypes.c_int64(123456789))  # Example larger integer
                elif ctype == ctypes.c_float:
                    dummy_args.append(ctypes.c_float(3.14159))  # Example float value
                elif ctype == ctypes.c_double:
                    dummy_args.append(ctypes.c_double(2.71828))  # Example double value
                else:
                    dummy_args.append(ctype())  # Default case for unsupported types

            print(f"Calling {func.name} with arguments {dummy_args}...")
            result = cfunc(*dummy_args)
            
            # Handle return values properly
            if c_ret_type == ctypes.c_char_p:
                print(f"Result of {func.name}: {result.decode()}")  # For string return values
            elif c_ret_type is not None:
                print(f"Result of {func.name}: {result}")
            else:
                print(f"{func.name} returned void.")

        print("[\u2713] Execution complete.")

    except Exception as e:
        print("[\u2717] Compilation error:", e)

def main():
    filename = "program.tri"
    output_file = "program.l"

    try:
        with open(filename, "r") as file:
            code = file.read()

        result = exec(code)

        if result:
            print("AST:", result)
            compile_ast(result, output_file)

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print("Runtime Error:", e)

if __name__ == "__main__":
    main()
