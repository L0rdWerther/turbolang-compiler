"""
Tests for code generator.
"""

import unittest
from lexer.lexer import Lexer
from parser.parser import Parser
from semantic.semantic_analyzer import SemanticAnalyzer
from codegen.code_generator import CodeGenerator


class TestCodeGenerator(unittest.TestCase):
    """Test cases for Code Generator."""
    
    def compile(self, code: str) -> str:
        """Helper to compile code."""
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        codegen = CodeGenerator()
        return codegen.generate(program)
    
    def test_simple_main(self):
        """Test code generation for simple main."""
        code = """
        func main() {
        }
        """
        assembly = self.compile(code)
        self.assertIn("STOP", assembly)
        self.assertIn("JUMPIND", assembly)
    
    def test_integer_literal(self):
        """Test code generation for integer literal."""
        code = """
        func main() {
            int x = 42;
        }
        """
        assembly = self.compile(code)
        self.assertIn("PUSHIMM 42", assembly)
    
    def test_addition(self):
        """Test code generation for addition."""
        code = """
        func add(int a, int b) -> int {
            return a + b;
        }
        
        func main() {
        }
        """
        assembly = self.compile(code)
        self.assertIn("ADD", assembly)
    
    def test_if_statement(self):
        """Test code generation for if statement."""
        code = """
        func main() {
            if (true) {
                int x = 1;
            }
        }
        """
        assembly = self.compile(code)
        self.assertIn("JUMPC", assembly)
    
    def test_while_loop(self):
        """Test code generation for while loop."""
        code = """
        func main() {
            while (true) {
                int x = 1;
            }
        }
        """
        assembly = self.compile(code)
        self.assertIn("JUMPC", assembly)
        self.assertIn("JUMP", assembly)

    def test_do_while_loop(self):
        """Test code generation for do-while loop."""
        code = """
        func main() {
            int x = 0;
            do {
                x = x + 1;
            } while (x < 3);
        }
        """
        assembly = self.compile(code)
        self.assertIn("JUMPC", assembly)
        self.assertIn("LESS", assembly)

    def test_counted_for_loop(self):
        """Test code generation for counted for loop."""
        code = """
        func main() {
            int i = 0;
            for i = 1 to 3 {
                print(i);
            }
        }
        """
        assembly = self.compile(code)
        self.assertIn("GREATER", assembly)
        self.assertIn("JUMPC", assembly)
        self.assertIn("WRITE", assembly)
    
    def test_function_call(self):
        """Test code generation for function call."""
        code = """
        func getValue() -> int {
            return 42;
        }
        
        func main() {
            getValue();
        }
        """
        assembly = self.compile(code)
        self.assertIn("JSR", assembly)

    def test_main_entry_jump_when_not_first_function(self):
        """Test that generated assembly starts by jumping to main."""
        code = """
        func helper() -> int {
            return 1;
        }

        func main() {
            print(helper());
        }
        """
        assembly = self.compile(code)
        first_line = assembly.splitlines()[0]
        self.assertEqual(first_line, "ADDSP 1")
        self.assertIn("JSR FUNCAO_main", assembly)
        self.assertIn("JSR FUNCAO_helper", assembly)

    def test_call_has_argument_count_and_return_flag(self):
        """Test function protocol operands."""
        code = """
        func add(int a, int b) -> int {
            return a + b;
        }

        func main() {
            print(add(1, 2));
        }
        """
        assembly = self.compile(code)
        self.assertIn("JSR FUNCAO_add", assembly)
        self.assertIn("POPFBR", assembly)
        self.assertIn("ADDSP -2", assembly)
        self.assertIn("JUMPIND", assembly)

    def test_float_literal_uses_float32_bits(self):
        """Test float literal emission as IEEE-754 single precision bits."""
        code = """
        func main() {
            float x = 1.5;
        }
        """
        assembly = self.compile(code)
        self.assertIn("PUSHIMMF 1.5", assembly)

    def test_int_to_float_conversion_and_float_operation(self):
        """Test int to float conversion and typed float arithmetic."""
        code = """
        func main() {
            float x = 1 + 2.5;
        }
        """
        assembly = self.compile(code)
        self.assertIn("ITOF", assembly)
        self.assertIn("ADDF", assembly)

    def test_char_literal_uses_numeric_code(self):
        """Test char literal emission as numeric code point."""
        code = """
        func main() {
            char c = 'A';
        }
        """
        assembly = self.compile(code)
        self.assertIn("PUSHIMMCH 'A'", assembly)

    def test_if_then_else_codegen(self):
        """Test code generation for if-then-else."""
        code = """
        func main() {
            if (true) then {
                int x = 1;
            } else {
                int y = 2;
            }
        }
        """
        assembly = self.compile(code)
        self.assertIn("JUMPC", assembly)
        self.assertIn("JUMP", assembly)


if __name__ == '__main__':
    unittest.main()
