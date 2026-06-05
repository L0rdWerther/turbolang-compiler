"""
Tests for semantic analyzer.
"""

import unittest
from lexer.lexer import Lexer
from parser.parser import Parser
from semantic.semantic_analyzer import SemanticAnalyzer, SemanticError


class TestSemanticAnalyzer(unittest.TestCase):
    """Test cases for Semantic Analyzer."""
    
    def analyze(self, code: str):
        """Helper to analyze code."""
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
    
    def test_undefined_variable(self):
        """Test error on undefined variable."""
        code = """
        func main() {
            print(x);
        }
        """
        with self.assertRaises(SemanticError):
            self.analyze(code)
    
    def test_duplicate_declaration(self):
        """Test error on duplicate variable declaration."""
        code = """
        func main() {
            int x = 1;
            int x = 2;
        }
        """
        with self.assertRaises(SemanticError):
            self.analyze(code)
    
    def test_missing_main(self):
        """Test error when main function is missing."""
        code = """
        func other() {
        }
        """
        with self.assertRaises(SemanticError):
            self.analyze(code)
    
    def test_type_mismatch_assignment(self):
        """Test error on type mismatch in assignment."""
        code = """
        func main() {
            int x = "hello";
        }
        """
        with self.assertRaises(SemanticError):
            self.analyze(code)
    
    def test_valid_int_to_float_conversion(self):
        """Test valid int to float conversion."""
        code = """
        func main() {
            float x = 1;
        }
        """
        # Should not raise
        self.analyze(code)
    
    def test_return_type_mismatch(self):
        """Test error on return type mismatch."""
        code = """
        func getValue() -> int {
            return "hello";
        }
        
        func main() {
        }
        """
        with self.assertRaises(SemanticError):
            self.analyze(code)
    
    def test_function_parameter_count(self):
        """Test error on function parameter count mismatch."""
        code = """
        func add(int a, int b) -> int {
            return a + b;
        }
        
        func main() {
            add(1);
        }
        """
        with self.assertRaises(SemanticError):
            self.analyze(code)
    
    def test_if_condition_type(self):
        """Test error when if condition is not bool."""
        code = """
        func main() {
            if (5) {
            }
        }
        """
        with self.assertRaises(SemanticError):
            self.analyze(code)
    
    def test_while_condition_type(self):
        """Test error when while condition is not bool."""
        code = """
        func main() {
            while (5) {
            }
        }
        """
        with self.assertRaises(SemanticError):
            self.analyze(code)
    
    def test_valid_program(self):
        """Test valid program."""
        code = """
        func add(int a, int b) -> int {
            return a + b;
        }
        
        func main() {
            int x = 5;
            int y = 10;
            int z = add(x, y);
            print(z);
        }
        """
        # Should not raise
        self.analyze(code)


if __name__ == '__main__':
    unittest.main()