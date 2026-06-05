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
        self.assertIn("HALT", assembly)
    
    def test_integer_literal(self):
        """Test code generation for integer literal."""
        code = """
        func main() {
            int x = 42;
        }
        """
        assembly = self.compile(code)
        self.assertIn("PUSH 42", assembly)
    
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
        self.assertIn("JZ", assembly)
    
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
        self.assertIn("JZ", assembly)
        self.assertIn("JMP", assembly)
    
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
        self.assertIn("CALL", assembly)


if __name__ == '__main__':
    unittest.main()