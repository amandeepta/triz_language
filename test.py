from src.lex.lex import run
from src.Parser.parser import Parser
from src.compiler.compiler import Compiler

import llvmlite.binding as llvm
import os
import subprocess

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



def compile_ast(ast_node, output_filename="program.l", exe_name="program.exe"):
    compiler = Compiler()

    try:
        llvm_ir = compiler.compile(ast_node)
        if not llvm_ir:
            print("Compilation failed: No IR returned.")
            return

        # Save LLVM IR to .ll
        with open(output_filename, "w") as f:
            f.write(str(llvm_ir))
        print(f"[✓] LLVM IR saved to '{output_filename}'")

        # Initialize LLVM
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()

        # Parse IR and verify
        mod = llvm.parse_assembly(str(llvm_ir))
        mod.verify()

        # Target machine for native code generation
        target = llvm.Target.from_default_triple()
        target_machine = target.create_target_machine()

        # Emit object file
        obj_code = target_machine.emit_object(mod)
        obj_filename = "program.o"
        with open(obj_filename, "wb") as f:
            f.write(obj_code)
        print(f"[✓] Object file generated: {obj_filename}")

        # Link using clang
        clang_cmd = f"clang {obj_filename} -o {exe_name}"
        result = subprocess.run(clang_cmd, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            print("[✗] Linking failed:")
            print(result.stderr)
        else:
            print(f"[✓] Executable created: {exe_name}")

    except Exception as e:
        print("[✗] Compilation error:", e)



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
