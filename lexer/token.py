from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, Optional

class TokenType(Enum):
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    CHAR = auto()
    TRUE = auto()
    FALSE = auto()
    IDENTIFIER = auto()
    FUNC = auto()
    IF = auto()
    THEN = auto()
    ELSE = auto()
    WHILE = auto()
    DO = auto()
    FOR = auto()
    TO = auto()
    RETURN = auto()
    INT = auto()
    FLOAT_TYPE = auto()
    CHAR_TYPE = auto()
    BOOL = auto()
    PRINT = auto()
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    MODULO = auto()
    ASSIGN = auto()
    EQ = auto()
    NE = auto()
    LT = auto()
    GT = auto()
    LE = auto()
    GE = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    SEMICOLON = auto()
    COMMA = auto()
    ARROW = auto()
    COLON = auto()
    EOF = auto()
    NEWLINE = auto()

@dataclass
class Token:
    type: TokenType
    value: Any
    line: int
    column: int
    length: int

    def __repr__(self) -> str:
        return f'Token({self.type.name}, {repr(self.value)}, {self.line}, {self.column})'

    def __str__(self) -> str:
        return f'{self.type.name}:{self.value}'
