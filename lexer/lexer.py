from typing import List, Optional
from lexer.token import Token, TokenType
from lexer.keywords import is_keyword, get_keyword_token_type

class LexError(Exception):
    pass

class Lexer:

    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []

    def current_char(self) -> Optional[str]:
        if self.position < len(self.source):
            return self.source[self.position]
        return None

    def peek_char(self, offset: int=1) -> Optional[str]:
        pos = self.position + offset
        if pos < len(self.source):
            return self.source[pos]
        return None

    def advance(self) -> Optional[str]:
        if self.position < len(self.source):
            char = self.source[self.position]
            self.position += 1
            if char == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            return char
        return None

    def skip_whitespace(self):
        while self.current_char() and self.current_char() in ' \t\r':
            self.advance()

    def skip_comment(self):
        if self.current_char() == '/' and self.peek_char() == '/':
            while self.current_char() and self.current_char() != '\n':
                self.advance()

    def read_number(self) -> Token:
        start_line = self.line
        start_column = self.column
        start_pos = self.position
        num_str = ''
        while self.current_char() and self.current_char().isdigit():
            num_str += self.advance()
        is_float = False
        if self.current_char() == '.' and self.peek_char() and self.peek_char().isdigit():
            is_float = True
            num_str += self.advance()
            while self.current_char() and self.current_char().isdigit():
                num_str += self.advance()
        length = self.position - start_pos
        if is_float:
            return Token(TokenType.FLOAT, float(num_str), start_line, start_column, length)
        else:
            return Token(TokenType.INTEGER, int(num_str), start_line, start_column, length)

    def read_identifier_or_keyword(self) -> Token:
        start_line = self.line
        start_column = self.column
        start_pos = self.position
        word = ''
        while self.current_char() and (self.current_char().isalnum() or self.current_char() == '_'):
            word += self.advance()
        length = self.position - start_pos
        if is_keyword(word):
            token_type = get_keyword_token_type(word)
            if token_type == TokenType.TRUE:
                return Token(token_type, True, start_line, start_column, length)
            elif token_type == TokenType.FALSE:
                return Token(token_type, False, start_line, start_column, length)
            return Token(token_type, word, start_line, start_column, length)
        else:
            return Token(TokenType.IDENTIFIER, word, start_line, start_column, length)

    def read_string(self) -> Token:
        start_line = self.line
        start_column = self.column
        start_pos = self.position
        quote = self.advance()
        string_val = ''
        while self.current_char() and self.current_char() != quote:
            if self.current_char() == '\\':
                self.advance()
                escape_char = self.current_char()
                if escape_char == 'n':
                    string_val += '\n'
                    self.advance()
                elif escape_char == 't':
                    string_val += '\t'
                    self.advance()
                elif escape_char == 'r':
                    string_val += '\r'
                    self.advance()
                elif escape_char == '\\':
                    string_val += '\\'
                    self.advance()
                elif escape_char == quote:
                    string_val += quote
                    self.advance()
                else:
                    string_val += self.advance()
            else:
                string_val += self.advance()
        if not self.current_char():
            raise LexError(f'Unterminated string at line {start_line}, column {start_column}')
        self.advance()
        length = self.position - start_pos
        return Token(TokenType.STRING, string_val, start_line, start_column, length)

    def read_char(self) -> Token:
        start_line = self.line
        start_column = self.column
        start_pos = self.position
        self.advance()
        if not self.current_char():
            raise LexError(f'Unterminated char at line {start_line}, column {start_column}')
        char_val = ''
        if self.current_char() == '\\':
            self.advance()
            escape_char = self.current_char()
            if escape_char == 'n':
                char_val = '\n'
            elif escape_char == 't':
                char_val = '\t'
            elif escape_char == 'r':
                char_val = '\r'
            elif escape_char == '\\':
                char_val = '\\'
            else:
                char_val = escape_char
            self.advance()
        else:
            char_val = self.advance()
        if self.current_char() != "'":
            raise LexError(f'Unterminated char at line {start_line}, column {start_column}')
        self.advance()
        length = self.position - start_pos
        return Token(TokenType.CHAR, char_val, start_line, start_column, length)

    def tokenize(self) -> List[Token]:
        while self.position < len(self.source):
            self.skip_whitespace()
            if self.position >= len(self.source):
                break
            if self.current_char() == '/' and self.peek_char() == '/':
                self.skip_comment()
                continue
            current = self.current_char()
            line = self.line
            column = self.column
            if current.isdigit():
                self.tokens.append(self.read_number())
            elif current.isalpha() or current == '_':
                self.tokens.append(self.read_identifier_or_keyword())
            elif current == '"':
                self.tokens.append(self.read_string())
            elif current == "'":
                self.tokens.append(self.read_char())
            elif current == '+':
                self.advance()
                self.tokens.append(Token(TokenType.PLUS, '+', line, column, 1))
            elif current == '-':
                self.advance()
                if self.current_char() == '>':
                    self.advance()
                    self.tokens.append(Token(TokenType.ARROW, '->', line, column, 2))
                else:
                    self.tokens.append(Token(TokenType.MINUS, '-', line, column, 1))
            elif current == '*':
                self.advance()
                self.tokens.append(Token(TokenType.MULTIPLY, '*', line, column, 1))
            elif current == '/':
                self.advance()
                self.tokens.append(Token(TokenType.DIVIDE, '/', line, column, 1))
            elif current == '%':
                self.advance()
                self.tokens.append(Token(TokenType.MODULO, '%', line, column, 1))
            elif current == '=':
                self.advance()
                if self.current_char() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.EQ, '==', line, column, 2))
                else:
                    self.tokens.append(Token(TokenType.ASSIGN, '=', line, column, 1))
            elif current == '!':
                self.advance()
                if self.current_char() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.NE, '!=', line, column, 2))
                else:
                    self.tokens.append(Token(TokenType.NOT, '!', line, column, 1))
            elif current == '<':
                self.advance()
                if self.current_char() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.LE, '<=', line, column, 2))
                else:
                    self.tokens.append(Token(TokenType.LT, '<', line, column, 1))
            elif current == '>':
                self.advance()
                if self.current_char() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.GE, '>=', line, column, 2))
                else:
                    self.tokens.append(Token(TokenType.GT, '>', line, column, 1))
            elif current == '&':
                self.advance()
                if self.current_char() == '&':
                    self.advance()
                    self.tokens.append(Token(TokenType.AND, '&&', line, column, 2))
                else:
                    raise LexError(f"Unexpected character '&' at line {line}, column {column}")
            elif current == '|':
                self.advance()
                if self.current_char() == '|':
                    self.advance()
                    self.tokens.append(Token(TokenType.OR, '||', line, column, 2))
                else:
                    raise LexError(f"Unexpected character '|' at line {line}, column {column}")
            elif current == '(':
                self.advance()
                self.tokens.append(Token(TokenType.LPAREN, '(', line, column, 1))
            elif current == ')':
                self.advance()
                self.tokens.append(Token(TokenType.RPAREN, ')', line, column, 1))
            elif current == '{':
                self.advance()
                self.tokens.append(Token(TokenType.LBRACE, '{', line, column, 1))
            elif current == '}':
                self.advance()
                self.tokens.append(Token(TokenType.RBRACE, '}', line, column, 1))
            elif current == '[':
                self.advance()
                self.tokens.append(Token(TokenType.LBRACKET, '[', line, column, 1))
            elif current == ']':
                self.advance()
                self.tokens.append(Token(TokenType.RBRACKET, ']', line, column, 1))
            elif current == ';':
                self.advance()
                self.tokens.append(Token(TokenType.SEMICOLON, ';', line, column, 1))
            elif current == ',':
                self.advance()
                self.tokens.append(Token(TokenType.COMMA, ',', line, column, 1))
            elif current == ':':
                self.advance()
                self.tokens.append(Token(TokenType.COLON, ':', line, column, 1))
            elif current == '\n':
                self.advance()
            else:
                raise LexError(f"Unexpected character '{current}' at line {line}, column {column}")
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column, 0))
        return self.tokens
