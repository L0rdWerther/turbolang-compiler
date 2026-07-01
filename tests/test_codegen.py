import unittest
from lexer.lexer import Lexer
from parser.parser import Parser
from semantic.semantic_analyzer import SemanticAnalyzer
from codegen.code_generator import CodeGenerator

class TestCodeGenerator(unittest.TestCase):

    def compile(self, code: str) -> str:
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        codegen = CodeGenerator()
        return codegen.generate(program)

    def test_simple_main(self):
        code = '\n        func main() {\n        }\n        '
        assembly = self.compile(code)
        self.assertIn('STOP', assembly)
        self.assertIn('JUMPIND', assembly)

    def test_integer_literal(self):
        code = '\n        func main() {\n            int x = 42;\n        }\n        '
        assembly = self.compile(code)
        self.assertIn('PUSHIMM 42', assembly)

    def test_addition(self):
        code = '\n        func add(int a, int b) -> int {\n            return a + b;\n        }\n        \n        func main() {\n        }\n        '
        assembly = self.compile(code)
        self.assertIn('ADD', assembly)

    def test_if_statement(self):
        code = '\n        func main() {\n            if (true) {\n                int x = 1;\n            }\n        }\n        '
        assembly = self.compile(code)
        self.assertIn('JUMPC', assembly)

    def test_while_loop(self):
        code = '\n        func main() {\n            while (true) {\n                int x = 1;\n            }\n        }\n        '
        assembly = self.compile(code)
        self.assertIn('JUMPC', assembly)
        self.assertIn('JUMP', assembly)

    def test_do_while_loop(self):
        code = '\n        func main() {\n            int x = 0;\n            do {\n                x = x + 1;\n            } while (x < 3);\n        }\n        '
        assembly = self.compile(code)
        self.assertIn('JUMPC', assembly)
        self.assertIn('LESS', assembly)

    def test_counted_for_loop(self):
        code = '\n        func main() {\n            int i = 0;\n            for i = 1 to 3 {\n                print(i);\n            }\n        }\n        '
        assembly = self.compile(code)
        self.assertIn('GREATER', assembly)
        self.assertIn('JUMPC', assembly)
        self.assertIn('WRITE', assembly)

    def test_function_call(self):
        code = '\n        func getValue() -> int {\n            return 42;\n        }\n        \n        func main() {\n            getValue();\n        }\n        '
        assembly = self.compile(code)
        self.assertIn('JSR', assembly)

    def test_main_entry_jump_when_not_first_function(self):
        code = '\n        func helper() -> int {\n            return 1;\n        }\n\n        func main() {\n            print(helper());\n        }\n        '
        assembly = self.compile(code)
        first_line = assembly.splitlines()[0]
        self.assertEqual(first_line, 'ADDSP 1')
        self.assertIn('JSR FUNCTION_main', assembly)
        self.assertIn('JSR FUNCTION_helper', assembly)

    def test_call_has_argument_count_and_return_flag(self):
        code = '\n        func add(int a, int b) -> int {\n            return a + b;\n        }\n\n        func main() {\n            print(add(1, 2));\n        }\n        '
        assembly = self.compile(code)
        self.assertIn('JSR FUNCTION_add', assembly)
        self.assertIn('POPFBR', assembly)
        self.assertIn('ADDSP -2', assembly)
        self.assertIn('JUMPIND', assembly)

    def test_float_literal_uses_float32_bits(self):
        code = '\n        func main() {\n            float x = 1.5;\n        }\n        '
        assembly = self.compile(code)
        self.assertIn('PUSHIMMF 1.5', assembly)

    def test_int_to_float_conversion_and_float_operation(self):
        code = '\n        func main() {\n            float x = 1 + 2.5;\n        }\n        '
        assembly = self.compile(code)
        self.assertIn('ITOF', assembly)
        self.assertIn('ADDF', assembly)

    def test_char_literal_uses_numeric_code(self):
        code = "\n        func main() {\n            char c = 'A';\n        }\n        "
        assembly = self.compile(code)
        self.assertIn("PUSHIMMCH 'A'", assembly)

    def test_if_then_else_codegen(self):
        code = '\n        func main() {\n            if (true) then {\n                int x = 1;\n            } else {\n                int y = 2;\n            }\n        }\n        '
        assembly = self.compile(code)
        self.assertIn('JUMPC', assembly)
        self.assertIn('JUMP', assembly)
if __name__ == '__main__':
    unittest.main()
