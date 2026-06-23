"""
Integration test to verify all compiler components are present and functional.
Tests the complete compilation pipeline end-to-end.
"""

import unittest
import os
import sys
from pathlib import Path


class TestCompilerIntegrity(unittest.TestCase):
    """Test that all required compiler components exist and work correctly."""

    def setUp(self):
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent

    # ============================================================================
    # STRUCTURE TESTS
    # ============================================================================

    def test_project_structure_exists(self):
        """Test that all required directories exist."""
        required_dirs = [
            'lexer',
            'parser',
            'semantic',
            'codegen',
            'tests',
            'examples',
        ]

        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            self.assertTrue(
                dir_path.exists() and dir_path.is_dir(),
                f"Required directory '{dir_name}' not found at {dir_path}"
            )

    def test_lexer_module_files_exist(self):
        """Test that all lexer module files exist."""
        required_files = [
            'lexer/__init__.py',
            'lexer/token.py',
            'lexer/lexer.py',
            'lexer/keywords.py',
        ]

        for file_name in required_files:
            file_path = self.project_root / file_name
            self.assertTrue(
                file_path.exists() and file_path.is_file(),
                f"Required file '{file_name}' not found at {file_path}"
            )

    def test_parser_module_files_exist(self):
        """Test that all parser module files exist."""
        required_files = [
            'parser/__init__.py',
            'parser/parser.py',
            'parser/ast_nodes.py',
        ]

        for file_name in required_files:
            file_path = self.project_root / file_name
            self.assertTrue(
                file_path.exists() and file_path.is_file(),
                f"Required file '{file_name}' not found at {file_path}"
            )

    def test_semantic_module_files_exist(self):
        """Test that all semantic module files exist."""
        required_files = [
            'semantic/__init__.py',
            'semantic/symbol_table.py',
            'semantic/type_checker.py',
            'semantic/semantic_analyzer.py',
        ]

        for file_name in required_files:
            file_path = self.project_root / file_name
            self.assertTrue(
                file_path.exists() and file_path.is_file(),
                f"Required file '{file_name}' not found at {file_path}"
            )

    def test_codegen_module_files_exist(self):
        """Test that all code generation module files exist."""
        required_files = [
            'codegen/__init__.py',
            'codegen/sam_instructions.py',
            'codegen/code_generator.py',
        ]

        for file_name in required_files:
            file_path = self.project_root / file_name
            self.assertTrue(
                file_path.exists() and file_path.is_file(),
                f"Required file '{file_name}' not found at {file_path}"
            )

    def test_root_level_files_exist(self):
        """Test that all root-level files exist."""
        required_files = [
            'main.py',
            'compiler.py',
            'README.md',
        ]

        for file_name in required_files:
            file_path = self.project_root / file_name
            self.assertTrue(
                file_path.exists() and file_path.is_file(),
                f"Required file '{file_name}' not found at {file_path}"
            )

    def test_example_files_exist(self):
        """Test that all example programs exist."""
        required_examples = [
            'examples/hello.turbo',
            'examples/fibonacci.turbo',
            'examples/factorial.turbo',
            'examples/array_sum.turbo',
            'examples/control_flow.turbo',
        ]

        for file_name in required_examples:
            file_path = self.project_root / file_name
            self.assertTrue(
                file_path.exists() and file_path.is_file(),
                f"Required example '{file_name}' not found at {file_path}"
            )

    def test_test_files_exist(self):
        """Test that all test files exist."""
        required_tests = [
            'tests/test_lexer.py',
            'tests/test_parser.py',
            'tests/test_semantic.py',
            'tests/test_codegen.py',
        ]

        for file_name in required_tests:
            file_path = self.project_root / file_name
            self.assertTrue(
                file_path.exists() and file_path.is_file(),
                f"Required test '{file_name}' not found at {file_path}"
            )

    # ============================================================================
    # IMPORT TESTS
    # ============================================================================

    def test_lexer_imports(self):
        """Test that lexer module can be imported."""
        try:
            from lexer.token import Token, TokenType
            from lexer.lexer import Lexer, LexError
            from lexer.keywords import KEYWORDS, is_keyword
        except ImportError as e:
            self.fail(f"Failed to import lexer modules: {e}")

    def test_parser_imports(self):
        """Test that parser module can be imported."""
        try:
            from parser.parser import Parser, ParseError
            from parser.ast_nodes import (
                Program, FunctionDecl, Parameter, Block, Statement,
                VariableDecl, Assignment, IfStatement, WhileStatement,
                ReturnStatement, Expression, BinaryExpression,
                UnaryExpression, FunctionCall, Literal, Identifier
            )
        except ImportError as e:
            self.fail(f"Failed to import parser modules: {e}")

    def test_semantic_imports(self):
        """Test that semantic module can be imported."""
        try:
            from semantic.symbol_table import SymbolTable, FunctionTable, Symbol
            from semantic.type_checker import TypeChecker, TypeCheckError
            from semantic.semantic_analyzer import SemanticAnalyzer, SemanticError
        except ImportError as e:
            self.fail(f"Failed to import semantic modules: {e}")

    def test_codegen_imports(self):
        """Test that code generation module can be imported."""
        try:
            from codegen.sam_instructions import OpCode, Instruction, InstructionBuffer
            from codegen.code_generator import CodeGenerator, CodeGenError
        except ImportError as e:
            self.fail(f"Failed to import code generation modules: {e}")

    def test_compiler_imports(self):
        """Test that main compiler module can be imported."""
        try:
            from compiler import TurboLangCompiler, CompilationResult, compile_file, compile_string
        except ImportError as e:
            self.fail(f"Failed to import compiler: {e}")

    # ============================================================================
    # CLASS TESTS
    # ============================================================================

    def test_token_class_exists(self):
        """Test that Token class exists and has required attributes."""
        from lexer.token import Token, TokenType

        token = Token(TokenType.INTEGER, 42, 1, 1, 2)
        self.assertEqual(token.type, TokenType.INTEGER)
        self.assertEqual(token.value, 42)
        self.assertEqual(token.line, 1)
        self.assertEqual(token.column, 1)
        self.assertEqual(token.length, 2)

    def test_lexer_class_exists(self):
        """Test that Lexer class exists and has required methods."""
        from lexer.lexer import Lexer

        lexer = Lexer("int x = 42;")
        self.assertTrue(hasattr(lexer, 'tokenize'))
        self.assertTrue(callable(lexer.tokenize))

        tokens = lexer.tokenize()
        self.assertIsInstance(tokens, list)
        self.assertGreater(len(tokens), 0)

    def test_parser_class_exists(self):
        """Test that Parser class exists and has required methods."""
        from lexer.lexer import Lexer
        from parser.parser import Parser

        lexer = Lexer("func main() { }")
        tokens = lexer.tokenize()
        parser = Parser(tokens)

        self.assertTrue(hasattr(parser, 'parse'))
        self.assertTrue(callable(parser.parse))

        ast = parser.parse()
        self.assertIsNotNone(ast)

    def test_semantic_analyzer_class_exists(self):
        """Test that SemanticAnalyzer class exists and has required methods."""
        from semantic.semantic_analyzer import SemanticAnalyzer

        analyzer = SemanticAnalyzer()
        self.assertTrue(hasattr(analyzer, 'analyze'))
        self.assertTrue(callable(analyzer.analyze))

    def test_code_generator_class_exists(self):
        """Test that CodeGenerator class exists and has required methods."""
        from codegen.code_generator import CodeGenerator

        codegen = CodeGenerator()
        self.assertTrue(hasattr(codegen, 'generate'))
        self.assertTrue(callable(codegen.generate))

    def test_compiler_class_exists(self):
        """Test that TurboLangCompiler class exists and has required methods."""
        from compiler import TurboLangCompiler

        compiler = TurboLangCompiler()
        self.assertTrue(hasattr(compiler, 'compile'))
        self.assertTrue(callable(compiler.compile))

    # ============================================================================
    # FUNCTIONALITY TESTS
    # ============================================================================

    def test_lexer_basic_functionality(self):
        """Test that lexer can tokenize basic code."""
        from lexer.lexer import Lexer
        from lexer.token import TokenType

        code = "int x = 42;"
        lexer = Lexer(code)
        tokens = lexer.tokenize()

        # Should have: INT, IDENTIFIER, ASSIGN, INTEGER, SEMICOLON, EOF
        self.assertGreaterEqual(len(tokens), 6)
        self.assertEqual(tokens[-1].type, TokenType.EOF)

    def test_parser_basic_functionality(self):
        """Test that parser can parse basic function."""
        from lexer.lexer import Lexer
        from parser.parser import Parser
        from parser.ast_nodes import Program, FunctionDecl

        code = "func main() { }"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()

        self.assertIsInstance(program, Program)
        self.assertEqual(len(program.functions), 1)
        self.assertIsInstance(program.functions[0], FunctionDecl)

    def test_semantic_analyzer_basic_functionality(self):
        """Test that semantic analyzer can validate code."""
        from lexer.lexer import Lexer
        from parser.parser import Parser
        from semantic.semantic_analyzer import SemanticAnalyzer

        code = "func main() { }"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        analyzer = SemanticAnalyzer()

        # Should not raise exception
        try:
            analyzer.analyze(program)
        except Exception as e:
            self.fail(f"Semantic analyzer raised exception: {e}")

    def test_code_generator_basic_functionality(self):
        """Test that code generator can generate assembly."""
        from lexer.lexer import Lexer
        from parser.parser import Parser
        from semantic.semantic_analyzer import SemanticAnalyzer
        from codegen.code_generator import CodeGenerator

        code = "func main() { }"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        codegen = CodeGenerator()

        assembly = codegen.generate(program)
        self.assertIsInstance(assembly, str)
        self.assertGreater(len(assembly), 0)
        self.assertIn("STOP", assembly)

    def test_compiler_basic_functionality(self):
        """Test that compiler can compile complete program."""
        from compiler import compile_string

        code = "func main() { }"
        result = compile_string(code)

        self.assertTrue(result.success)
        self.assertIsNotNone(result.output)
        self.assertIn("STOP", result.output)

    # ============================================================================
    # END-TO-END TESTS
    # ============================================================================

    def test_end_to_end_simple_program(self):
        """Test complete compilation pipeline with simple program."""
        from compiler import compile_string

        code = """
        func add(int a, int b) -> int {
            return a + b;
        }

        func main() {
            int x = 5;
            int y = 3;
            print(add(x, y));
        }
        """

        result = compile_string(code)
        self.assertTrue(result.success, f"Compilation failed: {result.error}")
        self.assertIn("PUSHIMM", result.output)
        self.assertIn("ADD", result.output)
        self.assertIn("WRITE", result.output)
        self.assertIn("STOP", result.output)

    def test_end_to_end_with_control_flow(self):
        """Test compilation with control flow structures."""
        from compiler import compile_string

        code = """
        func main() {
            int x = 0;
            if (x > 5) {
                print(1);
            } else {
                print(0);
            }
        }
        """

        result = compile_string(code)
        self.assertTrue(result.success, f"Compilation failed: {result.error}")
        self.assertIn("JUMPC", result.output)
        self.assertIn("JUMP", result.output)

    def test_end_to_end_with_while_loop(self):
        """Test compilation with while loop."""
        from compiler import compile_string

        code = """
        func main() {
            int x = 0;
            while (x < 10) {
                x = x + 1;
            }
        }
        """

        result = compile_string(code)
        self.assertTrue(result.success, f"Compilation failed: {result.error}")
        self.assertIn("JUMPC", result.output)
        self.assertIn("JUMP", result.output)

    def test_end_to_end_fibonacci(self):
        """Test compilation of fibonacci function."""
        from compiler import compile_string

        code = """
        func fibonacci(int n) -> int {
            if (n <= 1) {
                return n;
            }
            return fibonacci(n - 1) + fibonacci(n - 2);
        }

        func main() {
            print(fibonacci(5));
        }
        """

        result = compile_string(code)
        self.assertTrue(result.success, f"Compilation failed: {result.error}")
        self.assertIn("JSR", result.output)
        self.assertIn("JUMPIND", result.output)

    # ============================================================================
    # ERROR HANDLING TESTS
    # ============================================================================

    def test_lexer_error_handling(self):
        """Test that lexer properly reports errors."""
        from lexer.lexer import Lexer, LexError

        code = '"unterminated string'
        lexer = Lexer(code)

        with self.assertRaises(LexError):
            lexer.tokenize()

    def test_parser_error_handling(self):
        """Test that parser properly reports errors."""
        from lexer.lexer import Lexer
        from parser.parser import Parser, ParseError

        code = "int x 42;"  # Missing = and semicolon
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)

        with self.assertRaises(ParseError):
            parser.parse()

    def test_semantic_error_handling(self):
        """Test that semantic analyzer properly reports errors."""
        from lexer.lexer import Lexer
        from parser.parser import Parser
        from semantic.semantic_analyzer import SemanticAnalyzer, SemanticError

        code = """
        func main() {
            print(undefined_variable);
        }
        """

        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        analyzer = SemanticAnalyzer()

        with self.assertRaises(SemanticError):
            analyzer.analyze(program)

    # ============================================================================
    # TYPE SYSTEM TESTS
    # ============================================================================

    def test_type_checker_arithmetic(self):
        """Test that type checker validates arithmetic operations."""
        from semantic.type_checker import TypeChecker, TypeCheckError

        # Valid: int + int = int
        result = TypeChecker.binary_operation_type('int', '+', 'int')
        self.assertEqual(result, 'int')

        # Valid: int + float = float
        result = TypeChecker.binary_operation_type('int', '+', 'float')
        self.assertEqual(result, 'float')

        # Invalid: string + int
        with self.assertRaises(TypeCheckError):
            TypeChecker.binary_operation_type('string', '+', 'int')

    def test_type_checker_comparison(self):
        """Test that type checker validates comparison operations."""
        from semantic.type_checker import TypeChecker, TypeCheckError

        # Valid: int < int = bool
        result = TypeChecker.binary_operation_type('int', '<', 'int')
        self.assertEqual(result, 'bool')

        # Valid: int == int = bool
        result = TypeChecker.binary_operation_type('int', '==', 'int')
        self.assertEqual(result, 'bool')

        # Invalid: int < string
        with self.assertRaises(TypeCheckError):
            TypeChecker.binary_operation_type('int', '<', 'string')

    def test_type_checker_logical(self):
        """Test that type checker validates logical operations."""
        from semantic.type_checker import TypeChecker, TypeCheckError

        # Valid: bool && bool = bool
        result = TypeChecker.binary_operation_type('bool', '&&', 'bool')
        self.assertEqual(result, 'bool')

        # Invalid: int && int
        with self.assertRaises(TypeCheckError):
            TypeChecker.binary_operation_type('int', '&&', 'int')

    # ============================================================================
    # SYMBOL TABLE TESTS
    # ============================================================================

    def test_symbol_table_basic(self):
        """Test that symbol table works correctly."""
        from semantic.symbol_table import SymbolTable

        table = SymbolTable()

        # Define a symbol
        symbol = table.define("x", "int")
        self.assertEqual(symbol.name, "x")
        self.assertEqual(symbol.type_name, "int")

        # Look up symbol
        found = table.lookup("x")
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "x")

    def test_symbol_table_scopes(self):
        """Test that symbol table handles scopes correctly."""
        from semantic.symbol_table import SymbolTable

        table = SymbolTable()

        # Define in global scope
        table.define("x", "int")

        # Enter new scope
        table.push_scope()
        table.define("y", "float")

        # Can find both
        self.assertIsNotNone(table.lookup("x"))
        self.assertIsNotNone(table.lookup("y"))

        # Exit scope
        table.pop_scope()

        # Can only find x
        self.assertIsNotNone(table.lookup("x"))
        self.assertIsNone(table.lookup("y"))

    def test_function_table_basic(self):
        """Test that function table works correctly."""
        from semantic.symbol_table import FunctionTable

        table = FunctionTable()

        # Define a function
        info = table.define("add", "int", [("int", "a"), ("int", "b")])
        self.assertEqual(info.name, "add")
        self.assertEqual(info.return_type, "int")
        self.assertEqual(info.parameters_count, 2)

        # Look up function
        found = table.lookup("add")
        self.assertIsNotNone(found)

    # ============================================================================
    # INSTRUCTION SET TESTS
    # ============================================================================

    def test_instruction_buffer(self):
        """Test that instruction buffer works correctly."""
        from codegen.sam_instructions import InstructionBuffer, OpCode

        buffer = InstructionBuffer()

        # Emit instructions
        buffer.emit(OpCode.PUSHIMM, 42)
        buffer.emit(OpCode.PUSHIMM, 10)
        buffer.emit(OpCode.ADD)
        buffer.emit(OpCode.WRITE)
        buffer.emit(OpCode.STOP)

        instructions = buffer.get_instructions()
        self.assertEqual(len(instructions), 5)
        self.assertEqual(instructions[0].opcode, OpCode.PUSHIMM)
        self.assertEqual(instructions[0].operand, 42)

    # ============================================================================
    # SUMMARY TEST
    # ============================================================================

    def test_all_components_working_together(self):
        """Comprehensive test of all components working together."""
        from compiler import compile_string

        # Test simple program
        simple = "func main() { }"
        result = compile_string(simple)
        self.assertTrue(result.success)

        # Test with variables
        vars_prog = """
        func main() {
            int x = 10;
            int y = 20;
            print(x + y);
        }
        """
        result = compile_string(vars_prog)
        self.assertTrue(result.success)

        # Test with functions
        func_prog = """
        func double(int x) -> int {
            return x * 2;
        }

        func main() {
            print(double(5));
        }
        """
        result = compile_string(func_prog)
        self.assertTrue(result.success)

        # Test with control flow
        flow_prog = """
        func main() {
            int x = 5;
            if (x > 3) {
                print(1);
            }
            while (x < 10) {
                x = x + 1;
            }
        }
        """
        result = compile_string(flow_prog)
        self.assertTrue(result.success)


class TestCompilerComponentChecklist(unittest.TestCase):
    """Detailed checklist of required components."""

    def test_checklist(self):
        """Print a detailed checklist of all compiler components."""
        print("\n" + "=" * 70)
        print("TURBOLANG COMPILER - COMPONENT CHECKLIST")
        print("=" * 70)

        components = {
            "Lexer Components": [
                ("lexer/token.py", "Token and TokenType classes"),
                ("lexer/lexer.py", "Lexer with tokenize() method"),
                ("lexer/keywords.py", "Keyword definitions"),
            ],
            "Parser Components": [
                ("parser/parser.py", "Parser with recursive descent"),
                ("parser/ast_nodes.py", "All AST node classes"),
            ],
            "Semantic Components": [
                ("semantic/symbol_table.py", "SymbolTable and FunctionTable"),
                ("semantic/type_checker.py", "TypeChecker with type rules"),
                ("semantic/semantic_analyzer.py", "SemanticAnalyzer"),
            ],
            "Code Generation": [
                ("codegen/sam_instructions.py", "SaM instructions and buffer"),
                ("codegen/code_generator.py", "CodeGenerator with generate()"),
            ],
            "Main Components": [
                ("compiler.py", "TurboLangCompiler and compilation API"),
                ("main.py", "Command-line interface"),
            ],
            "Documentation": [
                ("README.md", "Complete documentation"),
            ],
            "Tests": [
                ("tests/test_lexer.py", "Lexer tests"),
                ("tests/test_parser.py", "Parser tests"),
                ("tests/test_semantic.py", "Semantic tests"),
                ("tests/test_codegen.py", "Code generation tests"),
            ],
            "Examples": [
                ("examples/hello.turbo", "Hello world program"),
                ("examples/fibonacci.turbo", "Fibonacci"),
                ("examples/factorial.turbo", "Factorial"),
                ("examples/array_sum.turbo", "Array operations"),
                ("examples/control_flow.turbo", "Control flow"),
            ],
        }

        total = 0
        found = 0

        for category, items in components.items():
            print(f"\n{category}:")
            for file_path, description in items:
                full_path = Path(__file__).parent.parent / file_path
                exists = full_path.exists()
                status = "[OK]" if exists else "[FAIL]"
                print(f"  {status} {file_path:40} - {description}")
                total += 1
                if exists:
                    found += 1

        print("\n" + "=" * 70)
        print(f"SUMMARY: {found}/{total} components found")
        print("=" * 70 + "\n")

        self.assertEqual(found, total, f"Missing {total - found} component(s)")


if __name__ == '__main__':
    unittest.main(verbosity=2)
