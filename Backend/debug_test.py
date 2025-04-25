from src.lex.lex import run  # Import the lexer function
from src.Parser.parser import Parser  # Import the parser class
from src.compiler.compiler import Compiler  # Import the compiler class

debug_lex = True
debug_parser = True and debug_lex
debug_compiler = True and debug_parser and debug_lex

def lex(text):
    tokens, error = run(text)
    if error:
        print(f"Lexer Error: {error}")
        return None

    print(tokens)
    print("\n\n")
    return tokens

def parse(tokens):
    parser = Parser(tokens)
    ast = parser.parse()

    # Check if there is any parser error
    if ast.error:
        print("Parser Error:", ast.error)
        return None

    # If no errors, return the AST node (root node of the AST)
    return ast.node



def compile_ast(ast_node):
    # Instantiate the compiler and compile the AST
    compiler = Compiler()
    ir = compiler.compile(ast_node)
    
    if ir:
        print("LLVM IR:")
        print(ir)  # Print the generated LLVM IR


def main():
    filename = "program.tri"  # Hardcoded filename
    tokens = None
    

    try:
        with open(filename, "r") as file:
            code = file.read()
        
        if debug_lex:
            tokens = lex(code)
        
        result = None

        if tokens and debug_parser:
            result = parse(tokens)
            



        if result and debug_compiler:
            if result:
                print("AST:", result)
                print("\n\n")
                compile_ast(result)

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print("Runtime Error:", e)


if __name__ == "__main__":
    main()

