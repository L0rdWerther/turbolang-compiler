from typing import Optional
from lexer.lexer import Lexer, LexError
from parser.parser import Parser, ParseError
from semantic.semantic_analyzer import SemanticAnalyzer, SemanticError
from codegen.code_generator import CodeGenerator, CodeGenError

class CompilationResult:

    def __init__(self, success: bool, output: Optional[str]=None, error: Optional[str]=None):
        self.success = success
        self.output = output
        self.error = error

    def __str__(self) -> str:
        if self.success:
            return f'Compilation successful\n\n{self.output}'
        else:
            return f'Compilation failed:\n{self.error}'

class TurboLangCompiler:

    def __init__(self, verbose: bool=False):
        self.verbose = verbose

    def compile(self, source_code: str) -> CompilationResult:
        try:
            if self.verbose:
                print('Phase 1: Pre-Race Inspection...')
            lexer = Lexer(source_code)
            tokens = lexer.tokenize()
            if self.verbose:
                print(f'  Scrutineering: {len(tokens)} components inspected')
                for token in tokens[:10]:
                    print(f'    {token}')
                if len(tokens) > 10:
                    print(f'    ... ({len(tokens) - 10} more)')
            if self.verbose:
                print('\nPhase 2: Track Mapping...')
            parser = Parser(tokens)
            ast = parser.parse()
            if self.verbose:
                print(f'  AST mapped with {len(ast.functions)} functions')
            if self.verbose:
                print('\nPhase 3: Safety Check...')
            analyzer = SemanticAnalyzer()
            analyzer.analyze(ast)
            if self.verbose:
                print('  Safety check passed')
            if self.verbose:
                print('\nPhase 4: Turbo Injection...')
            codegen = CodeGenerator()
            assembly_code = codegen.generate(ast)
            if self.verbose:
                lines = assembly_code.split('\n')
                print(f'  Engine performance: {len(lines)} instructions generated')
            return CompilationResult(success=True, output=assembly_code)
        except LexError as e:
            error_msg = f'Pit Stop Error (Lexical): {str(e)}'
            if self.verbose:
                print(f'\n{error_msg}')
            return CompilationResult(success=False, error=error_msg)
        except ParseError as e:
            error_msg = f'Pit Stop Error (Syntax): {str(e)}'
            if self.verbose:
                print(f'\n{error_msg}')
            return CompilationResult(success=False, error=error_msg)
        except SemanticError as e:
            error_msg = f'Pit Stop Error (Semantic): {str(e)}'
            if self.verbose:
                print(f'\n{error_msg}')
            return CompilationResult(success=False, error=error_msg)
        except CodeGenError as e:
            error_msg = f'Pit Stop Error (CodeGen): {str(e)}'
            if self.verbose:
                print(f'\n{error_msg}')
            return CompilationResult(success=False, error=error_msg)
        except Exception as e:
            error_msg = f'Engine Failure (Internal): {str(e)}'
            if self.verbose:
                print(f'\n{error_msg}')
            return CompilationResult(success=False, error=error_msg)

def compile_file(filename: str, verbose: bool=False) -> CompilationResult:
    try:
        with open(filename, 'r') as f:
            source_code = f.read()
    except IOError as e:
        return CompilationResult(success=False, error=f'Cannot read file: {str(e)}')
    compiler = TurboLangCompiler(verbose=verbose)
    return compiler.compile(source_code)

def compile_string(source_code: str, verbose: bool=False) -> CompilationResult:
    compiler = TurboLangCompiler(verbose=verbose)
    return compiler.compile(source_code)
