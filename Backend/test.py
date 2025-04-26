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
    tokens, err = run(text)
    if err:
        logging.error("Lexer error: %s", err)
        return None, f"Lexer error: {err}"
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error:
        logging.error("Parser error: %s", ast.error)
        return None, f"Parser error: {ast.error}"
    logging.debug("AST generated: %r", ast.node)
    return ast.node, None

def compile_ast(ast_node, output_basename="program"):
    compiler = Compiler()
    mod_ir, ir_text = compiler.compile(ast_node)

    ll_path = f"{output_basename}.ll"
    exe_path = f"{output_basename}{'.exe' if os.name == 'nt' else '.out'}"

    with open(ll_path, "w") as f:
        f.write(ir_text)
    logging.debug("Wrote LLVM IR to %s", ll_path)

    cc_env = os.environ.get("CC", "")
    clang = shutil.which(cc_env) or shutil.which("clang") or shutil.which("clang.exe")
    logging.debug("Locating clang: %s", clang)
    if not clang:
        msg = "clang not found. Please install LLVM/Clang and add it to your PATH."
        logging.error(msg)
        return None, msg

    proc = subprocess.run([clang, ll_path, "-o", exe_path], capture_output=True, text=True)
    logging.debug("clang return code: %d", proc.returncode)
    logging.debug("clang stderr: %s", proc.stderr.strip())
    if proc.returncode != 0:
        return None, proc.stderr.strip()

    logging.debug("Compiled executable: %s", exe_path)
    runner = subprocess.run([os.path.abspath(exe_path)], capture_output=True, text=True)
    logging.debug("Program stdout: %s", runner.stdout.strip())
    logging.debug("Program return code: %d", runner.returncode)

    return {
        "name": output_basename,
        "stdout": runner.stdout.strip(),
        "return": runner.returncode
    }, None

@app.route('/compile', methods=['POST'])
def compile_code():
    data = request.get_json() or {}
    code = data.get("inputCode", "").strip()
    if not code:
        logging.error("No code provided")
        return jsonify(error="No code provided"), 400

    ast_node, lex_err = exec_ast(code)
    if lex_err:
        return jsonify(error=lex_err), 400

    result, compile_err = compile_ast(ast_node)
    if compile_err:
        return jsonify(error=compile_err), 400

    return jsonify(results=[result]), 200

if __name__ == "__main__":
    app.run(debug=True)
