import unittest
from lexer.lexer import Lexer
from parser.parser import Parser, ParseError
from parser.ast_nodes import *

class TestParser(unittest.TestCase):

    def parse(self, code: str) -> Program:
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        return parser.parse()

    def test_simple_function(self):
        code = '\n        func main() {\n        }\n        '
        program = self.parse(code)
        self.assertEqual(len(program.functions), 1)
        self.assertEqual(program.functions[0].name, 'main')

    def test_function_with_parameters(self):
        code = '\n        func add(int a, int b) -> int {\n            return a + b;\n        }\n        '
        program = self.parse(code)
        func = program.functions[0]
        self.assertEqual(func.name, 'add')
        self.assertEqual(len(func.parameters), 2)
        self.assertEqual(func.parameters[0].name, 'a')
        self.assertEqual(func.parameters[1].name, 'b')
        self.assertEqual(func.return_type, 'int')

    def test_variable_declaration(self):
        code = '\n        func main() {\n            int x = 10;\n        }\n        '
        program = self.parse(code)
        func = program.functions[0]
        stmt = func.body.statements[0]
        self.assertIsInstance(stmt, VariableDecl)
        self.assertEqual(stmt.name, 'x')
        self.assertEqual(stmt.type_name, 'int')

    def test_assignment(self):
        code = '\n        func main() {\n            int x;\n            x = 42;\n        }\n        '
        program = self.parse(code)
        func = program.functions[0]
        stmt = func.body.statements[1]
        self.assertIsInstance(stmt, Assignment)
        self.assertEqual(stmt.target, 'x')

    def test_if_statement(self):
        code = '\n        func main() {\n            if (true) {\n                int x = 1;\n            }\n        }\n        '
        program = self.parse(code)
        func = program.functions[0]
        stmt = func.body.statements[0]
        self.assertIsInstance(stmt, IfStatement)

    def test_if_else_statement(self):
        code = '\n        func main() {\n            if (true) {\n                int x = 1;\n            } else {\n                int y = 2;\n            }\n        }\n        '
        program = self.parse(code)
        func = program.functions[0]
        stmt = func.body.statements[0]
        self.assertIsInstance(stmt, IfStatement)
        self.assertIsNotNone(stmt.else_block)

    def test_if_then_else_statement(self):
        code = '\n        func main() {\n            if (true) then {\n                int x = 1;\n            } else {\n                int y = 2;\n            }\n        }\n        '
        program = self.parse(code)
        stmt = program.functions[0].body.statements[0]
        self.assertIsInstance(stmt, IfStatement)
        self.assertIsNotNone(stmt.else_block)

    def test_while_statement(self):
        code = '\n        func main() {\n            while (true) {\n                int x = 1;\n            }\n        }\n        '
        program = self.parse(code)
        func = program.functions[0]
        stmt = func.body.statements[0]
        self.assertIsInstance(stmt, WhileStatement)

    def test_do_while_statement(self):
        code = '\n        func main() {\n            do {\n                print(1);\n            } while (false);\n        }\n        '
        program = self.parse(code)
        stmt = program.functions[0].body.statements[0]
        self.assertIsInstance(stmt, DoWhileStatement)

    def test_counted_for_statement(self):
        code = '\n        func main() {\n            int i = 0;\n            for i = 1 to 3 {\n                print(i);\n            }\n        }\n        '
        program = self.parse(code)
        stmt = program.functions[0].body.statements[1]
        self.assertIsInstance(stmt, ForStatement)
        self.assertEqual(stmt.variable, 'i')

    def test_return_statement(self):
        code = '\n        func add(int a, int b) -> int {\n            return a + b;\n        }\n        '
        program = self.parse(code)
        func = program.functions[0]
        stmt = func.body.statements[0]
        self.assertIsInstance(stmt, ReturnStatement)

    def test_function_call(self):
        code = '\n        func main() {\n            add(1, 2);\n        }\n        '
        program = self.parse(code)
        func = program.functions[0]
        stmt = func.body.statements[0]
        self.assertIsInstance(stmt, ExpressionStatement)
        self.assertIsInstance(stmt.expression, FunctionCall)
        self.assertEqual(stmt.expression.name, 'add')
        self.assertEqual(len(stmt.expression.arguments), 2)

    def test_binary_expression(self):
        code = '\n        func main() {\n            int x = 1 + 2;\n        }\n        '
        program = self.parse(code)
        func = program.functions[0]
        stmt = func.body.statements[0]
        self.assertIsInstance(stmt.initial_value, BinaryExpression)
        self.assertEqual(stmt.initial_value.operator, '+')

    def test_unary_expression(self):
        code = '\n        func main() {\n            bool x = !true;\n        }\n        '
        program = self.parse(code)
        func = program.functions[0]
        stmt = func.body.statements[0]
        self.assertIsInstance(stmt.initial_value, UnaryExpression)
        self.assertEqual(stmt.initial_value.operator, '!')

    def test_missing_semicolon(self):
        code = '\n        func main() {\n            int x = 10\n        }\n        '
        with self.assertRaises(ParseError):
            self.parse(code)

    def test_missing_brace(self):
        code = '\n        func main() {\n        '
        with self.assertRaises(ParseError):
            self.parse(code)
if __name__ == '__main__':
    unittest.main()
