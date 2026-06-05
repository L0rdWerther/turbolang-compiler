"""
Tests for parser.
"""

import unittest
from lexer.lexer import Lexer
from parser.parser import Parser, ParseError
from parser.ast_nodes import *


class TestParser(unittest.TestCase):
    """Test cases for Parser."""
    
    def parse(self, code: str) -> Program:
        """Helper to parse code."""
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        return parser.parse()
    
    def test_simple_function(self):
        """Test parsing simple function."""
        code = """
        func main() {
        }
        """
        program = self.parse(code)
        self.assertEqual(len(program.functions), 1)
        self.assertEqual(program.functions[0].name, "main")
    
    def test_function_with_parameters(self):
        """Test parsing function with parameters."""
        code = """
        func add(int a, int b) -> int {
            return a + b;
        }
        """
        program = self.parse(code)
        func = program.functions[0]
        self.assertEqual(func.name, "add")
        self.assertEqual(len(func.parameters), 2)
        self.assertEqual(func.parameters[0].name, "a")
        self.assertEqual(func.parameters[1].name, "b")
        self.assertEqual(func.return_type, "int")
    
    def test_variable_declaration(self):
        """Test parsing variable declaration."""
        code = """
        func main() {
            int x = 10;
        }
        """
        program = self.parse(code)
        func = program.functions[0]
        stmt = func.body.statements[0]
        self.assertIsInstance(stmt, VariableDecl)
        self.assertEqual(stmt.name, "x")
        self.assertEqual(stmt.type_name, "int")
    
    def test_assignment(self):
        """Test parsing assignment."""
        code = """
        func main() {
            int x;
            x = 42;
        }
        """
        program = self.parse(code)
        func = program.functions[0]
        stmt = func.body.statements[1]
        self.assertIsInstance(stmt, Assignment)
        self.assertEqual(stmt.target, "x")
    
    def test_if_statement(self):
        """Test parsing if statement."""
        code = """
        func main() {
            if (true) {
                int x = 1;
            }
        }
        """
        program = self.parse(code)
        func = program.functions[0]
        stmt = func.body.statements[0]
        self.assertIsInstance(stmt, IfStatement)
    
    def test_if_else_statement(self):
        """Test parsing if-else statement."""
        code = """
        func main() {
            if (true) {
                int x = 1;
            } else {
                int y = 2;
            }
        }
        """
        program = self.parse(code)
        func = program.functions[0]
        stmt = func.body.statements[0]
        self.assertIsInstance(stmt, IfStatement)
        self.assertIsNotNone(stmt.else_block)

    def test_if_then_else_statement(self):
        """Test parsing if-then-else statement."""
        code = """
        func main() {
            if (true) then {
                int x = 1;
            } else {
                int y = 2;
            }
        }
        """
        program = self.parse(code)
        stmt = program.functions[0].body.statements[0]
        self.assertIsInstance(stmt, IfStatement)
        self.assertIsNotNone(stmt.else_block)

    def test_if_entao_statement(self):
        """Test parsing Portuguese then alias without else alias."""
        code = """
        func main() {
            if (true) entao {
                int x = 1;
            }
        }
        """
        program = self.parse(code)
        stmt = program.functions[0].body.statements[0]
        self.assertIsInstance(stmt, IfStatement)

    def test_if_entao_senao_statement(self):
        """Test parsing Portuguese then/else aliases."""
        code = """
        func main() {
            if (true) entao {
                int x = 1;
            } senao {
                int y = 2;
            }
        }
        """
        program = self.parse(code)
        stmt = program.functions[0].body.statements[0]
        self.assertIsInstance(stmt, IfStatement)
        self.assertIsNotNone(stmt.else_block)

    def test_if_entao_senao_accented_statement(self):
        """Test parsing accented Portuguese then/else aliases."""
        code = """
        func main() {
            if (true) então {
                int x = 1;
            } senão {
                int y = 2;
            }
        }
        """
        program = self.parse(code)
        stmt = program.functions[0].body.statements[0]
        self.assertIsInstance(stmt, IfStatement)
        self.assertIsNotNone(stmt.else_block)
    
    def test_while_statement(self):
        """Test parsing while loop."""
        code = """
        func main() {
            while (true) {
                int x = 1;
            }
        }
        """
        program = self.parse(code)
        func = program.functions[0]
        stmt = func.body.statements[0]
        self.assertIsInstance(stmt, WhileStatement)
    
    def test_return_statement(self):
        """Test parsing return statement."""
        code = """
        func add(int a, int b) -> int {
            return a + b;
        }
        """
        program = self.parse(code)
        func = program.functions[0]
        stmt = func.body.statements[0]
        self.assertIsInstance(stmt, ReturnStatement)
    
    def test_function_call(self):
        """Test parsing function call."""
        code = """
        func main() {
            add(1, 2);
        }
        """
        program = self.parse(code)
        func = program.functions[0]
        stmt = func.body.statements[0]
        self.assertIsInstance(stmt, ExpressionStatement)
        self.assertIsInstance(stmt.expression, FunctionCall)
        self.assertEqual(stmt.expression.name, "add")
        self.assertEqual(len(stmt.expression.arguments), 2)
    
    def test_binary_expression(self):
        """Test parsing binary expression."""
        code = """
        func main() {
            int x = 1 + 2;
        }
        """
        program = self.parse(code)
        func = program.functions[0]
        stmt = func.body.statements[0]
        self.assertIsInstance(stmt.initial_value, BinaryExpression)
        self.assertEqual(stmt.initial_value.operator, "+")
    
    def test_unary_expression(self):
        """Test parsing unary expression."""
        code = """
        func main() {
            bool x = !true;
        }
        """
        program = self.parse(code)
        func = program.functions[0]
        stmt = func.body.statements[0]
        self.assertIsInstance(stmt.initial_value, UnaryExpression)
        self.assertEqual(stmt.initial_value.operator, "!")
    
    def test_missing_semicolon(self):
        """Test error on missing semicolon."""
        code = """
        func main() {
            int x = 10
        }
        """
        with self.assertRaises(ParseError):
            self.parse(code)
    
    def test_missing_brace(self):
        """Test error on missing brace."""
        code = """
        func main() {
        """
        with self.assertRaises(ParseError):
            self.parse(code)


if __name__ == '__main__':
    unittest.main()
