import os
import shutil
import subprocess
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from src.lex.lex import run
from src.Parser.parser import Parser
from src.compiler.compiler import Compiler

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
CORS(app)

def exec_ast(text):
    print("[DEBUG] exec_ast: received text:", text)
    tokens, err = run(text)
    if err:
        print(f"[ERROR] exec_ast: lexer error: {err}")
        return None, f"Lexer error: {err}"
    print("[DEBUG] exec_ast: tokens:", tokens)
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error:
        print(f"[ERROR] exec_ast: parser error: {ast.error}")
        return None, f"Parser error: {ast.error}"
    print("[DEBUG] exec_ast: AST node:", ast.node)
    return ast.node, None

def compile_ast(ast_node, base="program"):
    print("[DEBUG] compile_ast: starting compilation")
    compiler = Compiler()
    _, ir = compiler.compile(ast_node)
    print("[DEBUG] compile_ast: generated LLVM IR:\n", ir)
    ll = f"{base}.ll"
    exe = f"{base}.exe" if os.name == "nt" else f"{base}.out"
    print(f"[DEBUG] compile_ast: writing IR to {ll}")
    with open(ll, "w") as f:
        f.write(ir)

    cc = os.environ.get("CC", "")
    clang = shutil.which(cc) or shutil.which("clang") or shutil.which("clang.exe")
    print(f"[DEBUG] compile_ast: located clang at: {clang}")
    if not clang:
        msg = "clang not found"
        print(f"[ERROR] compile_ast: {msg}")
        return None, msg
    
    # Corrected MinGW paths for Windows
    mingw_dir = "C:/MinGW"  # Make sure this is correct for your installation
    clang_flags = [
        clang, ll, "-o", exe, 
        "--target=i686-w64-mingw32",  # Use i686 for 32-bit MinGW target
        "-fuse-ld=lld", 
        "-L", os.path.join(mingw_dir, "lib"),  # Ensure you're using 32-bit MinGW libraries
        "-I", os.path.join(mingw_dir, "include"),  # Ensure the include path for MinGW headers
        "-m32",  # Explicitly set 32-bit architecture
    ]
    print(f"[DEBUG] compile_ast: running clang with flags: {clang_flags}")
    proc = subprocess.run(clang_flags, capture_output=True, text=True)

    print(f"[DEBUG] compile_ast: clang return code: {proc.returncode}")
    print(f"[DEBUG] compile_ast: clang stdout:\n{proc.stdout.strip()}")
    print(f"[DEBUG] compile_ast: clang stderr:\n{proc.stderr.strip()}")
    if proc.returncode != 0:
        msg = proc.stderr.strip()
        print(f"[ERROR] compile_ast: compilation failed: {msg}")
        return None, msg

    abs_exe = os.path.abspath(exe)
    print(f"[DEBUG] compile_ast: running executable {abs_exe}")
    runp = subprocess.run([abs_exe], capture_output=True, text=True)
    print(f"[DEBUG] compile_ast: program return code: {runp.returncode}")
    print(f"[DEBUG] compile_ast: program stdout:\n{runp.stdout.strip()}")
    return {"name": base, "stdout": runp.stdout.strip(), "return": runp.returncode}, None

@app.route('/compile', methods=['POST'])
def compile_code():
    data = request.get_json() or {}
    print("[DEBUG] compile_code: received JSON:", data)
    code = data.get("inputCode", "").strip()
    if not code:
        print("[ERROR] compile_code: No code provided")
        return jsonify(error="No code provided"), 400
    ast_node, err = exec_ast(code)
    if err:
        print(f"[ERROR] compile_code: exec_ast error: {err}")
        return jsonify(error=err), 400
    res, err = compile_ast(ast_node)
    if err:
        print(f"[ERROR] compile_code: compile_ast error: {err}")
        return jsonify(error=err), 500
    print("[DEBUG] compile_code: successful result:", res)
    return jsonify(results=[res]), 200

if __name__ == "__main__":
    print("[INFO] Starting Flask app...")
    app.run(debug=True)
