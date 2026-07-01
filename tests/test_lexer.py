import unittest
from lexer.lexer import Lexer, LexError
from lexer.token import TokenType

class TestLexer(unittest.TestCase):

    def test_integer_literal(self):
        lexer = Lexer('42')
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.INTEGER)
        self.assertEqual(tokens[0].value, 42)

    def test_float_literal(self):
        lexer = Lexer('3.14')
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.FLOAT)
        self.assertAlmostEqual(tokens[0].value, 3.14)

    def test_string_literal(self):
        lexer = Lexer('"hello"')
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.STRING)
        self.assertEqual(tokens[0].value, 'hello')

    def test_identifier(self):
        lexer = Lexer('variable')
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[0].value, 'variable')

    def test_keyword_func(self):
        lexer = Lexer('func')
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.FUNC)

    def test_keyword_if(self):
        lexer = Lexer('if')
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.IF)

    def test_arithmetic_operators(self):
        lexer = Lexer('+ - * / %')
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.PLUS)
        self.assertEqual(tokens[1].type, TokenType.MINUS)
        self.assertEqual(tokens[2].type, TokenType.MULTIPLY)
        self.assertEqual(tokens[3].type, TokenType.DIVIDE)
        self.assertEqual(tokens[4].type, TokenType.MODULO)

    def test_comparison_operators(self):
        lexer = Lexer('== != < > <= >=')
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.EQ)
        self.assertEqual(tokens[1].type, TokenType.NE)
        self.assertEqual(tokens[2].type, TokenType.LT)
        self.assertEqual(tokens[3].type, TokenType.GT)
        self.assertEqual(tokens[4].type, TokenType.LE)
        self.assertEqual(tokens[5].type, TokenType.GE)

    def test_logical_operators(self):
        lexer = Lexer('&& || !')
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.AND)
        self.assertEqual(tokens[1].type, TokenType.OR)
        self.assertEqual(tokens[2].type, TokenType.NOT)

    def test_delimiters(self):
        lexer = Lexer('( ) { } [ ] ; , -> :')
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.LPAREN)
        self.assertEqual(tokens[1].type, TokenType.RPAREN)
        self.assertEqual(tokens[2].type, TokenType.LBRACE)
        self.assertEqual(tokens[3].type, TokenType.RBRACE)
        self.assertEqual(tokens[4].type, TokenType.LBRACKET)
        self.assertEqual(tokens[5].type, TokenType.RBRACKET)
        self.assertEqual(tokens[6].type, TokenType.SEMICOLON)
        self.assertEqual(tokens[7].type, TokenType.COMMA)
        self.assertEqual(tokens[8].type, TokenType.ARROW)
        self.assertEqual(tokens[9].type, TokenType.COLON)

    def test_line_tracking(self):
        lexer = Lexer('x\ny')
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].line, 1)
        self.assertEqual(tokens[1].line, 2)

    def test_unterminated_string(self):
        lexer = Lexer('"hello')
        with self.assertRaises(LexError):
            lexer.tokenize()

    def test_invalid_character(self):
        lexer = Lexer('@')
        with self.assertRaises(LexError):
            lexer.tokenize()

    def test_bool_literal(self):
        lexer = Lexer('true false')
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.TRUE)
        self.assertTrue(tokens[0].value)
        self.assertEqual(tokens[1].type, TokenType.FALSE)
        self.assertFalse(tokens[1].value)

    def test_loop_keywords(self):
        lexer = Lexer('do for to')
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.DO)
        self.assertEqual(tokens[1].type, TokenType.FOR)
        self.assertEqual(tokens[2].type, TokenType.TO)
if __name__ == '__main__':
    unittest.main()
