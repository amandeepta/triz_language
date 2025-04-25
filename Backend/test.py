from flask import Flask, request, jsonify
from flask_cors import CORS
import io
import sys
import contextlib
import ctypes
import llvmlite.binding as llvm
from src.lex.lex import run
from src.Parser.parser import Parser
from src.compiler.compiler import Compiler

app = Flask(__name__)
CORS(app)

# Initialize LLVM for JIT
llvm.initialize()
llvm.initialize_native_target()
llvm.initialize_native_asmprinter()
_target = llvm.Target.from_default_triple()
_target_machine = _target.create_target_machine()

# Create execution engine
def _create_execution_engine():
    backing_mod = llvm.parse_assembly("")
    engine = llvm.create_mcjit_compiler(backing_mod, _target_machine)
    return engine

# Compile IR module to engine
def _compile_ir(mod):
    llvm_ir = str(mod)
    parsed_mod = llvm.parse_assembly(llvm_ir)
    parsed_mod.verify()
    engine = _create_execution_engine()
    engine.add_module(parsed_mod)
    engine.finalize_object()
    engine.run_static_constructors()
    return engine

# Generate AST from source code
def _exec_text(text):
    tokens, error = run(text)
    if error:
        return None, f"Lexer Error: {error}"
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error:
        return None, f"Parser Error: {ast.error}"
    return ast.node, None

# JIT run the AST and capture output
def _jit_run(ast_node):
    # Compile AST to IR Module
    compiler = Compiler()
    ir_mod = compiler.compile(ast_node)
    if not ir_mod:
        return None, "Compilation returned no IR"

    # Set triple and data layout
    ir_mod.triple = llvm.get_default_triple()
    ir_mod.data_layout = _target_machine.target_data

    libc = ctypes.CDLL("msvcrt.dll")
    printf_addr = ctypes.cast(libc.printf, ctypes.c_void_p).value
    llvm.add_symbol("printf", printf_addr)

    # Capture stdout
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        engine = _compile_ir(ir_mod)
        # Invoke main
        main_addr = engine.get_function_address("main")
        if not main_addr:
            print("Error: 'main' not found")
        else:
            func = ctypes.CFUNCTYPE(ctypes.c_int)(main_addr)
            ret = func()
            print(f"Return: {ret}")
    output = buf.getvalue()
    return output, None

@app.route('/', methods=['POST'])
def compile_code():
    data = request.get_json() or {}
    code = data.get('inputCode', '')
    input_values = data.get('input', None)

    # Get AST
    ast_root, err = _exec_text(code)
    if err:
        return jsonify({'error': err}), 400

    # Run JIT and capture output
    output, err = _jit_run(ast_root)
    if err:
        return jsonify({'error': err}), 500

    return jsonify({'output': output})

if __name__ == '__main__':
    app.run(debug=True)
