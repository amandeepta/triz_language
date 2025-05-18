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
    tokens_list = []
    if tokens is not None:
        tokens_list = [{'type': t.type if t.type else 'UNKNOWN', 'value': t.value} for t in tokens]
    if err:
        print(f"[ERROR] exec_ast: lexer error: {err}")
        return None, tokens_list, None, f"Lexer error: {err}"
    print("[DEBUG] exec_ast: tokens:", tokens)
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error:
        print(f"[ERROR] exec_ast: parser error: {ast.error}")
        return None, tokens_list, None, f"Parser error: {ast.error}"
    print("[DEBUG] exec_ast: AST node:", ast.node)
    ast_str = str(ast.node)
    return ast.node, tokens_list, ast_str, None

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
        return None, ir, msg
    
    # Corrected MinGW paths for Windows
    mingw_dir = "C:/MinGW"
    clang_flags = [
        clang, ll, "-o", exe, 
        "--target=i686-w64-mingw32",
        "-fuse-ld=lld", 
        "-L", os.path.join(mingw_dir, "lib"),
        "-I", os.path.join(mingw_dir, "include"),
        "-m32",
    ]
    print(f"[DEBUG] compile_ast: running clang with flags: {clang_flags}")
    proc = subprocess.run(clang_flags, capture_output=True, text=True)

    print(f"[DEBUG] compile_ast: clang return code: {proc.returncode}")
    print(f"[DEBUG] compile_ast: clang stdout:\n{proc.stdout.strip()}")
    print(f"[DEBUG] compile_ast: clang stderr:\n{proc.stderr.strip()}")
    if proc.returncode != 0:
        msg = proc.stderr.strip()
        print(f"[ERROR] compile_ast: compilation failed: {msg}")
        return None, ir, msg

    abs_exe = os.path.abspath(exe)
    print(f"[DEBUG] compile_ast: running executable {abs_exe}")
    runp = subprocess.run([abs_exe], capture_output=True, text=True)
    print(f"[DEBUG] compile_ast: program return code: {runp.returncode}")
    res = {"name": base, "stdout": runp.stdout.strip(), "return": runp.returncode}
    return res, ir, None

@app.route('/compile', methods=['POST'])
def compile_code():
    data = request.get_json() or {}
    print("[DEBUG] compile_code: received JSON:", data)
    code = data.get("inputCode", "").strip()
    if not code:
        print("[ERROR] compile_code: No code provided")
        return jsonify(error="No code provided"), 400
    ast_node, tokens, ast_repr, err = exec_ast(code)
    if err:
        return jsonify({
            'tokens': tokens,
            'ast': ast_repr,
            'ir': None,
            'result': None,
            'error': err
        }), 200
    res, ir, compile_err = compile_ast(ast_node)
    if compile_err:
        return jsonify({
            'tokens': tokens,
            'ast': ast_repr,
            'ir': ir,
            'result': None,
            'error': compile_err
        }), 200
    print(res)
    return jsonify({
        'tokens': tokens,
        'ast': ast_repr,
        'ir': ir,
        'result': res,
        'error': None
    }), 200

if __name__ == "__main__":
    print("[INFO] Starting Flask app...")
    app.run(debug=True)