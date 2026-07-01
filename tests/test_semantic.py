import unittest
from lexer.lexer import Lexer
from parser.parser import Parser
from semantic.semantic_analyzer import SemanticAnalyzer, SemanticError

class TestSemanticAnalyzer(unittest.TestCase):

    def analyze(self, code: str):
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)

    def test_undefined_variable(self):
        code = '\n        func main() {\n            print(x);\n        }\n        '
        with self.assertRaises(SemanticError):
            self.analyze(code)

    def test_duplicate_declaration(self):
        code = '\n        func main() {\n            int x = 1;\n            int x = 2;\n        }\n        '
        with self.assertRaises(SemanticError):
            self.analyze(code)

    def test_missing_main(self):
        code = '\n        func other() {\n        }\n        '
        with self.assertRaises(SemanticError):
            self.analyze(code)

    def test_type_mismatch_assignment(self):
        code = '\n        func main() {\n            int x = "hello";\n        }\n        '
        with self.assertRaises(SemanticError):
            self.analyze(code)

    def test_valid_int_to_float_conversion(self):
        code = '\n        func main() {\n            float x = 1;\n        }\n        '
        self.analyze(code)

    def test_return_type_mismatch(self):
        code = '\n        func getValue() -> int {\n            return "hello";\n        }\n        \n        func main() {\n        }\n        '
        with self.assertRaises(SemanticError):
            self.analyze(code)

    def test_typed_function_without_return_fails(self):
        code = '\n        func getValue() -> int {\n            int x = 1;\n        }\n\n        func main() {\n        }\n        '
        with self.assertRaises(SemanticError):
            self.analyze(code)

    def test_procedure_returning_value_fails(self):
        code = '\n        func log() {\n            return 1;\n        }\n\n        func main() {\n        }\n        '
        with self.assertRaises(SemanticError):
            self.analyze(code)

    def test_function_parameter_count(self):
        code = '\n        func add(int a, int b) -> int {\n            return a + b;\n        }\n        \n        func main() {\n            add(1);\n        }\n        '
        with self.assertRaises(SemanticError):
            self.analyze(code)

    def test_if_condition_type(self):
        code = '\n        func main() {\n            if (5) {\n            }\n        }\n        '
        with self.assertRaises(SemanticError):
            self.analyze(code)

    def test_while_condition_type(self):
        code = '\n        func main() {\n            while (5) {\n            }\n        }\n        '
        with self.assertRaises(SemanticError):
            self.analyze(code)

    def test_do_while_condition_type(self):
        code = '\n        func main() {\n            do {\n                print(1);\n            } while (5);\n        }\n        '
        with self.assertRaises(SemanticError):
            self.analyze(code)

    def test_for_loop_requires_int_control_variable(self):
        code = '\n        func main() {\n            float i = 0.0;\n            for i = 1 to 3 {\n                print(i);\n            }\n        }\n        '
        with self.assertRaises(SemanticError):
            self.analyze(code)

    def test_valid_counted_and_do_while_loops(self):
        code = '\n        func main() {\n            int i = 0;\n            do {\n                i = i + 1;\n            } while (i < 3);\n            for i = 1 to 3 {\n                print(i);\n            }\n        }\n        '
        self.analyze(code)

    def test_valid_program(self):
        code = '\n        func add(int a, int b) -> int {\n            return a + b;\n        }\n        \n        func main() {\n            int x = 5;\n            int y = 10;\n            int z = add(x, y);\n            print(z);\n        }\n        '
        self.analyze(code)
if __name__ == '__main__':
    unittest.main()
